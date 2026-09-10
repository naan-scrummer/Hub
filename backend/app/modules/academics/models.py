from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    internal_marks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_internal_marks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    external_marks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_external_marks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_marks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_sync_run_id: Mapped[int | None] = mapped_column(ForeignKey("sync_runs.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "semester", name="uq_student_subject_semester_academic"),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="academic_records")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="academic_records")
    sync_run: Mapped["SyncRun | None"] = relationship("SyncRun")