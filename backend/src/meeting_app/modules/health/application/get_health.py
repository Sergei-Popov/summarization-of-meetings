from meeting_app.modules.health.domain import HealthStatus
from meeting_app.modules.health.ports import Clock


class GetHealth:
    def __init__(self, clock: Clock, version: str) -> None:
        self._clock = clock
        self._version = version

    def execute(self, *, ready: bool) -> HealthStatus:
        return HealthStatus(
            status="ready" if ready else "not_ready",
            version=self._version,
            timestamp=self._clock.now(),
        )
