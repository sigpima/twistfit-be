from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.blog import service
from app.domains.blog.schemas import BlogPostInput, BlogPostResponse

router = APIRouter(prefix="/blog", tags=["blog"])


@router.get("", response_model=list[BlogPostResponse])
def list_items(db: Session = Depends(get_db)):
    return service.list_blog_posts(db)


@router.get("/slug/{slug}", response_model=BlogPostResponse)
def get_by_slug(slug: str, db: Session = Depends(get_db)):
    post = service.get_blog_post_by_slug(db, slug)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    return post


@router.get("/{post_id}", response_model=BlogPostResponse)
def get_item(post_id: int, db: Session = Depends(get_db)):
    post = service.get_blog_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    return post


@router.post("", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
def create_item(body: BlogPostInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    try:
        return service.create_blog_post(db, body)
    except service.SlugAlreadyTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SLUG_TAKEN")


@router.put("/{post_id}", response_model=BlogPostResponse)
def update_item(post_id: int, body: BlogPostInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    try:
        updated = service.update_blog_post(db, post_id, body)
    except service.SlugAlreadyTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SLUG_TAKEN")
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
    return updated


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(post_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    deleted = service.delete_blog_post(db, post_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bài viết")
