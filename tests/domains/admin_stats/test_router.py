def test_get_stats_requires_authentication(client):
    assert client.get("/admin/stats").status_code == 401


def test_get_stats_requires_admin_role(client):
    client.post(
        "/auth/register",
        json={"name": "User", "email": "admin-stats-user@example.com", "password": "password123"},
    )
    client.post("/auth/login", json={"email": "admin-stats-user@example.com", "password": "password123"})
    response = client.get("/admin/stats")
    assert response.status_code == 403


def test_get_stats_returns_the_full_shape_for_an_admin(client, db_session):
    from app.domains.auth.models import User

    client.post(
        "/auth/register",
        json={"name": "Admin", "email": "admin-stats-admin@example.com", "password": "password123"},
    )
    db_session.query(User).filter(User.email == "admin-stats-admin@example.com").update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"email": "admin-stats-admin@example.com", "password": "password123"})

    response = client.get("/admin/stats")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"blogPosts", "forumPosts", "users", "quizAttempts", "contactMessages"}
    assert set(body["blogPosts"].keys()) == {"total", "new30d"}
    assert set(body["contactMessages"].keys()) == {"total", "unread"}
