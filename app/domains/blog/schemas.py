from datetime import datetime

from pydantic import field_validator

from app.domains.auth.schemas import CamelModel

BLOG_CATEGORIES = ["personal-color", "styling", "sustainable", "beauty", "community"]


class BlogPostInput(CamelModel):
    slug: str = ""
    title: str
    excerpt: str
    content: str
    cover_image_url: str
    cover_image_alt: str | None = None
    category: str
    author_name: str | None = None
    is_featured: bool = False
    published_at: str

    @field_validator("title", "excerpt", "content", "cover_image_url", "published_at")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Trường này không được để trống")
        return value.strip()

    @field_validator("category")
    @classmethod
    def category_valid(cls, value: str) -> str:
        if value not in BLOG_CATEGORIES:
            raise ValueError("Chuyên mục không hợp lệ")
        return value

    @field_validator("author_name", "cover_image_alt")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str) -> str:
        return value.strip()


class BlogPostResponse(CamelModel):
    id: int
    slug: str
    title: str
    excerpt: str
    content: str
    cover_image_url: str
    cover_image_alt: str | None
    category: str
    author_name: str | None
    is_featured: bool
    published_at: str
    created_at: datetime
    updated_at: datetime
