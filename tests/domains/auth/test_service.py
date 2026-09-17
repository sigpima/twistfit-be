import pytest

from app.domains.auth import service


def test_create_user_hashes_password_and_defaults_role(db_session):
    user = service.create_user(db_session, name="Linh", email="Linh@Example.com ", password="password123")
    assert user.email == "linh@example.com"
    assert user.password_hash != "password123"
    assert user.role == "user"


def test_create_user_rejects_duplicate_email(db_session):
    service.create_user(db_session, name="A", email="dup@example.com", password="password123")
    with pytest.raises(service.EmailAlreadyTakenError):
        service.create_user(db_session, name="B", email="dup@example.com", password="password456")


def test_create_user_accepts_a_phone_number_instead_of_email(db_session):
    user = service.create_user(db_session, name="Linh", phone="0912345678", password="password123")
    assert user.email is None
    assert user.phone == "+84912345678"


def test_create_user_rejects_duplicate_phone(db_session):
    service.create_user(db_session, name="A", phone="0912345678", password="password123")
    with pytest.raises(service.PhoneAlreadyTakenError):
        service.create_user(db_session, name="B", phone="0912345678", password="password456")


def test_create_user_requires_at_least_one_of_email_or_phone(db_session):
    with pytest.raises(ValueError):
        service.create_user(db_session, name="A", password="password123")


def test_authenticate_user_accepts_correct_password(db_session):
    service.create_user(db_session, name="A", email="auth@example.com", password="password123")
    user = service.authenticate_user(db_session, "auth@example.com", "password123")
    assert user is not None
    assert user.email == "auth@example.com"


def test_authenticate_user_accepts_a_phone_number_identifier(db_session):
    service.create_user(db_session, name="A", phone="0912345678", password="password123")
    user = service.authenticate_user(db_session, "0912345678", "password123")
    assert user is not None
    assert user.phone == "+84912345678"


def test_authenticate_user_rejects_wrong_password(db_session):
    service.create_user(db_session, name="A", email="auth2@example.com", password="password123")
    assert service.authenticate_user(db_session, "auth2@example.com", "wrong") is None


def test_authenticate_user_rejects_inactive_user(db_session):
    user = service.create_user(db_session, name="A", email="inactive@example.com", password="password123")
    user.is_active = False
    db_session.commit()
    assert service.authenticate_user(db_session, "inactive@example.com", "password123") is None


def test_issue_and_rotate_refresh_token(db_session):
    user = service.create_user(db_session, name="A", email="rotate@example.com", password="password123")
    _access_token, refresh_token = service.issue_tokens(db_session, user)

    rotated = service.rotate_refresh_token(db_session, refresh_token)
    assert rotated is not None
    _new_access_token, new_refresh_token, rotated_user = rotated
    assert new_refresh_token != refresh_token
    assert rotated_user.id == user.id

    assert service.rotate_refresh_token(db_session, refresh_token) is None


def test_revoke_all_refresh_tokens_for_user_blocks_future_rotation(db_session):
    user = service.create_user(db_session, name="A", email="revoke@example.com", password="password123")
    _access_token, refresh_token = service.issue_tokens(db_session, user)

    service.revoke_all_refresh_tokens_for_user(db_session, user.id)

    assert service.rotate_refresh_token(db_session, refresh_token) is None


def test_update_profile_updates_name_and_normalized_phone(db_session):
    user = service.create_user(db_session, name="A", email="profile@example.com", password="password123")
    updated = service.update_profile(db_session, user, name="A Nguyễn", phone="0912345678")
    assert updated.name == "A Nguyễn"
    assert updated.phone == "+84912345678"


def test_update_profile_rejects_a_phone_taken_by_another_user(db_session):
    service.create_user(db_session, name="A", phone="0912345678", password="password123")
    user_b = service.create_user(db_session, name="B", email="b@example.com", password="password123")
    with pytest.raises(service.PhoneAlreadyTakenError):
        service.update_profile(db_session, user_b, name="B", phone="0912345678")


def test_change_password_rejects_an_incorrect_current_password(db_session):
    user = service.create_user(db_session, name="A", email="pw@example.com", password="password123")
    with pytest.raises(service.InvalidCurrentPasswordError):
        service.change_password(db_session, user, current_password="wrong", new_password="newpassword456")


def test_change_password_rehashes_the_password(db_session):
    user = service.create_user(db_session, name="A", email="pw2@example.com", password="password123")
    old_hash = user.password_hash
    service.change_password(db_session, user, current_password="password123", new_password="newpassword456")
    assert user.password_hash != old_hash
    assert service.authenticate_user(db_session, "pw2@example.com", "newpassword456") is not None
