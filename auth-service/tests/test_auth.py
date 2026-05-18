def test_register_login_and_verify(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "farmer@test.com",
            "password": "password123",
            "farm_name": "Test Farm",
        },
    )
    assert register.status_code == 201
    user = register.json()
    assert user["email"] == "farmer@test.com"
    assert user["farm_name"] == "Test Farm"
    assert user["farm_id"]

    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "email": "farmer@test.com",
            "password": "otherpass99",
            "farm_name": "Other",
        },
    )
    assert duplicate.status_code == 409

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "farmer@test.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]
    assert login.json()["refresh_token"]
    token = login.json()["access_token"]
    refresh = login.json()["refresh_token"]

    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": "farmer@test.com", "password": "wrong"},
    )
    assert bad_login.status_code == 401

    verify = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert verify.status_code == 200
    assert verify.json()["valid"] is True
    assert verify.json()["email"] == "farmer@test.com"
    assert verify.json()["farm_id"] == user["farm_id"]

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert refreshed.status_code == 200
    new_access = refreshed.json()["access_token"]

    logout = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_access}"},
        json={"refresh_token": refreshed.json()["refresh_token"]},
    )
    assert logout.status_code == 204

    after_logout = client.get(
        "/api/v1/auth/verify",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert after_logout.json()["valid"] is False

    no_token = client.get("/api/v1/auth/verify")
    assert no_token.json()["valid"] is False

    health = client.get("/health")
    assert health.json()["users_registered"] == 1
