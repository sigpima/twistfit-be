from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.admin_stats import service
from app.domains.admin_stats.schemas import AdminStatsResponse
from app.domains.auth.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return service.get_admin_stats(db)
