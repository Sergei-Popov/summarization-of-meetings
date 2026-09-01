import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from meeting_app.bootstrap.app import create_app
from meeting_app.bootstrap.errors import ApplicationStartupError
from meeting_app.bootstrap.settings import Settings
from meeting_app.bootstrap.storage import prepare_storage
from meeting_app.platform.storage import StorageInitializationError


def _app(tmp_path: Path) -> FastAPI:
    return create_app(
        settings=Settings(data_directory=tmp_path),
        storage_starter=lambda _path: None,
    )


def _client(tmp_path: Path) -> TestClient:
    return TestClient(_app(tmp_path))


def test_health_is_versioned_ready_json_with_rfc3339_utc(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["status"] == "ready"
    assert response.json()["version"] == "0.1.0"
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z",
        response.json()["timestamp"],
    )


def test_unknown_api_route_is_stable_rfc9457_problem(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {
        "type": "urn:meeting-app:problem:http.route_not_found",
        "title": "Маршрут не найден",
        "status": 404,
        "detail": "Запрошенный API-маршрут не существует.",
        "instance": "/api/v1/does-not-exist",
        "code": "http.route_not_found",
        "stage": "http",
        "retryable": False,
    }


def test_generic_error_is_safe_rfc9457_problem(tmp_path: Path) -> None:
    app = _app(tmp_path)

    @app.get("/api/v1/crash")
    async def crash() -> None:
        raise RuntimeError("sensitive /private/path")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/v1/crash")

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/problem+json"
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["code"] == "http.internal_error"
    assert "/private/path" not in response.text


def test_http_exception_headers_are_preserved(tmp_path: Path) -> None:
    app = _app(tmp_path)

    @app.get("/api/v1/rate-limited")
    async def rate_limited() -> None:
        raise HTTPException(status_code=429, headers={"Retry-After": "7"})

    with TestClient(app) as client:
        response = client.get("/api/v1/rate-limited")

    assert response.status_code == 429
    assert response.headers["retry-after"] == "7"
    assert response.headers["cache-control"] == "no-store"


def test_security_headers_restrict_network_to_self(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.get("/api/v1/health")

    csp = response.headers["content-security-policy"]
    assert "connect-src 'self'" in csp
    assert "http:" not in csp
    assert "https:" not in csp
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_openapi_problem_media_type_references_problem_details(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.get("/api/v1/openapi.json")

    document: dict[str, Any] = response.json()
    problem_schema = document["paths"]["/api/v1/health"]["get"]["responses"]["503"][
        "content"
    ]["application/problem+json"]["schema"]
    assert response.status_code == 200
    assert document["info"]["version"] == "0.1.0"
    assert problem_schema == {"$ref": "#/components/schemas/ProblemDetails"}
    assert {"HealthResponse", "ProblemDetails"} <= set(document["components"]["schemas"])


def test_health_is_not_ready_before_and_after_lifespan(tmp_path: Path) -> None:
    app = _app(tmp_path)
    client = TestClient(app)
    before = client.get("/api/v1/health")
    with client:
        assert client.get("/api/v1/health").status_code == 200
    after = client.get("/api/v1/health")

    assert before.status_code == 503
    assert before.headers["cache-control"] == "no-store"
    assert before.json()["code"] == "application.not_ready"
    assert after.status_code == 503


def test_configured_static_assets_serve_index_and_referenced_asset(tmp_path: Path) -> None:
    static = tmp_path / "dist"
    static.mkdir()
    (static / "assets").mkdir()
    (static / "index.html").write_text(
        '<!doctype html><script type="module" src="/assets/app.js"></script>',
        encoding="utf-8",
    )
    (static / "assets" / "app.js").write_text("window.__appLoaded = true;", encoding="utf-8")
    app = create_app(
        settings=Settings(data_directory=tmp_path / "data", static_directory=static),
        storage_starter=lambda _path: None,
    )

    with TestClient(app) as client:
        index = client.get("/")
        asset = client.get("/assets/app.js")

    assert index.status_code == 200
    assert "/assets/app.js" in index.text
    assert asset.status_code == 200
    assert "__appLoaded" in asset.text


def test_missing_static_index_fails_fast_and_resets_readiness(tmp_path: Path) -> None:
    static = tmp_path / "dist"
    static.mkdir()
    app = create_app(
        settings=Settings(data_directory=tmp_path / "data", static_directory=static),
        storage_starter=lambda _path: None,
    )

    with pytest.raises(ApplicationStartupError) as caught, TestClient(app):
        pass

    assert caught.value.code == "application.static_assets_missing"
    assert app.state.ready is False


def test_storage_startup_failure_is_safe_logged_and_never_ready(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    def fail_storage(_path: Path) -> None:
        raise StorageInitializationError()

    app = create_app(
        settings=Settings(data_directory=tmp_path / "private-data"),
        storage_starter=fail_storage,
    )
    caplog.set_level(logging.ERROR, logger="meeting_app.startup")

    with pytest.raises(StorageInitializationError), TestClient(app):
        pass

    payload = json.loads(caplog.records[-1].message)
    assert payload == {
        "cleanupFailed": False,
        "code": "storage.initialization_failed",
        "retryable": False,
        "stage": "storage_initialization",
    }
    assert str(tmp_path) not in caplog.text
    assert app.state.ready is False


def test_real_startup_wiring_migrates_database_and_persists_wal(tmp_path: Path) -> None:
    def start_storage(directory: Path) -> None:
        prepare_storage(directory, preflight=lambda _directory: None)

    app = create_app(
        settings=Settings(data_directory=tmp_path),
        storage_starter=start_storage,
    )
    with TestClient(app) as client:
        assert client.get("/api/v1/health").status_code == 200

    database = tmp_path / "meeting-app.sqlite3"
    with sqlite3.connect(database) as connection:
        marker = connection.execute(
            "SELECT value FROM schema_metadata WHERE key = 'seed'"
        ).fetchone()
        mode = connection.execute("PRAGMA journal_mode").fetchone()
    assert marker == ("1",)
    assert mode == ("wal",)
