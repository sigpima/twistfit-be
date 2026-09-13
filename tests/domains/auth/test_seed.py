from app.domains.auth import service
from app.domains.auth.models import User
from app.domains.auth.seed import seed_demo_users


def test_seed_demo_users_creates_both_accounts(db_session):
    seed_demo_users(db_session)
    user = service.get_user_by_email(db_session, "user@twistfit.vn")
    admin = service.get_user_by_email(db_session, "admin@twistfit.vn")
    assert user is not None and user.role == "user"
    assert admin is not None and admin.role == "admin"


def test_seed_demo_users_is_idempotent(db_session):
    seed_demo_users(db_session)
    seed_demo_users(db_session)
    count = db_session.query(User).filter(User.email == "admin@twistfit.vn").count()
    assert count == 1
