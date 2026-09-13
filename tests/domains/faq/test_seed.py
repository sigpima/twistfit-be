from app.domains.faq.models import FaqItem
from app.domains.faq.seed import seed_demo_faq_items


def test_seed_demo_faq_items_creates_six_items(db_session):
    seed_demo_faq_items(db_session)
    assert db_session.query(FaqItem).count() == 6


def test_seed_demo_faq_items_is_idempotent(db_session):
    seed_demo_faq_items(db_session)
    seed_demo_faq_items(db_session)
    assert db_session.query(FaqItem).count() == 6
