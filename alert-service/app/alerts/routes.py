from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.alerts import schemas, service
from app.database import get_session
from app.security.deps import CurrentUser, get_current_user

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["alerts"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=List[schemas.AlertResponse])
def list_alerts(
    open_only: bool = Query(default=False),
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[schemas.AlertResponse]:
    return service.list_alerts(session, user.farm_id, open_only=open_only)


@router.post("", response_model=schemas.AlertResponse, status_code=201)
async def create_alert(
    body: schemas.AlertCreate,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.AlertResponse:
    response = service.create_alert(session, user.farm_id, body)
    await service.notify_farmer(response)
    return response


@router.post("/{alert_id}/acknowledge", response_model=schemas.AlertResponse)
def acknowledge_alert(
    alert_id: str,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.AlertResponse:
    try:
        return service.acknowledge_alert(session, user.farm_id, alert_id, user.user_id)
    except service.AlertNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
