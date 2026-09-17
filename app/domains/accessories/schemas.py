from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel
from app.domains.quiz_attempts.schemas import PARENT_SEASONS
from app.domains.wardrobe.schemas import OCCASION_TAGS, STYLE_TAGS

ACCESSORY_CATEGORIES = ["tui-xach", "giay", "trang-suc", "mu-non", "khan"]


class AccessoryProductInput(CamelModel):
    name: str
    image_url: str
    affiliate_link: str
    category: str
    style_tags: list[str]
    occasion_tags: list[str]
    tone_tags: list[str]

    @field_validator("name", "image_url", "affiliate_link")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Trường này không được để trống")
        return value.strip()

    @field_validator("category")
    @classmethod
    def category_valid(cls, value: str) -> str:
        if value not in ACCESSORY_CATEGORIES:
            raise ValueError("Danh mục phụ kiện không hợp lệ")
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

    @field_validator("tone_tags")
    @classmethod
    def tone_tags_valid(cls, value: list[str]) -> list[str]:
        if any(tag not in PARENT_SEASONS for tag in value):
            raise ValueError("Tag tone màu không hợp lệ")
        return value


class SuggestTagsRequest(CamelModel):
    blob_path: str


class AccessoryProductResponse(CamelModel):
    id: int
    name: str
    image_url: str
    affiliate_link: str
    category: str
    style_tags: list[str]
    occasion_tags: list[str]
    tone_tags: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
