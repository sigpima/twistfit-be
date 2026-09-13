from app.core.security import hash_password
from app.domains.auth.models import User
from app.domains.forum.models import ForumPost, ForumReport


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
