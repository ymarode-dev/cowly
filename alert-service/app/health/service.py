from sqlmodel import Session

from app.alerts import service as alert_service
from app.health.schemas import HealthResponse


def get_health(session: Session) -> HealthResponse:
    total, open_count = alert_service.count_alerts(session)
    return HealthResponse(
        status="ok",
        service="alert-service",
        alerts_total=total,
        alerts_open=open_count,
    )
