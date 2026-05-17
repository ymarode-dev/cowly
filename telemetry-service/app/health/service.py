from sqlmodel import Session

from app.health.schemas import HealthResponse
from app.readings import service as readings_service


def get_health(session: Session) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="telemetry-service",
        readings_total=readings_service.count_readings(session),
    )
