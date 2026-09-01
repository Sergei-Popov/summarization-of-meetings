from collections.abc import Mapping

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _problem(
    request: Request,
    *,
    status_code: int,
    title: str,
    detail: str,
    code: str,
    stage: str = "http",
    retryable: bool = False,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    response_headers = dict(headers or {})
    response_headers["Cache-Control"] = "no-store"
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        headers=response_headers,
        content={
            "type": f"urn:meeting-app:problem:{code}",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": request.url.path,
            "code": code,
            "stage": stage,
            "retryable": retryable,
        },
    )


def install_problem_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_problem(request: Request, error: StarletteHTTPException) -> JSONResponse:
        if error.status_code == status.HTTP_404_NOT_FOUND:
            return _problem(
                request,
                status_code=error.status_code,
                title="Маршрут не найден",
                detail="Запрошенный API-маршрут не существует.",
                code="http.route_not_found",
                headers=error.headers,
            )
        return _problem(
            request,
            status_code=error.status_code,
            title="Ошибка HTTP",
            detail="Запрос не может быть выполнен.",
            code="http.request_failed",
            headers=error.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_problem(request: Request, _error: RequestValidationError) -> JSONResponse:
        return _problem(
            request,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            title="Некорректный запрос",
            detail="Проверьте формат и обязательные поля запроса.",
            code="http.validation_failed",
        )

    @app.exception_handler(Exception)
    async def internal_problem(request: Request, _error: Exception) -> JSONResponse:
        return _problem(
            request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Внутренняя ошибка",
            detail="Запрос не удалось выполнить.",
            code="http.internal_error",
        )
