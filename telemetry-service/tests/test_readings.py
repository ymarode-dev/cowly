import respx
from httpx import Response


@respx.mock
def test_ingest_and_latest(client) -> None:
    respx.post("http://alert.test/api/v1/internal/evaluate").mock(
        return_value=Response(200, json=[])
    )

    ingest = client.post(
        "/api/v1/telemetry/readings",
        json={
            "collar_id": "collar-1",
            "cow_id": "cow-1",
            "latitude": 52.1,
            "longitude": -1.2,
            "activity_score": 80.0,
            "battery_percent": 90.0,
        },
    )
    assert ingest.status_code == 201
    assert ingest.json()["collar_id"] == "collar-1"
    assert ingest.json()["farm_id"] == "test-farm-id"
    assert respx.calls.call_count == 1

    client.post(
        "/api/v1/telemetry/readings",
        json={
            "collar_id": "collar-1",
            "latitude": 52.2,
            "longitude": -1.3,
            "activity_score": 70.0,
        },
    )

    latest = client.get("/api/v1/telemetry/collars/collar-1/latest?limit=10")
    assert latest.status_code == 200
    readings = latest.json()
    assert len(readings) == 2
    assert readings[-1]["latitude"] == 52.2
