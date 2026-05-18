from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.readings import schemas, service
from app.security.deps import CurrentUser, get_current_user

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["telemetry"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/readings", response_model=schemas.TelemetryReadingResponse, status_code=201)
async def ingest_reading(
    body: schemas.TelemetryIngest,
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> schemas.TelemetryReadingResponse:
    response = service.ingest_reading(session, user.farm_id, body)
    await service.trigger_alert_evaluation(user.farm_id, response)
    return response


@router.get(
    "/collars/{collar_id}/latest",
    response_model=List[schemas.TelemetryReadingResponse],
)
def latest_readings(
    collar_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[schemas.TelemetryReadingResponse]:
    return service.latest_for_collar(session, user.farm_id, collar_id, limit)
