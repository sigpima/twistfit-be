VALID_BODY = {
    "image": "/outfit/capsule-test.jpg",
    "alt": "Ảnh test",
    "tagVariant": "primary",
    "tagLabel": "Set test",
    "fitFor": "Phù hợp: Test",
    "title": "Set Test",
    "tone": "Test Tone",
    "description": "Mô tả test",
    "items": [{"label": "Món đồ:", "price": "100.000 ₫"}],
}


def _promote_to_admin(db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()


def test_list_capsule_sets_is_public(client):
    response = client.get("/capsule-wardrobe")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_capsule_set_returns_404_when_missing(client):
    response = client.get("/capsule-wardrobe/99999")
    assert response.status_code == 404


def test_create_capsule_set_requires_authentication(client):
    response = client.post("/capsule-wardrobe", json=VALID_BODY)
    assert response.status_code == 401


def test_create_capsule_set_requires_admin_role(client, db_session):
    client.post("/auth/register", json={"name": "T", "email": "capsule-user@example.com", "password": "password123"})
    client.post("/auth/login", json={"email": "capsule-user@example.com", "password": "password123"})
    response = client.post("/capsule-wardrobe", json=VALID_BODY)
    assert response.status_code == 403


def test_admin_can_create_get_update_and_delete_capsule_set(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "email": "capsule-admin@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "capsule-admin@example.com")
    client.post("/auth/login", json={"email": "capsule-admin@example.com", "password": "password123"})

    create_response = client.post("/capsule-wardrobe", json=VALID_BODY)
    assert create_response.status_code == 201
    set_id = create_response.json()["id"]

    get_response = client.get(f"/capsule-wardrobe/{set_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Set Test"

    update_response = client.put(f"/capsule-wardrobe/{set_id}", json={**VALID_BODY, "title": "Đã sửa"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Đã sửa"

    delete_response = client.delete(f"/capsule-wardrobe/{set_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/capsule-wardrobe/{set_id}").status_code == 404


def test_create_capsule_set_rejects_invalid_body(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "email": "capsule-admin2@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "capsule-admin2@example.com")
    client.post("/auth/login", json={"email": "capsule-admin2@example.com", "password": "password123"})

    response = client.post("/capsule-wardrobe", json={**VALID_BODY, "items": []})
    assert response.status_code == 422
