from sqlmodel import Session

from app.auth import service as auth_service
from app.health.schemas import HealthResponse


def get_health(session: Session) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="auth-service",
        users_registered=auth_service.count_users(session),
    )
