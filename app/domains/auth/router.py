from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    ACCESS_TOKEN_TTL_SECONDS,
    LEGACY_SESSION_COOKIE_NAME,
    LEGACY_SESSION_TTL_SECONDS,
    REFRESH_TOKEN_TTL_SECONDS,
    create_legacy_session_cookie_value,
)
from app.db.session import get_db
from app.deps import get_current_user
from app.domains.auth import service
from app.domains.auth.models import User
from app.domains.auth.schemas import AccountResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, user: User, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        "access_token", access_token, httponly=True, secure=settings.cookie_secure, samesite="lax",
        domain=settings.cookie_domain, max_age=ACCESS_TOKEN_TTL_SECONDS, path="/",
    )
    response.set_cookie(
        "refresh_token", refresh_token, httponly=True, secure=settings.cookie_secure, samesite="lax",
        domain=settings.cookie_domain, max_age=REFRESH_TOKEN_TTL_SECONDS, path="/",
    )
    response.set_cookie(
        LEGACY_SESSION_COOKIE_NAME, create_legacy_session_cookie_value(user.email, user.role),
        httponly=True, secure=settings.cookie_secure, samesite="lax",
        domain=settings.cookie_domain, max_age=LEGACY_SESSION_TTL_SECONDS, path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    for name in ("access_token", "refresh_token", LEGACY_SESSION_COOKIE_NAME):
        response.delete_cookie(name, domain=settings.cookie_domain, path="/")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> User:
    try:
        return service.create_user(db, name=body.name, email=body.email, password=body.password)
    except service.EmailAlreadyTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EMAIL_TAKEN")


@router.post("/login", response_model=AccountResponse)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = service.authenticate_user(db, body.email, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_CREDENTIALS")

    access_token, refresh_token = service.issue_tokens(db, user)
    _set_auth_cookies(response, user, access_token, refresh_token)
    return user


@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    if refresh_token:
        service.revoke_refresh_token(db, refresh_token)
    _clear_auth_cookies(response)
    return {"ok": True}


@router.post("/refresh", response_model=AccountResponse)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MISSING_REFRESH_TOKEN")

    rotated = service.rotate_refresh_token(db, refresh_token)
    if rotated is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_REFRESH_TOKEN")

    new_access_token, new_refresh_token, user = rotated
    _set_auth_cookies(response, user, new_access_token, new_refresh_token)
    return user


@router.get("/me", response_model=AccountResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user
