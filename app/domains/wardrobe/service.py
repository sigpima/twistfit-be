from sqlalchemy.orm import Session

from app.domains.taxonomy import service as taxonomy_service
from app.domains.wardrobe.models import WardrobeItem
from app.domains.wardrobe.schemas import WardrobeItemCreate


def list_items(db: Session, user_id: int) -> list[WardrobeItem]:
    return db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).order_by(WardrobeItem.id.desc()).all()


def get_item(db: Session, user_id: int, item_id: int) -> WardrobeItem | None:
    return db.query(WardrobeItem).filter(WardrobeItem.id == item_id, WardrobeItem.user_id == user_id).first()


def _validate_attributes(db: Session, attributes: dict[str, list[str]]) -> None:
    for group_key, value_keys in attributes.items():
        valid_values = taxonomy_service.get_group_values(db, group_key)
        if not valid_values:
            raise ValueError(f'Nhóm thuộc tính "{group_key}" không hợp lệ')
        for value_key in value_keys:
            if value_key not in valid_values:
                raise ValueError(f'Giá trị "{value_key}" không hợp lệ trong nhóm "{group_key}"')


def create_item(db: Session, user_id: int, data: WardrobeItemCreate) -> WardrobeItem:
    _validate_attributes(db, data.attributes)
    item = WardrobeItem(user_id=user_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
