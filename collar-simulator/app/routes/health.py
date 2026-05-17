from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse
from app.store import store

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    collars_assigned = sum(1 for c in store.collars.values() if c.cow_id)
    cows_assigned = sum(1 for c in store.cows.values() if c.collar_id)
    return HealthResponse(
        status="ok",
        service="collar-simulator",
        herd_size=settings.herd_size,
        collars_total=len(store.collars),
        collars_assigned=collars_assigned,
        cows_total=len(store.cows),
        cows_assigned=cows_assigned,
    )
