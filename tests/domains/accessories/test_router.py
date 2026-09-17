VALID_BODY = {
    "name": "Túi tote nâu",
    "imageUrl": "https://example.com/tote.png",
    "affiliateLink": "https://shop.example.com/tote",
    "category": "tui-xach",
    "styleTags": ["casual"],
    "occasionTags": ["hang-ngay"],
    "toneTags": ["autumn"],
}


def _promote_to_admin(db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()


def test_list_accessories_is_public(client):
    response = client.get("/accessories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_accessory_returns_404_when_missing(client):
    response = client.get("/accessories/99999")
    assert response.status_code == 404


def test_create_accessory_requires_authentication(client):
    response = client.post("/accessories", json=VALID_BODY)
    assert response.status_code == 401


def test_create_accessory_requires_admin_role(client):
    client.post(
        "/auth/register", json={"name": "T", "identifier": "accessory-user@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"identifier": "accessory-user@example.com", "password": "password123"})
    response = client.post("/accessories", json=VALID_BODY)
    assert response.status_code == 403


def test_admin_can_create_get_update_and_delete_accessory(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "accessory-admin@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "accessory-admin@example.com")
    client.post("/auth/login", json={"identifier": "accessory-admin@example.com", "password": "password123"})

    create_response = client.post("/accessories", json=VALID_BODY)
    assert create_response.status_code == 201
    accessory_id = create_response.json()["id"]
    assert create_response.json()["isActive"] is True

    get_response = client.get(f"/accessories/{accessory_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Túi tote nâu"

    update_response = client.put(f"/accessories/{accessory_id}", json={**VALID_BODY, "name": "Túi tote đã sửa"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Túi tote đã sửa"

    delete_response = client.delete(f"/accessories/{accessory_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/accessories/{accessory_id}").status_code == 404


def test_create_accessory_rejects_an_invalid_category(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "accessory-admin2@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "accessory-admin2@example.com")
    client.post("/auth/login", json={"identifier": "accessory-admin2@example.com", "password": "password123"})

    response = client.post("/accessories", json={**VALID_BODY, "category": "not-a-real-category"})
    assert response.status_code == 422


def test_create_accessory_rejects_empty_style_tags(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "accessory-admin3@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "accessory-admin3@example.com")
    client.post("/auth/login", json={"identifier": "accessory-admin3@example.com", "password": "password123"})

    response = client.post("/accessories", json={**VALID_BODY, "styleTags": []})
    assert response.status_code == 422
