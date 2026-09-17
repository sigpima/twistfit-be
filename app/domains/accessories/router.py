import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.blob_storage import blob_public_url, download_bytes, ensure_container, generate_upload_sas_url
from app.db.session import get_db
from app.deps import get_current_user, require_admin
from app.domains.accessories import service
from app.domains.accessories.gemini_client import suggest_tags
from app.domains.accessories.schemas import (
    ACCESSORY_CATEGORIES,
    AccessoryProductInput,
    AccessoryProductResponse,
    AccessoryRecommendationResponse,
    SuggestTagsRequest,
)
from app.domains.auth.models import User
from app.domains.quiz_attempts.models import QuizAttempt

router = APIRouter(prefix="/accessories", tags=["accessories"])

# Gemini can fail independently of the upload (rate limit, outage,
# malformed response) — fall back to an empty-but-valid suggestion so the
# admin still gets the image back to tag by hand, instead of a dead end.
_FALLBACK_SUGGESTION = {
    "category": ACCESSORY_CATEGORIES[0],
    "styleTags": [],
    "occasionTags": [],
    "toneTags": [],
}


@router.post("/upload-url")
def get_upload_url(_admin: User = Depends(require_admin)):
    ensure_container("accessories")
    blob_path = f"{uuid.uuid4()}.png"
    upload_url = generate_upload_sas_url("accessories", blob_path)
    return {"uploadUrl": upload_url, "blobPath": blob_path}


@router.post("/suggest-tags")
def suggest_tags_endpoint(
    body: SuggestTagsRequest, db: Session = Depends(get_db), _admin: User = Depends(require_admin)
):
    image_bytes = download_bytes("accessories", body.blob_path)
    try:
        tags = suggest_tags(image_bytes, db)
    except Exception:  # noqa: BLE001 — any Gemini failure must degrade to the fallback, not 500
        tags = _FALLBACK_SUGGESTION
    return {**tags, "blobUrl": blob_public_url("accessories", body.blob_path)}


@router.get("/recommendations", response_model=list[AccessoryRecommendationResponse])
def get_recommendations(
    occasion: str,
    style: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    latest_attempt = (
        db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).order_by(QuizAttempt.id.desc()).first()
    )
    tone = latest_attempt.parent_season if latest_attempt else None
    return service.recommend(db, occasion, style, tone)


@router.get("", response_model=list[AccessoryProductResponse])
def list_accessories(db: Session = Depends(get_db)):
    return service.list_accessories(db)


@router.get("/{accessory_id}", response_model=AccessoryProductResponse)
def get_accessory(accessory_id: int, db: Session = Depends(get_db)):
    accessory = service.get_accessory(db, accessory_id)
    if accessory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phụ kiện")
    return accessory


@router.post("", response_model=AccessoryProductResponse, status_code=status.HTTP_201_CREATED)
def create_accessory(body: AccessoryProductInput, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    try:
        return service.create_accessory(db, body)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.put("/{accessory_id}", response_model=AccessoryProductResponse)
def update_accessory(
    accessory_id: int,
    body: AccessoryProductInput,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        updated = service.update_accessory(db, accessory_id, body)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phụ kiện")
    return updated


@router.delete("/{accessory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accessory(accessory_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    deleted = service.delete_accessory(db, accessory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phụ kiện")
