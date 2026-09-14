from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

CATEGORIES = ["ao-thun", "ao-so-mi", "quan-jean", "dam", "ao-khoac"]
STYLE_TAGS = ["casual", "minimalist", "street", "formal"]
OCCASION_TAGS = ["di-lam", "du-tiec", "di-bien", "hang-ngay"]


class WardrobeItemCreate(CamelModel):
    blob_url: str
    category: str
    style_tags: list[str]
    occasion_tags: list[str]
    dominant_colors: list[str]

    @field_validator("category")
    @classmethod
    def category_valid(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError("Danh mục không hợp lệ")
        return value

    @field_validator("style_tags")
    @classmethod
    def style_tags_valid(cls, value: list[str]) -> list[str]:
        if not value or any(tag not in STYLE_TAGS for tag in value):
            raise ValueError("Tag phong cách không hợp lệ")
        return value

    @field_validator("occasion_tags")
    @classmethod
    def occasion_tags_valid(cls, value: list[str]) -> list[str]:
        if not value or any(tag not in OCCASION_TAGS for tag in value):
            raise ValueError("Tag dịp không hợp lệ")
        return value


class WardrobeItemResponse(CamelModel):
    id: int
    user_id: int
    blob_url: str
    category: str
    style_tags: list[str]
    occasion_tags: list[str]
    dominant_colors: list[str]
    created_at: datetime
    updated_at: datetime
