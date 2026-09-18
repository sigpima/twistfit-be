from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

PARENT_SEASONS = ["spring", "summer", "autumn", "winter"]
SUB_SEASONS = [
    "light-spring", "true-spring", "bright-spring",
    "light-summer", "true-summer", "soft-summer",
    "soft-autumn", "true-autumn", "deep-autumn",
    "deep-winter", "true-winter", "bright-winter",
]


class QuizAnswerInput(CamelModel):
    question_id: int
    option_id: int


class QuizAttemptCreate(CamelModel):
    answers: list[QuizAnswerInput]

    @field_validator("answers")
    @classmethod
    def exactly_ten_answers(cls, value: list[QuizAnswerInput]) -> list[QuizAnswerInput]:
        if len(value) != 10:
            raise ValueError("Cần đúng 10 câu trả lời")
        return value


class QuizAttemptResponse(CamelModel):
    id: int
    sub_season: str
    parent_season: str
    hue_result: str
    value_result: str
    chroma_result: str
    hue_score: int | None
    value_score: int | None
    chroma_score: int | None
    user_id: int | None
    created_at: datetime
