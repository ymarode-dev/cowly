import respx
from httpx import Response


@respx.mock
def test_health_reports_simulator_status(client) -> None:
    respx.get("http://simulator.test/health").mock(
        return_value=Response(200, json={"status": "ok"})
    )
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "collar-registry"
    assert data["simulator_reachable"] is True
