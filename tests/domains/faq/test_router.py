def _register_and_login(client, email: str) -> None:
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "password123"})
    client.post("/auth/login", json={"email": email, "password": "password123"})


def test_list_faq_items_is_public(client):
    response = client.get("/faq")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_faq_item_returns_404_when_missing(client):
    response = client.get("/faq/99999")
    assert response.status_code == 404


def test_create_faq_item_requires_authentication(client):
    response = client.post(
        "/faq",
        json={
            "categories": ["account"],
            "question": "Q?",
            "answerMarkdown": "A.",
            "highlightIcon": None,
            "highlightText": None,
        },
    )
    assert response.status_code == 401


def test_create_faq_item_requires_admin_role(client, db_session):
    _register_and_login(client, "faq-user@example.com")
    response = client.post(
        "/faq",
        json={
            "categories": ["account"],
            "question": "Q?",
            "answerMarkdown": "A.",
            "highlightIcon": None,
            "highlightText": None,
        },
    )
    assert response.status_code == 403


def test_admin_can_create_get_update_and_delete_faq_item(client, db_session):
    from app.domains.auth.models import User

    client.post(
        "/auth/register", json={"name": "Admin", "email": "faq-admin@example.com", "password": "password123"}
    )
    db_session.query(User).filter(User.email == "faq-admin@example.com").update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"email": "faq-admin@example.com", "password": "password123"})

    create_response = client.post(
        "/faq",
        json={
            "categories": ["account"],
            "question": "Câu hỏi mới?",
            "answerMarkdown": "Trả lời mới.",
            "highlightIcon": "info",
            "highlightText": None,
        },
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    get_response = client.get(f"/faq/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["question"] == "Câu hỏi mới?"

    update_response = client.put(
        f"/faq/{item_id}",
        json={
            "categories": ["account"],
            "question": "Câu hỏi đã sửa?",
            "answerMarkdown": "Trả lời mới.",
            "highlightIcon": "info",
            "highlightText": None,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["question"] == "Câu hỏi đã sửa?"

    delete_response = client.delete(f"/faq/{item_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/faq/{item_id}").status_code == 404


def test_create_faq_item_rejects_invalid_body(client, db_session):
    from app.domains.auth.models import User

    client.post(
        "/auth/register", json={"name": "Admin", "email": "faq-admin2@example.com", "password": "password123"}
    )
    db_session.query(User).filter(User.email == "faq-admin2@example.com").update({"role": "admin"})
    db_session.commit()
    client.post("/auth/login", json={"email": "faq-admin2@example.com", "password": "password123"})

    response = client.post(
        "/faq",
        json={"categories": [], "question": "", "answerMarkdown": "", "highlightIcon": None, "highlightText": None},
    )
    assert response.status_code == 422
