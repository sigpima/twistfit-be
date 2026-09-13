from pydantic import Field

from app.domains.auth.schemas import CamelModel


class CountStats(CamelModel):
    total: int
    new_30d: int = Field(alias="new30d")


class ContactStats(CamelModel):
    total: int
    unread: int


class AdminStatsResponse(CamelModel):
    blog_posts: CountStats
    forum_posts: CountStats
    users: CountStats
    quiz_attempts: CountStats
    contact_messages: ContactStats
