from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.domains.admin_stats import service
from app.domains.auth.models import User
from app.domains.blog.models import BlogPost
from app.domains.contact.models import ContactMessage
from app.domains.forum.models import ForumPost
from app.domains.quiz_attempts.models import QuizAttempt


def _make_user(db_session, email: str) -> User:
    user = User(name="Author", email=email, password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_admin_stats_counts_across_all_domains(db_session):
    user = _make_user(db_session, "admin-stats-1@example.com")

    blog_post = BlogPost(
        slug="bai-test",
        title="Bài test",
        excerpt="Tóm tắt",
        content="Nội dung",
        cover_image_url="/x.jpg",
        category="community",
        author_name=None,
        is_featured=False,
        published_at="2026-01-01",
    )
    forum_post = ForumPost(title="Bài diễn đàn", body="Nội dung", category="general", author_id=user.id)
    quiz_attempt = QuizAttempt(
        sub_season="true-summer",
        parent_season="summer",
        hue_result="cool",
        value_result="medium",
        chroma_result="muted",
        user_id=user.id,
    )
    contact_message = ContactMessage(
        name="Khách", email="khach@twistfit.vn", phone=None, subject="other", message="Xin chào"
    )
    db_session.add_all([blog_post, forum_post, quiz_attempt, contact_message])
    db_session.commit()

    stats = service.get_admin_stats(db_session)

    assert stats.blog_posts.total == 1
    assert stats.forum_posts.total == 1
    assert stats.users.total == 1
    assert stats.quiz_attempts.total == 1
    assert stats.contact_messages.total == 1


def test_get_admin_stats_new_30d_excludes_older_rows(db_session):
    user = _make_user(db_session, "admin-stats-2@example.com")
    old_post = ForumPost(title="Bài cũ", body="Nội dung", category="general", author_id=user.id)
    db_session.add(old_post)
    db_session.commit()
    db_session.refresh(old_post)
    old_post.created_at = datetime.now(timezone.utc) - timedelta(days=40)
    db_session.commit()

    new_post = ForumPost(title="Bài mới", body="Nội dung", category="general", author_id=user.id)
    db_session.add(new_post)
    db_session.commit()

    stats = service.get_admin_stats(db_session)

    assert stats.forum_posts.total == 2
    assert stats.forum_posts.new_30d == 1


def test_get_admin_stats_contact_messages_unread_vs_total(db_session):
    read_message = ContactMessage(
        name="Khách 1", email="khach1@twistfit.vn", phone=None, subject="other", message="Xin chào", is_read=True
    )
    unread_message = ContactMessage(
        name="Khách 2", email="khach2@twistfit.vn", phone=None, subject="other", message="Xin chào"
    )
    db_session.add_all([read_message, unread_message])
    db_session.commit()

    stats = service.get_admin_stats(db_session)

    assert stats.contact_messages.total == 2
    assert stats.contact_messages.unread == 1
