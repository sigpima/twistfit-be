from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    sub_season: Mapped[str] = mapped_column(String(30), nullable=False)
    parent_season: Mapped[str] = mapped_column(String(20), nullable=False)
    hue_result: Mapped[str] = mapped_column(String(20), nullable=False)
    value_result: Mapped[str] = mapped_column(String(20), nullable=False)
    chroma_result: Mapped[str] = mapped_column(String(20), nullable=False)
    hue_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chroma_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
