from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True, slots=True)
class HealthStatus:
    status: Literal["ready", "not_ready"]
    version: str
    timestamp: datetime
