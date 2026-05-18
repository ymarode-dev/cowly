"""Populate Cowly with demo data after the stack is healthy (idempotent)."""

from __future__ import annotations

import os
import sys
import time

import httpx

GATEWAY = os.environ.get("COWLY_SEED_GATEWAY_URL", "http://api-gateway:8000").rstrip("/")
EMAIL = os.environ.get("COWLY_SEED_EMAIL", "demo@cowly.local")
PASSWORD = os.environ.get("COWLY_SEED_PASSWORD", "demo-password-1")
FARM_NAME = os.environ.get("COWLY_SEED_FARM_NAME", "Demo Farm")
MAX_WAIT_SEC = int(os.environ.get("COWLY_SEED_MAX_WAIT_SEC", "180"))


def wait_for_gateway(client: httpx.Client) -> None:
    deadline = time.monotonic() + MAX_WAIT_SEC
    while time.monotonic() < deadline:
        try:
            response = client.get(f"{GATEWAY}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                down = [s["name"] for s in data.get("services", []) if s.get("status") == "down"]
                if not down:
                    return
                print(f"Waiting for services: {down}")
        except httpx.HTTPError as exc:
            print(f"Gateway not ready: {exc}")
        time.sleep(3)
    raise SystemExit(f"Gateway did not become healthy within {MAX_WAIT_SEC}s")


def obtain_token(client: httpx.Client) -> str:
    register = client.post(
        f"{GATEWAY}/api/v1/auth/register",
        json={"email": EMAIL, "password": PASSWORD, "farm_name": FARM_NAME},
    )
    if register.status_code == 201:
        print(f"Registered demo user {EMAIL}")
    elif register.status_code == 409:
        print(f"Demo user {EMAIL} already exists")
    else:
        print(f"Register skipped ({register.status_code}): {register.text}")

    login = client.post(
        f"{GATEWAY}/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
    )
    login.raise_for_status()
    return login.json()["access_token"]


def seed_data(client: httpx.Client, headers: dict[str, str]) -> None:
    cows = client.get(f"{GATEWAY}/api/v1/herd", headers=headers)
    cows.raise_for_status()
    if cows.json():
        print("Herd already has cows — skipping cow/collar seed")
        return

    bessie = client.post(
        f"{GATEWAY}/api/v1/herd",
        headers=headers,
        json={
            "name": "Bessie",
            "ear_tag": "DEMO-001",
            "breed": "Holstein",
            "weight_kg": 620.0,
        },
    )
    bessie.raise_for_status()
    cow_id = bessie.json()["id"]
    print(f"Created cow Bessie ({cow_id})")

    client.post(
        f"{GATEWAY}/api/v1/herd",
        headers=headers,
        json={"name": "Daisy", "ear_tag": "DEMO-002", "breed": "Jersey"},
    ).raise_for_status()
    print("Created cow Daisy")

    collar = client.post(
        f"{GATEWAY}/api/v1/collars",
        headers=headers,
        json={"mac_address": "AA:BB:CC:DD:EE:01"},
    )
    collar.raise_for_status()
    collar_id = collar.json()["id"]
    print(f"Created collar ({collar_id})")

    client.post(
        f"{GATEWAY}/api/v1/collars/{collar_id}/assign/{cow_id}",
        headers=headers,
    ).raise_for_status()
    print("Assigned collar to Bessie")

    client.post(
        f"{GATEWAY}/api/v1/geofences",
        headers=headers,
        json={
            "name": "Pasture A",
            "center_latitude": 52.2053,
            "center_longitude": 0.1218,
            "radius_meters": 500.0,
            "active": True,
        },
    ).raise_for_status()
    print("Created demo geofence Pasture A")

    client.post(
        f"{GATEWAY}/api/v1/telemetry/readings",
        headers=headers,
        json={
            "collar_id": collar_id,
            "cow_id": cow_id,
            "latitude": 52.2053,
            "longitude": 0.1218,
            "activity_score": 72.0,
            "battery_percent": 15.0,
            "temperature_c": 38.6,
        },
    ).raise_for_status()
    print("Posted sample telemetry (triggers low-battery auto-alert)")


def main() -> None:
    print(f"Seeding Cowly via {GATEWAY}")
    with httpx.Client(timeout=30.0) as client:
        wait_for_gateway(client)
        token = obtain_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        seed_data(client, headers)
    print("Seed complete.")
    print(f"  Login: {EMAIL} / {PASSWORD}")
    print(f"  API:   {GATEWAY}/docs")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPStatusError as exc:
        print(f"Seed failed: {exc.response.status_code} {exc.response.text}", file=sys.stderr)
        raise SystemExit(1) from exc
    except httpx.HTTPError as exc:
        print(f"Seed failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
