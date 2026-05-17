import respx
from httpx import Response


@respx.mock
def test_proxy_scan(client) -> None:
    respx.get("http://simulator.test/api/v1/collars/scan").mock(
        return_value=Response(
            200,
            json={"scanned_at": "2026-01-01T00:00:00Z", "collars": []},
        )
    )
    response = client.get("/api/v1/simulator/scan")
    assert response.status_code == 200
    assert "collars" in response.json()
