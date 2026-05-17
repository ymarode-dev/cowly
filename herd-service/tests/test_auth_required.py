from fastapi.testclient import TestClient

from app.main import app


def test_cows_require_authentication() -> None:
    with TestClient(app) as unauthenticated:
        response = unauthenticated.get("/api/v1/cows")
    assert response.status_code == 401
