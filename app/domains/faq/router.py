from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.faq import service
from app.domains.faq.schemas import FaqItemInput, FaqItemResponse

router = APIRouter(prefix="/faq", tags=["faq"])


@router.get("", response_model=list[FaqItemResponse])
def list_items(db: Session = Depends(get_db)):
    return service.list_faq_items(db)


@router.get("/{item_id}", response_model=FaqItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = service.get_faq_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
    return item


@router.post("", response_model=FaqItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(body: FaqItemInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return service.create_faq_item(db, body)


@router.put("/{item_id}", response_model=FaqItemResponse)
def update_item(item_id: int, body: FaqItemInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    updated = service.update_faq_item(db, item_id, body)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
    return updated


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    deleted = service.delete_faq_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi")
