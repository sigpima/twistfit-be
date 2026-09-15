from pydantic import field_validator, model_validator

from app.domains.auth.schemas import CamelModel

AXES = ["hue", "value", "chroma"]
AXIS_VALUES = {
    "hue": ["warm", "cool", "neutral"],
    "value": ["dark", "light", "medium"],
    "chroma": ["bright", "muted", "neutral"],
}


class QuizOptionInput(CamelModel):
    label: str
    axis_value: str

    @field_validator("label")
    @classmethod
    def label_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Lựa chọn không được để trống")
        return value.strip()


class QuizQuestionInput(CamelModel):
    question_text: str
    axis: str
    image_url: str | None = None
    sort_order: int = 0
    options: list[QuizOptionInput]

    @field_validator("question_text")
    @classmethod
    def question_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Nội dung câu hỏi không được để trống")
        return value.strip()

    @field_validator("axis")
    @classmethod
    def axis_valid(cls, value: str) -> str:
        if value not in AXES:
            raise ValueError("Trục không hợp lệ")
        return value

    @field_validator("options")
    @classmethod
    def at_least_two_options(cls, value: list[QuizOptionInput]) -> list[QuizOptionInput]:
        if len(value) < 2:
            raise ValueError("Cần ít nhất 2 lựa chọn")
        return value

    @model_validator(mode="after")
    def options_match_axis(self) -> "QuizQuestionInput":
        valid_values = AXIS_VALUES[self.axis]
        for option in self.options:
            if option.axis_value not in valid_values:
                raise ValueError(f"Giá trị trục '{option.axis_value}' không hợp lệ cho trục '{self.axis}'")
        return self


class QuizOptionResponse(CamelModel):
    id: int
    label: str
    axis_value: str
    sort_order: int


class QuizQuestionResponse(CamelModel):
    id: int
    question_text: str
    axis: str
    image_url: str | None
    sort_order: int
    options: list[QuizOptionResponse]
