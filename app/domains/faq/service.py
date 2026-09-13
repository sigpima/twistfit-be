from sqlalchemy.orm import Session

from app.domains.faq.models import FaqItem
from app.domains.faq.schemas import FaqItemInput


def list_faq_items(db: Session) -> list[FaqItem]:
    return db.query(FaqItem).order_by(FaqItem.id.asc()).all()


def get_faq_item(db: Session, item_id: int) -> FaqItem | None:
    return db.get(FaqItem, item_id)


def create_faq_item(db: Session, data: FaqItemInput) -> FaqItem:
    item = FaqItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_faq_item(db: Session, item_id: int, data: FaqItemInput) -> FaqItem | None:
    item = get_faq_item(db, item_id)
    if item is None:
        return None
    for field, value in data.model_dump().items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_faq_item(db: Session, item_id: int) -> bool:
    item = get_faq_item(db, item_id)
    if item is None:
        return False
    db.delete(item)
    db.commit()
    return True
