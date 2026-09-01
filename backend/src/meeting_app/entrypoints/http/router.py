from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse

from meeting_app.entrypoints.http.models import HealthResponse, ProblemDetails, rfc3339_utc
from meeting_app.modules.health.application import GetHealth


def build_api_router(get_health: GetHealth) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    @router.get(
        "/health",
        response_model=HealthResponse,
        responses={
            status.HTTP_503_SERVICE_UNAVAILABLE: {
                "model": ProblemDetails,
                "description": "Service Unavailable",
                "content": {
                    "application/problem+json": {
                        "schema": {"$ref": "#/components/schemas/ProblemDetails"}
                    }
                },
            }
        },
        tags=["system"],
    )
    async def health(request: Request, response: Response) -> HealthResponse | JSONResponse:
        health_status = get_health.execute(ready=bool(request.app.state.ready))
        if health_status.status != "ready":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/problem+json",
                headers={"Cache-Control": "no-store"},
                content={
                    "type": "urn:meeting-app:problem:not-ready",
                    "title": "Приложение не готово",
                    "status": status.HTTP_503_SERVICE_UNAVAILABLE,
                    "detail": "Инициализация локального хранилища ещё не завершена.",
                    "instance": request.url.path,
                    "code": "application.not_ready",
                    "stage": "startup",
                    "retryable": True,
                },
            )
        response.headers["Cache-Control"] = "no-store"
        return HealthResponse(
            status="ready",
            version=health_status.version,
            timestamp=rfc3339_utc(health_status),
        )

    return router
