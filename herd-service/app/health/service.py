from sqlmodel import Session

from app.cows import service as cow_service
from app.health.schemas import HealthResponse


def get_health(session: Session) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="herd-service",
        cows_total=cow_service.count_cows(session),
    )
