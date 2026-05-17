def test_cow_crud(client) -> None:
    create = client.post(
        "/api/v1/cows",
        json={
            "name": "Bessie",
            "ear_tag": "TAG-001",
            "breed": "Holstein",
            "weight_kg": 450.0,
        },
    )
    assert create.status_code == 201
    cow = create.json()
    cow_id = cow["id"]
    assert cow["name"] == "Bessie"
    assert cow["collar_id"] is None

    dup = client.post(
        "/api/v1/cows",
        json={"name": "Other", "ear_tag": "TAG-001", "breed": "Jersey"},
    )
    assert dup.status_code == 409

    listed = client.get("/api/v1/cows")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    get_one = client.get(f"/api/v1/cows/{cow_id}")
    assert get_one.status_code == 200

    updated = client.patch(
        f"/api/v1/cows/{cow_id}",
        json={"name": "Bessie II", "collar_id": "collar-abc"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Bessie II"
    assert updated.json()["collar_id"] == "collar-abc"

    missing = client.get("/api/v1/cows/not-a-uuid")
    assert missing.status_code == 404

    deleted = client.delete(f"/api/v1/cows/{cow_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/cows/{cow_id}").status_code == 404
