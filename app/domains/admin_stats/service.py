from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.domains.admin_stats.schemas import AdminStatsResponse, ContactStats, CountStats
from app.domains.auth.models import User
from app.domains.blog.models import BlogPost
from app.domains.contact.models import ContactMessage
from app.domains.forum.models import ForumPost
from app.domains.quiz_attempts.models import QuizAttempt


def get_admin_stats(db: Session) -> AdminStatsResponse:
    since = datetime.now(timezone.utc) - timedelta(days=30)

    return AdminStatsResponse(
        blog_posts=CountStats(
            total=db.query(BlogPost).count(),
            new_30d=db.query(BlogPost).filter(BlogPost.created_at >= since).count(),
        ),
        forum_posts=CountStats(
            total=db.query(ForumPost).count(),
            new_30d=db.query(ForumPost).filter(ForumPost.created_at >= since).count(),
        ),
        users=CountStats(
            total=db.query(User).count(),
            new_30d=db.query(User).filter(User.created_at >= since).count(),
        ),
        quiz_attempts=CountStats(
            total=db.query(QuizAttempt).count(),
            new_30d=db.query(QuizAttempt).filter(QuizAttempt.created_at >= since).count(),
        ),
        contact_messages=ContactStats(
            total=db.query(ContactMessage).count(),
            unread=db.query(ContactMessage).filter(ContactMessage.is_read.is_(False)).count(),
        ),
    )
