def test_root_lists_routes(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "api-gateway"
    assert "auth" in data["routes"]
