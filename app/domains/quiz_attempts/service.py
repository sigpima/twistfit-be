from sqlalchemy.orm import Session

from app.domains.quiz.models import QuizOption, QuizQuestion
from app.domains.quiz_attempts.models import QuizAttempt
from app.domains.quiz_attempts.schemas import QuizAnswerInput
from app.domains.quiz_attempts.scoring import score_quiz


class InvalidAnswerError(Exception):
    pass


def create_quiz_attempt(db: Session, answers: list[QuizAnswerInput], user_id: int | None) -> QuizAttempt:
    hue_votes: list[str] = []
    value_votes: list[str] = []
    chroma_votes: list[str] = []

    for answer in answers:
        option = db.get(QuizOption, answer.option_id)
        if option is None or option.question_id != answer.question_id:
            raise InvalidAnswerError(f"option {answer.option_id} does not belong to question {answer.question_id}")
        question = db.get(QuizQuestion, answer.question_id)
        if question.axis == "hue":
            hue_votes.append(option.axis_value)
        elif question.axis == "value":
            value_votes.append(option.axis_value)
        else:
            chroma_votes.append(option.axis_value)

    result = score_quiz(hue_votes, value_votes, chroma_votes)

    attempt = QuizAttempt(
        sub_season=result["sub_season"],
        parent_season=result["parent_season"],
        hue_result=result["hue_result"],
        value_result=result["value_result"],
        chroma_result=result["chroma_result"],
        hue_score=result["hue_score"],
        value_score=result["value_score"],
        chroma_score=result["chroma_score"],
        user_id=user_id,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_latest_attempt(db: Session, user_id: int) -> QuizAttempt | None:
    return (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.id.desc())
        .first()
    )
