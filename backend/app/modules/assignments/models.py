import enum
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AssignmentStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    OVERDUE = "overdue"
    COMPLETED = "completed"


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[AssignmentStatus] = mapped_column(default=AssignmentStatus.UPCOMING, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_assignments_due_date_status", "due_date", "status"),
    )

    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="assignments")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="assignments")
    reminders: Mapped[list["Reminder"]] = relationship("Reminder", back_populates="assignment")


class CodingAssignment(Base):
    __tablename__ = "coding_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), default="Medium")
    allowed_languages: Mapped[str] = mapped_column(String(200), default="C,C++,Java,Python") # Comma separated
    input_format: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_format: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_limit: Mapped[float] = mapped_column(default=1.0) # In seconds
    memory_limit: Mapped[int] = mapped_column(default=128) # In MB
    max_points: Mapped[int] = mapped_column(default=100)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    test_cases: Mapped[list["TestCase"]] = relationship("TestCase", back_populates="assignment", cascade="all, delete-orphan")
    submissions: Mapped[list["CodingSubmission"]] = relationship("CodingSubmission", back_populates="assignment", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("coding_assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    input_data: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(default=10)
    order_index: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    assignment: Mapped["CodingAssignment"] = relationship("CodingAssignment", back_populates="test_cases")


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("coding_assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. ACCEPTED, WRONG_ANSWER, COMPILATION_ERROR
    execution_time: Mapped[float | None] = mapped_column(nullable=True)
    passed_tests: Mapped[int] = mapped_column(default=0)
    total_tests: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    assignment: Mapped["CodingAssignment"] = relationship("CodingAssignment", back_populates="submissions")
    test_results: Mapped[list["SubmissionTestResult"]] = relationship("SubmissionTestResult", back_populates="submission", cascade="all, delete-orphan")


class SubmissionTestResult(Base):
    __tablename__ = "submission_test_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("coding_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id: Mapped[int] = mapped_column(ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    actual_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time: Mapped[float | None] = mapped_column(nullable=True)
    points_awarded: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    submission: Mapped["CodingSubmission"] = relationship("CodingSubmission", back_populates="test_results")