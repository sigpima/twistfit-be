from app.domains.quiz_attempts import service


def test_create_quiz_attempt_with_no_user(db_session):
    created = service.create_quiz_attempt(db_session, "summer", None)
    assert created.id is not None
    assert created.season == "summer"
    assert created.user_id is None


def test_create_quiz_attempt_with_a_user(db_session):
    from app.domains.auth import service as auth_service

    user = auth_service.create_user(db_session, name="Test", email="quiz-attempt-svc@example.com", password="password123")
    created = service.create_quiz_attempt(db_session, "winter", user.id)
    assert created.user_id == user.id
