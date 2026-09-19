from datetime import datetime

from pydantic import model_validator

from app.domains.auth.schemas import CamelModel


class TryOnJobCreate(CamelModel):
    catalog_model_id: int
    occasion: str | None = None
    style: str | None = None

    @model_validator(mode="after")
    def exactly_one_of_occasion_or_style(self) -> "TryOnJobCreate":
        if (self.occasion is None) == (self.style is None):
            raise ValueError("Cần chọn đúng một trong hai: dịp hoặc phong cách")
        return self


class TryOnQuotaResponse(CamelModel):
    used_today: int
    limit: int
    remaining_today: int


class TryOnJobResponse(CamelModel):
    id: int
    user_id: int
    wardrobe_item_id: int | None
    catalog_model_id: int
    occasion: str | None
    style: str | None
    status: str
    result_front_blob_url: str | None
    result_side_blob_url: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
