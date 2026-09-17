import pytest

from app.domains.taxonomy import service
from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyValueInput


def test_create_and_list_groups(db_session):
    service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    service.create_group(db_session, TaxonomyGroupInput(key="occasion", label="Loại dịp"))

    groups = service.list_groups(db_session)

    assert [g.key for g in groups] == ["clothing-type", "occasion"]


def test_create_group_rejects_duplicate_key(db_session):
    service.create_group(db_session, TaxonomyGroupInput(key="style", label="Loại phong cách"))

    with pytest.raises(ValueError):
        service.create_group(db_session, TaxonomyGroupInput(key="style", label="Trùng khóa"))


def test_create_value_adds_it_to_the_group(db_session):
    group = service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))

    value = service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))

    assert value is not None
    assert value.group_id == group.id
    refreshed = service.get_group(db_session, group.id)
    assert [v.key for v in refreshed.values] == ["ao"]


def test_create_value_returns_none_for_missing_group(db_session):
    result = service.create_value(db_session, 999999, TaxonomyValueInput(key="ao", label="Áo"))
    assert result is None


def test_create_value_rejects_duplicate_key_within_group(db_session):
    group = service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))

    with pytest.raises(ValueError):
        service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo (trùng)"))


def test_update_value_changes_its_label(db_session):
    group = service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    value = service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))

    updated = service.update_value(db_session, value.id, TaxonomyValueInput(key="ao", label="Áo (đã sửa)"))

    assert updated.label == "Áo (đã sửa)"


def test_delete_value_removes_it(db_session):
    group = service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    value = service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))

    deleted = service.delete_value(db_session, value.id)

    assert deleted is True
    assert service.get_group(db_session, group.id).values == []


def test_get_group_values_returns_value_keys_for_a_group(db_session):
    group = service.create_group(db_session, TaxonomyGroupInput(key="style", label="Loại phong cách"))
    service.create_value(db_session, group.id, TaxonomyValueInput(key="casual", label="Casual"))
    service.create_value(db_session, group.id, TaxonomyValueInput(key="formal", label="Formal"))

    assert service.get_group_values(db_session, "style") == ["casual", "formal"]


def test_get_group_values_returns_empty_list_for_unknown_group(db_session):
    assert service.get_group_values(db_session, "does-not-exist") == []


def test_delete_value_rejects_when_referenced_by_a_wardrobe_item(db_session):
    from app.domains.auth import service as auth_service
    from app.domains.wardrobe.models import WardrobeItem

    user = auth_service.create_user(db_session, name="Test", email="taxonomy-svc-1@example.com", password="password123")
    group = service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    value = service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))
    db_session.add(
        WardrobeItem(
            user_id=user.id,
            blob_url="https://example.com/a.png",
            attributes={"clothing-type": ["ao"]},
            dominant_colors=["#ffffff"],
        )
    )
    db_session.commit()

    with pytest.raises(ValueError):
        service.delete_value(db_session, value.id)
