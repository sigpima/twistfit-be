from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

FAQ_CATEGORIES = ["personal-color", "fitting-room", "account", "stylist"]
FAQ_HIGHLIGHT_ICONS = [
    "palette",
    "wb_sunny",
    "face_retouching_off",
    "center_focus_strong",
    "qr_code_scanner",
    "verified_user",
    "info",
    "lightbulb",
]


class FaqItemInput(CamelModel):
    categories: list[str]
    question: str
    answer_markdown: str
    highlight_icon: str | None = None
    highlight_text: str | None = None

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Câu hỏi không được để trống")
        return value.strip()

    @field_validator("answer_markdown")
    @classmethod
    def answer_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Câu trả lời không được để trống")
        return value.strip()

    @field_validator("categories")
    @classmethod
    def categories_valid_and_non_empty(cls, value: list[str]) -> list[str]:
        filtered = [category for category in value if category in FAQ_CATEGORIES]
        if not filtered:
            raise ValueError("Chọn ít nhất 1 chuyên mục")
        return filtered

    @field_validator("highlight_icon")
    @classmethod
    def highlight_icon_valid(cls, value: str | None) -> str | None:
        if value is not None and value not in FAQ_HIGHLIGHT_ICONS:
            raise ValueError("Icon không hợp lệ")
        return value

    @field_validator("highlight_text")
    @classmethod
    def normalize_highlight_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class FaqItemResponse(CamelModel):
    id: int
    categories: list[str]
    question: str
    answer_markdown: str
    highlight_icon: str | None
    highlight_text: str | None
    created_at: datetime
    updated_at: datetime
