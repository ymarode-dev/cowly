from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.health import schemas, service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=schemas.HealthResponse)
async def health(session: Session = Depends(get_session)) -> schemas.HealthResponse:
    return await service.get_health(session)
