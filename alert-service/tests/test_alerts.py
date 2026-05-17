import respx
from httpx import Response


@respx.mock
def test_create_list_and_acknowledge(client) -> None:
    respx.post("http://notification.test/api/v1/notifications").mock(
        return_value=Response(201, json={"id": "n1", "status": "sent"})
    )

    create = client.post(
        "/api/v1/alerts",
        json={
            "collar_id": "collar-1",
            "cow_id": "cow-1",
            "alert_type": "low_battery",
            "severity": "warning",
            "message": "Battery low",
            "metadata": {"percent": 10},
        },
    )
    assert create.status_code == 201
    alert_id = create.json()["id"]
    assert create.json()["acknowledged"] is False

    open_only = client.get("/api/v1/alerts?open_only=true")
    assert len(open_only.json()) == 1

    ack = client.post(f"/api/v1/alerts/{alert_id}/acknowledge")
    assert ack.status_code == 200
    assert ack.json()["acknowledged"] is True

    open_after = client.get("/api/v1/alerts?open_only=true")
    assert len(open_after.json()) == 0

    missing = client.post("/api/v1/alerts/missing/acknowledge")
    assert missing.status_code == 404
