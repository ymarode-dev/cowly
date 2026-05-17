from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.health.routes import router as health_router
from app.notifications.routes import router as notifications_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Cowly Notification Service",
    description="Delivers push, email, and SMS alerts to farmers.",
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
app.include_router(notifications_router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "notification-service",
        "docs": "/docs",
        "health": "/health",
    }
