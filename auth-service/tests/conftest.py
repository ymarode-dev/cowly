from __future__ import annotations

import os

os.environ["COWLY_AUTH_DATABASE_URL"] = "sqlite://"
os.environ["COWLY_AUTH_REDIS_URL"] = "redis://localhost:6379/15"
os.environ["COWLY_SKIP_MIGRATIONS"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.auth.models import Farm, User  # noqa: F401
import app.database as database
from app.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
database.engine = test_engine


def _init_db() -> None:
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)


class FakeRedis:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def setex(self, key: str, ttl: int, value: str) -> None:
        self._data[key] = value

    def exists(self, key: str) -> int:
        return 1 if key in self._data else 0

    def delete(self, key: str) -> int:
        return 1 if self._data.pop(key, None) is not None else 0


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> FakeRedis:
    store = FakeRedis()
    monkeypatch.setattr("app.auth.service.get_redis", lambda: store)
    return store


@pytest.fixture
def client():
    _init_db()

    def get_test_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[database.get_session] = get_test_session
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()
