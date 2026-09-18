from sqlalchemy.orm import Session

from app.domains.quiz.models import QuizOption, QuizQuestion
from app.domains.quiz.schemas import QuizQuestionInput


def list_quiz_questions(db: Session) -> list[QuizQuestion]:
    return db.query(QuizQuestion).order_by(QuizQuestion.sort_order.asc()).all()


def get_quiz_question(db: Session, question_id: int) -> QuizQuestion | None:
    return db.get(QuizQuestion, question_id)


def create_quiz_question(db: Session, data: QuizQuestionInput) -> QuizQuestion:
    question = QuizQuestion(
        question_text=data.question_text, axis=data.axis, image_url=data.image_url, sort_order=data.sort_order
    )
    db.add(question)
    db.flush()
    for index, option in enumerate(data.options):
        db.add(
            QuizOption(
                question_id=question.id,
                label=option.label,
                axis_value=option.axis_value,
                image_url=option.image_url,
                sort_order=index,
            )
        )
    db.commit()
    db.refresh(question)
    return question


def update_quiz_question(db: Session, question_id: int, data: QuizQuestionInput) -> QuizQuestion | None:
    question = get_quiz_question(db, question_id)
    if question is None:
        return None

    question.question_text = data.question_text
    question.axis = data.axis
    question.image_url = data.image_url
    question.sort_order = data.sort_order
    db.query(QuizOption).filter(QuizOption.question_id == question_id).delete()
    db.flush()
    for index, option in enumerate(data.options):
        db.add(
            QuizOption(
                question_id=question.id,
                label=option.label,
                axis_value=option.axis_value,
                image_url=option.image_url,
                sort_order=index,
            )
        )
    db.commit()
    db.refresh(question)
    return question


def delete_quiz_question(db: Session, question_id: int) -> bool:
    question = get_quiz_question(db, question_id)
    if question is None:
        return False
    db.delete(question)
    db.commit()
    return True
