from sqlalchemy.orm import Session

from app.domains.accessories.models import AccessoryProduct
from app.domains.accessories.schemas import AccessoryProductInput


def list_accessories(db: Session) -> list[AccessoryProduct]:
    return db.query(AccessoryProduct).order_by(AccessoryProduct.id.desc()).all()


def get_accessory(db: Session, accessory_id: int) -> AccessoryProduct | None:
    return db.get(AccessoryProduct, accessory_id)


def create_accessory(db: Session, data: AccessoryProductInput) -> AccessoryProduct:
    accessory = AccessoryProduct(**data.model_dump())
    db.add(accessory)
    db.commit()
    db.refresh(accessory)
    return accessory


def update_accessory(db: Session, accessory_id: int, data: AccessoryProductInput) -> AccessoryProduct | None:
    accessory = get_accessory(db, accessory_id)
    if accessory is None:
        return None
    for field, value in data.model_dump().items():
        setattr(accessory, field, value)
    db.commit()
    db.refresh(accessory)
    return accessory


def delete_accessory(db: Session, accessory_id: int) -> bool:
    accessory = get_accessory(db, accessory_id)
    if accessory is None:
        return False
    db.delete(accessory)
    db.commit()
    return True
