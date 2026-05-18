import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.cows.routes import router as cows_router
from app.database import init_db
from app.migrate import run_migrations
from app.health.routes import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("COWLY_SKIP_MIGRATIONS") != "1":
        run_migrations()
    init_db()
    yield


app = FastAPI(
    title="Cowly Herd Service",
    description="Canonical herd and cow records for farms.",
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
app.include_router(cows_router)


@app.get("/")
async def root() -> dict:
    return {"service": "herd-service", "docs": "/docs", "health": "/health"}
