from app.domains.model_catalog.models import CatalogModel
from app.domains.model_catalog.seed import seed_demo_models


def test_seed_demo_models_creates_eight_models(db_session):
    seed_demo_models(db_session)
    models = db_session.query(CatalogModel).order_by(CatalogModel.id.asc()).all()
    assert len(models) == 8
    assert models[0].name == "Mảnh mai"
    assert models[0].image == "/outfit/models/female-1.jpg"
    assert models[0].side_image == "/outfit/models/female-1-side.jpg"


def test_seed_demo_models_gives_every_model_a_distinct_side_image(db_session):
    seed_demo_models(db_session)
    models = db_session.query(CatalogModel).all()
    for model in models:
        assert model.side_image is not None
        assert model.side_image != model.image


def test_seed_demo_models_is_idempotent(db_session):
    seed_demo_models(db_session)
    seed_demo_models(db_session)
    assert db_session.query(CatalogModel).count() == 8
