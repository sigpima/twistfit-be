def test_register_creates_user(client):
    response = client.post(
        "/auth/register", json={"name": "Linh", "identifier": "reg@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "reg@example.com"
    assert body["phone"] is None
    assert body["role"] == "user"
    assert "id" in body


def test_register_rejects_duplicate_email(client):
    client.post("/auth/register", json={"name": "A", "identifier": "dup@example.com", "password": "password123"})
    response = client.post(
        "/auth/register", json={"name": "B", "identifier": "dup@example.com", "password": "password456"}
    )
    assert response.status_code == 409


def test_register_creates_user_with_a_phone_number(client):
    response = client.post(
        "/auth/register", json={"name": "Linh", "identifier": "0912345678", "password": "password123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["phone"] == "+84912345678"
    assert body["email"] is None


def test_register_rejects_duplicate_phone(client):
    client.post("/auth/register", json={"name": "A", "identifier": "0912345678", "password": "password123"})
    response = client.post(
        "/auth/register", json={"name": "B", "identifier": "0912345678", "password": "password456"}
    )
    assert response.status_code == 409


def test_register_rejects_an_invalid_identifier(client):
    response = client.post(
        "/auth/register", json={"name": "A", "identifier": "not-an-identifier", "password": "password123"}
    )
    assert response.status_code == 422


def test_login_sets_cookies_and_returns_account(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "login@example.com", "password": "password123"}
    )
    response = client.post("/auth/login", json={"identifier": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Linh"
    assert body["email"] == "login@example.com"
    assert body["phone"] is None
    assert body["role"] == "user"
    assert body["username"] is None
    assert body["birthDate"] is None
    assert body["gender"] is None
    assert body["heightCm"] is None
    assert body["weightKg"] is None
    assert "createdAt" in body
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_login_with_a_phone_number(client):
    client.post("/auth/register", json={"name": "Linh", "identifier": "0912345678", "password": "password123"})
    response = client.post("/auth/login", json={"identifier": "0912345678", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["phone"] == "+84912345678"


def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "wrongpw@example.com", "password": "password123"}
    )
    response = client.post("/auth/login", json={"identifier": "wrongpw@example.com", "password": "nope"})
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_account_when_authenticated(client):
    client.post("/auth/register", json={"name": "Linh", "identifier": "me@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "me@example.com", "password": "password123"})
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_refresh_rotates_tokens(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "refresh@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "refresh@example.com", "password": "password123"})
    old_refresh_cookie = client.cookies.get("refresh_token")

    response = client.post("/auth/refresh")
    assert response.status_code == 200
    assert client.cookies.get("refresh_token") != old_refresh_cookie


def test_refresh_rejects_missing_cookie(client):
    response = client.post("/auth/refresh")
    assert response.status_code == 401


def test_logout_clears_cookies(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "logout@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "logout@example.com", "password": "password123"})

    response = client.post("/auth/logout")
    assert response.status_code == 200
    response_after = client.get("/auth/me")
    assert response_after.status_code == 401


def test_update_me_requires_authentication(client):
    response = client.patch("/auth/me", json={"name": "Tên mới"})
    assert response.status_code == 401


def test_update_me_updates_name_and_phone(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "update-me@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "update-me@example.com", "password": "password123"})

    response = client.patch("/auth/me", json={"name": "Linh Đan", "phone": "0912345678"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Linh Đan"
    assert body["phone"] == "+84912345678"
    assert body["email"] == "update-me@example.com"


def test_update_me_can_clear_the_phone_number(client):
    client.post(
        "/auth/register",
        json={"name": "Linh", "identifier": "clear-phone@example.com", "password": "password123"},
    )
    client.post("/auth/login", json={"identifier": "clear-phone@example.com", "password": "password123"})
    client.patch("/auth/me", json={"name": "Linh", "phone": "0912345678"})

    response = client.patch("/auth/me", json={"name": "Linh", "phone": None})
    assert response.status_code == 200
    assert response.json()["phone"] is None


def test_update_me_rejects_an_invalid_phone(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "bad-phone@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "bad-phone@example.com", "password": "password123"})

    response = client.patch("/auth/me", json={"name": "Linh", "phone": "not-a-phone"})
    assert response.status_code == 422


def test_update_me_rejects_a_phone_already_taken_by_another_account(client):
    client.post(
        "/auth/register", json={"name": "A", "identifier": "0912345678", "password": "password123"}
    )
    client.post(
        "/auth/register", json={"name": "B", "identifier": "taken-phone@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "taken-phone@example.com", "password": "password123"})

    response = client.patch("/auth/me", json={"name": "B", "phone": "0912345678"})
    assert response.status_code == 409


def test_update_me_updates_the_new_profile_fields(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "profile-fields@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "profile-fields@example.com", "password": "password123"})

    response = client.patch(
        "/auth/me",
        json={
            "name": "Linh",
            "username": "linh_dan",
            "birthDate": "2000-05-20",
            "gender": "female",
            "heightCm": 162.5,
            "weightKg": 50.5,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "linh_dan"
    assert body["birthDate"] == "2000-05-20"
    assert body["gender"] == "female"
    assert body["heightCm"] == 162.5
    assert body["weightKg"] == 50.5


def test_update_me_rejects_a_username_already_taken_by_another_account(client):
    client.post("/auth/register", json={"name": "A", "identifier": "user-a@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "user-a@example.com", "password": "password123"})
    client.patch("/auth/me", json={"name": "A", "username": "twistfan"})

    client.post("/auth/register", json={"name": "B", "identifier": "user-b@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "user-b@example.com", "password": "password123"})

    response = client.patch("/auth/me", json={"name": "B", "username": "twistfan"})
    assert response.status_code == 409


def test_change_password_requires_authentication(client):
    response = client.post("/auth/me/change-password", json={"currentPassword": "a", "newPassword": "b"})
    assert response.status_code == 401


def test_change_password_updates_the_password(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "change-pw@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "change-pw@example.com", "password": "password123"})

    response = client.post(
        "/auth/me/change-password",
        json={"currentPassword": "password123", "newPassword": "newpassword456"},
    )
    assert response.status_code == 200

    client.post("/auth/logout")
    old_password_login = client.post(
        "/auth/login", json={"identifier": "change-pw@example.com", "password": "password123"}
    )
    assert old_password_login.status_code == 401
    new_password_login = client.post(
        "/auth/login", json={"identifier": "change-pw@example.com", "password": "newpassword456"}
    )
    assert new_password_login.status_code == 200


def test_change_password_rejects_an_incorrect_current_password(client):
    client.post(
        "/auth/register", json={"name": "Linh", "identifier": "wrong-current@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "wrong-current@example.com", "password": "password123"})

    response = client.post(
        "/auth/me/change-password",
        json={"currentPassword": "wrong-password", "newPassword": "newpassword456"},
    )
    assert response.status_code == 401
