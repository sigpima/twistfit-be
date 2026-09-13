from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.model_catalog import service
from app.domains.model_catalog.schemas import CatalogModelInput, CatalogModelResponse

router = APIRouter(prefix="/model-catalog", tags=["model-catalog"])


@router.get("", response_model=list[CatalogModelResponse])
def list_items(db: Session = Depends(get_db)):
    return service.list_models(db)


@router.get("/{model_id}", response_model=CatalogModelResponse)
def get_item(model_id: int, db: Session = Depends(get_db)):
    model = service.get_model(db, model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người mẫu")
    return model


@router.post("", response_model=CatalogModelResponse, status_code=status.HTTP_201_CREATED)
def create_item(body: CatalogModelInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return service.create_model(db, body)


@router.put("/{model_id}", response_model=CatalogModelResponse)
def update_item(model_id: int, body: CatalogModelInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    updated = service.update_model(db, model_id, body)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người mẫu")
    return updated


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(model_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    deleted = service.delete_model(db, model_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người mẫu")
