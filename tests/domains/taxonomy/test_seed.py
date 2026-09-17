from app.domains.taxonomy import service
from app.domains.taxonomy.seed import seed_demo_taxonomy_groups


def test_seed_creates_the_three_known_groups(db_session):
    seed_demo_taxonomy_groups(db_session)

    groups = {g.key: g for g in service.list_groups(db_session)}
    assert set(groups) == {"clothing-type", "occasion", "style"}
    assert {v.key for v in groups["clothing-type"].values} == {"ao", "quan", "vay", "dam", "ao-khoac"}
    assert {v.key for v in groups["occasion"].values} == {"hang-ngay", "di-lam", "du-tiec", "di-bien"}
    assert {v.key for v in groups["style"].values} == {"casual", "minimalist", "street", "formal"}


def test_seed_is_idempotent(db_session):
    seed_demo_taxonomy_groups(db_session)
    seed_demo_taxonomy_groups(db_session)

    groups = service.list_groups(db_session)
    assert len(groups) == 3
