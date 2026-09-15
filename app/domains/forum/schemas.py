from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

FORUM_CATEGORIES = ["general", "outfit-showcase", "styling-help", "personal-color", "sustainable-swap"]
FORUM_POST_STATUSES = ["pending", "published", "rejected", "hidden"]


class ForumPostCreate(CamelModel):
    title: str
    body: str
    category: str
    image_url: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Tiêu đề không được để trống")
        return stripped

    @field_validator("body")
    @classmethod
    def body_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Nội dung không được để trống")
        return stripped

    @field_validator("category")
    @classmethod
    def category_valid(cls, value: str) -> str:
        if value not in FORUM_CATEGORIES:
            raise ValueError("Chuyên mục không hợp lệ")
        return value


class ForumPostStatusUpdate(CamelModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, value: str) -> str:
        if value not in FORUM_POST_STATUSES:
            raise ValueError("Trạng thái không hợp lệ")
        return value


class ForumPostResponse(CamelModel):
    id: int
    title: str
    body: str
    image_url: str | None
    category: str
    status: str
    author_id: int
    author_name: str
    like_count: int
    liked_by_me: bool
    comment_count: int
    created_at: datetime
    updated_at: datetime


class ForumReportCreate(CamelModel):
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Vui lòng nhập lý do báo cáo")
        return stripped


class ForumReportResponse(CamelModel):
    id: int
    post_id: int
    post_title: str
    post_status: str
    reporter_id: int
    reason: str
    status: str
    created_at: datetime


class ForumLikeResponse(CamelModel):
    liked: bool
    like_count: int


class ForumCommentCreate(CamelModel):
    body: str

    @field_validator("body")
    @classmethod
    def body_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Nội dung bình luận không được để trống")
        return stripped


class ForumCommentResponse(CamelModel):
    id: int
    post_id: int
    author_id: int
    author_name: str
    body: str
    created_at: datetime
    updated_at: datetime
    can_delete: bool
