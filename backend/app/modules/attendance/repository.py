from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.models import Subject, AttendanceRecord


class SubjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Subject):
        return select(parameter)

    async def get_by_id(self, subject_id: int) -> Optional[Subject]:
        result = await self.session.execute(select(Subject).where(Subject.id == subject_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Subject]:
        result = await self.session.execute(select(Subject).where(Subject.code == code))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Subject]:
        result = await self.session.execute(select(Subject).order_by(Subject.code))
        return list(result.scalars().all())

    async def create(self, subject: Subject) -> Subject:
        self.session.add(subject)
        await self.session.flush()
        await self.session.refresh(subject)
        return subject

    async def bulk_create(self, subjects: List[Subject]) -> List[Subject]:
        self.session.add_all(subjects)
        await self.session.flush()
        for s in subjects:
            await self.session.refresh(s)
        return subjects


class AttendanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: AttendanceRecord):
        return select(parameter)

    async def get_by_id(self, record_id: int) -> Optional[AttendanceRecord]:
        result = await self.session.execute(select(AttendanceRecord).where(AttendanceRecord.id == record_id))
        return result.scalar_one_or_none()

    async def get_by_student_and_subject(self, student_id: int, subject_id: int) -> Optional[AttendanceRecord]:
        result = await self.session.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.subject_id == subject_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: int) -> List[AttendanceRecord]:
        result = await self.session.execute(
            select(AttendanceRecord).where(AttendanceRecord.student_id == student_id).order_by(AttendanceRecord.subject_id)
        )
        return list(result.scalars().all())

    async def create(self, record: AttendanceRecord) -> AttendanceRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def update(self, record: AttendanceRecord) -> AttendanceRecord:
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def bulk_upsert(self, records: List[AttendanceRecord]) -> List[AttendanceRecord]:
        processed_records = []
        for record in records:
            existing = await self.get_by_student_and_subject(record.student_id, record.subject_id)
            if existing:
                existing.classes_attended = record.classes_attended
                existing.total_classes = record.total_classes
                existing.attendance_percentage = record.attendance_percentage
                existing.last_synced_at = record.last_synced_at
                existing.source_sync_run_id = record.source_sync_run_id
                processed_records.append(existing)
            else:
                self.session.add(record)
                processed_records.append(record)
        await self.session.flush()
        for record in processed_records:
            await self.session.refresh(record)
        return processed_records

    async def get_summary_for_student(self, student_id: int) -> dict:
        result = await self.session.execute(
            select(
                func.sum(AttendanceRecord.classes_attended),
                func.sum(AttendanceRecord.total_classes),
                func.count(AttendanceRecord.id),
            ).where(AttendanceRecord.student_id == student_id)
        )
        total_attended, total_classes, subject_count = result.one()
        total_attended = total_attended or 0
        total_classes = total_classes or 0
        overall_percentage = (total_attended / total_classes * 100) if total_classes > 0 else 0.0
        return {
            "total_classes_attended": total_attended,
            "total_classes": total_classes,
            "overall_percentage": round(overall_percentage, 2),
            "subjects_count": subject_count or 0,
            "records": [],
        }

from datetime import date
from app.modules.attendance.models import DailyAttendance

class DailyAttendanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_student_and_date(self, student_id: int, date_val: date) -> Optional[DailyAttendance]:
        result = await self.session.execute(
            select(DailyAttendance).where(
                DailyAttendance.student_id == student_id,
                DailyAttendance.date == date_val
            )
        )
        return result.scalar_one_or_none()

    async def get_by_date(self, date_val: date) -> List[DailyAttendance]:
        result = await self.session.execute(
            select(DailyAttendance)
            .where(DailyAttendance.date == date_val)
        )
        return list(result.scalars().all())
        
    async def get_history_by_student(self, student_id: int) -> List[DailyAttendance]:
        result = await self.session.execute(
            select(DailyAttendance).where(
                DailyAttendance.student_id == student_id
            ).order_by(DailyAttendance.date.desc())
        )
        return list(result.scalars().all())
        
    async def get_summary_by_student(self, student_id: int) -> dict:
        history = await self.get_history_by_student(student_id)
        total_classes = len(history)
        present = sum(1 for r in history if r.status.value == "present")
        absent = total_classes - present
        percentage = (present / total_classes * 100) if total_classes > 0 else 0.0
        
        return {
            "total_classes": total_classes,
            "present": present,
            "absent": absent,
            "attendance_percentage": round(percentage, 2),
            "history": history
        }
        
    async def upsert(self, attendance: DailyAttendance) -> DailyAttendance:
        existing = await self.get_by_student_and_date(attendance.student_id, attendance.date)
        if existing:
            existing.status = attendance.status
            existing.teacher_id = attendance.teacher_id
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        else:
            self.session.add(attendance)
            await self.session.flush()
            await self.session.refresh(attendance)
            return attendance