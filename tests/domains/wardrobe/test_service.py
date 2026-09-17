import pytest

from app.domains.auth import service as auth_service
from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyValueInput
from app.domains.taxonomy import service as taxonomy_service
from app.domains.wardrobe import service
from app.domains.wardrobe.schemas import WardrobeItemCreate


def _seed_clothing_type_group(db_session):
    group = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    taxonomy_service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))
    taxonomy_service.create_value(db_session, group.id, TaxonomyValueInput(key="dam", label="Đầm"))
    taxonomy_service.create_value(db_session, group.id, TaxonomyValueInput(key="quan", label="Quần"))
    return group


def test_create_and_list_items_for_a_user(db_session):
    _seed_clothing_type_group(db_session)
    user = auth_service.create_user(db_session, name="Test", email="wardrobe-svc@example.com", password="password123")
    other_user = auth_service.create_user(db_session, name="Other", email="wardrobe-svc-2@example.com", password="password123")

    service.create_item(
        db_session,
        user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/a.png",
            attributes={"clothing-type": ["ao"]},
            dominant_colors=["#ff0000"],
        ),
    )
    service.create_item(
        db_session,
        other_user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/b.png",
            attributes={"clothing-type": ["dam"]},
            dominant_colors=["#0000ff"],
        ),
    )

    items = service.list_items(db_session, user.id)

    assert len(items) == 1
    assert items[0].attributes == {"clothing-type": ["ao"]}


def test_get_item_returns_none_for_another_users_item(db_session):
    _seed_clothing_type_group(db_session)
    user = auth_service.create_user(db_session, name="Test", email="wardrobe-svc-3@example.com", password="password123")
    other_user = auth_service.create_user(db_session, name="Other", email="wardrobe-svc-4@example.com", password="password123")
    item = service.create_item(
        db_session,
        other_user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/c.png",
            attributes={"clothing-type": ["quan"]},
            dominant_colors=["#111111"],
        ),
    )

    assert service.get_item(db_session, user.id, item.id) is None


def test_create_item_accepts_valid_attributes(db_session):
    _seed_clothing_type_group(db_session)

    item = service.create_item(
        db_session,
        user_id=1,
        data=WardrobeItemCreate(
            blob_url="https://example.com/a.png",
            attributes={"clothing-type": ["ao"]},
            dominant_colors=["#ffffff"],
        ),
    )

    assert item.attributes == {"clothing-type": ["ao"]}


def test_create_item_rejects_unknown_group_key(db_session):
    _seed_clothing_type_group(db_session)

    with pytest.raises(ValueError):
        service.create_item(
            db_session,
            user_id=1,
            data=WardrobeItemCreate(
                blob_url="https://example.com/a.png",
                attributes={"not-a-real-group": ["x"]},
                dominant_colors=["#ffffff"],
            ),
        )


def test_create_item_rejects_unknown_value_within_a_valid_group(db_session):
    _seed_clothing_type_group(db_session)

    with pytest.raises(ValueError):
        service.create_item(
            db_session,
            user_id=1,
            data=WardrobeItemCreate(
                blob_url="https://example.com/a.png",
                attributes={"clothing-type": ["not-a-real-value"]},
                dominant_colors=["#ffffff"],
            ),
        )
