from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal, get_db
from app.deps import get_current_user
from app.domains.auth.models import User
from app.domains.model_catalog.models import CatalogModel
from app.domains.quiz_attempts.models import QuizAttempt
from app.domains.tryon import service
from app.domains.tryon.schemas import TryOnJobCreate, TryOnJobResponse, TryOnQuotaResponse

router = APIRouter(prefix="/tryon", tags=["tryon"])


def _resolve_asset_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{settings.frontend_base_url.rstrip('/')}/{path.lstrip('/')}"


def _process_job_with_fresh_session(job_id: int, season: str, front_image_url: str, side_image_url: str | None) -> None:
    db = SessionLocal()
    try:
        service.process_job(db, job_id, season, front_image_url, side_image_url)
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

    if not service.reserve_tryon_quota(db, user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bạn đã dùng hết {service.DAILY_TRYON_LIMIT} lượt thử hôm nay, quay lại vào ngày mai nhé.",
        )

    latest_attempt = (
        db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).order_by(QuizAttempt.id.desc()).first()
    )
    season = latest_attempt.parent_season if latest_attempt else "spring"

    job = service.create_job(db, user.id, body.catalog_model_id, body.occasion, body.style)
    front_image_url = _resolve_asset_url(catalog_model.image)
    side_image_url = _resolve_asset_url(catalog_model.side_image) if catalog_model.side_image else None
    print(
        f"[TRYON-DEBUG] POST /tryon created job_id={job.id} user_id={user.id} season={season} "
        f"front_image_url={front_image_url} side_image_url={side_image_url}",
        flush=True,
    )
    background_tasks.add_task(_process_job_with_fresh_session, job.id, season, front_image_url, side_image_url)
    return job


@router.get("", response_model=list[TryOnJobResponse])
def list_tryon_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_jobs(db, user.id)


@router.get("/quota", response_model=TryOnQuotaResponse)
def get_tryon_quota(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    used_today, remaining_today = service.get_tryon_quota(db, user.id)
    return TryOnQuotaResponse(used_today=used_today, limit=service.DAILY_TRYON_LIMIT, remaining_today=remaining_today)


@router.get("/{job_id}", response_model=TryOnJobResponse)
def get_tryon_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = service.get_job(db, user.id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy job")
    print(
        f"[TRYON-DEBUG] GET /tryon/{job_id} status={job.status} error_message={job.error_message!r}",
        flush=True,
    )
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tryon_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not service.delete_job(db, user.id, job_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy job")
