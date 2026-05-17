def test_health(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "herd-service"
    assert response.json()["cows_total"] == 0
