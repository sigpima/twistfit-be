import pytest

from app.domains.forum import service
from app.domains.forum.schemas import ForumPostCreate

VALID_POST = ForumPostCreate(title="Bài test", body="Nội dung", category="general")


def _make_user(db_session, email: str):
    from app.domains.auth import service as auth_service

    return auth_service.create_user(db_session, name="Author", email=email, password="password123")


def test_create_post_defaults_to_pending(db_session):
    user = _make_user(db_session, "forum-svc-1@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    assert post.status == "pending"
    assert post.author_id == user.id


def test_list_published_posts_excludes_non_published(db_session):
    user = _make_user(db_session, "forum-svc-2@example.com")
    published = service.create_post(db_session, user.id, VALID_POST)
    service.set_post_status(db_session, published.id, "published")
    service.create_post(db_session, user.id, VALID_POST.model_copy(update={"title": "Bài chờ"}))

    posts = service.list_published_posts(db_session, None)
    assert [p.id for p in posts] == [published.id]


def test_list_published_posts_filters_by_category(db_session):
    user = _make_user(db_session, "forum-svc-3@example.com")
    general = service.create_post(db_session, user.id, VALID_POST)
    service.set_post_status(db_session, general.id, "published")
    styling = service.create_post(
        db_session, user.id, VALID_POST.model_copy(update={"category": "styling-help"})
    )
    service.set_post_status(db_session, styling.id, "published")

    posts = service.list_published_posts(db_session, "styling-help")
    assert [p.id for p in posts] == [styling.id]


def test_list_posts_by_author_returns_all_statuses_for_that_author_only(db_session):
    user = _make_user(db_session, "forum-svc-4@example.com")
    other = _make_user(db_session, "forum-svc-5@example.com")
    mine = service.create_post(db_session, user.id, VALID_POST)
    service.create_post(db_session, other.id, VALID_POST)

    posts = service.list_posts_by_author(db_session, user.id)
    assert [p.id for p in posts] == [mine.id]


def test_list_pending_posts_orders_oldest_first(db_session):
    user = _make_user(db_session, "forum-svc-6@example.com")
    first = service.create_post(db_session, user.id, VALID_POST)
    second = service.create_post(db_session, user.id, VALID_POST)

    posts = service.list_pending_posts(db_session)
    assert [p.id for p in posts] == [first.id, second.id]


def test_can_view_post_rules(db_session):
    user = _make_user(db_session, "forum-svc-7@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)

    assert service.can_view_post(post, None, None) is False
    assert service.can_view_post(post, user.id, "user") is True
    assert service.can_view_post(post, 999999, "admin") is True
    assert service.can_view_post(post, 999999, "user") is False

    service.set_post_status(db_session, post.id, "published")
    published = service.get_post(db_session, post.id)
    assert service.can_view_post(published, None, None) is True


def test_update_post_resets_status_to_pending_even_from_published(db_session):
    user = _make_user(db_session, "forum-svc-8@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    service.set_post_status(db_session, post.id, "published")

    updated = service.update_post(db_session, post.id, VALID_POST.model_copy(update={"title": "Đã sửa"}))
    assert updated.status == "pending"
    assert updated.title == "Đã sửa"


def test_update_post_returns_none_when_missing(db_session):
    assert service.update_post(db_session, 999999, VALID_POST) is None


def test_delete_post_removes_it(db_session):
    user = _make_user(db_session, "forum-svc-9@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    assert service.delete_post(db_session, post.id) is True
    assert service.get_post(db_session, post.id) is None
    assert service.delete_post(db_session, post.id) is False


def test_set_post_status_valid_transition(db_session):
    user = _make_user(db_session, "forum-svc-10@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    updated = service.set_post_status(db_session, post.id, "published")
    assert updated.status == "published"


def test_set_post_status_rejects_invalid_transition(db_session):
    user = _make_user(db_session, "forum-svc-11@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    with pytest.raises(service.InvalidStatusTransitionError):
        service.set_post_status(db_session, post.id, "hidden")


def test_set_post_status_rejects_transition_from_a_terminal_status(db_session):
    user = _make_user(db_session, "forum-svc-12@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    service.set_post_status(db_session, post.id, "rejected")
    with pytest.raises(service.InvalidStatusTransitionError):
        service.set_post_status(db_session, post.id, "published")


def test_set_post_status_returns_none_when_missing(db_session):
    assert service.set_post_status(db_session, 999999, "published") is None


def test_create_report_defaults_to_open(db_session):
    user = _make_user(db_session, "forum-svc-13@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    report = service.create_report(db_session, post.id, user.id, "Spam")
    assert report.status == "open"
    assert report.post_id == post.id


def test_list_open_reports_excludes_resolved(db_session):
    user = _make_user(db_session, "forum-svc-14@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    open_report = service.create_report(db_session, post.id, user.id, "Spam")
    resolved_report = service.create_report(db_session, post.id, user.id, "Khác")
    service.resolve_report(db_session, resolved_report.id)

    reports = service.list_open_reports(db_session)
    assert [r.id for r in reports] == [open_report.id]


def test_resolve_report_marks_it_resolved(db_session):
    user = _make_user(db_session, "forum-svc-15@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    report = service.create_report(db_session, post.id, user.id, "Spam")
    resolved = service.resolve_report(db_session, report.id)
    assert resolved.status == "resolved"


def test_resolve_report_returns_none_when_missing(db_session):
    assert service.resolve_report(db_session, 999999) is None
