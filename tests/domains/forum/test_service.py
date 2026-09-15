import pytest

from app.domains.forum import service
from app.domains.forum.schemas import ForumCommentCreate, ForumPostCreate

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


def test_build_post_response_includes_author_name_and_zeroed_counts(db_session):
    user = _make_user(db_session, "forum-svc-shape1@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)

    data = service.build_post_response(db_session, post, viewer_id=None)

    assert data["author_name"] == "Author"
    assert data["image_url"] is None
    assert data["like_count"] == 0
    assert data["liked_by_me"] is False
    assert data["comment_count"] == 0


def test_create_post_persists_an_image_url(db_session):
    user = _make_user(db_session, "forum-svc-shape2@example.com")
    post = service.create_post(
        db_session, user.id, VALID_POST.model_copy(update={"image_url": "https://example.com/a.jpg"})
    )
    assert post.image_url == "https://example.com/a.jpg"


def test_update_post_can_replace_the_image_url(db_session):
    user = _make_user(db_session, "forum-svc-shape3@example.com")
    post = service.create_post(
        db_session, user.id, VALID_POST.model_copy(update={"image_url": "https://example.com/old.jpg"})
    )
    updated = service.update_post(
        db_session, post.id, VALID_POST.model_copy(update={"image_url": "https://example.com/new.jpg"})
    )
    assert updated.image_url == "https://example.com/new.jpg"


def test_toggle_like_creates_then_removes_a_like(db_session):
    user = _make_user(db_session, "forum-svc-like1@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)

    liked, count = service.toggle_like(db_session, post.id, user.id)
    assert (liked, count) == (True, 1)

    liked, count = service.toggle_like(db_session, post.id, user.id)
    assert (liked, count) == (False, 0)


def test_toggle_like_counts_multiple_users_independently(db_session):
    user = _make_user(db_session, "forum-svc-like2@example.com")
    other = _make_user(db_session, "forum-svc-like3@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)

    service.toggle_like(db_session, post.id, user.id)
    liked, count = service.toggle_like(db_session, post.id, other.id)
    assert (liked, count) == (True, 2)


def test_create_comment_persists_it(db_session):
    user = _make_user(db_session, "forum-svc-comment1@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)

    comment = service.create_comment(db_session, post.id, user.id, ForumCommentCreate(body="Đẹp quá!"))
    assert comment.id is not None
    assert comment.post_id == post.id
    assert comment.author_id == user.id


def test_list_comments_orders_oldest_first(db_session):
    user = _make_user(db_session, "forum-svc-comment2@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    first = service.create_comment(db_session, post.id, user.id, ForumCommentCreate(body="Đầu tiên"))
    second = service.create_comment(db_session, post.id, user.id, ForumCommentCreate(body="Thứ hai"))

    comments = service.list_comments(db_session, post.id)
    assert [c.id for c in comments] == [first.id, second.id]


def test_delete_comment_removes_it(db_session):
    user = _make_user(db_session, "forum-svc-comment3@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    comment = service.create_comment(db_session, post.id, user.id, ForumCommentCreate(body="Xoá tôi"))

    assert service.delete_comment(db_session, comment.id) is True
    assert service.get_comment(db_session, comment.id) is None
    assert service.delete_comment(db_session, comment.id) is False


def test_build_comment_response_allows_delete_for_the_author(db_session):
    user = _make_user(db_session, "forum-svc-comment4@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    comment = service.create_comment(db_session, post.id, user.id, ForumCommentCreate(body="Của tôi"))

    data = service.build_comment_response(comment, viewer_id=user.id, viewer_role="user")
    assert data["can_delete"] is True
    assert data["author_name"] == "Author"


def test_build_comment_response_allows_delete_for_an_admin(db_session):
    user = _make_user(db_session, "forum-svc-comment5@example.com")
    other = _make_user(db_session, "forum-svc-comment6@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    comment = service.create_comment(db_session, post.id, user.id, ForumCommentCreate(body="Của tôi"))

    data = service.build_comment_response(comment, viewer_id=other.id, viewer_role="admin")
    assert data["can_delete"] is True


def test_build_comment_response_forbids_delete_for_a_stranger(db_session):
    user = _make_user(db_session, "forum-svc-comment7@example.com")
    other = _make_user(db_session, "forum-svc-comment8@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)
    comment = service.create_comment(db_session, post.id, user.id, ForumCommentCreate(body="Của tôi"))

    data = service.build_comment_response(comment, viewer_id=other.id, viewer_role="user")
    assert data["can_delete"] is False


def test_toggle_bookmark_creates_then_removes_a_bookmark(db_session):
    user = _make_user(db_session, "forum-svc-bookmark1@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)

    assert service.toggle_bookmark(db_session, post.id, user.id) is True
    assert service.toggle_bookmark(db_session, post.id, user.id) is False


def test_build_post_response_reflects_bookmarked_by_me(db_session):
    user = _make_user(db_session, "forum-svc-bookmark2@example.com")
    post = service.create_post(db_session, user.id, VALID_POST)

    data = service.build_post_response(db_session, post, viewer_id=user.id)
    assert data["bookmarked_by_me"] is False

    service.toggle_bookmark(db_session, post.id, user.id)
    data = service.build_post_response(db_session, post, viewer_id=user.id)
    assert data["bookmarked_by_me"] is True


def test_list_saved_posts_returns_only_the_caller_bookmarked_posts(db_session):
    user = _make_user(db_session, "forum-svc-saved1@example.com")
    other = _make_user(db_session, "forum-svc-saved2@example.com")
    mine = service.create_post(db_session, user.id, VALID_POST)
    others_post = service.create_post(db_session, other.id, VALID_POST)

    service.toggle_bookmark(db_session, mine.id, user.id)
    service.toggle_bookmark(db_session, others_post.id, other.id)

    saved = service.list_saved_posts(db_session, user.id)
    assert [p.id for p in saved] == [mine.id]


def test_list_saved_posts_orders_newest_bookmark_first(db_session):
    user = _make_user(db_session, "forum-svc-saved3@example.com")
    first = service.create_post(db_session, user.id, VALID_POST)
    second = service.create_post(db_session, user.id, VALID_POST)

    service.toggle_bookmark(db_session, first.id, user.id)
    service.toggle_bookmark(db_session, second.id, user.id)

    saved = service.list_saved_posts(db_session, user.id)
    assert [p.id for p in saved] == [second.id, first.id]
