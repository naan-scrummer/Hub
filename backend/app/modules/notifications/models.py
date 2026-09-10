import enum
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NotificationSource(str, enum.Enum):
    ASSIGNMENT_DEADLINE = "assignment_deadline"
    REMINDER_TRIGGER = "reminder_trigger"
    ANNOUNCEMENT = "announcement"
    EXAMINATION = "examination"
    PLACEMENT = "placement"


class NotificationStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    source: Mapped[NotificationSource] = mapped_column(nullable=False, index=True)
    source_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(default=NotificationStatus.UNREAD, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index("ix_notifications_student_status_created", "student_id", "status", "created_at"),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="notifications")