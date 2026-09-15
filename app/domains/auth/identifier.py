import re
from typing import Literal

from pydantic import EmailStr, TypeAdapter, ValidationError

_PHONE_SEPARATORS = re.compile(r"[ \-.()]")
_VN_MOBILE_PATTERN = re.compile(r"^(0|\+84)(3|5|7|8|9)\d{8}$")

_email_adapter = TypeAdapter(EmailStr)


def normalize_phone(raw: str) -> str | None:
    cleaned = _PHONE_SEPARATORS.sub("", raw.strip())
    if not _VN_MOBILE_PATTERN.match(cleaned):
        return None
    local_digits = cleaned[1:] if cleaned.startswith("0") else cleaned[3:]
    return f"+84{local_digits}"


def classify_identifier(raw: str) -> tuple[Literal["phone"], str] | tuple[Literal["email"], str] | None:
    phone = normalize_phone(raw)
    if phone is not None:
        return "phone", phone

    try:
        email = _email_adapter.validate_python(raw.strip())
    except ValidationError:
        return None
    return "email", email.lower()
