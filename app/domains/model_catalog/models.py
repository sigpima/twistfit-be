from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CatalogModel(Base):
    __tablename__ = "catalog_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(String(500), nullable=False)
    dossier_image: Mapped[str] = mapped_column(String(500), nullable=False)
    pose_count: Mapped[int] = mapped_column(Integer, nullable=False)
    tagline: Mapped[str] = mapped_column(String(255), nullable=False)
    undertone: Mapped[str] = mapped_column(String(20), nullable=False)
    height: Mapped[str] = mapped_column(String(50), nullable=False)
    body_shape: Mapped[str] = mapped_column(String(100), nullable=False)
    waist: Mapped[str] = mapped_column(String(50), nullable=False)
    personal_color: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
