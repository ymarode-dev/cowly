def test_scan_and_list(client) -> None:
    scan = client.get("/api/v1/collars/scan")
    assert scan.status_code == 200
    data = scan.json()
    assert "collars" in data
    assert "scanned_at" in data

    all_collars = client.get("/api/v1/collars")
    assert all_collars.status_code == 200
    assert len(all_collars.json()) == 20

    unassigned = client.get("/api/v1/collars?assigned=false")
    assert all(c["assigned"] is False for c in unassigned.json())
