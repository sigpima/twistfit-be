import hashlib
import hmac
import json
import secrets
import time
from base64 import urlsafe_b64encode

import jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_TTL_SECONDS = 15 * 60
REFRESH_TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60
LEGACY_SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
LEGACY_SESSION_COOKIE_NAME = "twistfit_session"


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, role: str) -> str:
    payload = {"sub": str(user_id), "role": role, "exp": int(time.time()) + ACCESS_TOKEN_TTL_SECONDS}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _b64url_encode(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_legacy_session_cookie_value(email: str, role: str) -> str:
    """Mirrors frontend/lib/auth/session.ts's HMAC-SHA256 cookie scheme byte-for-byte
    so the 10 not-yet-migrated Next.js domains keep accepting sessions issued here."""
    payload = {"email": email, "role": role, "exp": int(time.time() * 1000) + LEGACY_SESSION_TTL_SECONDS * 1000}
    encoded = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(settings.auth_cookie_secret.encode("utf-8"), encoded.encode("utf-8"), hashlib.sha256).digest()
    return f"{encoded}.{_b64url_encode(signature)}"
