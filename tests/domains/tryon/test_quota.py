from datetime import date, timedelta

from app.domains.auth import service as auth_service
from app.domains.tryon import service as tryon_service
from app.domains.tryon.models import TryOnDailyQuota


def _user(db_session, email="quota@example.com"):
    return auth_service.create_user(db_session, name="Test", email=email, password="password123")


def test_reserve_tryon_quota_succeeds_up_to_the_limit_then_fails(db_session):
    user = _user(db_session)

    for _ in range(5):
        assert tryon_service.reserve_tryon_quota(db_session, user.id, limit=5) is True

    assert tryon_service.reserve_tryon_quota(db_session, user.id, limit=5) is False


def test_reserve_tryon_quota_is_scoped_per_user(db_session):
    user_a = _user(db_session, "quota-a@example.com")
    user_b = _user(db_session, "quota-b@example.com")

    for _ in range(5):
        assert tryon_service.reserve_tryon_quota(db_session, user_a.id, limit=5) is True

    # user_a is exhausted, but user_b's quota is independent.
    assert tryon_service.reserve_tryon_quota(db_session, user_a.id, limit=5) is False
    assert tryon_service.reserve_tryon_quota(db_session, user_b.id, limit=5) is True


def test_release_tryon_quota_frees_up_a_slot(db_session):
    user = _user(db_session)
    for _ in range(5):
        assert tryon_service.reserve_tryon_quota(db_session, user.id, limit=5) is True
    assert tryon_service.reserve_tryon_quota(db_session, user.id, limit=5) is False

    tryon_service.release_tryon_quota(db_session, user.id)

    assert tryon_service.reserve_tryon_quota(db_session, user.id, limit=5) is True


def test_release_tryon_quota_never_goes_below_zero(db_session):
    user = _user(db_session)

    # No reservation made yet — releasing must not underflow into negative territory.
    tryon_service.release_tryon_quota(db_session, user.id)

    used, remaining = tryon_service.get_tryon_quota(db_session, user.id, limit=5)
    assert used == 0
    assert remaining == 5


def test_get_tryon_quota_reports_used_and_remaining(db_session):
    user = _user(db_session)
    tryon_service.reserve_tryon_quota(db_session, user.id, limit=5)
    tryon_service.reserve_tryon_quota(db_session, user.id, limit=5)

    used, remaining = tryon_service.get_tryon_quota(db_session, user.id, limit=5)
    assert used == 2
    assert remaining == 3


def test_get_tryon_quota_ignores_reservations_from_a_different_day(db_session):
    user = _user(db_session)
    tryon_service.reserve_tryon_quota(db_session, user.id, limit=5)

    yesterday = date.today() - timedelta(days=2)
    db_session.query(TryOnDailyQuota).filter(TryOnDailyQuota.user_id == user.id).update({"quota_date": yesterday})
    db_session.commit()

    used, remaining = tryon_service.get_tryon_quota(db_session, user.id, limit=5)
    assert used == 0
    assert remaining == 5
