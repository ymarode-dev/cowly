from datetime import datetime, timedelta, timezone

import respx
from httpx import Response
from jose import jwt

from app.config import settings


def _token() -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode(
        {
            "sub": "user-1",
            "email": "user@test.com",
            "farm_id": "farm-1",
            "jti": "gw-test-jti",
            "type": "access",
            "exp": expire,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def test_protected_route_requires_token(client) -> None:
    response = client.get("/api/v1/herd")
    assert response.status_code == 401


@respx.mock
def test_protected_route_forwards_with_valid_token(client) -> None:
    respx.get("http://herd.test/api/v1/cows").mock(
        return_value=Response(200, json=[])
    )
    response = client.get(
        "/api/v1/herd",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert response.status_code == 200
    request = respx.calls.last.request
    assert request.headers["X-User-Id"] == "user-1"
    assert request.headers["X-User-Email"] == "user@test.com"
    assert request.headers["X-Farm-Id"] == "farm-1"


@respx.mock
def test_auth_register_is_public(client) -> None:
    respx.post("http://auth.test/api/v1/auth/register").mock(
        return_value=Response(422, json={"detail": "validation error"})
    )
    response = client.post("/api/v1/auth/register", json={})
    assert response.status_code != 401
