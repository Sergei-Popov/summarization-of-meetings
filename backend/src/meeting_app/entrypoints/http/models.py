from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from meeting_app.modules.health.domain import HealthStatus


def rfc3339_utc(status: HealthStatus) -> str:
    return status.timestamp.isoformat().replace("+00:00", "Z")


class HealthResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: Literal["ready"]
    version: str
    timestamp: str = Field(description="RFC 3339 UTC timestamp", examples=["2026-09-01T12:00:00Z"])


class ProblemDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    stage: str
    retryable: bool
