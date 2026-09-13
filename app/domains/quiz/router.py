from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.quiz import service
from app.domains.quiz.schemas import QuizQuestionInput, QuizQuestionResponse

router = APIRouter(prefix="/quiz-questions", tags=["quiz-questions"])


@router.get("", response_model=list[QuizQuestionResponse])
def list_items(db: Session = Depends(get_db)):
    return service.list_quiz_questions(db)


@router.get("/{question_id}", response_model=QuizQuestionResponse)
def get_item(question_id: int, db: Session = Depends(get_db)):
    question = service.get_quiz_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
    return question


@router.post("", response_model=QuizQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_item(body: QuizQuestionInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return service.create_quiz_question(db, body)


@router.put("/{question_id}", response_model=QuizQuestionResponse)
def update_item(
    question_id: int, body: QuizQuestionInput, db: Session = Depends(get_db), _admin=Depends(require_admin)
):
    updated = service.update_quiz_question(db, question_id, body)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
    return updated


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(question_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    deleted = service.delete_quiz_question(db, question_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
