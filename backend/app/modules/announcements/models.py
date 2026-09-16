from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnnouncementSource(Base):
    __tablename__ = "announcement_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    announcements: Mapped[list["Announcement"]] = relationship("Announcement", back_populates="source")


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("announcement_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    source_reference: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    source_sync_run_id: Mapped[int | None] = mapped_column(ForeignKey("sync_runs.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_announcements_published_at_desc", "published_at"),
    )

    source: Mapped["AnnouncementSource"] = relationship("AnnouncementSource", back_populates="announcements")
    sync_run: Mapped["SyncRun | None"] = relationship("SyncRun")