from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings


def _token(farm_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode(
        {
            "sub": "user-1",
            "email": "a@test.com",
            "farm_id": farm_id,
            "jti": f"jti-{farm_id}",
            "type": "access",
            "exp": expire,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def test_cows_are_isolated_by_farm(client) -> None:
    farm_a_headers = {"Authorization": f"Bearer {_token('farm-a')}"}
    farm_b_headers = {"Authorization": f"Bearer {_token('farm-b')}"}

    created = client.post(
        "/api/v1/cows",
        headers=farm_a_headers,
        json={"name": "Bessie", "ear_tag": "A-001", "breed": "Holstein"},
    )
    assert created.status_code == 201
    cow_id = created.json()["id"]

    other_farm_list = client.get("/api/v1/cows", headers=farm_b_headers)
    assert other_farm_list.status_code == 200
    assert other_farm_list.json() == []

    missing = client.get(f"/api/v1/cows/{cow_id}", headers=farm_b_headers)
    assert missing.status_code == 404
