import pytest
from pydantic import ValidationError

from app.domains.quiz.schemas import QuizQuestionInput

HUE_QUESTION = {
    "questionText": "Câu hue test?",
    "axis": "hue",
    "sortOrder": 0,
    "options": [
        {"label": "A", "axisValue": "warm"},
        {"label": "B", "axisValue": "cool"},
        {"label": "C", "axisValue": "neutral"},
    ],
}


def test_accepts_option_axis_values_matching_the_question_axis():
    question = QuizQuestionInput(**HUE_QUESTION)
    assert question.axis == "hue"
    assert [option.axis_value for option in question.options] == ["warm", "cool", "neutral"]


def test_rejects_an_option_axis_value_not_valid_for_the_question_axis():
    with pytest.raises(ValidationError):
        QuizQuestionInput(
            **{**HUE_QUESTION, "options": [{"label": "A", "axisValue": "dark"}, {"label": "B", "axisValue": "cool"}]}
        )


def test_rejects_an_invalid_axis():
    with pytest.raises(ValidationError):
        QuizQuestionInput(**{**HUE_QUESTION, "axis": "not-a-real-axis"})


def test_image_url_is_optional_and_defaults_to_none():
    question = QuizQuestionInput(**HUE_QUESTION)
    assert question.image_url is None


def test_image_url_can_be_set():
    question = QuizQuestionInput(**{**HUE_QUESTION, "imageUrl": "/personal-color/quiz/wrist-veins.jpg"})
    assert question.image_url == "/personal-color/quiz/wrist-veins.jpg"
