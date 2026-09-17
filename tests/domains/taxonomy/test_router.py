def _register_and_promote_admin(client, db_session, email: str) -> None:
    from app.domains.auth.models import User

    client.post("/auth/register", json={"name": "Admin", "identifier": email, "password": "password123"})
    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


def test_list_taxonomy_is_public(client):
    response = client.get("/taxonomy")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_group_requires_admin(client):
    response = client.post("/taxonomy/groups", json={"key": "clothing-type", "label": "Loại quần áo"})
    assert response.status_code == 401


def test_create_group_rejects_non_admin(client, db_session):
    client.post("/auth/register", json={"name": "User", "identifier": "tax-user@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "tax-user@example.com", "password": "password123"})
    response = client.post("/taxonomy/groups", json={"key": "clothing-type", "label": "Loại quần áo"})
    assert response.status_code == 403


def test_admin_can_create_group_and_it_appears_in_the_public_list(client, db_session):
    _register_and_promote_admin(client, db_session, "tax-admin1@example.com")

    create_response = client.post("/taxonomy/groups", json={"key": "clothing-type", "label": "Loại quần áo"})
    assert create_response.status_code == 201
    assert create_response.json()["values"] == []

    list_response = client.get("/taxonomy")
    assert any(g["key"] == "clothing-type" for g in list_response.json())


def test_create_group_rejects_duplicate_key(client, db_session):
    _register_and_promote_admin(client, db_session, "tax-admin2@example.com")
    client.post("/taxonomy/groups", json={"key": "style", "label": "Loại phong cách"})

    response = client.post("/taxonomy/groups", json={"key": "style", "label": "Trùng khóa"})
    assert response.status_code == 400


def test_admin_can_add_update_and_delete_a_value(client, db_session):
    _register_and_promote_admin(client, db_session, "tax-admin3@example.com")
    group_id = client.post("/taxonomy/groups", json={"key": "occasion", "label": "Loại dịp"}).json()["id"]

    create_response = client.post(f"/taxonomy/groups/{group_id}/values", json={"key": "hang-ngay", "label": "Hằng ngày"})
    assert create_response.status_code == 201
    value_id = create_response.json()["id"]

    update_response = client.put(f"/taxonomy/values/{value_id}", json={"key": "hang-ngay", "label": "Hằng ngày (đã sửa)"})
    assert update_response.status_code == 200
    assert update_response.json()["label"] == "Hằng ngày (đã sửa)"

    delete_response = client.delete(f"/taxonomy/values/{value_id}")
    assert delete_response.status_code == 204

    group_after = client.get("/taxonomy").json()
    matching = next(g for g in group_after if g["id"] == group_id)
    assert matching["values"] == []


def test_add_value_to_missing_group_returns_404(client, db_session):
    _register_and_promote_admin(client, db_session, "tax-admin4@example.com")
    response = client.post("/taxonomy/groups/999999/values", json={"key": "ao", "label": "Áo"})
    assert response.status_code == 404
