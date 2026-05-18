from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

os.environ["COWLY_NOTIFICATION_DATABASE_URL"] = "sqlite://"
os.environ["COWLY_SKIP_MIGRATIONS"] = "1"

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings
import app.database as database
from app.main import app
from app.notifications.models import Notification  # noqa: F401

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
database.engine = test_engine


def _init_db() -> None:
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {
            "sub": "test-user-id",
            "email": "test@example.com",
            "farm_id": "test-farm-id",
            "jti": "test-jti",
            "type": "access",
            "exp": expire,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(auth_headers: dict[str, str]):
    _init_db()

    def get_test_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[database.get_session] = get_test_session
    with TestClient(app, raise_server_exceptions=True) as test_client:
        test_client.headers.update(auth_headers)
        yield test_client
    app.dependency_overrides.clear()
