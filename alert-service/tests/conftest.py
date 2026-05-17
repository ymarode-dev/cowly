import os
from datetime import datetime, timedelta, timezone

os.environ["COWLY_ALERT_DATABASE_URL"] = "sqlite://"
os.environ["COWLY_ALERT_NOTIFICATION_SERVICE_URL"] = "http://notification.test"
os.environ["COWLY_ALERT_INTERNAL_API_KEY"] = "test-internal-key"

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import SQLModel

from app.config import settings
from app.database import engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"sub": "test-user-id", "email": "test@example.com", "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(auth_headers: dict[str, str]) -> TestClient:
    with TestClient(app) as test_client:
        test_client.headers.update(auth_headers)
        yield test_client
