from datetime import datetime, timedelta, timezone

from app.domains.auth.models import RefreshToken, User


def test_can_insert_and_query_user(db_session):
    user = User(name="Test", email="test@example.com", password_hash="hashed", role="user")
    db_session.add(user)
    db_session.flush()

    fetched = db_session.query(User).filter_by(email="test@example.com").one()
    assert fetched.id == user.id
    assert fetched.is_active is True


def test_can_insert_refresh_token_linked_to_user(db_session):
    user = User(name="Test", email="test2@example.com", password_hash="hashed", role="user")
    db_session.add(user)
    db_session.flush()

    token = RefreshToken(
        user_id=user.id,
        token_hash="abc123",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(token)
    db_session.flush()

    fetched = db_session.query(RefreshToken).filter_by(token_hash="abc123").one()
    assert fetched.user_id == user.id
