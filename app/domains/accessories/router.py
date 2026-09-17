from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.accessories import service
from app.domains.accessories.schemas import AccessoryProductInput, AccessoryProductResponse
from app.domains.auth.models import User

router = APIRouter(prefix="/accessories", tags=["accessories"])


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
    return service.create_accessory(db, body)


@router.put("/{accessory_id}", response_model=AccessoryProductResponse)
def update_accessory(
    accessory_id: int,
    body: AccessoryProductInput,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    updated = service.update_accessory(db, accessory_id, body)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phụ kiện")
    return updated


@router.delete("/{accessory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accessory(accessory_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    deleted = service.delete_accessory(db, accessory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy phụ kiện")
