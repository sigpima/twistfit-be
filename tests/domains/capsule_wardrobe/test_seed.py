from app.domains.capsule_wardrobe.models import CapsuleSet
from app.domains.capsule_wardrobe.seed import seed_demo_capsule_sets


def test_seed_demo_capsule_sets_creates_three_sets(db_session):
    seed_demo_capsule_sets(db_session)
    sets = db_session.query(CapsuleSet).order_by(CapsuleSet.id.asc()).all()
    assert len(sets) == 3
    assert sets[0].title == "Thanh Lịch Công Sở"
    assert sets[0].items == [
        {"label": "Quần ống suông ngà:", "price": "490.000 ₫"},
        {"label": "Túi xách Minimalist:", "price": "720.000 ₫"},
    ]


def test_seed_demo_capsule_sets_is_idempotent(db_session):
    seed_demo_capsule_sets(db_session)
    seed_demo_capsule_sets(db_session)
    assert db_session.query(CapsuleSet).count() == 3
