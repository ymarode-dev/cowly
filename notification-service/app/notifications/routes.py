from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.notifications import schemas, service
from app.security.deps import CurrentUser, get_current_user

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["notifications"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=List[schemas.NotificationResponse])
def list_notifications(
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[schemas.NotificationResponse]:
    if user.internal:
        raise HTTPException(status_code=403, detail="JWT required to list notifications")
    return service.list_notifications(session, user.farm_id)


@router.post("", response_model=schemas.NotificationResponse, status_code=201)
def send_notification(
    body: schemas.NotificationCreate,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.NotificationResponse:
    farm_id = body.farm_id if user.internal else user.farm_id
    if not farm_id:
        raise HTTPException(status_code=400, detail="farm_id is required")
    return service.send_notification(session, farm_id, body)
