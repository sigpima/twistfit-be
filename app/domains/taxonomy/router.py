from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.taxonomy import service
from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyGroupResponse, TaxonomyValueInput, TaxonomyValueResponse

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.get("", response_model=list[TaxonomyGroupResponse])
def list_groups(db: Session = Depends(get_db)):
    return service.list_groups(db)


@router.post("/groups", response_model=TaxonomyGroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(body: TaxonomyGroupInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    try:
        return service.create_group(db, body)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.put("/groups/{group_id}", response_model=TaxonomyGroupResponse)
def update_group(
    group_id: int, body: TaxonomyGroupInput, db: Session = Depends(get_db), _admin=Depends(require_admin)
):
    try:
        updated = service.update_group(db, group_id, body)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy nhóm")
    return updated


@router.post(
    "/groups/{group_id}/values", response_model=TaxonomyValueResponse, status_code=status.HTTP_201_CREATED
)
def create_value(
    group_id: int, body: TaxonomyValueInput, db: Session = Depends(get_db), _admin=Depends(require_admin)
):
    try:
        value = service.create_value(db, group_id, body)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy nhóm")
    return value


@router.put("/values/{value_id}", response_model=TaxonomyValueResponse)
def update_value(
    value_id: int, body: TaxonomyValueInput, db: Session = Depends(get_db), _admin=Depends(require_admin)
):
    try:
        updated = service.update_value(db, value_id, body)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy giá trị")
    return updated


@router.delete("/values/{value_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_value(value_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    try:
        deleted = service.delete_value(db, value_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy giá trị")
