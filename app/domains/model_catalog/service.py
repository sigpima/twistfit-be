from sqlalchemy.orm import Session

from app.domains.model_catalog.models import CatalogModel
from app.domains.model_catalog.schemas import CatalogModelInput


def list_models(db: Session) -> list[CatalogModel]:
    return db.query(CatalogModel).order_by(CatalogModel.id.asc()).all()


def get_model(db: Session, model_id: int) -> CatalogModel | None:
    return db.get(CatalogModel, model_id)


def create_model(db: Session, data: CatalogModelInput) -> CatalogModel:
    model = CatalogModel(**data.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def update_model(db: Session, model_id: int, data: CatalogModelInput) -> CatalogModel | None:
    model = get_model(db, model_id)
    if model is None:
        return None
    for field, value in data.model_dump().items():
        setattr(model, field, value)
    db.commit()
    db.refresh(model)
    return model


def delete_model(db: Session, model_id: int) -> bool:
    model = get_model(db, model_id)
    if model is None:
        return False
    db.delete(model)
    db.commit()
    return True
