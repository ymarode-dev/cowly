def test_collar_lifecycle(client) -> None:
    register = client.post(
        "/api/v1/collars",
        json={"mac_address": "AA:BB:CC:DD:EE:01", "firmware_version": "1.0.0"},
    )
    assert register.status_code == 201
    collar = register.json()
    collar_id = collar["id"]
    assert collar["status"] == "available"
    assert collar["mac_address"] == "AA:BB:CC:DD:EE:01"

    dup = client.post(
        "/api/v1/collars",
        json={"mac_address": "AA:BB:CC:DD:EE:01"},
    )
    assert dup.status_code == 409

    assigned = client.post(f"/api/v1/collars/{collar_id}/assign/cow-123")
    assert assigned.status_code == 200
    assert assigned.json()["cow_id"] == "cow-123"
    assert assigned.json()["status"] == "assigned"

    listed = client.get("/api/v1/collars")
    assert len(listed.json()) == 1

    missing = client.get("/api/v1/collars/missing-id")
    assert missing.status_code == 404
