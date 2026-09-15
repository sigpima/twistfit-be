VALID_BODY = {
    "image": "/about/a.jpg",
    "name": "Nguyễn Văn A",
    "role": "Stylist",
    "bio": "Tiểu sử mẫu.",
    "badgeVariant": "primary",
    "roleVariant": "primary",
    "footerIcon": "star",
    "footerLabel": "Nhãn mẫu",
}


def _promote_to_admin(db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()


def test_list_team_members_is_public(client):
    response = client.get("/team")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_team_member_returns_404_when_missing(client):
    response = client.get("/team/99999")
    assert response.status_code == 404


def test_create_team_member_requires_authentication(client):
    response = client.post("/team", json=VALID_BODY)
    assert response.status_code == 401


def test_create_team_member_requires_admin_role(client, db_session):
    client.post("/auth/register", json={"name": "T", "identifier": "team-user@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "team-user@example.com", "password": "password123"})
    response = client.post("/team", json=VALID_BODY)
    assert response.status_code == 403


def test_admin_can_create_get_update_and_delete_team_member(client, db_session):
    client.post("/auth/register", json={"name": "Admin", "identifier": "team-admin@example.com", "password": "password123"})
    _promote_to_admin(db_session, "team-admin@example.com")
    client.post("/auth/login", json={"identifier": "team-admin@example.com", "password": "password123"})

    create_response = client.post("/team", json=VALID_BODY)
    assert create_response.status_code == 201
    member_id = create_response.json()["id"]

    get_response = client.get(f"/team/{member_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Nguyễn Văn A"

    update_response = client.put(f"/team/{member_id}", json={**VALID_BODY, "name": "Đã sửa"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Đã sửa"

    delete_response = client.delete(f"/team/{member_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/team/{member_id}").status_code == 404


def test_create_team_member_rejects_invalid_body(client, db_session):
    client.post("/auth/register", json={"name": "Admin", "identifier": "team-admin2@example.com", "password": "password123"})
    _promote_to_admin(db_session, "team-admin2@example.com")
    client.post("/auth/login", json={"identifier": "team-admin2@example.com", "password": "password123"})

    response = client.post("/team", json={**VALID_BODY, "name": ""})
    assert response.status_code == 422
