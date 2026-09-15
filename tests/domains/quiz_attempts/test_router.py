def test_create_attempt_allows_anonymous_submission(client):
    response = client.post("/quiz-attempts", json={"season": "summer"})
    assert response.status_code == 201
    body = response.json()
    assert body["season"] == "summer"
    assert body["userId"] is None


def test_create_attempt_attributes_to_the_logged_in_user(client, db_session):
    from app.domains.auth.models import User

    client.post(
        "/auth/register",
        json={"name": "Test", "identifier": "quiz-attempt-router@example.com", "password": "password123"},
    )
    client.post("/auth/login", json={"identifier": "quiz-attempt-router@example.com", "password": "password123"})
    user = db_session.query(User).filter(User.email == "quiz-attempt-router@example.com").one()

    response = client.post("/quiz-attempts", json={"season": "winter"})
    assert response.status_code == 201
    assert response.json()["userId"] == user.id


def test_create_attempt_treats_an_invalid_access_token_as_anonymous(client):
    client.cookies.set("access_token", "not-a-valid-jwt")
    response = client.post("/quiz-attempts", json={"season": "spring"})
    assert response.status_code == 201
    assert response.json()["userId"] is None


def test_create_attempt_rejects_an_invalid_season(client):
    response = client.post("/quiz-attempts", json={"season": "not-a-season"})
    assert response.status_code == 422


def test_get_me_requires_authentication(client):
    response = client.get("/quiz-attempts/me")
    assert response.status_code == 401


def test_get_me_returns_null_when_no_attempt_exists(client):
    client.post("/auth/register", json={"name": "Test", "identifier": "quiz-me-1@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "quiz-me-1@example.com", "password": "password123"})

    response = client.get("/quiz-attempts/me")

    assert response.status_code == 200
    assert response.json() is None


def test_get_me_returns_the_latest_attempt(client):
    client.post("/auth/register", json={"name": "Test", "identifier": "quiz-me-2@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "quiz-me-2@example.com", "password": "password123"})

    client.post("/quiz-attempts", json={"season": "spring"})
    client.post("/quiz-attempts", json={"season": "autumn"})

    response = client.get("/quiz-attempts/me")

    assert response.status_code == 200
    assert response.json()["season"] == "autumn"
