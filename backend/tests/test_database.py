import sqlite3
from pathlib import Path
from typing import Any

import pytest
from alembic.config import Config
from meeting_app.platform.storage import StorageInitializationError
from meeting_app.platform.storage import database as database_module
from meeting_app.platform.storage.database import upgrade_database


class TrackingConnection(sqlite3.Connection):
    closed = False

    def close(self) -> None:
        self.closed = True
        super().close()


def _journal_mode(database: Path) -> str:
    with sqlite3.connect(database) as connection:
        row = connection.execute("PRAGMA journal_mode").fetchone()
    assert row is not None
    return str(row[0]).lower()


def test_alembic_seed_creates_product_schema_and_persists_wal(tmp_path: Path) -> None:
    database = tmp_path / "meeting-app.sqlite3"
    upgrade_database(database)

    with sqlite3.connect(database) as connection:
        marker = connection.execute(
            "SELECT value FROM schema_metadata WHERE key = 'seed'"
        ).fetchone()
        revision = connection.execute("SELECT version_num FROM alembic_version").fetchone()

    assert marker == ("1",)
    assert revision == ("0001_seed",)
    assert _journal_mode(database) == "wal"


def test_sqlalchemy_url_treats_question_mark_as_filename_data(tmp_path: Path) -> None:
    database = tmp_path / "meeting?notes.sqlite3"
    upgrade_database(database)

    assert database.is_file()
    assert not (tmp_path / "meeting").exists()
    assert _journal_mode(database) == "wal"


def test_database_connections_close_before_atomic_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database = tmp_path / "meeting-app.sqlite3"
    real_connect = sqlite3.connect
    real_replace = database_module.os.replace
    opened_connections: list[TrackingConnection] = []

    def tracking_connect(*args: Any, **kwargs: Any) -> TrackingConnection:
        kwargs.setdefault("factory", TrackingConnection)
        connection = real_connect(*args, **kwargs)
        assert isinstance(connection, TrackingConnection)
        opened_connections.append(connection)
        return connection

    def replace_after_connections_close(source: Path, destination: Path) -> None:
        assert opened_connections
        assert all(connection.closed for connection in opened_connections)
        real_replace(source, destination)

    monkeypatch.setattr(database_module.sqlite3, "connect", tracking_connect)
    monkeypatch.setattr(database_module.os, "replace", replace_after_connections_close)

    upgrade_database(database)

    assert database.is_file()


def test_failed_migration_does_not_publish_partial_new_database(tmp_path: Path) -> None:
    database = tmp_path / "meeting-app.sqlite3"

    def fail_migration(_config: Config, _revision: str) -> None:
        raise RuntimeError("migration leaked /private/path")

    with pytest.raises(StorageInitializationError) as caught:
        upgrade_database(database, migration_runner=fail_migration)

    assert caught.value.code == "storage.initialization_failed"
    assert str(caught.value) == "storage.initialization_failed"
    assert not database.exists()
    assert list(tmp_path.glob(".meeting-app-init-*")) == []


def test_failed_migration_preserves_existing_database(tmp_path: Path) -> None:
    database = tmp_path / "meeting-app.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
        connection.execute("INSERT INTO sentinel VALUES ('preserved')")
        connection.commit()

    def fail_migration(_config: Config, _revision: str) -> None:
        raise RuntimeError("migration failed")

    with pytest.raises(StorageInitializationError):
        upgrade_database(database, migration_runner=fail_migration)

    with sqlite3.connect(database) as connection:
        sentinel = connection.execute("SELECT value FROM sentinel").fetchone()
    assert sentinel == ("preserved",)
    assert list(tmp_path.glob(".meeting-app-init-*")) == []
