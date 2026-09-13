VALID_BODY = {
    "name": "Test Model",
    "image": "/outfit/models/test.jpg",
    "dossierImage": "/outfit/models/test-dossier.jpg",
    "poseCount": 10,
    "tagline": "Test tagline",
    "undertone": "warm",
    "height": "1m70",
    "bodyShape": "Chữ nhật",
    "waist": "70cm",
    "personalColor": "Warm Spring",
}


def _promote_to_admin(db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()


def test_list_models_is_public(client):
    response = client.get("/model-catalog")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_model_returns_404_when_missing(client):
    response = client.get("/model-catalog/99999")
    assert response.status_code == 404


def test_create_model_requires_authentication(client):
    response = client.post("/model-catalog", json=VALID_BODY)
    assert response.status_code == 401


def test_create_model_requires_admin_role(client, db_session):
    client.post("/auth/register", json={"name": "T", "email": "model-user@example.com", "password": "password123"})
    client.post("/auth/login", json={"email": "model-user@example.com", "password": "password123"})
    response = client.post("/model-catalog", json=VALID_BODY)
    assert response.status_code == 403


def test_admin_can_create_get_update_and_delete_model(client, db_session):
    client.post("/auth/register", json={"name": "Admin", "email": "model-admin@example.com", "password": "password123"})
    _promote_to_admin(db_session, "model-admin@example.com")
    client.post("/auth/login", json={"email": "model-admin@example.com", "password": "password123"})

    create_response = client.post("/model-catalog", json=VALID_BODY)
    assert create_response.status_code == 201
    model_id = create_response.json()["id"]

    get_response = client.get(f"/model-catalog/{model_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Model"

    update_response = client.put(f"/model-catalog/{model_id}", json={**VALID_BODY, "name": "Đã sửa"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Đã sửa"

    delete_response = client.delete(f"/model-catalog/{model_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/model-catalog/{model_id}").status_code == 404


def test_create_model_rejects_invalid_body(client, db_session):
    client.post("/auth/register", json={"name": "Admin", "email": "model-admin2@example.com", "password": "password123"})
    _promote_to_admin(db_session, "model-admin2@example.com")
    client.post("/auth/login", json={"email": "model-admin2@example.com", "password": "password123"})

    response = client.post("/model-catalog", json={**VALID_BODY, "poseCount": 0})
    assert response.status_code == 422
