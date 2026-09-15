from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, get_current_user_optional
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
    try:
        return service.create_quiz_attempt(db, body.answers, user.id if user else None)
    except service.InvalidAnswerError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="INVALID_ANSWER")


@router.get("/me", response_model=QuizAttemptResponse | None)
def get_my_latest_attempt(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.get_latest_attempt(db, user.id)
