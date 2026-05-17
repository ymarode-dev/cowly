from fastapi import APIRouter, HTTPException, Query

from app.mappers import cow_to_response
from app.models import CowResponse
from app.store import store

router = APIRouter(prefix="/cows", tags=["cows"])


@router.get("", response_model=list[CowResponse])
async def list_cows(
    unassigned_only: bool = Query(
        default=False,
        description="Only cows without a linked collar",
    ),
) -> list[CowResponse]:
    cows = store.cows.values()
    if unassigned_only:
        cows = [c for c in cows if c.collar_id is None]
    return [cow_to_response(c) for c in sorted(cows, key=lambda x: x.id)]


@router.get("/{cow_id}", response_model=CowResponse)
async def get_cow(cow_id: str) -> CowResponse:
    cow = store.cows.get(cow_id)
    if cow is None:
        raise HTTPException(status_code=404, detail=f"Cow '{cow_id}' not found")
    return cow_to_response(cow)
