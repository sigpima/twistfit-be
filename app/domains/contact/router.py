from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.contact import service
from app.domains.contact.schemas import ContactMessageCreate, ContactMessageResponse, ContactMessageUpdate

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(body: ContactMessageCreate, db: Session = Depends(get_db)):
    return service.create_contact_message(db, body)


@router.get("", response_model=list[ContactMessageResponse])
def list_messages(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return service.list_contact_messages(db)


@router.patch("/{message_id}", response_model=ContactMessageResponse)
def update_message(
    message_id: int,
    body: ContactMessageUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    updated = service.set_contact_message_read(db, message_id, body.is_read)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tin nhắn")
    return updated


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    deleted = service.delete_contact_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tin nhắn")
