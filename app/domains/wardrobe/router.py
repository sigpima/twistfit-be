import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.blob_storage import blob_public_url, download_bytes, ensure_container, generate_upload_sas_url
from app.core.image_utils import normalize_to_png
from app.db.session import get_db
from app.deps import get_current_user
from app.domains.auth.models import User
from app.domains.wardrobe import service
from app.domains.wardrobe.color_extraction import extract_dominant_colors
from app.domains.wardrobe.gemini_client import suggest_tags
from app.domains.wardrobe.schemas import SuggestTagsRequest, WardrobeItemCreate, WardrobeItemResponse

router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])


@router.get("/items", response_model=list[WardrobeItemResponse])
def list_items(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_items(db, user.id)


@router.get("/items/{item_id}", response_model=WardrobeItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = service.get_item(db, user.id, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy món đồ")
    return item


@router.post("/items", response_model=WardrobeItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(body: WardrobeItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return service.create_item(db, user.id, body)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/upload-url")
def get_upload_url(user: User = Depends(get_current_user)):
    ensure_container("wardrobe")
    blob_path = f"{user.id}/{uuid.uuid4()}.png"
    upload_url = generate_upload_sas_url("wardrobe", blob_path)
    return {"uploadUrl": upload_url, "blobPath": blob_path}


@router.post("/items/suggest-tags")
def suggest_tags_endpoint(
    body: SuggestTagsRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    image_bytes = normalize_to_png(download_bytes("wardrobe", body.blob_path))
    attributes = suggest_tags(image_bytes, db)
    colors = extract_dominant_colors(image_bytes)
    return {**attributes, "dominantColors": colors, "blobUrl": blob_public_url("wardrobe", body.blob_path)}
