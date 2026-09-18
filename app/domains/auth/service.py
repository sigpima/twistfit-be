from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    REFRESH_TOKEN_TTL_SECONDS,
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.domains.auth.identifier import classify_identifier, normalize_phone
from app.domains.auth.models import RefreshToken, User


class EmailAlreadyTakenError(Exception):
    pass


class PhoneAlreadyTakenError(Exception):
    pass


class UsernameAlreadyTakenError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == normalize_email(email))).scalar_one_or_none()


def get_user_by_phone(db: Session, phone: str) -> User | None:
    normalized = normalize_phone(phone)
    if normalized is None:
        return None
    return db.execute(select(User).where(User.phone == normalized)).scalar_one_or_none()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.execute(select(User).where(User.username == username)).scalar_one_or_none()


def get_user_by_identifier(db: Session, identifier: str) -> User | None:
    classified = classify_identifier(identifier)
    if classified is None:
        return None
    kind, value = classified
    if kind == "phone":
        return db.execute(select(User).where(User.phone == value)).scalar_one_or_none()
    return db.execute(select(User).where(User.email == value)).scalar_one_or_none()


def create_user(
    db: Session,
    name: str,
    password: str,
    email: str | None = None,
    phone: str | None = None,
    role: str = "user",
) -> User:
    if not email and not phone:
        raise ValueError("Cần cung cấp email hoặc số điện thoại")

    normalized_email = normalize_email(email) if email else None
    normalized_phone = normalize_phone(phone) if phone else None
    if phone and normalized_phone is None:
        raise ValueError("Số điện thoại không hợp lệ")

    if normalized_email and get_user_by_email(db, normalized_email) is not None:
        raise EmailAlreadyTakenError(normalized_email)
    if normalized_phone and get_user_by_phone(db, normalized_phone) is not None:
        raise PhoneAlreadyTakenError(normalized_phone)

    user = User(
        name=name,
        email=normalized_email,
        phone=normalized_phone,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    user = get_user_by_identifier(db, identifier)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS),
        )
    )
    db.commit()
    return access_token, refresh_token


def rotate_refresh_token(db: Session, refresh_token: str) -> tuple[str, str, User] | None:
    token_hash = hash_refresh_token(refresh_token)
    row = db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).scalar_one_or_none()
    if row is None or row.revoked_at is not None or row.expires_at < datetime.now(timezone.utc):
        return None

    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        return None

    row.revoked_at = datetime.now(timezone.utc)
    db.commit()
    access_token, new_refresh_token = issue_tokens(db, user)
    return access_token, new_refresh_token, user


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    token_hash = hash_refresh_token(refresh_token)
    row = db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).scalar_one_or_none()
    if row is not None and row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)
        db.commit()


def update_profile(
    db: Session,
    user: User,
    name: str,
    phone: str | None,
    username: str | None = None,
    birth_date: date | None = None,
    gender: str | None = None,
    height_cm: float | None = None,
    weight_kg: float | None = None,
) -> User:
    normalized_phone = normalize_phone(phone) if phone else None
    if phone and normalized_phone is None:
        raise ValueError("Số điện thoại không hợp lệ")

    if normalized_phone and normalized_phone != user.phone:
        existing = get_user_by_phone(db, normalized_phone)
        if existing is not None and existing.id != user.id:
            raise PhoneAlreadyTakenError(normalized_phone)

    normalized_username = username.strip() if username else None
    if normalized_username and normalized_username != user.username:
        existing = get_user_by_username(db, normalized_username)
        if existing is not None and existing.id != user.id:
            raise UsernameAlreadyTakenError(normalized_username)

    user.name = name
    user.phone = normalized_phone
    user.username = normalized_username
    user.birth_date = birth_date
    user.gender = gender
    user.height_cm = height_cm
    user.weight_kg = weight_kg
    db.commit()
    db.refresh(user)
    return user


class InvalidCurrentPasswordError(Exception):
    pass


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.password_hash):
        raise InvalidCurrentPasswordError

    user.password_hash = hash_password(new_password)
    db.commit()


def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> None:
    rows = db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
    ).scalars()
    now = datetime.now(timezone.utc)
    for row in rows:
        row.revoked_at = now
    db.commit()
