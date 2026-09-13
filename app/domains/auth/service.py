from datetime import datetime, timedelta, timezone

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
from app.domains.auth.models import RefreshToken, User


class EmailAlreadyTakenError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == normalize_email(email))).scalar_one_or_none()


def create_user(db: Session, name: str, email: str, password: str, role: str = "user") -> User:
    if get_user_by_email(db, email) is not None:
        raise EmailAlreadyTakenError(email)

    user = User(name=name, email=normalize_email(email), password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
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


def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> None:
    rows = db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
    ).scalars()
    now = datetime.now(timezone.utc)
    for row in rows:
        row.revoked_at = now
    db.commit()
