from sqlalchemy.orm import Session

from app.domains.taxonomy import service as taxonomy_service
from app.domains.wardrobe.models import WardrobeItem
from app.domains.wardrobe.schemas import WardrobeItemCreate


def list_items(db: Session, user_id: int) -> list[WardrobeItem]:
    return db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).order_by(WardrobeItem.id.desc()).all()


def get_item(db: Session, user_id: int, item_id: int) -> WardrobeItem | None:
    return db.query(WardrobeItem).filter(WardrobeItem.id == item_id, WardrobeItem.user_id == user_id).first()


# A clothing-type-less item is silently invisible to every future outfit
# generation (garment_selection.py groups items by clothing-type and drops
# anything without one) — occasion/style are what tryon jobs filter by
# (see tryon/service.process_job). All three must have >= 1 value.
_REQUIRED_ATTRIBUTE_GROUPS = {
    "clothing-type": "Chọn ít nhất 1 loại quần áo",
    "occasion": "Chọn ít nhất 1 dịp",
    "style": "Chọn ít nhất 1 phong cách",
}


def _validate_attributes(db: Session, attributes: dict[str, list[str]]) -> None:
    for group_key, value_keys in attributes.items():
        valid_values = taxonomy_service.get_group_values(db, group_key)
        if not valid_values:
            raise ValueError(f'Nhóm thuộc tính "{group_key}" không hợp lệ')
        for value_key in value_keys:
            if value_key not in valid_values:
                raise ValueError(f'Giá trị "{value_key}" không hợp lệ trong nhóm "{group_key}"')

    for group_key, message in _REQUIRED_ATTRIBUTE_GROUPS.items():
        if not attributes.get(group_key):
            raise ValueError(message)


def create_item(db: Session, user_id: int, data: WardrobeItemCreate) -> WardrobeItem:
    _validate_attributes(db, data.attributes)
    item = WardrobeItem(user_id=user_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
