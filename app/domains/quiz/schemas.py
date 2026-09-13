from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

SEASONS = ["spring", "summer", "autumn", "winter"]


class QuizOptionInput(CamelModel):
    label: str
    season: str

    @field_validator("label")
    @classmethod
    def label_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Lựa chọn không được để trống")
        return value.strip()

    @field_validator("season")
    @classmethod
    def season_valid(cls, value: str) -> str:
        if value not in SEASONS:
            raise ValueError("Mùa không hợp lệ")
        return value


class QuizQuestionInput(CamelModel):
    question_text: str
    sort_order: int = 0
    options: list[QuizOptionInput]

    @field_validator("question_text")
    @classmethod
    def question_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Nội dung câu hỏi không được để trống")
        return value.strip()

    @field_validator("options")
    @classmethod
    def at_least_two_options(cls, value: list[QuizOptionInput]) -> list[QuizOptionInput]:
        if len(value) < 2:
            raise ValueError("Cần ít nhất 2 lựa chọn")
        return value


class QuizOptionResponse(CamelModel):
    id: int
    label: str
    season: str
    sort_order: int


class QuizQuestionResponse(CamelModel):
    id: int
    question_text: str
    sort_order: int
    options: list[QuizOptionResponse]
