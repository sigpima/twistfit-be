import pytest
from pydantic import ValidationError

from app.domains.quiz import service
from app.domains.quiz.models import QuizOption
from app.domains.quiz.schemas import QuizQuestionInput

VALID_INPUT = {
    "questionText": "Câu hỏi test?",
    "sortOrder": 0,
    "options": [
        {"label": "A", "season": "spring"},
        {"label": "B", "season": "summer"},
    ],
}


def test_create_quiz_question_with_options(db_session):
    question = service.create_quiz_question(db_session, QuizQuestionInput(**VALID_INPUT))
    assert question.id is not None
    assert len(question.options) == 2
    assert question.options[0].label == "A"


def test_list_quiz_questions_orders_by_sort_order(db_session):
    first = service.create_quiz_question(db_session, QuizQuestionInput(**{**VALID_INPUT, "sortOrder": 1}))
    second = service.create_quiz_question(db_session, QuizQuestionInput(**{**VALID_INPUT, "sortOrder": 0}))
    questions = service.list_quiz_questions(db_session)
    assert [q.id for q in questions] == [second.id, first.id]


def test_get_quiz_question_returns_none_when_missing(db_session):
    assert service.get_quiz_question(db_session, 99999) is None


def test_update_quiz_question_replaces_options_wholesale(db_session):
    question = service.create_quiz_question(db_session, QuizQuestionInput(**VALID_INPUT))
    updated = service.update_quiz_question(
        db_session,
        question.id,
        QuizQuestionInput(
            **{
                **VALID_INPUT,
                "questionText": "Đã sửa",
                "options": [
                    {"label": "C", "season": "autumn"},
                    {"label": "D", "season": "winter"},
                    {"label": "E", "season": "spring"},
                ],
            }
        ),
    )
    assert updated is not None
    assert updated.question_text == "Đã sửa"
    assert [option.label for option in updated.options] == ["C", "D", "E"]
    assert db_session.query(QuizOption).filter(QuizOption.question_id == question.id).count() == 3


def test_update_quiz_question_returns_none_when_missing(db_session):
    assert service.update_quiz_question(db_session, 99999, QuizQuestionInput(**VALID_INPUT)) is None


def test_delete_quiz_question_cascades_options(db_session):
    question = service.create_quiz_question(db_session, QuizQuestionInput(**VALID_INPUT))
    question_id = question.id
    assert service.delete_quiz_question(db_session, question_id) is True
    assert service.get_quiz_question(db_session, question_id) is None
    assert db_session.query(QuizOption).filter(QuizOption.question_id == question_id).count() == 0


def test_delete_quiz_question_returns_false_when_missing(db_session):
    assert service.delete_quiz_question(db_session, 99999) is False


def test_quiz_question_input_rejects_blank_question_text():
    with pytest.raises(ValidationError):
        QuizQuestionInput(**{**VALID_INPUT, "questionText": "   "})


def test_quiz_question_input_rejects_fewer_than_two_options():
    with pytest.raises(ValidationError):
        QuizQuestionInput(**{**VALID_INPUT, "options": [{"label": "Only one", "season": "spring"}]})


def test_quiz_question_input_rejects_invalid_season():
    with pytest.raises(ValidationError):
        QuizQuestionInput(
            **{
                **VALID_INPUT,
                "options": [
                    {"label": "A", "season": "not-a-real-season"},
                    {"label": "B", "season": "summer"},
                ],
            }
        )
