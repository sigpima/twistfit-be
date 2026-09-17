from datetime import datetime

from app.domains.auth.schemas import CamelModel


class TryOnJobCreate(CamelModel):
    catalog_model_id: int
    occasion: str
    style: str


class TryOnJobResponse(CamelModel):
    id: int
    user_id: int
    wardrobe_item_id: int | None
    catalog_model_id: int
    occasion: str
    style: str
    status: str
    result_front_blob_url: str | None
    result_side_blob_url: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
