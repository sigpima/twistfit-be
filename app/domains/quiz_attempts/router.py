from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user_optional
from app.domains.auth.models import User
from app.domains.quiz_attempts import service
from app.domains.quiz_attempts.schemas import QuizAttemptCreate, QuizAttemptResponse

router = APIRouter(prefix="/quiz-attempts", tags=["quiz-attempts"])


@router.post("", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
def create_attempt(
    body: QuizAttemptCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    return service.create_quiz_attempt(db, body.season, user.id if user else None)
