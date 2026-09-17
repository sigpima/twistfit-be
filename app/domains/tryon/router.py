from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal, get_db
from app.deps import get_current_user
from app.domains.auth.models import User
from app.domains.model_catalog.models import CatalogModel
from app.domains.quiz_attempts.models import QuizAttempt
from app.domains.tryon import service
from app.domains.tryon.schemas import TryOnJobCreate, TryOnJobResponse

router = APIRouter(prefix="/tryon", tags=["tryon"])


def _resolve_asset_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{settings.frontend_base_url.rstrip('/')}/{path.lstrip('/')}"


def _process_job_with_fresh_session(job_id: int, season: str, catalog_model_image_url: str) -> None:
    db = SessionLocal()
    try:
        service.process_job(db, job_id, season, catalog_model_image_url)
    finally:
        db.close()


@router.post("", response_model=TryOnJobResponse, status_code=status.HTTP_201_CREATED)
def create_tryon_job(
    body: TryOnJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    catalog_model = db.get(CatalogModel, body.catalog_model_id)
    if catalog_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy model")

    latest_attempt = (
        db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).order_by(QuizAttempt.id.desc()).first()
    )
    season = latest_attempt.parent_season if latest_attempt else "spring"

    job = service.create_job(db, user.id, body.catalog_model_id, body.occasion, body.style, body.pose)
    person_image_path = catalog_model.side_image if body.pose == "side" and catalog_model.side_image else catalog_model.image
    person_image_url = _resolve_asset_url(person_image_path)
    background_tasks.add_task(_process_job_with_fresh_session, job.id, season, person_image_url)
    return job


@router.get("/{job_id}", response_model=TryOnJobResponse)
def get_tryon_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = service.get_job(db, user.id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy job")
    return job
