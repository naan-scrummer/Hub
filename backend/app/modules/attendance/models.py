from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    credits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    attendances: Mapped[list["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="subject")
    academic_records: Mapped[list["AcademicRecord"]] = relationship("AcademicRecord", back_populates="subject")
    assignments: Mapped[list["Assignment"]] = relationship("Assignment", back_populates="subject")
    study_materials: Mapped[list["StudyMaterial"]] = relationship("StudyMaterial", back_populates="subject")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    classes_attended: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_classes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attendance_percentage: Mapped[float] = mapped_column(default=0.0, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_sync_run_id: Mapped[int | None] = mapped_column(ForeignKey("sync_runs.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_student_subject_attendance"),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="attendances")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="attendances")
    sync_run: Mapped["SyncRun | None"] = relationship("SyncRun")


import enum
import datetime as dt
from sqlalchemy import Enum, Date

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"

class DailyAttendance(Base):
    __tablename__ = "daily_attendances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_student_date_attendance"),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile")
    teacher: Mapped["User"] = relationship("User")