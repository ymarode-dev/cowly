"""End-to-end tests through the API gateway (requires docker compose up)."""

import uuid

import httpx
import pytest


pytestmark = pytest.mark.integration


def test_gateway_health(http_client: httpx.Client) -> None:
    response = http_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "api-gateway"
    assert len(data["services"]) >= 7
    down = [s for s in data["services"] if s["status"] == "down"]
    assert not down, f"Services down: {down}"


def test_protected_routes_reject_unauthenticated(http_client: httpx.Client) -> None:
    response = http_client.get("/api/v1/herd")
    assert response.status_code == 401


def test_full_cowly_flow(http_client: httpx.Client) -> None:
    suffix = uuid.uuid4().hex[:8]
    email = f"integration-{suffix}@test.com"

    register = http_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "farm_name": "Integration Farm",
        },
    )
    assert register.status_code == 201, register.text

    login = http_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    verify = http_client.get("/api/v1/auth/verify", headers=headers)
    assert verify.json()["valid"] is True

    cow = http_client.post(
        "/api/v1/herd",
        headers=headers,
        json={
            "name": "Bessie",
            "ear_tag": f"TAG-{suffix}",
            "breed": "Holstein",
        },
    )
    assert cow.status_code == 201, cow.text
    cow_id = cow.json()["id"]

    collar = http_client.post(
        "/api/v1/collars",
        headers=headers,
        json={"mac_address": f"AA:BB:CC:DD:{suffix[:2]}:{suffix[2:4]}"},
    )
    assert collar.status_code == 201, collar.text
    collar_id = collar.json()["id"]

    assigned = http_client.post(
        f"/api/v1/collars/{collar_id}/assign/{cow_id}",
        headers=headers,
    )
    assert assigned.status_code == 200

    scan = http_client.get("/api/v1/simulator/collars/scan", headers=headers)
    assert scan.status_code == 200
    assert "collars" in scan.json()

    telemetry = http_client.post(
        "/api/v1/telemetry/readings",
        headers=headers,
        json={
            "collar_id": collar_id,
            "cow_id": cow_id,
            "latitude": 52.1,
            "longitude": -1.2,
            "activity_score": 75.0,
        },
    )
    assert telemetry.status_code == 201

    latest = http_client.get(
        f"/api/v1/telemetry/collars/{collar_id}/latest",
        headers=headers,
    )
    assert latest.status_code == 200
    assert len(latest.json()) >= 1

    alert = http_client.post(
        "/api/v1/alerts",
        headers=headers,
        json={
            "collar_id": collar_id,
            "cow_id": cow_id,
            "alert_type": "low_battery",
            "severity": "warning",
            "message": "Integration test alert",
        },
    )
    assert alert.status_code == 201
    alert_id = alert.json()["id"]

    ack = http_client.post(
        f"/api/v1/alerts/{alert_id}/acknowledge",
        headers=headers,
    )
    assert ack.status_code == 200
    assert ack.json()["acknowledged"] is True

    notifications = http_client.get("/api/v1/notifications", headers=headers)
    assert notifications.status_code == 200
    assert len(notifications.json()) >= 1
