from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.taxonomy.models import TaxonomyGroup, TaxonomyValue
from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyValueInput


def list_groups(db: Session) -> list[TaxonomyGroup]:
    return db.query(TaxonomyGroup).order_by(TaxonomyGroup.sort_order.asc(), TaxonomyGroup.id.asc()).all()


def get_group(db: Session, group_id: int) -> TaxonomyGroup | None:
    return db.get(TaxonomyGroup, group_id)


def create_group(db: Session, data: TaxonomyGroupInput) -> TaxonomyGroup:
    group = TaxonomyGroup(key=data.key, label=data.label)
    db.add(group)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f'Mã nhóm "{data.key}" đã tồn tại')
    db.refresh(group)
    return group


def update_group(db: Session, group_id: int, data: TaxonomyGroupInput) -> TaxonomyGroup | None:
    group = get_group(db, group_id)
    if group is None:
        return None
    group.key = data.key
    group.label = data.label
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f'Mã nhóm "{data.key}" đã tồn tại')
    db.refresh(group)
    return group


def create_value(db: Session, group_id: int, data: TaxonomyValueInput) -> TaxonomyValue | None:
    group = get_group(db, group_id)
    if group is None:
        return None
    value = TaxonomyValue(group_id=group_id, key=data.key, label=data.label)
    db.add(value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f'Mã giá trị "{data.key}" đã tồn tại trong nhóm này')
    db.refresh(value)
    return value


def get_value(db: Session, value_id: int) -> TaxonomyValue | None:
    return db.get(TaxonomyValue, value_id)


def update_value(db: Session, value_id: int, data: TaxonomyValueInput) -> TaxonomyValue | None:
    value = get_value(db, value_id)
    if value is None:
        return None
    value.key = data.key
    value.label = data.label
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f'Mã giá trị "{data.key}" đã tồn tại trong nhóm này')
    db.refresh(value)
    return value


def delete_value(db: Session, value_id: int) -> bool:
    value = get_value(db, value_id)
    if value is None:
        return False
    db.delete(value)
    db.commit()
    return True


def get_group_values(db: Session, group_key: str) -> list[str]:
    group = db.query(TaxonomyGroup).filter(TaxonomyGroup.key == group_key).first()
    if group is None:
        return []
    return [value.key for value in group.values]
