from sqlalchemy.orm import Session

from app.domains.wardrobe.models import WardrobeItem
from app.domains.wardrobe.schemas import WardrobeItemCreate


def list_items(db: Session, user_id: int) -> list[WardrobeItem]:
    return db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).order_by(WardrobeItem.id.desc()).all()


def get_item(db: Session, user_id: int, item_id: int) -> WardrobeItem | None:
    return db.query(WardrobeItem).filter(WardrobeItem.id == item_id, WardrobeItem.user_id == user_id).first()


def create_item(db: Session, user_id: int, data: WardrobeItemCreate) -> WardrobeItem:
    item = WardrobeItem(user_id=user_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
