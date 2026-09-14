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


def test_get_latest_attempt_returns_none_when_the_user_has_no_attempts(db_session):
    from app.domains.auth import service as auth_service

    user = auth_service.create_user(db_session, name="Test", email="quiz-latest-1@example.com", password="password123")
    assert service.get_latest_attempt(db_session, user.id) is None


def test_get_latest_attempt_returns_the_most_recent_one(db_session):
    from app.domains.auth import service as auth_service

    user = auth_service.create_user(db_session, name="Test", email="quiz-latest-2@example.com", password="password123")
    service.create_quiz_attempt(db_session, "spring", user.id)
    latest = service.create_quiz_attempt(db_session, "winter", user.id)

    result = service.get_latest_attempt(db_session, user.id)

    assert result is not None
    assert result.id == latest.id
    assert result.season == "winter"


def test_get_latest_attempt_ignores_other_users_attempts(db_session):
    from app.domains.auth import service as auth_service

    user = auth_service.create_user(db_session, name="Test", email="quiz-latest-3@example.com", password="password123")
    other_user = auth_service.create_user(db_session, name="Other", email="quiz-latest-4@example.com", password="password123")
    service.create_quiz_attempt(db_session, "summer", other_user.id)

    assert service.get_latest_attempt(db_session, user.id) is None
