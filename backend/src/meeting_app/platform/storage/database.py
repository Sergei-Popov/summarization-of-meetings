from __future__ import annotations

import os
import sqlite3
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Connection

from meeting_app.platform.storage.sqlite_preflight import StorageInitializationError

MigrationRunner = Callable[[Config, str], None]


@contextmanager
def _sqlite_connection(database_path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(database_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def _sidecars(path: Path) -> tuple[Path, ...]:
    return (Path(f"{path}-journal"), Path(f"{path}-wal"), Path(f"{path}-shm"))


def _remove_sidecars(path: Path) -> None:
    for sidecar in _sidecars(path):
        with suppress(FileNotFoundError):
            sidecar.unlink()


def _backup_existing(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    with _sqlite_connection(source) as source_connection:
        source_connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        with _sqlite_connection(destination) as destination_connection:
            source_connection.backup(destination_connection)


def _alembic_config(connection: Connection) -> Config:
    backend_root = Path(__file__).resolve().parents[4]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.attributes["connection"] = connection
    return config


def _verify_wal(connection: Connection) -> None:
    mode = connection.exec_driver_sql("PRAGMA journal_mode=WAL").scalar_one()
    if str(mode).lower() != "wal":
        raise StorageInitializationError("storage.product_wal_unavailable")
    connection.exec_driver_sql("PRAGMA synchronous=NORMAL")


def upgrade_database(
    database_path: Path,
    *,
    migration_runner: MigrationRunner = command.upgrade,
) -> None:
    staging_path: Path | None = None
    engine = None
    try:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, raw_path = tempfile.mkstemp(
            prefix=".meeting-app-init-",
            suffix=".sqlite3",
            dir=database_path.parent,
        )
        os.close(descriptor)
        staging_path = Path(raw_path)
        _backup_existing(database_path, staging_path)

        url = URL.create("sqlite", database=str(staging_path))
        engine = create_engine(url)
        with engine.begin() as connection:
            _verify_wal(connection)
            migration_runner(_alembic_config(connection), "head")
        with engine.connect() as connection:
            _verify_wal(connection)
            connection.exec_driver_sql("PRAGMA wal_checkpoint(TRUNCATE)")
        engine.dispose()
        engine = None

        with _sqlite_connection(staging_path) as verification:
            mode = verification.execute("PRAGMA journal_mode").fetchone()
            if mode is None or str(mode[0]).lower() != "wal":
                raise StorageInitializationError("storage.product_wal_unavailable")

        _remove_sidecars(database_path)
        os.replace(staging_path, database_path)
        staging_path = None
    except StorageInitializationError:
        raise
    except Exception as error:
        raise StorageInitializationError() from error
    finally:
        if engine is not None:
            engine.dispose()
        if staging_path is not None:
            with suppress(FileNotFoundError, OSError):
                staging_path.unlink()
            with suppress(OSError):
                _remove_sidecars(staging_path)
