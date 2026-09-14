from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.domains.auth.models import User
from app.domains.model_catalog.models import CatalogModel
from app.domains.tryon import service
from app.domains.tryon.schemas import TryOnJobCreate, TryOnJobResponse

router = APIRouter(prefix="/tryon", tags=["tryon"])


@router.post("", response_model=TryOnJobResponse, status_code=status.HTTP_201_CREATED)
def create_tryon_job(body: TryOnJobCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    catalog_model = db.get(CatalogModel, body.catalog_model_id)
    if catalog_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy model")

    return service.create_job(db, user.id, body.catalog_model_id, body.occasion, body.style)


@router.get("/{job_id}", response_model=TryOnJobResponse)
def get_tryon_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = service.get_job(db, user.id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy job")
    return job
