VALID_BODY = {
    "questionText": "Câu hỏi test?",
    "sortOrder": 0,
    "options": [
        {"label": "A", "season": "spring"},
        {"label": "B", "season": "summer"},
    ],
}


def _promote_to_admin(db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()


def test_list_quiz_questions_is_public(client):
    response = client.get("/quiz-questions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_quiz_question_returns_404_when_missing(client):
    response = client.get("/quiz-questions/99999")
    assert response.status_code == 404


def test_create_quiz_question_requires_authentication(client):
    response = client.post("/quiz-questions", json=VALID_BODY)
    assert response.status_code == 401


def test_create_quiz_question_requires_admin_role(client, db_session):
    client.post("/auth/register", json={"name": "T", "identifier": "quiz-user@example.com", "password": "password123"})
    client.post("/auth/login", json={"identifier": "quiz-user@example.com", "password": "password123"})
    response = client.post("/quiz-questions", json=VALID_BODY)
    assert response.status_code == 403


def test_admin_can_create_get_update_and_delete_quiz_question(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "quiz-admin@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "quiz-admin@example.com")
    client.post("/auth/login", json={"identifier": "quiz-admin@example.com", "password": "password123"})

    create_response = client.post("/quiz-questions", json=VALID_BODY)
    assert create_response.status_code == 201
    question_id = create_response.json()["id"]
    assert len(create_response.json()["options"]) == 2

    get_response = client.get(f"/quiz-questions/{question_id}")
    assert get_response.status_code == 200
    assert get_response.json()["questionText"] == "Câu hỏi test?"

    update_response = client.put(
        f"/quiz-questions/{question_id}",
        json={
            **VALID_BODY,
            "questionText": "Đã sửa?",
            "options": [
                {"label": "C", "season": "autumn"},
                {"label": "D", "season": "winter"},
                {"label": "E", "season": "spring"},
            ],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["questionText"] == "Đã sửa?"
    assert len(update_response.json()["options"]) == 3

    delete_response = client.delete(f"/quiz-questions/{question_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/quiz-questions/{question_id}").status_code == 404


def test_create_quiz_question_rejects_invalid_body(client, db_session):
    client.post(
        "/auth/register", json={"name": "Admin", "identifier": "quiz-admin2@example.com", "password": "password123"}
    )
    _promote_to_admin(db_session, "quiz-admin2@example.com")
    client.post("/auth/login", json={"identifier": "quiz-admin2@example.com", "password": "password123"})

    response = client.post(
        "/quiz-questions", json={**VALID_BODY, "options": [{"label": "Only one", "season": "spring"}]}
    )
    assert response.status_code == 422
