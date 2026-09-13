from datetime import datetime

from pydantic import EmailStr, field_validator

from app.domains.auth.schemas import CamelModel

CONTACT_SUBJECTS = ["color-test", "virtual-fitting", "stylist", "other"]


class ContactMessageCreate(CamelModel):
    name: str
    email: EmailStr
    phone: str | None = None
    subject: str
    message: str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Họ tên không được để trống")
        return stripped

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("subject")
    @classmethod
    def subject_valid(cls, value: str) -> str:
        if value not in CONTACT_SUBJECTS:
            raise ValueError("Chủ đề không hợp lệ")
        return value

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Nội dung không được để trống")
        return stripped


class ContactMessageUpdate(CamelModel):
    is_read: bool


class ContactMessageResponse(CamelModel):
    id: int
    name: str
    email: str
    phone: str | None
    subject: str
    message: str
    is_read: bool
    created_at: datetime
