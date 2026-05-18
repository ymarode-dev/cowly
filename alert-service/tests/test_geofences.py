def test_geofence_crud(client) -> None:
    create = client.post(
        "/api/v1/geofences",
        json={
            "name": "Pasture",
            "center_latitude": 52.0,
            "center_longitude": -1.0,
            "radius_meters": 500.0,
        },
    )
    assert create.status_code == 201
    geofence_id = create.json()["id"]
    assert create.json()["farm_id"] == "test-farm-id"

    listed = client.get("/api/v1/geofences")
    assert len(listed.json()) == 1

    updated = client.patch(
        f"/api/v1/geofences/{geofence_id}",
        json={"radius_meters": 600.0},
    )
    assert updated.status_code == 200
    assert updated.json()["radius_meters"] == 600.0

    client.delete(f"/api/v1/geofences/{geofence_id}")
    assert client.get("/api/v1/geofences").json() == []
