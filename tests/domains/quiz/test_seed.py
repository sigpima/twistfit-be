from app.domains.quiz.models import QuizOption, QuizQuestion
from app.domains.quiz.seed import seed_demo_quiz_questions


def test_seed_demo_quiz_questions_creates_five_questions_with_options(db_session):
    seed_demo_quiz_questions(db_session)
    questions = db_session.query(QuizQuestion).order_by(QuizQuestion.sort_order.asc()).all()
    assert len(questions) == 5
    assert len(questions[0].options) == 4
    assert questions[0].options[0].label == "Xanh lá hoặc xanh ô liu"


def test_seed_demo_quiz_questions_is_idempotent(db_session):
    seed_demo_quiz_questions(db_session)
    seed_demo_quiz_questions(db_session)
    assert db_session.query(QuizQuestion).count() == 5
    assert db_session.query(QuizOption).count() == 20


def test_deleting_question_cascades_to_options(db_session):
    seed_demo_quiz_questions(db_session)
    question = db_session.query(QuizQuestion).first()
    question_id = question.id
    db_session.delete(question)
    db_session.commit()
    assert db_session.query(QuizOption).filter(QuizOption.question_id == question_id).count() == 0
