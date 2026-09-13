def _register_and_promote_admin(client, db_session, email: str) -> None:
    from app.domains.auth.models import User

    client.post("/auth/register", json={"name": "Admin", "email": email, "password": "password123"})
    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"email": email, "password": "password123"})


VALID_BODY = {
    "name": "Nguyễn Văn Test",
    "email": "test@twistfit.vn",
    "phone": "0909123456",
    "subject": "other",
    "message": "Nội dung test",
}


def test_create_message_requires_no_authentication(client):
    response = client.post("/contact", json=VALID_BODY)
    assert response.status_code == 201
    body = response.json()
    assert body["isRead"] is False
    assert body["name"] == "Nguyễn Văn Test"


def test_create_message_rejects_invalid_body(client):
    response = client.post("/contact", json={**VALID_BODY, "email": "not-an-email"})
    assert response.status_code == 422


def test_list_messages_requires_authentication(client):
    response = client.get("/contact")
    assert response.status_code == 401


def test_list_messages_requires_admin_role(client, db_session):
    client.post(
        "/auth/register", json={"name": "User", "email": "contact-user@example.com", "password": "password123"}
    )
    client.post("/auth/login", json={"email": "contact-user@example.com", "password": "password123"})
    response = client.get("/contact")
    assert response.status_code == 403


def test_admin_can_list_update_and_delete_messages(client, db_session):
    _register_and_promote_admin(client, db_session, "contact-admin@example.com")

    create_response = client.post("/contact", json=VALID_BODY)
    message_id = create_response.json()["id"]

    list_response = client.get("/contact")
    assert list_response.status_code == 200
    assert any(message["id"] == message_id for message in list_response.json())

    update_response = client.patch(f"/contact/{message_id}", json={"isRead": True})
    assert update_response.status_code == 200
    assert update_response.json()["isRead"] is True

    delete_response = client.delete(f"/contact/{message_id}")
    assert delete_response.status_code == 204

    assert client.patch(f"/contact/{message_id}", json={"isRead": True}).status_code == 404


def test_update_and_delete_return_404_when_missing(client, db_session):
    _register_and_promote_admin(client, db_session, "contact-admin2@example.com")
    assert client.patch("/contact/999999", json={"isRead": True}).status_code == 404
    assert client.delete("/contact/999999").status_code == 404
