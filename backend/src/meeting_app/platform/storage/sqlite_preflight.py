from __future__ import annotations

import ctypes
import os
import sqlite3
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Final, Protocol, cast

REQUIRED_SQLITE_VERSION: Final = "3.53.4"
DENIED_FILESYSTEMS: Final = frozenset({"nfs", "nfs4", "cifs", "smbfs", "sshfs", "fuse.sshfs"})
UNKNOWN_FILESYSTEMS: Final = frozenset({"", "unknown"})


class CursorLike(Protocol):
    def fetchone(self) -> tuple[object, ...] | None: ...


class ConnectionLike(Protocol):
    def execute(self, statement: str) -> CursorLike: ...

    def commit(self) -> None: ...

    def close(self) -> None: ...


FilesystemDetector = Callable[[Path], str]
ConnectionFactory = Callable[[Path], ConnectionLike]


class StorageError(RuntimeError):
    def __init__(self, code: str, *, stage: str) -> None:
        super().__init__(code)
        self.code = code
        self.stage = stage
        self.retryable = False
        self.cleanup_failed = False


class StoragePreflightError(StorageError):
    def __init__(self, code: str) -> None:
        super().__init__(code, stage="storage_preflight")


class StorageInitializationError(StorageError):
    def __init__(self, code: str = "storage.initialization_failed") -> None:
        super().__init__(code, stage="storage_initialization")


def _unescape_mount_path(value: str) -> str:
    return (
        value.replace("\\040", " ")
        .replace("\\011", "\t")
        .replace("\\012", "\n")
        .replace("\\134", "\\")
    )


def _filesystem_from_mountinfo(path: Path, mountinfo: str) -> str:
    resolved = path.resolve()
    best_match: tuple[int, str] | None = None
    for line in mountinfo.splitlines():
        fields = line.split()
        try:
            separator = fields.index("-")
            mountpoint = Path(_unescape_mount_path(fields[4]))
            filesystem = fields[separator + 1].lower()
        except (IndexError, ValueError):
            continue
        try:
            resolved.relative_to(mountpoint)
        except ValueError:
            continue
        candidate = (len(str(mountpoint)), filesystem)
        if best_match is None or candidate[0] > best_match[0]:
            best_match = candidate
    return best_match[1] if best_match else "unknown"


def _linux_filesystem(path: Path) -> str:
    try:
        mountinfo = Path("/proc/self/mountinfo").read_text(encoding="utf-8")
    except OSError:
        return "unknown"
    return _filesystem_from_mountinfo(path, mountinfo)


def _windows_filesystem(path: Path) -> str:
    try:
        drive = path.resolve().drive + "\\"
        if not drive.strip("\\"):
            return "unknown"
        get_drive_type = ctypes.windll.kernel32.GetDriveTypeW  # type: ignore[attr-defined]
        if get_drive_type(drive) == 4:  # DRIVE_REMOTE
            return "cifs"
        name_buffer = ctypes.create_unicode_buffer(256)
        ok = ctypes.windll.kernel32.GetVolumeInformationW(  # type: ignore[attr-defined]
            drive,
            None,
            0,
            None,
            None,
            None,
            name_buffer,
            len(name_buffer),
        )
    except (AttributeError, OSError):
        return "unknown"
    return name_buffer.value.lower() if ok else "unknown"


