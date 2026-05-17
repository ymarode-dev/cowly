from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import assignments, collars, cows, health
from app.store import store


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.seed(settings.herd_size)
    yield


app = FastAPI(
    title="Cowly Collar Simulator",
    description=(
        "Simulates smart collars and cows for local development. "
        "Scan → identify (LED blink) → assign pairing flow."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(collars.router, prefix="/api/v1")
app.include_router(cows.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    return {
        "service": "collar-simulator",
        "docs": "/docs",
        "health": "/health",
    }
