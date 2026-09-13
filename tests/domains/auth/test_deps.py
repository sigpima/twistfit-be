import pytest
from fastapi import HTTPException

from app.core.security import create_access_token
from app.deps import get_current_user, require_admin
from app.domains.auth import service


def test_get_current_user_rejects_missing_cookie(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(access_token=None, db=db_session)
    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(access_token="garbage", db=db_session)
    assert exc_info.value.status_code == 401


def test_get_current_user_returns_user_for_valid_token(db_session):
    user = service.create_user(db_session, name="A", email="deps@example.com", password="password123")
    token = create_access_token(user_id=user.id, role=user.role)

    result = get_current_user(access_token=token, db=db_session)
    assert result.id == user.id


def test_get_current_user_rejects_inactive_user(db_session):
    user = service.create_user(db_session, name="A", email="deps2@example.com", password="password123")
    token = create_access_token(user_id=user.id, role=user.role)
    user.is_active = False
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(access_token=token, db=db_session)
    assert exc_info.value.status_code == 401


def test_require_admin_rejects_non_admin(db_session):
    user = service.create_user(db_session, name="A", email="deps3@example.com", password="password123")
    with pytest.raises(HTTPException) as exc_info:
        require_admin(user=user)
    assert exc_info.value.status_code == 403


def test_require_admin_accepts_admin(db_session):
    user = service.create_user(
        db_session, name="A", email="deps4@example.com", password="password123", role="admin"
    )
    assert require_admin(user=user).id == user.id
