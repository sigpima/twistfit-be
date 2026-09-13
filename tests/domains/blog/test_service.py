import pytest
from pydantic import ValidationError

from app.domains.blog import service
from app.domains.blog.schemas import BlogPostInput

VALID_INPUT = {
    "title": "Bài Test",
    "excerpt": "Mô tả",
    "content": "Nội dung",
    "coverImageUrl": "/blog/test.jpg",
    "category": "styling",
    "authorName": None,
    "isFeatured": False,
    "publishedAt": "2026-01-01",
}


def test_slugify_strips_vietnamese_diacritics_and_dashes():
    assert (
        service.slugify("Bí quyết chọn trang phục tôn da chuẩn tone Mùa Đông")
        == "bi-quyet-chon-trang-phuc-ton-da-chuan-tone-mua-dong"
    )


def test_create_blog_post_generates_slug_from_title_when_blank(db_session):
    post = service.create_blog_post(db_session, BlogPostInput(**VALID_INPUT))
    assert post.slug == "bai-test"


def test_create_blog_post_uses_provided_slug(db_session):
    post = service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "custom-slug"}))
    assert post.slug == "custom-slug"


def test_create_blog_post_rejects_duplicate_slug(db_session):
    service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "dup"}))
    with pytest.raises(service.SlugAlreadyTakenError):
        service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "dup", "title": "Khác"}))


def test_update_blog_post_allows_keeping_its_own_slug(db_session):
    post = service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "keep-me"}))
    updated = service.update_blog_post(
        db_session, post.id, BlogPostInput(**{**VALID_INPUT, "slug": "keep-me", "title": "Đã sửa"})
    )
    assert updated is not None
    assert updated.title == "Đã sửa"
    assert updated.slug == "keep-me"


def test_update_blog_post_rejects_slug_taken_by_another_post(db_session):
    service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "post-a"}))
    post_b = service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "post-b"}))
    with pytest.raises(service.SlugAlreadyTakenError):
        service.update_blog_post(db_session, post_b.id, BlogPostInput(**{**VALID_INPUT, "slug": "post-a"}))


def test_update_blog_post_returns_none_when_missing(db_session):
    assert service.update_blog_post(db_session, 99999, BlogPostInput(**VALID_INPUT)) is None


def test_list_blog_posts_orders_by_published_at_desc(db_session):
    service.create_blog_post(
        db_session, BlogPostInput(**{**VALID_INPUT, "slug": "older", "publishedAt": "2026-01-01"})
    )
    service.create_blog_post(
        db_session, BlogPostInput(**{**VALID_INPUT, "slug": "newer", "publishedAt": "2026-06-01"})
    )
    posts = service.list_blog_posts(db_session)
    assert [post.slug for post in posts] == ["newer", "older"]


def test_get_blog_post_by_slug(db_session):
    service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "find-me"}))
    found = service.get_blog_post_by_slug(db_session, "find-me")
    assert found is not None
    assert found.slug == "find-me"


def test_get_blog_post_by_slug_returns_none_when_missing(db_session):
    assert service.get_blog_post_by_slug(db_session, "nope") is None


def test_delete_blog_post(db_session):
    post = service.create_blog_post(db_session, BlogPostInput(**{**VALID_INPUT, "slug": "to-delete"}))
    assert service.delete_blog_post(db_session, post.id) is True
    assert service.get_blog_post(db_session, post.id) is None


def test_delete_blog_post_returns_false_when_missing(db_session):
    assert service.delete_blog_post(db_session, 99999) is False


def test_blog_post_input_rejects_blank_title():
    with pytest.raises(ValidationError):
        BlogPostInput(**{**VALID_INPUT, "title": "   "})


def test_blog_post_input_rejects_invalid_category():
    with pytest.raises(ValidationError):
        BlogPostInput(**{**VALID_INPUT, "category": "not-a-real-category"})
