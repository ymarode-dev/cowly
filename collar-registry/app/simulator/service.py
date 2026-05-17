import httpx
from fastapi import HTTPException

from app.config import settings


async def proxy_scan() -> dict:
    url = f"{settings.collar_simulator_url}/api/v1/collars/scan"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503, detail="Collar simulator unavailable"
        ) from exc
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


async def check_simulator_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.collar_simulator_url}/health")
            return response.status_code == 200
    except httpx.HTTPError:
        return False
