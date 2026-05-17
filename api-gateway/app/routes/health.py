import httpx
from fastapi import APIRouter

from app.config import settings
from app.models import GatewayHealthResponse, ServiceHealth

router = APIRouter(tags=["health"])

SERVICE_TARGETS = [
    ("auth-service", settings.auth_service_url),
    ("herd-service", settings.herd_service_url),
    ("collar-registry", settings.collar_registry_url),
    ("collar-simulator", settings.collar_simulator_url),
    ("telemetry-service", settings.telemetry_service_url),
    ("alert-service", settings.alert_service_url),
    ("notification-service", settings.notification_service_url),
]


@router.get("/health", response_model=GatewayHealthResponse)
async def health() -> GatewayHealthResponse:
    results: list[ServiceHealth] = []
    all_ok = True

    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, base_url in SERVICE_TARGETS:
            try:
                response = await client.get(f"{base_url}/health")
                if response.status_code == 200:
                    results.append(
                        ServiceHealth(
                            name=name,
                            url=base_url,
                            status="ok",
                            detail=response.json(),
                        )
                    )
                else:
                    all_ok = False
                    results.append(
                        ServiceHealth(
                            name=name,
                            url=base_url,
                            status="degraded",
                            detail={"status_code": response.status_code},
                        )
                    )
            except httpx.HTTPError as exc:
                all_ok = False
                results.append(
                    ServiceHealth(
                        name=name,
                        url=base_url,
                        status="down",
                        detail={"error": str(exc)},
                    )
                )

    return GatewayHealthResponse(
        status="ok" if all_ok else "degraded",
        service="api-gateway",
        services=results,
    )
