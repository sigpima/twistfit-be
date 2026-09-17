from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ACCESS_TOKEN_TTL_SECONDS, REFRESH_TOKEN_TTL_SECONDS
from app.db.session import get_db
from app.deps import get_current_user
from app.domains.auth import service
from app.domains.auth.identifier import classify_identifier
from app.domains.auth.models import User
from app.domains.auth.schemas import (
    AccountResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    UpdateProfileRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        "access_token", access_token, httponly=True, secure=settings.cookie_secure, samesite="lax",
        domain=settings.cookie_domain, max_age=ACCESS_TOKEN_TTL_SECONDS, path="/",
    )
    response.set_cookie(
        "refresh_token", refresh_token, httponly=True, secure=settings.cookie_secure, samesite="lax",
        domain=settings.cookie_domain, max_age=REFRESH_TOKEN_TTL_SECONDS, path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    for name in ("access_token", "refresh_token"):
        response.delete_cookie(name, domain=settings.cookie_domain, path="/")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> User:
    classified = classify_identifier(body.identifier)
    if classified is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="INVALID_IDENTIFIER")
    kind, value = classified

    try:
        return service.create_user(
            db,
            name=body.name,
            password=body.password,
            email=value if kind == "email" else None,
            phone=value if kind == "phone" else None,
        )
    except service.EmailAlreadyTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EMAIL_TAKEN")
    except service.PhoneAlreadyTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PHONE_TAKEN")


@router.post("/login", response_model=AccountResponse)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = service.authenticate_user(db, body.identifier, body.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_CREDENTIALS")

    access_token, refresh_token = service.issue_tokens(db, user)
    _set_auth_cookies(response, access_token, refresh_token)
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
    _set_auth_cookies(response, new_access_token, new_refresh_token)
    return user


@router.get("/me", response_model=AccountResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=AccountResponse)
def update_me(
    body: UpdateProfileRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> User:
    try:
        return service.update_profile(db, user, name=body.name, phone=body.phone)
    except service.PhoneAlreadyTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="PHONE_TAKEN")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="INVALID_PHONE")


@router.post("/me/change-password")
def change_password(
    body: ChangePasswordRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> dict[str, bool]:
    try:
        service.change_password(db, user, current_password=body.current_password, new_password=body.new_password)
    except service.InvalidCurrentPasswordError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INVALID_CURRENT_PASSWORD")
    return {"ok": True}
