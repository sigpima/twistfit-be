import pytest

from app.domains.auth import service as auth_service
from app.domains.quiz import service as quiz_service
from app.domains.quiz.schemas import QuizQuestionInput
from app.domains.quiz_attempts import service
from app.domains.quiz_attempts.schemas import QuizAnswerInput


def _seed_one_question_per_axis(db_session):
    hue_question = quiz_service.create_quiz_question(
        db_session,
        QuizQuestionInput(
            question_text="Hue?",
            axis="hue",
            options=[{"label": "A", "axisValue": "warm"}, {"label": "B", "axisValue": "cool"}],
        ),
    )
    value_question = quiz_service.create_quiz_question(
        db_session,
        QuizQuestionInput(
            question_text="Value?",
            axis="value",
            options=[{"label": "A", "axisValue": "light"}, {"label": "B", "axisValue": "dark"}],
        ),
    )
    chroma_question = quiz_service.create_quiz_question(
        db_session,
        QuizQuestionInput(
            question_text="Chroma?",
            axis="chroma",
            options=[{"label": "A", "axisValue": "bright"}, {"label": "B", "axisValue": "muted"}],
        ),
    )
    return hue_question, value_question, chroma_question


def test_create_quiz_attempt_scores_and_persists_the_full_result(db_session):
    hue_question, value_question, chroma_question = _seed_one_question_per_axis(db_session)

    answers = [
        QuizAnswerInput(question_id=hue_question.id, option_id=hue_question.options[0].id),  # warm
        QuizAnswerInput(question_id=value_question.id, option_id=value_question.options[0].id),  # light
        QuizAnswerInput(question_id=chroma_question.id, option_id=chroma_question.options[0].id),  # bright
    ]

    attempt = service.create_quiz_attempt(db_session, answers, user_id=None)

    assert attempt.hue_result == "warm"
    assert attempt.value_result == "light"
    assert attempt.chroma_result == "bright"
    assert attempt.parent_season == "spring"
    # With only 1 question per axis, value share (1/1) ties chroma share (1/1),
    # so this falls to the hue-dominant "true-*" slot per the tie-break rule.
    assert attempt.sub_season == "true-spring"
    assert attempt.user_id is None
    # 1/1 vote matched the winning bucket on every axis -> full confidence, so each
    # score lands at the top of true-spring's official band: hue (75,95),
    # value (60,75), chroma (70,85).
    assert attempt.hue_score == 95
    assert attempt.value_score == 75
    assert attempt.chroma_score == 85


def test_create_quiz_attempt_attributes_to_a_user(db_session):
    hue_question, value_question, chroma_question = _seed_one_question_per_axis(db_session)
    user = auth_service.create_user(db_session, name="Test", email="quiz-attempt-svc@example.com", password="password123")

    answers = [
        QuizAnswerInput(question_id=hue_question.id, option_id=hue_question.options[1].id),  # cool
        QuizAnswerInput(question_id=value_question.id, option_id=value_question.options[1].id),  # dark
        QuizAnswerInput(question_id=chroma_question.id, option_id=chroma_question.options[1].id),  # muted
    ]

    attempt = service.create_quiz_attempt(db_session, answers, user_id=user.id)
    assert attempt.user_id == user.id
    assert attempt.parent_season == "summer"


def test_create_quiz_attempt_rejects_an_option_that_does_not_belong_to_its_question(db_session):
    hue_question, value_question, _chroma_question = _seed_one_question_per_axis(db_session)

    answers = [
        QuizAnswerInput(question_id=hue_question.id, option_id=value_question.options[0].id),
    ]

    with pytest.raises(service.InvalidAnswerError):
        service.create_quiz_attempt(db_session, answers, user_id=None)


def test_get_latest_attempt_returns_none_when_the_user_has_no_attempts(db_session):
    user = auth_service.create_user(db_session, name="Test", email="quiz-latest-1@example.com", password="password123")
    assert service.get_latest_attempt(db_session, user.id) is None


def test_get_latest_attempt_returns_the_most_recent_one(db_session):
    hue_question, value_question, chroma_question = _seed_one_question_per_axis(db_session)
    user = auth_service.create_user(db_session, name="Test", email="quiz-latest-2@example.com", password="password123")

    first_answers = [
        QuizAnswerInput(question_id=hue_question.id, option_id=hue_question.options[0].id),
        QuizAnswerInput(question_id=value_question.id, option_id=value_question.options[0].id),
        QuizAnswerInput(question_id=chroma_question.id, option_id=chroma_question.options[0].id),
    ]
    second_answers = [
        QuizAnswerInput(question_id=hue_question.id, option_id=hue_question.options[1].id),
        QuizAnswerInput(question_id=value_question.id, option_id=value_question.options[1].id),
        QuizAnswerInput(question_id=chroma_question.id, option_id=chroma_question.options[1].id),
    ]
    service.create_quiz_attempt(db_session, first_answers, user.id)
    latest = service.create_quiz_attempt(db_session, second_answers, user.id)

    result = service.get_latest_attempt(db_session, user.id)

    assert result is not None
    assert result.id == latest.id
    assert result.parent_season == "summer"


def test_get_latest_attempt_ignores_other_users_attempts(db_session):
    hue_question, value_question, chroma_question = _seed_one_question_per_axis(db_session)
    user = auth_service.create_user(db_session, name="Test", email="quiz-latest-3@example.com", password="password123")
    other_user = auth_service.create_user(db_session, name="Other", email="quiz-latest-4@example.com", password="password123")

    answers = [
        QuizAnswerInput(question_id=hue_question.id, option_id=hue_question.options[0].id),
        QuizAnswerInput(question_id=value_question.id, option_id=value_question.options[0].id),
        QuizAnswerInput(question_id=chroma_question.id, option_id=chroma_question.options[0].id),
    ]
    service.create_quiz_attempt(db_session, answers, other_user.id)

    assert service.get_latest_attempt(db_session, user.id) is None
