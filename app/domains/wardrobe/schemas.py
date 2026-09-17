from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel


class WardrobeItemCreate(CamelModel):
    blob_url: str
    attributes: dict[str, list[str]]
    dominant_colors: list[str]

    @field_validator("attributes")
    @classmethod
    def attributes_not_empty(cls, value: dict[str, list[str]]) -> dict[str, list[str]]:
        if not value:
            raise ValueError("Cần chọn ít nhất 1 thuộc tính")
        return value


class WardrobeItemResponse(CamelModel):
    id: int
    user_id: int
    blob_url: str
    attributes: dict[str, list[str]]
    dominant_colors: list[str]
    created_at: datetime
    updated_at: datetime


class SuggestTagsRequest(CamelModel):
    blob_path: str
