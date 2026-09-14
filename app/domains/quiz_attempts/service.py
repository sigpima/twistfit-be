from sqlalchemy.orm import Session

from app.domains.quiz_attempts.models import QuizAttempt


def create_quiz_attempt(db: Session, season: str, user_id: int | None) -> QuizAttempt:
    attempt = QuizAttempt(season=season, user_id=user_id)
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
