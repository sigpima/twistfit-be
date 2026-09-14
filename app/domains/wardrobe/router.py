from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.domains.auth.models import User
from app.domains.wardrobe import service
from app.domains.wardrobe.schemas import WardrobeItemCreate, WardrobeItemResponse

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
    return service.create_item(db, user.id, body)
