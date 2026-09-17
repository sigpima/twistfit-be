from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel


class TaxonomyValueInput(CamelModel):
    key: str
    label: str

    @field_validator("key")
    @classmethod
    def key_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Mã giá trị không được để trống")
        return value.strip()

    @field_validator("label")
    @classmethod
    def label_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Tên giá trị không được để trống")
        return value.strip()


class TaxonomyValueResponse(CamelModel):
    id: int
    key: str
    label: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class TaxonomyGroupInput(CamelModel):
    key: str
    label: str

    @field_validator("key")
    @classmethod
    def key_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Mã nhóm không được để trống")
        return value.strip()

    @field_validator("label")
    @classmethod
    def label_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Tên nhóm không được để trống")
        return value.strip()


class TaxonomyGroupResponse(CamelModel):
    id: int
    key: str
    label: str
    sort_order: int
    values: list[TaxonomyValueResponse]
    created_at: datetime
    updated_at: datetime
