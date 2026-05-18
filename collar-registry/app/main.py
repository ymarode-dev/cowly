import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.collars.routes import router as collars_router
from app.database import init_db
from app.migrate import run_migrations
from app.health.routes import router as health_router
from app.simulator.routes import router as simulator_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("COWLY_SKIP_MIGRATIONS") != "1":
        run_migrations()
    init_db()
    yield


app = FastAPI(
    title="Cowly Collar Registry",
    description="Collar inventory and pairing state; proxies simulator in dev.",
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
app.include_router(collars_router)
app.include_router(simulator_router)


@app.get("/")
async def root() -> dict:
    return {"service": "collar-registry", "docs": "/docs", "health": "/health"}
