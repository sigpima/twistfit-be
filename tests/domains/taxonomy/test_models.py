from app.domains.taxonomy.models import TaxonomyGroup, TaxonomyValue


def test_group_can_be_created_with_values(db_session):
    group = TaxonomyGroup(key="clothing-type", label="Loại quần áo", sort_order=0)
    group.values.append(TaxonomyValue(key="ao", label="Áo", sort_order=0))
    group.values.append(TaxonomyValue(key="quan", label="Quần", sort_order=1))
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    assert group.id is not None
    assert [v.key for v in group.values] == ["ao", "quan"]
    assert group.values[0].group_id == group.id


def test_deleting_group_cascades_to_its_values(db_session):
    group = TaxonomyGroup(key="occasion", label="Loại dịp", sort_order=0)
    group.values.append(TaxonomyValue(key="hang-ngay", label="Hằng ngày", sort_order=0))
    db_session.add(group)
    db_session.commit()
    value_id = group.values[0].id

    db_session.delete(group)
    db_session.commit()

    assert db_session.get(TaxonomyValue, value_id) is None
