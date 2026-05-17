from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.readings import schemas, service
from app.security.deps import get_current_user

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["telemetry"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/readings", response_model=schemas.TelemetryReadingResponse, status_code=201)
def ingest_reading(
    body: schemas.TelemetryIngest,
    session: Session = Depends(get_session),
) -> schemas.TelemetryReadingResponse:
    return service.ingest_reading(session, body)


@router.get(
    "/collars/{collar_id}/latest",
    response_model=list[schemas.TelemetryReadingResponse],
)
def latest_readings(
    collar_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[schemas.TelemetryReadingResponse]:
    return service.latest_for_collar(session, collar_id, limit)
