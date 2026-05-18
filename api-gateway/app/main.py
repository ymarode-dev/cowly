from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.auth import AuthMiddleware
from app.routes import health, proxy, version

app = FastAPI(
    title="Cowly API Gateway",
    description="Single entry point for Cowly microservices.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(health.router)
app.include_router(version.router)
app.include_router(proxy.router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "api-gateway",
        "docs": "/docs",
        "health": "/health",
        "version": "/version",
        "routes": {
            "auth": "/api/v1/auth",
            "herd": "/api/v1/herd",
            "collars": "/api/v1/collars",
            "telemetry": "/api/v1/telemetry",
            "alerts": "/api/v1/alerts",
            "geofences": "/api/v1/geofences",
            "notifications": "/api/v1/notifications",
            "simulator": "/api/v1/simulator",
        },
        "service_urls": {
            "auth": settings.auth_service_url,
            "herd": settings.herd_service_url,
            "collar_registry": settings.collar_registry_url,
            "collar_simulator": settings.collar_simulator_url,
            "telemetry": settings.telemetry_service_url,
            "alert": settings.alert_service_url,
            "notification": settings.notification_service_url,
        },
    }
