def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["alerts_total"] == 0
