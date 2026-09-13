from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

SEASONS = ["spring", "summer", "autumn", "winter"]


class QuizAttemptCreate(CamelModel):
    season: str

    @field_validator("season")
    @classmethod
    def season_valid(cls, value: str) -> str:
        if value not in SEASONS:
            raise ValueError("Kết quả mùa không hợp lệ")
        return value


class QuizAttemptResponse(CamelModel):
    id: int
    season: str
    user_id: int | None
    created_at: datetime
