from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

COLOR_VARIANTS = ["primary", "secondary", "tertiary"]


class TeamMemberInput(CamelModel):
    image: str
    name: str
    role: str
    bio: str
    badge_variant: str
    role_variant: str
    footer_icon: str
    footer_label: str

    @field_validator("image", "name", "role", "bio", "footer_icon", "footer_label")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Trường này không được để trống")
        return value.strip()

    @field_validator("badge_variant", "role_variant")
    @classmethod
    def variant_valid(cls, value: str) -> str:
        if value not in COLOR_VARIANTS:
            raise ValueError("Giá trị màu không hợp lệ")
        return value


class TeamMemberResponse(CamelModel):
    id: int
    image: str
    name: str
    role: str
    bio: str
    badge_variant: str
    role_variant: str
    footer_icon: str
    footer_label: str
    created_at: datetime
    updated_at: datetime
