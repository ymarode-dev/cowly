from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.alerts.routes import router as alerts_router
from app.database import init_db
from app.health.routes import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Cowly Alert Service",
    description="Geofence, health, and operational alerts for the herd.",
    version="0.2.0",
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


@app.get("/")
async def root() -> dict:
    return {"service": "alert-service", "docs": "/docs", "health": "/health"}
