import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.alerts.routes import router as alerts_router
from app.database import init_db
from app.migrate import run_migrations
from app.geofences.routes import router as geofences_router
from app.health.routes import router as health_router
from app.internal.routes import router as internal_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("COWLY_SKIP_MIGRATIONS") != "1":
        run_migrations()
    init_db()
    yield


app = FastAPI(
    title="Cowly Alert Service",
    description="Geofence, health, and operational alerts for the herd.",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(alerts_router)
app.include_router(geofences_router)
app.include_router(internal_router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "alert-service",
        "docs": "/docs",
        "health": "/health",
        "geofences": "/api/v1/geofences",
    }
