import pytest
from pydantic import ValidationError

from app.domains.model_catalog import service
from app.domains.model_catalog.schemas import CatalogModelInput

VALID_INPUT = {
    "name": "Test Model",
    "image": "/outfit/models/test.jpg",
    "dossierImage": "/outfit/models/test-dossier.jpg",
    "poseCount": 10,
    "tagline": "Test tagline",
    "undertone": "warm",
    "height": "1m70",
    "bodyShape": "Chữ nhật",
    "waist": "70cm",
    "personalColor": "Warm Spring",
}


def test_create_model(db_session):
    model = service.create_model(db_session, CatalogModelInput(**VALID_INPUT))
    assert model.id is not None
    assert model.name == "Test Model"


def test_list_models_orders_by_id(db_session):
    first = service.create_model(db_session, CatalogModelInput(**VALID_INPUT))
    second = service.create_model(db_session, CatalogModelInput(**{**VALID_INPUT, "name": "Second"}))
    models = service.list_models(db_session)
    assert [m.id for m in models] == [first.id, second.id]


def test_get_model_returns_none_when_missing(db_session):
    assert service.get_model(db_session, 99999) is None


def test_update_model(db_session):
    model = service.create_model(db_session, CatalogModelInput(**VALID_INPUT))
    updated = service.update_model(db_session, model.id, CatalogModelInput(**{**VALID_INPUT, "name": "Đã sửa"}))
    assert updated is not None
    assert updated.name == "Đã sửa"


def test_update_model_returns_none_when_missing(db_session):
    assert service.update_model(db_session, 99999, CatalogModelInput(**VALID_INPUT)) is None


def test_delete_model(db_session):
    model = service.create_model(db_session, CatalogModelInput(**VALID_INPUT))
    assert service.delete_model(db_session, model.id) is True
    assert service.get_model(db_session, model.id) is None


def test_delete_model_returns_false_when_missing(db_session):
    assert service.delete_model(db_session, 99999) is False


def test_model_input_rejects_blank_name():
    with pytest.raises(ValidationError):
        CatalogModelInput(**{**VALID_INPUT, "name": "   "})


def test_model_input_rejects_invalid_undertone():
    with pytest.raises(ValidationError):
        CatalogModelInput(**{**VALID_INPUT, "undertone": "not-a-real-undertone"})


def test_model_input_rejects_non_positive_pose_count():
    with pytest.raises(ValidationError):
        CatalogModelInput(**{**VALID_INPUT, "poseCount": 0})
