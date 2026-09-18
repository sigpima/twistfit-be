from app.domains.quiz.models import QuizOption, QuizQuestion
from app.domains.quiz.seed import seed_demo_quiz_questions


def test_seed_demo_quiz_questions_creates_ten_questions(db_session):
    seed_demo_quiz_questions(db_session)
    questions = db_session.query(QuizQuestion).order_by(QuizQuestion.sort_order.asc()).all()
    assert len(questions) == 10
    assert questions[0].axis == "hue"
    assert questions[0].image_url == "/personal-color/quiz/q1-veins.jpg"
    assert questions[0].options[0].label == "Xanh lá / Olive"
    assert questions[0].options[0].axis_value == "warm"


def test_seed_demo_quiz_questions_has_the_right_axis_distribution(db_session):
    seed_demo_quiz_questions(db_session)
    questions = db_session.query(QuizQuestion).all()
    axis_counts = {"hue": 0, "value": 0, "chroma": 0}
    for question in questions:
        axis_counts[question.axis] += 1
    assert axis_counts == {"hue": 5, "value": 3, "chroma": 2}


def test_seed_demo_quiz_questions_every_option_matches_a_valid_axis_value(db_session):
    from app.domains.quiz.schemas import AXIS_VALUES

    seed_demo_quiz_questions(db_session)
    for question in db_session.query(QuizQuestion).all():
        for option in question.options:
            assert option.axis_value in AXIS_VALUES[question.axis]


def test_seed_demo_quiz_questions_is_idempotent(db_session):
    seed_demo_quiz_questions(db_session)
    seed_demo_quiz_questions(db_session)
    assert db_session.query(QuizQuestion).count() == 10
    assert db_session.query(QuizOption).count() == 30


def test_deleting_question_cascades_to_options(db_session):
    seed_demo_quiz_questions(db_session)
    question = db_session.query(QuizQuestion).first()
    question_id = question.id
    db_session.delete(question)
    db_session.commit()
    assert db_session.query(QuizOption).filter(QuizOption.question_id == question_id).count() == 0
