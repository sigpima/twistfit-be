from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

UNDERTONES = ["warm", "cool", "neutral"]


class CatalogModelInput(CamelModel):
    name: str
    image: str
    dossier_image: str
    pose_count: int
    tagline: str
    undertone: str
    height: str
    body_shape: str
    waist: str
    personal_color: str

    @field_validator("name", "image", "dossier_image", "tagline", "height", "body_shape", "waist", "personal_color")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Trường này không được để trống")
        return value.strip()

    @field_validator("undertone")
    @classmethod
    def undertone_valid(cls, value: str) -> str:
        if value not in UNDERTONES:
            raise ValueError("Undertone không hợp lệ")
        return value

    @field_validator("pose_count")
    @classmethod
    def pose_count_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Số dáng chụp phải là số nguyên dương")
        return value


class CatalogModelResponse(CamelModel):
    id: int
    name: str
    image: str
    dossier_image: str
    side_image: str | None
    pose_count: int
    tagline: str
    undertone: str
    height: str
    body_shape: str
    waist: str
    personal_color: str
    created_at: datetime
    updated_at: datetime
