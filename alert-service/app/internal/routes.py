from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.alerts import schemas, service
from app.database import get_session
from app.security.deps import CurrentUser, require_internal

router = APIRouter(
    prefix="/api/v1/internal",
    tags=["internal"],
    dependencies=[Depends(require_internal)],
)


@router.post("/evaluate", response_model=List[schemas.AlertResponse])
async def evaluate_telemetry(
    body: schemas.TelemetryEvaluate,
    session: Session = Depends(get_session),
    _: CurrentUser = Depends(require_internal),
) -> list[schemas.AlertResponse]:
    return await service.process_telemetry_evaluation(session, body)
