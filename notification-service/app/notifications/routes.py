from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.notifications import schemas, service
from app.security.deps import get_current_user

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["notifications"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[schemas.NotificationResponse])
def list_notifications(
    session: Session = Depends(get_session),
) -> list[schemas.NotificationResponse]:
    return service.list_notifications(session)


@router.post("", response_model=schemas.NotificationResponse, status_code=201)
def send_notification(
    body: schemas.NotificationCreate,
    session: Session = Depends(get_session),
) -> schemas.NotificationResponse:
    return service.send_notification(session, body)