def _macos_filesystem(path: Path) -> str:
    try:
        result = subprocess.run(
            ["stat", "-f", "%T", str(path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "unknown"
    return result.stdout.strip().lower() or "unknown"


def detect_filesystem(path: Path) -> str:
    if sys.platform.startswith("linux"):
        return _linux_filesystem(path)
    if sys.platform == "win32":
        return _windows_filesystem(path)
    if sys.platform == "darwin":
        return _macos_filesystem(path)
    return "unknown"


def _sqlite_connect(path: Path) -> ConnectionLike:
    return cast(ConnectionLike, sqlite3.connect(path))


def _cleanup_candidates(path: Path) -> tuple[Path, ...]:
    return (
        path,
        Path(f"{path}-journal"),
        Path(f"{path}-wal"),
        Path(f"{path}-shm"),
    )


def _close_and_cleanup(connection: ConnectionLike | None, path: Path | None) -> bool:
    failed = False
    if connection is not None:
        try:
            connection.close()
        except Exception:
            failed = True
    if path is not None:
        for candidate in _cleanup_candidates(path):
            try:
                candidate.unlink()
            except FileNotFoundError:
                continue
            except OSError:
                failed = True
    return failed


def _execute(connection: ConnectionLike, statement: str, *, code: str) -> CursorLike:
    try:
        return connection.execute(statement)
    except (OSError, sqlite3.Error) as error:
        raise StoragePreflightError(code) from error


def _fetchone(cursor: CursorLike, *, code: str) -> tuple[object, ...] | None:
    try:
        return cursor.fetchone()
    except (OSError, sqlite3.Error) as error:
        raise StoragePreflightError(code) from error


def run_sqlite_preflight(
    target_directory: Path,
    *,
    filesystem_detector: FilesystemDetector = detect_filesystem,
    connection_factory: ConnectionFactory = _sqlite_connect,
    required_version: str = REQUIRED_SQLITE_VERSION,
) -> None:
    try:
        target_directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise StoragePreflightError("storage.io_failed") from error

    try:
        filesystem = filesystem_detector(target_directory).lower().strip()
    except Exception as error:
        raise StoragePreflightError("storage.filesystem_unknown") from error
    if filesystem in UNKNOWN_FILESYSTEMS:
        raise StoragePreflightError("storage.filesystem_unknown")
    if filesystem in DENIED_FILESYSTEMS:
        raise StoragePreflightError("storage.filesystem_unsupported")

    probe_path: Path | None = None
    connection: ConnectionLike | None = None
    primary_error: StoragePreflightError | None = None
    try:
        try:
            descriptor, raw_path = tempfile.mkstemp(
                prefix=".sqlite-preflight-",
                suffix=".sqlite3",
                dir=target_directory,
            )
            probe_path = Path(raw_path)
        except OSError as error:
            raise StoragePreflightError("storage.io_failed") from error
        try:
            os.close(descriptor)
        except OSError as error:
            raise StoragePreflightError("storage.io_failed") from error

        try:
            connection = connection_factory(probe_path)
        except (OSError, sqlite3.Error) as error:
            raise StoragePreflightError("storage.io_failed") from error

        version_row = _fetchone(
            _execute(
                connection,
                "SELECT sqlite_version()",
                code="storage.sqlite_version_unsupported",
            ),
            code="storage.sqlite_version_unsupported",
        )
        version = str(version_row[0]) if version_row else ""
        if version != required_version:
            raise StoragePreflightError("storage.sqlite_version_unsupported")

        _execute(
            connection,
            "CREATE VIRTUAL TABLE preflight_fts USING fts5(content)",
            code="storage.fts5_unavailable",
        )
        wal_row = _fetchone(
            _execute(
                connection,
                "PRAGMA journal_mode=wal",
                code="storage.wal_unavailable",
            ),
            code="storage.wal_unavailable",
        )
        wal_mode = str(wal_row[0]).lower() if wal_row else ""
        if wal_mode != "wal":
            raise StoragePreflightError("storage.wal_unavailable")
        _execute(
            connection,
            "INSERT INTO preflight_fts(content) VALUES ('ok')",
            code="storage.write_failed",
        )
        try:
            connection.commit()
        except (OSError, sqlite3.Error) as error:
            raise StoragePreflightError("storage.commit_failed") from error
    except StoragePreflightError as error:
        primary_error = error
    except Exception:
        primary_error = StoragePreflightError("storage.io_failed")

    cleanup_failed = _close_and_cleanup(connection, probe_path)
    if primary_error is not None:
        primary_error.cleanup_failed = cleanup_failed
        raise primary_error
    if cleanup_failed:
        raise StoragePreflightError("storage.cleanup_failed")
