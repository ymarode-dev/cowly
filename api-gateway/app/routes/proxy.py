from __future__ import annotations


import httpx
from fastapi import APIRouter, Request, Response

from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["proxy"])

ROUTE_MAP: dict[str, tuple[str, str]] = {
    "auth": (settings.auth_service_url, "/api/v1/auth"),
    "herd": (settings.herd_service_url, "/api/v1/cows"),
    "collars": (settings.collar_registry_url, "/api/v1/collars"),
    "telemetry": (settings.telemetry_service_url, "/api/v1/telemetry"),
    "alerts": (settings.alert_service_url, "/api/v1/alerts"),
    "geofences": (settings.alert_service_url, "/api/v1/geofences"),
    "notifications": (settings.notification_service_url, "/api/v1/notifications"),
    "simulator": (settings.collar_simulator_url, "/api/v1"),
}


async def _forward(
    request: Request,
    base_url: str,
    path_prefix: str,
    subpath: str,
) -> Response:
    target = f"{base_url}{path_prefix}"
    if subpath:
        target = f"{target}/{subpath}"
    if request.url.query:
        target = f"{target}?{request.url.query}"

    body = await request.body()
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length"}
    }
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        headers["X-User-Id"] = user_id
        user_email = getattr(request.state, "user_email", None)
        if user_email:
            headers["X-User-Email"] = user_email
        farm_id = getattr(request.state, "farm_id", None)
        if farm_id:
            headers["X-Farm-Id"] = farm_id

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream = await client.request(
            request.method,
            target,
            content=body,
            headers=headers,
        )

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers={
            k: v
            for k, v in upstream.headers.items()
            if k.lower() not in {"content-encoding", "transfer-encoding"}
        },
        media_type=upstream.headers.get("content-type"),
    )


def _make_handler(base_url: str, path_prefix: str):
    async def handler(request: Request, subpath: str = "") -> Response:
        return await _forward(request, base_url, path_prefix, subpath)

    return handler


HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

for prefix, (base_url, path_prefix) in ROUTE_MAP.items():
    handler = _make_handler(base_url, path_prefix)
    router.add_api_route(f"/{prefix}", handler, methods=HTTP_METHODS, include_in_schema=False)
    router.add_api_route(
        f"/{prefix}/{{subpath:path}}",
        handler,
        methods=HTTP_METHODS,
        include_in_schema=False,
    )
