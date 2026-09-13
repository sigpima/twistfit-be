from sqlalchemy.orm import Session

from app.domains.contact.models import ContactMessage
from app.domains.contact.schemas import ContactMessageCreate


def list_contact_messages(db: Session) -> list[ContactMessage]:
    return db.query(ContactMessage).order_by(ContactMessage.id.desc()).all()


def get_contact_message(db: Session, message_id: int) -> ContactMessage | None:
    return db.get(ContactMessage, message_id)


def create_contact_message(db: Session, data: ContactMessageCreate) -> ContactMessage:
    message = ContactMessage(**data.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def set_contact_message_read(db: Session, message_id: int, is_read: bool) -> ContactMessage | None:
    message = get_contact_message(db, message_id)
    if message is None:
        return None
    message.is_read = is_read
    db.commit()
    db.refresh(message)
    return message


def delete_contact_message(db: Session, message_id: int) -> bool:
    message = get_contact_message(db, message_id)
    if message is None:
        return False
    db.delete(message)
    db.commit()
    return True
