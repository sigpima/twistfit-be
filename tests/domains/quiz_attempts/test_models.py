from app.core.security import hash_password
from app.domains.auth.models import User
from app.domains.quiz_attempts.models import QuizAttempt


def test_create_quiz_attempt_allows_a_null_user_id(db_session):
    attempt = QuizAttempt(
        sub_season="true-winter",
        parent_season="winter",
        hue_result="cool",
        value_result="medium",
        chroma_result="neutral",
        user_id=None,
    )
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)

    assert attempt.id is not None
    assert attempt.user_id is None
    assert attempt.created_at is not None


def test_create_quiz_attempt_can_be_attributed_to_a_user(db_session):
    user = User(
        name="Test", email="quiz-attempt-model@example.com", password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    attempt = QuizAttempt(
        sub_season="true-winter",
        parent_season="winter",
        hue_result="cool",
        value_result="medium",
        chroma_result="neutral",
        user_id=user.id,
    )
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)

    assert attempt.user_id == user.id
