import enum
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReminderTriggerType(str, enum.Enum):
    ASSIGNMENT_DUE = "assignment_due"
    EXAMINATION = "examination"
    CUSTOM = "custom"


class ReminderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    assignment_id: Mapped[int | None] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), nullable=True, index=True)
    examination_id: Mapped[int | None] = mapped_column(ForeignKey("examinations.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[ReminderTriggerType] = mapped_column(default=ReminderTriggerType.CUSTOM, nullable=False)
    trigger_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[ReminderStatus] = mapped_column(default=ReminderStatus.PENDING, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_reminders_trigger_time_status", "trigger_time", "status"),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="reminders")
    assignment: Mapped["Assignment | None"] = relationship("Assignment", back_populates="reminders")
    examination: Mapped["Examination | None"] = relationship("Examination")