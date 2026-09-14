from app.domains.model_catalog.models import CatalogModel
from app.domains.model_catalog.seed import seed_demo_models


def test_seed_demo_models_creates_twelve_models(db_session):
    seed_demo_models(db_session)
    models = db_session.query(CatalogModel).order_by(CatalogModel.id.asc()).all()
    assert len(models) == 12
    assert models[0].name == "Carmen"
    assert models[0].undertone == "neutral"
    assert models[0].side_image == models[0].image


def test_seed_demo_models_is_idempotent(db_session):
    seed_demo_models(db_session)
    seed_demo_models(db_session)
    assert db_session.query(CatalogModel).count() == 12
