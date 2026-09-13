from sqlalchemy.orm import Session

from app.domains.capsule_wardrobe.models import CapsuleSet
from app.domains.capsule_wardrobe.schemas import CapsuleSetInput


def _to_row_data(data: CapsuleSetInput) -> dict:
    row = data.model_dump()
    row["items"] = [item.model_dump() for item in data.items]
    return row


def list_capsule_sets(db: Session) -> list[CapsuleSet]:
    return db.query(CapsuleSet).order_by(CapsuleSet.id.asc()).all()


def get_capsule_set(db: Session, set_id: int) -> CapsuleSet | None:
    return db.get(CapsuleSet, set_id)


def create_capsule_set(db: Session, data: CapsuleSetInput) -> CapsuleSet:
    capsule_set = CapsuleSet(**_to_row_data(data))
    db.add(capsule_set)
    db.commit()
    db.refresh(capsule_set)
    return capsule_set


def update_capsule_set(db: Session, set_id: int, data: CapsuleSetInput) -> CapsuleSet | None:
    capsule_set = get_capsule_set(db, set_id)
    if capsule_set is None:
        return None
    for field, value in _to_row_data(data).items():
        setattr(capsule_set, field, value)
    db.commit()
    db.refresh(capsule_set)
    return capsule_set


def delete_capsule_set(db: Session, set_id: int) -> bool:
    capsule_set = get_capsule_set(db, set_id)
    if capsule_set is None:
        return False
    db.delete(capsule_set)
    db.commit()
    return True
