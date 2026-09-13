import base64
import hashlib
import hmac

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_legacy_session_cookie_value,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_hash_password_round_trips():
    hashed = hash_password("s3cret123")
    assert hashed != "s3cret123"
    assert verify_password("s3cret123", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_round_trips():
    token = create_access_token(user_id=42, role="admin")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"


def test_decode_access_token_rejects_garbage():
    assert decode_access_token("not-a-token") is None


def test_generate_refresh_token_is_unique_and_hash_is_deterministic():
    token_a = generate_refresh_token()
    token_b = generate_refresh_token()
    assert token_a != token_b
    assert hash_refresh_token(token_a) == hash_refresh_token(token_a)
    assert hash_refresh_token(token_a) != hash_refresh_token(token_b)


def test_legacy_session_cookie_value_matches_node_hmac_scheme():
    value = create_legacy_session_cookie_value("user@twistfit.vn", "user")
    encoded, signature = value.split(".")

    expected_signature = hmac.new(
        settings.auth_cookie_secret.encode("utf-8"), encoded.encode("utf-8"), hashlib.sha256
    ).digest()
    expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).rstrip(b"=").decode("ascii")
    assert signature == expected_signature_b64

    padded = encoded + "=" * (-len(encoded) % 4)
    payload = base64.urlsafe_b64decode(padded).decode("utf-8")
    assert '"email":"user@twistfit.vn"' in payload
    assert '"role":"user"' in payload
