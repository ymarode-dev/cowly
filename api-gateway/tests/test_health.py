import respx
from httpx import Response


@respx.mock
def test_health_aggregates_services(client) -> None:
    for base in (
        "http://auth.test",
        "http://herd.test",
        "http://registry.test",
        "http://simulator.test",
        "http://telemetry.test",
        "http://alert.test",
        "http://notification.test",
    ):
        respx.get(f"{base}/health").mock(
            return_value=Response(200, json={"status": "ok"})
        )

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["services"]) == 7
    assert all(s["status"] == "ok" for s in data["services"])
