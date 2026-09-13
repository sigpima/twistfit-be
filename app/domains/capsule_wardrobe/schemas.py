from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

TAG_VARIANTS = ["primary", "secondary", "tertiary"]


class CapsuleItem(CamelModel):
    label: str
    price: str

    @field_validator("label", "price")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Trường này không được để trống")
        return value.strip()


class CapsuleSetInput(CamelModel):
    image: str
    alt: str
    tag_variant: str
    tag_label: str
    fit_for: str
    title: str
    tone: str
    description: str
    items: list[CapsuleItem]

    @field_validator("image", "alt", "tag_label", "fit_for", "title", "tone", "description")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Trường này không được để trống")
        return value.strip()

    @field_validator("tag_variant")
    @classmethod
    def tag_variant_valid(cls, value: str) -> str:
        if value not in TAG_VARIANTS:
            raise ValueError("Màu nhãn không hợp lệ")
        return value

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, value: list[CapsuleItem]) -> list[CapsuleItem]:
        if not value:
            raise ValueError("Cần ít nhất 1 món đồ")
        return value


class CapsuleSetResponse(CamelModel):
    id: int
    image: str
    alt: str
    tag_variant: str
    tag_label: str
    fit_for: str
    title: str
    tone: str
    description: str
    items: list[CapsuleItem]
    created_at: datetime
    updated_at: datetime
