def test_version_endpoint(client) -> None:
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "api-gateway"
    assert "version" in data
    assert "build_timestamp" in data
    assert "vcs_ref" in data
