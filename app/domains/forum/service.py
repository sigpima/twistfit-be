from sqlalchemy.orm import Session

from app.domains.forum.models import ForumBookmark, ForumComment, ForumLike, ForumPost, ForumReport
from app.domains.forum.schemas import ForumCommentCreate, ForumPostCreate

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


def list_saved_posts(db: Session, user_id: int) -> list[ForumPost]:
    return (
        db.query(ForumPost)
        .join(ForumBookmark, ForumBookmark.post_id == ForumPost.id)
        .filter(ForumBookmark.user_id == user_id)
        .order_by(ForumBookmark.id.desc())
        .all()
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
        title=data.title,
        body=data.body,
        category=data.category,
        image_url=data.image_url,
        status="pending",
        author_id=author_id,
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
    post.image_url = data.image_url
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


def count_likes(db: Session, post_id: int) -> int:
    return db.query(ForumLike).filter(ForumLike.post_id == post_id).count()


def user_has_liked(db: Session, post_id: int, user_id: int) -> bool:
    return (
        db.query(ForumLike).filter(ForumLike.post_id == post_id, ForumLike.user_id == user_id).first()
        is not None
    )


def count_comments(db: Session, post_id: int) -> int:
    return db.query(ForumComment).filter(ForumComment.post_id == post_id).count()


def toggle_like(db: Session, post_id: int, user_id: int) -> tuple[bool, int]:
    existing = (
        db.query(ForumLike).filter(ForumLike.post_id == post_id, ForumLike.user_id == user_id).first()
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
        return False, count_likes(db, post_id)

    db.add(ForumLike(post_id=post_id, user_id=user_id))
    db.commit()
    return True, count_likes(db, post_id)


def user_has_bookmarked(db: Session, post_id: int, user_id: int) -> bool:
    return (
        db.query(ForumBookmark)
        .filter(ForumBookmark.post_id == post_id, ForumBookmark.user_id == user_id)
        .first()
        is not None
    )


def toggle_bookmark(db: Session, post_id: int, user_id: int) -> bool:
    existing = (
        db.query(ForumBookmark)
        .filter(ForumBookmark.post_id == post_id, ForumBookmark.user_id == user_id)
        .first()
    )
    if existing is not None:
        db.delete(existing)
        db.commit()
        return False
    db.add(ForumBookmark(post_id=post_id, user_id=user_id))
    db.commit()
    return True


def create_comment(db: Session, post_id: int, author_id: int, data: ForumCommentCreate) -> ForumComment:
    comment = ForumComment(post_id=post_id, author_id=author_id, body=data.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, post_id: int) -> list[ForumComment]:
    return db.query(ForumComment).filter(ForumComment.post_id == post_id).order_by(ForumComment.id.asc()).all()


def get_comment(db: Session, comment_id: int) -> ForumComment | None:
    return db.get(ForumComment, comment_id)


def delete_comment(db: Session, comment_id: int) -> bool:
    comment = get_comment(db, comment_id)
    if comment is None:
        return False
    db.delete(comment)
    db.commit()
    return True


def build_comment_response(comment: ForumComment, viewer_id: int | None, viewer_role: str | None) -> dict:
    can_delete = viewer_id is not None and (viewer_id == comment.author_id or viewer_role == "admin")
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_name": comment.author.name,
        "body": comment.body,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "can_delete": can_delete,
    }


def build_post_response(db: Session, post: ForumPost, viewer_id: int | None) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "image_url": post.image_url,
        "category": post.category,
        "status": post.status,
        "author_id": post.author_id,
        "author_name": post.author.name,
        "like_count": count_likes(db, post.id),
        "liked_by_me": viewer_id is not None and user_has_liked(db, post.id, viewer_id),
        "comment_count": count_comments(db, post.id),
        "bookmarked_by_me": viewer_id is not None and user_has_bookmarked(db, post.id, viewer_id),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }
