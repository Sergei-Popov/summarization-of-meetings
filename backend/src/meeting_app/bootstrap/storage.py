from collections.abc import Callable
from pathlib import Path

from meeting_app.platform.storage.database import upgrade_database
from meeting_app.platform.storage.sqlite_preflight import (
    StorageError,
    StorageInitializationError,
    run_sqlite_preflight,
)

Preflight = Callable[[Path], None]
DatabaseInitializer = Callable[[Path], None]


def prepare_storage(
    data_directory: Path,
    *,
    preflight: Preflight = run_sqlite_preflight,
    database_initializer: DatabaseInitializer = upgrade_database,
) -> None:
    preflight(data_directory)
    try:
        database_initializer(data_directory / "meeting-app.sqlite3")
    except StorageError:
        raise
    except Exception as error:
        raise StorageInitializationError() from error
