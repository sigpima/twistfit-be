from datetime import datetime
from typing import Literal

from app.domains.auth.schemas import CamelModel


class TryOnJobCreate(CamelModel):
    catalog_model_id: int
    occasion: str
    style: str
    pose: Literal["front", "side"] = "front"


class TryOnJobResponse(CamelModel):
    id: int
    user_id: int
    wardrobe_item_id: int | None
    catalog_model_id: int
    occasion: str
    style: str
    pose: str
    status: str
    result_blob_url: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
