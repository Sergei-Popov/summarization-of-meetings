from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Protocol

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from meeting_app import __version__
from meeting_app.bootstrap.errors import ApplicationStartupError
from meeting_app.bootstrap.settings import Settings
from meeting_app.bootstrap.storage import prepare_storage
from meeting_app.entrypoints.http import build_api_router
from meeting_app.entrypoints.http.problems import install_problem_handlers
from meeting_app.entrypoints.http.security import install_security_headers
from meeting_app.modules.health.application import GetHealth
from meeting_app.platform.storage import StorageError
from meeting_app.platform.time import SystemClock

StorageStarter = Callable[[Path], None]
logger = logging.getLogger("meeting_app.startup")


class StartupFailure(Protocol):
    code: str
    stage: str
    retryable: bool
    cleanup_failed: bool


def _verify_static_assets(static_directory: Path) -> None:
    if not static_directory.is_dir() or not (static_directory / "index.html").is_file():
        raise ApplicationStartupError("application.static_assets_missing")


def _log_startup_failure(error: StartupFailure) -> None:
    logger.error(
        json.dumps(
            {
                "cleanupFailed": error.cleanup_failed,
                "code": error.code,
                "retryable": error.retryable,
                "stage": error.stage,
            },
            sort_keys=True,
        )
    )


def create_app(
    *,
    settings: Settings | None = None,
    storage_starter: StorageStarter = prepare_storage,
    static_directory: Path | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings.from_environment()
    resolved_static = static_directory or resolved_settings.static_directory

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.ready = False
        try:
            if resolved_static is not None:
                _verify_static_assets(resolved_static)
            storage_starter(resolved_settings.data_directory)
            application.state.ready = True
            yield
        except (StorageError, ApplicationStartupError) as error:
            _log_startup_failure(error)
            raise
        finally:
            application.state.ready = False

    application = FastAPI(
        title="Meeting App API",
        version=__version__,
        openapi_url="/api/v1/openapi.json",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    application.state.ready = False
    application.include_router(build_api_router(GetHealth(SystemClock(), __version__)))
    install_problem_handlers(application)
    install_security_headers(application)

    if resolved_static is not None:
        application.mount(
            "/",
            StaticFiles(directory=resolved_static, html=True, check_dir=False),
            name="frontend",
        )
    return application


app = create_app()
