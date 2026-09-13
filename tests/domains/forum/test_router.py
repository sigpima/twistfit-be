def _register_and_login(client, email: str) -> None:
    client.post("/auth/register", json={"name": "User", "email": email, "password": "password123"})
    client.post("/auth/login", json={"email": email, "password": "password123"})


def _promote_to_admin_and_relogin(client, db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"email": email, "password": "password123"})


VALID_BODY = {"title": "Bài test", "body": "Nội dung", "category": "general"}


def _publish(db_session, post_id: int) -> None:
    from app.domains.forum.models import ForumPost

    db_session.query(ForumPost).filter(ForumPost.id == post_id).update({"status": "published"})
    db_session.commit()


def test_list_posts_is_public_and_only_returns_published(client, db_session):
    _register_and_login(client, "forum-author@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    assert client.get("/forum/posts").json() == []

    _publish(db_session, post["id"])

    published = client.get("/forum/posts").json()
    assert [p["id"] for p in published] == [post["id"]]


def test_list_posts_filters_by_category(client, db_session):
    _register_and_login(client, "forum-cat@example.com")
    general = client.post("/forum/posts", json=VALID_BODY).json()
    styling = client.post("/forum/posts", json={**VALID_BODY, "category": "styling-help"}).json()
    _publish(db_session, general["id"])
    _publish(db_session, styling["id"])

    response = client.get("/forum/posts?category=styling-help")
    assert [p["id"] for p in response.json()] == [styling["id"]]


def test_list_posts_ignores_an_invalid_category_filter(client, db_session):
    _register_and_login(client, "forum-cat2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    response = client.get("/forum/posts?category=not-a-real-category")
    assert [p["id"] for p in response.json()] == [post["id"]]


def test_create_post_requires_authentication(client):
    response = client.post("/forum/posts", json=VALID_BODY)
    assert response.status_code == 401


def test_create_post_rejects_invalid_body(client):
    _register_and_login(client, "forum-invalid@example.com")
    response = client.post("/forum/posts", json={**VALID_BODY, "category": "not-a-category"})
    assert response.status_code == 422


def test_get_post_returns_404_for_a_pending_post_to_a_stranger(client):
    _register_and_login(client, "forum-owner@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-stranger@example.com")
    assert client.get(f"/forum/posts/{post['id']}").status_code == 404


def test_get_post_is_visible_to_its_owner_while_pending(client):
    _register_and_login(client, "forum-owner2@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    assert client.get(f"/forum/posts/{post['id']}").status_code == 200


def test_get_post_is_visible_to_an_admin_while_pending(client, db_session):
    _register_and_login(client, "forum-owner3@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-admin-viewer@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-admin-viewer@example.com")
    assert client.get(f"/forum/posts/{post['id']}").status_code == 200


def test_get_post_returns_404_for_a_nonexistent_id(client):
    assert client.get("/forum/posts/999999").status_code == 404


def test_list_my_posts_requires_authentication(client):
    assert client.get("/forum/posts/mine").status_code == 401


def test_list_my_posts_returns_only_the_caller_own_posts_any_status(client):
    _register_and_login(client, "forum-mine@example.com")
    mine = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-other@example.com")
    client.post("/forum/posts", json=VALID_BODY)

    _register_and_login(client, "forum-mine@example.com")
    response = client.get("/forum/posts/mine")
    assert [p["id"] for p in response.json()] == [mine["id"]]


def test_update_post_requires_authentication(client):
    assert client.put("/forum/posts/1", json=VALID_BODY).status_code == 401


def test_update_post_requires_ownership(client):
    _register_and_login(client, "forum-owner4@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-not-owner@example.com")
    response = client.put(f"/forum/posts/{post['id']}", json=VALID_BODY)
    assert response.status_code == 403


def test_update_post_resets_status_to_pending_even_from_published(client, db_session):
    _register_and_login(client, "forum-owner5@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    _publish(db_session, post["id"])

    updated = client.put(f"/forum/posts/{post['id']}", json={**VALID_BODY, "title": "Đã sửa"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "pending"
    assert updated.json()["title"] == "Đã sửa"


def test_update_post_returns_404_when_missing(client):
    _register_and_login(client, "forum-owner6@example.com")
    assert client.put("/forum/posts/999999", json=VALID_BODY).status_code == 404


def test_delete_post_requires_authentication(client):
    assert client.delete("/forum/posts/1").status_code == 401


def test_delete_post_allowed_for_owner(client):
    _register_and_login(client, "forum-owner7@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()
    assert client.delete(f"/forum/posts/{post['id']}").status_code == 204


def test_delete_post_allowed_for_admin(client, db_session):
    _register_and_login(client, "forum-owner8@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-admin-deleter@example.com")
    _promote_to_admin_and_relogin(client, db_session, "forum-admin-deleter@example.com")
    assert client.delete(f"/forum/posts/{post['id']}").status_code == 204


def test_delete_post_forbidden_for_non_owner_non_admin(client):
    _register_and_login(client, "forum-owner9@example.com")
    post = client.post("/forum/posts", json=VALID_BODY).json()

    _register_and_login(client, "forum-stranger2@example.com")
    assert client.delete(f"/forum/posts/{post['id']}").status_code == 403


def test_delete_post_returns_404_when_missing(client):
    _register_and_login(client, "forum-owner10@example.com")
    assert client.delete("/forum/posts/999999").status_code == 404
