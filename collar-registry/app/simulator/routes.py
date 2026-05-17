from fastapi import APIRouter, Depends

from app.security.deps import get_current_user
from app.simulator import service

router = APIRouter(
    prefix="/api/v1/simulator",
    tags=["simulator-proxy"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/scan")
async def proxy_scan() -> dict:
    """Proxy BLE scan from collar-simulator for mobile/web clients."""
    return await service.proxy_scan()
