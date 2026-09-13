from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user, get_current_user_optional, require_admin
from app.domains.auth.models import User
from app.domains.forum import service
from app.domains.forum.schemas import (
    FORUM_CATEGORIES,
    ForumPostCreate,
    ForumPostResponse,
    ForumPostStatusUpdate,
    ForumReportCreate,
    ForumReportResponse,
)

router = APIRouter(prefix="/forum", tags=["forum"])


@router.get("/posts", response_model=list[ForumPostResponse])
def list_posts(category: str | None = None, db: Session = Depends(get_db)):
    valid_category = category if category in FORUM_CATEGORIES else None
    return service.list_published_posts(db, valid_category)


@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(body: ForumPostCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.create_post(db, user.id, body)


# Registered before /posts/{post_id} — a literal "mine" segment would
# otherwise be swallowed by the {post_id} path parameter.
@router.get("/posts/mine", response_model=list[ForumPostResponse])
def list_my_posts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.list_posts_by_author(db, user.id)


@router.get("/posts/{post_id}", response_model=ForumPostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_current_user_optional),
):
    post = service.get_post(db, post_id)
    viewer_id = viewer.id if viewer else None
    viewer_role = viewer.role if viewer else None
    if post is None or not service.can_view_post(post, viewer_id, viewer_role):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    return post


@router.put("/posts/{post_id}", response_model=ForumPostResponse)
def update_post(
    post_id: int,
    body: ForumPostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = service.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    if post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền sửa bài này")
    return service.update_post(db, post_id, body)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    post = service.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    if post.author_id != user.id and user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xóa bài này")
    service.delete_post(db, post_id)


@router.patch("/posts/{post_id}", response_model=ForumPostResponse)
def update_post_status(
    post_id: int,
    body: ForumPostStatusUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        updated = service.set_post_status(db, post_id, body.status)
    except service.InvalidStatusTransitionError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="INVALID_STATUS_TRANSITION")
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    return updated


@router.post("/posts/{post_id}/report", response_model=ForumReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    post_id: int,
    body: ForumReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = service.get_post(db, post_id)
    if post is None or not service.can_view_post(post, user.id, user.role):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    return service.create_report(db, post_id, user.id, body.reason)


@router.get("/moderation/pending", response_model=list[ForumPostResponse])
def list_pending_posts(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return service.list_pending_posts(db)


@router.get("/moderation/reports", response_model=list[ForumReportResponse])
def list_open_reports(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return service.list_open_reports(db)


@router.patch("/reports/{report_id}", response_model=ForumReportResponse)
def resolve_report(report_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    resolved = service.resolve_report(db, report_id)
    if resolved is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy báo cáo")
    return resolved
