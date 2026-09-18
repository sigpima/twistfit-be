from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TryOnJob(Base):
    __tablename__ = "tryon_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    wardrobe_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("wardrobe_items.id", ondelete="SET NULL"), nullable=True
    )
    catalog_model_id: Mapped[int] = mapped_column(Integer, nullable=False)
    occasion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    result_front_blob_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    result_side_blob_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    items: Mapped[list["TryOnJobItem"]] = relationship(order_by="TryOnJobItem.sort_order")


class TryOnJobItem(Base):
    """One wardrobe item applied as part of a job's outfit combo, in the
    order it was applied (a áo khoác, if present, is always last)."""

    __tablename__ = "tryon_job_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    tryon_job_id: Mapped[int] = mapped_column(
        ForeignKey("tryon_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    wardrobe_item_id: Mapped[int] = mapped_column(
        ForeignKey("wardrobe_items.id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
