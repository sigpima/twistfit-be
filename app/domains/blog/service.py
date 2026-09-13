import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.blog.models import BlogPost
from app.domains.blog.schemas import BlogPostInput


class SlugAlreadyTakenError(Exception):
    pass


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    without_marks = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    without_marks = without_marks.replace("đ", "d").replace("Đ", "d")
    lowered = without_marks.lower().strip()
    dashed = re.sub(r"[^a-z0-9]+", "-", lowered)
    return dashed.strip("-")


def _is_slug_taken(db: Session, slug: str, exclude_id: int | None = None) -> bool:
    query = select(BlogPost.id).where(BlogPost.slug == slug)
    if exclude_id is not None:
        query = query.where(BlogPost.id != exclude_id)
    return db.execute(query).first() is not None


def list_blog_posts(db: Session) -> list[BlogPost]:
    return db.query(BlogPost).order_by(BlogPost.published_at.desc()).all()


def get_blog_post(db: Session, post_id: int) -> BlogPost | None:
    return db.get(BlogPost, post_id)


def get_blog_post_by_slug(db: Session, slug: str) -> BlogPost | None:
    return db.execute(select(BlogPost).where(BlogPost.slug == slug)).scalar_one_or_none()


def create_blog_post(db: Session, data: BlogPostInput) -> BlogPost:
    slug = slugify(data.slug or data.title)
    if _is_slug_taken(db, slug):
        raise SlugAlreadyTakenError(slug)

    row = data.model_dump()
    row["slug"] = slug
    post = BlogPost(**row)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_blog_post(db: Session, post_id: int, data: BlogPostInput) -> BlogPost | None:
    post = get_blog_post(db, post_id)
    if post is None:
        return None

    slug = slugify(data.slug or data.title)
    if _is_slug_taken(db, slug, exclude_id=post_id):
        raise SlugAlreadyTakenError(slug)

    row = data.model_dump()
    row["slug"] = slug
    for field, value in row.items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


def delete_blog_post(db: Session, post_id: int) -> bool:
    post = get_blog_post(db, post_id)
    if post is None:
        return False
    db.delete(post)
    db.commit()
    return True
