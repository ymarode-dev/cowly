from sqlmodel import Session

from app.health.schemas import HealthResponse
from app.notifications import service as notification_service


def get_health(session: Session) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="notification-service",
        notifications_total=notification_service.count_notifications(session),
    )
