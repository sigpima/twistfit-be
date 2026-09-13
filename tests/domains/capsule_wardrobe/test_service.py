import pytest
from pydantic import ValidationError

from app.domains.capsule_wardrobe import service
from app.domains.capsule_wardrobe.schemas import CapsuleSetInput

VALID_INPUT = {
    "image": "/outfit/capsule-test.jpg",
    "alt": "Ảnh test",
    "tagVariant": "primary",
    "tagLabel": "Set test",
    "fitFor": "Phù hợp: Test",
    "title": "Set Test",
    "tone": "Test Tone",
    "description": "Mô tả test",
    "items": [{"label": "Món đồ:", "price": "100.000 ₫"}],
}


def test_create_capsule_set(db_session):
    capsule_set = service.create_capsule_set(db_session, CapsuleSetInput(**VALID_INPUT))
    assert capsule_set.id is not None
    assert capsule_set.title == "Set Test"
    assert capsule_set.items == [{"label": "Món đồ:", "price": "100.000 ₫"}]


def test_list_capsule_sets_orders_by_id(db_session):
    first = service.create_capsule_set(db_session, CapsuleSetInput(**VALID_INPUT))
    second = service.create_capsule_set(db_session, CapsuleSetInput(**{**VALID_INPUT, "title": "Second"}))
    sets = service.list_capsule_sets(db_session)
    assert [s.id for s in sets] == [first.id, second.id]


def test_get_capsule_set_returns_none_when_missing(db_session):
    assert service.get_capsule_set(db_session, 99999) is None


def test_update_capsule_set(db_session):
    capsule_set = service.create_capsule_set(db_session, CapsuleSetInput(**VALID_INPUT))
    updated = service.update_capsule_set(
        db_session, capsule_set.id, CapsuleSetInput(**{**VALID_INPUT, "title": "Đã sửa"})
    )
    assert updated is not None
    assert updated.title == "Đã sửa"


def test_update_capsule_set_returns_none_when_missing(db_session):
    assert service.update_capsule_set(db_session, 99999, CapsuleSetInput(**VALID_INPUT)) is None


def test_delete_capsule_set(db_session):
    capsule_set = service.create_capsule_set(db_session, CapsuleSetInput(**VALID_INPUT))
    assert service.delete_capsule_set(db_session, capsule_set.id) is True
    assert service.get_capsule_set(db_session, capsule_set.id) is None


def test_delete_capsule_set_returns_false_when_missing(db_session):
    assert service.delete_capsule_set(db_session, 99999) is False


def test_capsule_set_input_rejects_blank_title():
    with pytest.raises(ValidationError):
        CapsuleSetInput(**{**VALID_INPUT, "title": "   "})


def test_capsule_set_input_rejects_invalid_tag_variant():
    with pytest.raises(ValidationError):
        CapsuleSetInput(**{**VALID_INPUT, "tagVariant": "not-a-real-variant"})


def test_capsule_set_input_rejects_empty_items():
    with pytest.raises(ValidationError):
        CapsuleSetInput(**{**VALID_INPUT, "items": []})


def test_capsule_set_input_rejects_item_with_blank_label():
    with pytest.raises(ValidationError):
        CapsuleSetInput(**{**VALID_INPUT, "items": [{"label": "  ", "price": "100.000 ₫"}]})
