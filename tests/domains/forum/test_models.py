import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.domains.auth.models import User
from app.domains.forum.models import ForumComment, ForumLike, ForumPost, ForumReport


def _make_user_and_post(db_session, email: str) -> tuple[User, ForumPost]:
    user = User(name="Author", email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    post = ForumPost(title="Bài test", body="Nội dung", category="general", author_id=user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return user, post


def test_create_forum_post_defaults_status_to_pending(db_session):
    user = User(
        name="Author", email="forum-model-author@example.com", password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    post = ForumPost(title="Bài test", body="Nội dung", category="general", author_id=user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    assert post.id is not None
    assert post.status == "pending"
    assert post.created_at is not None
    assert post.updated_at is not None


def test_forum_report_exposes_post_title_and_status_via_relationship(db_session):
    user = User(
        name="Author", email="forum-model-author2@example.com", password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    post = ForumPost(
        title="Bài bị báo cáo", body="Nội dung", category="general", status="published", author_id=user.id
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    report = ForumReport(post_id=post.id, reporter_id=user.id, reason="Spam")
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)

    assert report.status == "open"
    assert report.post_title == "Bài bị báo cáo"
    assert report.post_status == "published"


def test_forum_post_image_url_defaults_to_none(db_session):
    _, post = _make_user_and_post(db_session, "forum-model-image@example.com")
    assert post.image_url is None


def test_forum_comment_persists_and_exposes_its_author(db_session):
    user, post = _make_user_and_post(db_session, "forum-model-comment@example.com")

    comment = ForumComment(post_id=post.id, author_id=user.id, body="Đẹp quá!")
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)

    assert comment.id is not None
    assert comment.author.name == "Author"
    assert comment.created_at is not None
    assert comment.updated_at is not None


def test_forum_like_enforces_one_like_per_user_per_post(db_session):
    user, post = _make_user_and_post(db_session, "forum-model-like@example.com")

    db_session.add(ForumLike(post_id=post.id, user_id=user.id))
    db_session.commit()

    db_session.add(ForumLike(post_id=post.id, user_id=user.id))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
