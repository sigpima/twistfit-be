from app.domains.blog.models import BlogPost
from app.domains.blog.seed import seed_demo_blog_posts


def test_seed_demo_blog_posts_creates_eight_posts(db_session):
    seed_demo_blog_posts(db_session)
    posts = db_session.query(BlogPost).all()
    assert len(posts) == 8
    slugs = {post.slug for post in posts}
    assert "chon-trang-phuc-theo-dang-nguoi" in slugs


def test_seed_demo_blog_posts_is_idempotent(db_session):
    seed_demo_blog_posts(db_session)
    seed_demo_blog_posts(db_session)
    assert db_session.query(BlogPost).count() == 8
