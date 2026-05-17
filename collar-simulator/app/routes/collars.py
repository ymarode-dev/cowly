from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.mappers import collar_to_response
from app.models import (
    CollarResponse,
    IdentifyRequest,
    IdentifyResponse,
    IdentifyStatus,
    IdentifyStatusResponse,
    ScanResponse,
)
from app.services.blink import start_identify
from app.services.scan import scan_unassigned_collars
from app.store import _utcnow, store

router = APIRouter(prefix="/collars", tags=["collars"])


@router.get("/scan", response_model=ScanResponse)
async def scan_for_collars() -> ScanResponse:
    """Simulate discovering unassigned collars in range (BLE scan)."""
    collars = scan_unassigned_collars()
    return ScanResponse(scanned_at=_utcnow(), collars=collars)


@router.get("", response_model=list[CollarResponse])
async def list_collars(
    assigned: bool | None = Query(default=None, description="Filter by assignment state"),
) -> list[CollarResponse]:
    collars = store.collars.values()
    if assigned is True:
        collars = [c for c in collars if c.cow_id is not None]
    elif assigned is False:
        collars = [c for c in collars if c.cow_id is None]
    return [collar_to_response(c) for c in sorted(collars, key=lambda x: x.id)]


@router.get("/{collar_id}", response_model=CollarResponse)
async def get_collar(collar_id: str) -> CollarResponse:
    collar = store.collars.get(collar_id)
    if collar is None:
        raise HTTPException(status_code=404, detail=f"Collar '{collar_id}' not found")
    return collar_to_response(collar)


@router.post("/{collar_id}/identify", response_model=IdentifyResponse)
async def identify_collar(collar_id: str, body: IdentifyRequest | None = None) -> IdentifyResponse:
    """
    Blink the collar LED 2–3 times so the farmer can confirm the physical device
    matches the one selected in the app before assignment.
    """
    blinks = (body.blinks if body else None) or settings.identify_blink_count
    try:
        collar = await start_identify(collar_id, blinks)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Collar '{collar_id}' not found") from None
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return IdentifyResponse(
        collar_id=collar.id,
        status=collar.identify_status,
        target_blinks=collar.identify_target_blinks,
        completed_blinks=collar.identify_completed_blinks,
        led_state=collar.led_state,
        message=f"LED blinking {blinks} times on collar {collar_id} ({collar.mac_address})",
    )


@router.get("/{collar_id}/identify/status", response_model=IdentifyStatusResponse)
async def identify_status(collar_id: str) -> IdentifyStatusResponse:
    collar = store.collars.get(collar_id)
    if collar is None:
        raise HTTPException(status_code=404, detail=f"Collar '{collar_id}' not found")

    verified = store.is_identify_verified(collar)
    return IdentifyStatusResponse(
        collar_id=collar.id,
        status=collar.identify_status,
        target_blinks=collar.identify_target_blinks,
        completed_blinks=collar.identify_completed_blinks,
        led_state=collar.led_state,
        verified=verified,
        verified_until=collar.identify_verified_until if verified else None,
    )
