from typing import List, Optional
from datetime import datetime

from app.modules.attendance.models import Subject, AttendanceRecord
from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class AttendanceService:
    def __init__(
        self,
        subject_repo: SubjectRepository,
        attendance_repo: AttendanceRepository,
    ):
        self.subject_repo = subject_repo
        self.attendance_repo = attendance_repo

    async def get_subjects(self) -> List[Subject]:
        return await self.subject_repo.get_all()

    async def get_student_attendance(self, student_id: int) -> List[AttendanceRecord]:
        return await self.attendance_repo.get_by_student(student_id)

    async def get_attendance_summary(self, student_id: int) -> dict:
        return await self.attendance_repo.get_summary_for_student(student_id)

    async def get_subject_attendance(self, student_id: int, subject_id: int) -> Optional[AttendanceRecord]:
        return await self.attendance_repo.get_by_student_and_subject(student_id, subject_id)

    async def upsert_attendance_records(self, records: List[AttendanceRecord]) -> List[AttendanceRecord]:
        return await self.attendance_repo.bulk_upsert(records)

    def calculate_percentage(self, attended: int, total: int) -> float:
        if total == 0:
            return 0.0
        return round((attended / total) * 100, 2)

    def create_attendance_record(
        self,
        student_id: int,
        subject_id: int,
        classes_attended: int,
        total_classes: int,
        sync_run_id: Optional[int] = None,
    ) -> AttendanceRecord:
        percentage = self.calculate_percentage(classes_attended, total_classes)
        return AttendanceRecord(
            student_id=student_id,
            subject_id=subject_id,
            classes_attended=classes_attended,
            total_classes=total_classes,
            attendance_percentage=percentage,
            last_synced_at=datetime.utcnow(),
            source_sync_run_id=sync_run_id,
        )