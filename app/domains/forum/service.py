from sqlalchemy.orm import Session

from app.domains.forum.models import ForumPost, ForumReport
from app.domains.forum.schemas import ForumPostCreate

ALLOWED_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["published", "rejected"],
    "published": ["hidden"],
    "rejected": [],
    "hidden": [],
}


class InvalidStatusTransitionError(Exception):
    pass


def list_published_posts(db: Session, category: str | None) -> list[ForumPost]:
    query = db.query(ForumPost).filter(ForumPost.status == "published")
    if category is not None:
        query = query.filter(ForumPost.category == category)
    return query.order_by(ForumPost.id.desc()).all()


def list_posts_by_author(db: Session, author_id: int) -> list[ForumPost]:
    return (
        db.query(ForumPost).filter(ForumPost.author_id == author_id).order_by(ForumPost.id.desc()).all()
    )


def list_pending_posts(db: Session) -> list[ForumPost]:
    return db.query(ForumPost).filter(ForumPost.status == "pending").order_by(ForumPost.id.asc()).all()


def get_post(db: Session, post_id: int) -> ForumPost | None:
    return db.get(ForumPost, post_id)


def can_view_post(post: ForumPost, viewer_id: int | None, viewer_role: str | None) -> bool:
    if post.status == "published":
        return True
    if viewer_id is not None and viewer_id == post.author_id:
        return True
    if viewer_role == "admin":
        return True
    return False


def create_post(db: Session, author_id: int, data: ForumPostCreate) -> ForumPost:
    post = ForumPost(
        title=data.title, body=data.body, category=data.category, status="pending", author_id=author_id
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post_id: int, data: ForumPostCreate) -> ForumPost | None:
    post = get_post(db, post_id)
    if post is None:
        return None
    post.title = data.title
    post.body = data.body
    post.category = data.category
    post.status = "pending"
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int) -> bool:
    post = get_post(db, post_id)
    if post is None:
        return False
    db.delete(post)
    db.commit()
    return True


def set_post_status(db: Session, post_id: int, new_status: str) -> ForumPost | None:
    post = get_post(db, post_id)
    if post is None:
        return None
    allowed = ALLOWED_STATUS_TRANSITIONS.get(post.status, [])
    if new_status not in allowed:
        raise InvalidStatusTransitionError()
    post.status = new_status
    db.commit()
    db.refresh(post)
    return post


def create_report(db: Session, post_id: int, reporter_id: int, reason: str) -> ForumReport:
    report = ForumReport(post_id=post_id, reporter_id=reporter_id, reason=reason, status="open")
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_open_reports(db: Session) -> list[ForumReport]:
    return db.query(ForumReport).filter(ForumReport.status == "open").order_by(ForumReport.id.asc()).all()


def resolve_report(db: Session, report_id: int) -> ForumReport | None:
    report = db.get(ForumReport, report_id)
    if report is None:
        return None
    report.status = "resolved"
    db.commit()
    db.refresh(report)
    return report
