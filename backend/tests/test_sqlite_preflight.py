from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pytest
from meeting_app.bootstrap.storage import prepare_storage
from meeting_app.platform.storage import sqlite_preflight
from meeting_app.platform.storage.sqlite_preflight import (
    StorageInitializationError,
    StoragePreflightError,
    run_sqlite_preflight,
)


def _probe_files(path: Path) -> list[Path]:
    return list(path.glob(".sqlite-preflight-*"))


def test_preflight_uses_real_fts5_and_wal_then_removes_all_probe_files(tmp_path: Path) -> None:
    run_sqlite_preflight(
        tmp_path,
        filesystem_detector=lambda _path: "apfs",
        required_version=sqlite3.sqlite_version,
    )
    assert _probe_files(tmp_path) == []


def test_mountinfo_parser_uses_longest_mount_and_unescapes_path(tmp_path: Path) -> None:
    nested = tmp_path / "folder with space"
    nested.mkdir()
    escaped = str(nested).replace(" ", "\\040")
    mountinfo = f"1 0 0:1 / / rw - ext4 /dev/root rw\n2 1 0:2 / {escaped} rw - nfs4 host:/x rw"
    assert sqlite_preflight._filesystem_from_mountinfo(nested, mountinfo) == "nfs4"


def test_macos_detector_has_timeout_and_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def timeout(*_args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert kwargs["timeout"] == 2
        raise subprocess.TimeoutExpired("stat", 2)

    monkeypatch.setattr(sqlite_preflight.subprocess, "run", timeout)
    assert sqlite_preflight._macos_filesystem(tmp_path) == "unknown"


def test_platform_detector_routes_to_platform_implementation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(sqlite_preflight.sys, "platform", "darwin")
    monkeypatch.setattr(sqlite_preflight, "_macos_filesystem", lambda _path: "apfs")
    assert sqlite_preflight.detect_filesystem(tmp_path) == "apfs"

    monkeypatch.setattr(sqlite_preflight.sys, "platform", "linux")
    monkeypatch.setattr(sqlite_preflight, "_linux_filesystem", lambda _path: "ext4")
    assert sqlite_preflight.detect_filesystem(tmp_path) == "ext4"

    monkeypatch.setattr(sqlite_preflight.sys, "platform", "plan9")
    assert sqlite_preflight.detect_filesystem(tmp_path) == "unknown"


def test_windows_detector_fails_closed_when_win32_api_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delattr(sqlite_preflight.ctypes, "windll", raising=False)
    assert sqlite_preflight._windows_filesystem(tmp_path) == "unknown"


@pytest.mark.parametrize("filesystem", ["unknown", "", "nfs4", "cifs", "smbfs"])
def test_preflight_fails_closed_for_unknown_or_network_filesystem(
    tmp_path: Path, filesystem: str
) -> None:
    with pytest.raises(StoragePreflightError) as caught:
        run_sqlite_preflight(tmp_path, filesystem_detector=lambda _path: filesystem)
    expected = (
        "storage.filesystem_unknown"
        if filesystem in {"", "unknown"}
        else "storage.filesystem_unsupported"
    )
    assert caught.value.code == expected
    assert _probe_files(tmp_path) == []


def test_directory_and_probe_creation_fail_with_safe_io_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = tmp_path / "data"
    original_mkdir = Path.mkdir

    def failing_mkdir(path: Path, *args: object, **kwargs: object) -> None:
        if path == target:
            raise OSError("sensitive local path")
        original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", failing_mkdir)
    with pytest.raises(StoragePreflightError) as directory_error:
        run_sqlite_preflight(target, filesystem_detector=lambda _path: "ext4")
    assert directory_error.value.code == "storage.io_failed"

    monkeypatch.setattr(Path, "mkdir", original_mkdir)
    def failing_mkstemp(**_kwargs: object) -> tuple[int, str]:
        raise OSError("denied")

    monkeypatch.setattr(sqlite_preflight.tempfile, "mkstemp", failing_mkstemp)
    with pytest.raises(StoragePreflightError) as create_error:
        run_sqlite_preflight(tmp_path, filesystem_detector=lambda _path: "ext4")
    assert create_error.value.code == "storage.io_failed"


def test_descriptor_close_and_connection_creation_fail_with_safe_io_code(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    original_close = sqlite_preflight.os.close

    def failing_close(descriptor: int) -> None:
        original_close(descriptor)
        raise OSError("close denied")

    monkeypatch.setattr(sqlite_preflight.os, "close", failing_close)
    with pytest.raises(StoragePreflightError) as close_error:
        run_sqlite_preflight(tmp_path, filesystem_detector=lambda _path: "ext4")
    assert close_error.value.code == "storage.io_failed"

    monkeypatch.setattr(sqlite_preflight.os, "close", original_close)

    def failing_connect(_path: Path) -> sqlite3.Connection:
        raise sqlite3.OperationalError("connection denied")

    with pytest.raises(StoragePreflightError) as connect_error:
        run_sqlite_preflight(
            tmp_path,
            filesystem_detector=lambda _path: "ext4",
            connection_factory=failing_connect,
        )
    assert connect_error.value.code == "storage.io_failed"


def test_unexpected_filesystem_detector_failure_is_fail_closed(tmp_path: Path) -> None:
    def broken_detector(_path: Path) -> str:
        raise ValueError("unexpected parser result")

    with pytest.raises(StoragePreflightError) as caught:
        run_sqlite_preflight(tmp_path, filesystem_detector=broken_detector)
    assert caught.value.code == "storage.filesystem_unknown"


class _WrappedConnection:
    def __init__(self, path: Path) -> None:
        self._connection = sqlite3.connect(path)

    def execute(self, statement: str) -> sqlite3.Cursor:
        return self._connection.execute(statement)

    def commit(self) -> None:
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()


class _WalUnavailableConnection(_WrappedConnection):
    def execute(self, statement: str) -> sqlite3.Cursor:
        if statement == "PRAGMA journal_mode=wal":
            return self._connection.execute("SELECT 'delete'")
        return super().execute(statement)


class _FtsUnavailableConnection(_WrappedConnection):
    def execute(self, statement: str) -> sqlite3.Cursor:
        if statement.startswith("CREATE VIRTUAL TABLE"):
            raise sqlite3.OperationalError("disabled for test")
        return super().execute(statement)


class _WriteUnavailableConnection(_WrappedConnection):
    def execute(self, statement: str) -> sqlite3.Cursor:
        if statement.startswith("INSERT INTO"):
            raise sqlite3.OperationalError("read only")
        return super().execute(statement)


class _CommitUnavailableConnection(_WrappedConnection):
    def commit(self) -> None:
        raise sqlite3.OperationalError("commit denied")


class _VersionFetchUnavailableConnection(_WrappedConnection):
    class _BrokenCursor:
        def fetchone(self) -> tuple[object, ...] | None:
            raise sqlite3.OperationalError("version fetch failed")

    def execute(self, statement: str) -> sqlite3.Cursor:  # type: ignore[override]
        if statement == "SELECT sqlite_version()":
            return self._BrokenCursor()  # type: ignore[return-value]
        return super().execute(statement)


@pytest.mark.parametrize(
    ("factory", "expected_code"),
    [
        (_FtsUnavailableConnection, "storage.fts5_unavailable"),
        (_WalUnavailableConnection, "storage.wal_unavailable"),
        (_WriteUnavailableConnection, "storage.write_failed"),
        (_CommitUnavailableConnection, "storage.commit_failed"),
        (_VersionFetchUnavailableConnection, "storage.sqlite_version_unsupported"),
    ],
)
def test_preflight_preserves_stage_specific_capability_codes(
    tmp_path: Path, factory: type[_WrappedConnection], expected_code: str
) -> None:
    with pytest.raises(StoragePreflightError) as caught:
        run_sqlite_preflight(
            tmp_path,
            filesystem_detector=lambda _path: "ext4",
            connection_factory=factory,
            required_version=sqlite3.sqlite_version,
        )
    assert caught.value.code == expected_code
    assert _probe_files(tmp_path) == []


def test_wrong_version_remains_primary_when_cleanup_also_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    original_unlink = Path.unlink

    def failing_unlink(path: Path, *args: object, **kwargs: object) -> None:
        if path.name.startswith(".sqlite-preflight-"):
            raise OSError("cleanup denied")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", failing_unlink)
    with pytest.raises(StoragePreflightError) as caught:
        run_sqlite_preflight(
            tmp_path,
            filesystem_detector=lambda _path: "ext4",
            required_version="0.0.0",
        )
    assert caught.value.code == "storage.sqlite_version_unsupported"
    assert caught.value.cleanup_failed is True


def test_cleanup_failure_is_reported_when_no_primary_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    original_unlink = Path.unlink

    def failing_unlink(path: Path, *args: object, **kwargs: object) -> None:
        if path.name.startswith(".sqlite-preflight-"):
            raise OSError("cleanup denied")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", failing_unlink)
    with pytest.raises(StoragePreflightError) as caught:
        run_sqlite_preflight(
            tmp_path,
            filesystem_detector=lambda _path: "ext4",
            required_version=sqlite3.sqlite_version,
        )
    assert caught.value.code == "storage.cleanup_failed"


def test_product_database_is_never_initialized_after_preflight_failure(tmp_path: Path) -> None:
    calls: list[str] = []

    def failing_preflight(_directory: Path) -> None:
        calls.append("preflight")
        raise StoragePreflightError("storage.sqlite_version_unsupported")

    def initialize(_database: Path) -> None:
        calls.append("database")

    with pytest.raises(StoragePreflightError):
        prepare_storage(
            tmp_path,
            preflight=failing_preflight,
            database_initializer=initialize,
        )
    assert calls == ["preflight"]
    assert not (tmp_path / "meeting-app.sqlite3").exists()


def test_raw_initializer_failure_is_converted_to_safe_stable_error(tmp_path: Path) -> None:
    def failing_initializer(_database: Path) -> None:
        raise ValueError("/private/path must not escape")

    with pytest.raises(StorageInitializationError) as caught:
        prepare_storage(
            tmp_path,
            preflight=lambda _directory: None,
            database_initializer=failing_initializer,
        )
    assert caught.value.code == "storage.initialization_failed"
    assert str(caught.value) == "storage.initialization_failed"
