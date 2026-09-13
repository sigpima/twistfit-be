from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.capsule_wardrobe import service
from app.domains.capsule_wardrobe.schemas import CapsuleSetInput, CapsuleSetResponse

router = APIRouter(prefix="/capsule-wardrobe", tags=["capsule-wardrobe"])


@router.get("", response_model=list[CapsuleSetResponse])
def list_items(db: Session = Depends(get_db)):
    return service.list_capsule_sets(db)


@router.get("/{set_id}", response_model=CapsuleSetResponse)
def get_item(set_id: int, db: Session = Depends(get_db)):
    capsule_set = service.get_capsule_set(db, set_id)
    if capsule_set is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy set đồ")
    return capsule_set


@router.post("", response_model=CapsuleSetResponse, status_code=status.HTTP_201_CREATED)
def create_item(body: CapsuleSetInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return service.create_capsule_set(db, body)


@router.put("/{set_id}", response_model=CapsuleSetResponse)
def update_item(set_id: int, body: CapsuleSetInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    updated = service.update_capsule_set(db, set_id, body)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy set đồ")
    return updated


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(set_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    deleted = service.delete_capsule_set(db, set_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy set đồ")
