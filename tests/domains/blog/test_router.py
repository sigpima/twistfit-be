VALID_BODY = {
    "title": "Bài Test",
    "excerpt": "Mô tả",
    "content": "Nội dung",
    "coverImageUrl": "/blog/test.jpg",
    "category": "styling",
    "authorName": None,
    "isFeatured": False,
    "publishedAt": "2026-01-01",
}


def _promote_to_admin(db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()


def test_list_blog_posts_is_public(client):
    response = client.get("/blog")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_blog_post_by_id_returns_404_when_missing(client):
    response = client.get("/blog/99999")
    assert response.status_code == 404


def test_get_blog_post_by_slug_returns_404_when_missing(client):
    response = client.get("/blog/slug/khong-ton-tai")
    assert response.status_code == 404


def test_create_blog_post_requires_authentication(client):
    response = client.post("/blog", json=VALID_BODY)
    assert response.status_code == 401


def test_create_blog_post_requires_admin_role(client, db_session):
    client.post("/auth/register", json={"name": "T", "identifier": "blog-user@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "blog-user@example.com", "password": "password123"})
    response = client.post("/blog", json=VALID_BODY)
    assert response.status_code == 403


def test_admin_can_create_get_by_slug_update_and_delete_blog_post(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "blog-admin@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "blog-admin@example.com")
    client.post("/auth/login", json={"identifier": "blog-admin@example.com", "password": "password123"})

    create_response = client.post("/blog", json={**VALID_BODY, "slug": "bai-test-router"})
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    assert create_response.json()["slug"] == "bai-test-router"

    slug_response = client.get("/blog/slug/bai-test-router")
    assert slug_response.status_code == 200
    assert slug_response.json()["id"] == post_id

    update_response = client.put(
        f"/blog/{post_id}", json={**VALID_BODY, "slug": "bai-test-router", "title": "Đã sửa"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Đã sửa"

    delete_response = client.delete(f"/blog/{post_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/blog/{post_id}").status_code == 404


def test_create_blog_post_rejects_duplicate_slug_with_409(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "blog-admin2@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "blog-admin2@example.com")
    client.post("/auth/login", json={"identifier": "blog-admin2@example.com", "password": "password123"})

    client.post("/blog", json={**VALID_BODY, "slug": "trung-slug"})
    response = client.post("/blog", json={**VALID_BODY, "slug": "trung-slug"})
    assert response.status_code == 409
    assert response.json()["detail"] == "SLUG_TAKEN"


def test_upload_url_requires_authentication(client):
    response = client.post("/blog/upload-url")
    assert response.status_code == 401


def test_upload_url_requires_admin_role(client):
    client.post(
        "/auth/register", json={"name": "T", "identifier": "blog-upload-user@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "blog-upload-user@example.com", "password": "password123"})
    response = client.post("/blog/upload-url")
    assert response.status_code == 403


def test_upload_url_returns_a_writable_sas_url_and_final_image_url(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "blog-upload-admin@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "blog-upload-admin@example.com")
    client.post("/auth/login", json={"identifier": "blog-upload-admin@example.com", "password": "password123"})

    response = client.post("/blog/upload-url")
    assert response.status_code == 200
    body = response.json()
    assert "sig=" in body["uploadUrl"]
    assert body["blobPath"] in body["imageUrl"]


def test_create_blog_post_rejects_invalid_body(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "blog-admin3@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "blog-admin3@example.com")
    client.post("/auth/login", json={"identifier": "blog-admin3@example.com", "password": "password123"})

    response = client.post("/blog", json={**VALID_BODY, "title": ""})
    assert response.status_code == 422
