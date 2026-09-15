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
    assert response.json() == {"name": "Linh", "email": "login@example.com", "phone": None, "role": "user"}
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
