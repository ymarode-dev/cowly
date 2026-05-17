def test_send_and_list(client) -> None:
    send = client.post(
        "/api/v1/notifications",
        json={
            "channel": "push",
            "recipient": "farm-default",
            "subject": "Test",
            "body": "Hello",
            "metadata": {"key": "value"},
        },
    )
    assert send.status_code == 201
    assert send.json()["status"] == "sent"

    listed = client.get("/api/v1/notifications")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
