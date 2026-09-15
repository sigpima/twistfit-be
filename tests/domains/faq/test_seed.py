from app.domains.faq.models import FaqItem
from app.domains.faq.seed import seed_demo_faq_items


def test_seed_demo_faq_items_creates_thirty_three_items(db_session):
    seed_demo_faq_items(db_session)
    assert db_session.query(FaqItem).count() == 33


def test_seed_demo_faq_items_is_idempotent(db_session):
    seed_demo_faq_items(db_session)
    seed_demo_faq_items(db_session)
    assert db_session.query(FaqItem).count() == 33


def test_seed_demo_faq_items_covers_all_four_categories(db_session):
    seed_demo_faq_items(db_session)
    items = db_session.query(FaqItem).all()
    all_categories = {category for item in items for category in item.categories}
    assert all_categories == {"account", "personal-color", "fitting-room", "policy"}
