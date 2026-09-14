from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.academics.models import AcademicRecord


class AcademicRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: AcademicRecord):
        return select(parameter)

    async def get_by_id(self, record_id: int) -> Optional[AcademicRecord]:
        result = await self.session.execute(select(AcademicRecord).where(AcademicRecord.id == record_id))
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: int) -> List[AcademicRecord]:
        result = await self.session.execute(
            select(AcademicRecord).where(AcademicRecord.student_id == student_id).order_by(AcademicRecord.semester.desc())
        )
        return list(result.scalars().all())

    async def get_by_student_and_subject(self, student_id: int, subject_id: int, semester: int) -> Optional[AcademicRecord]:
        result = await self.session.execute(
            select(AcademicRecord).where(
                AcademicRecord.student_id == student_id,
                AcademicRecord.subject_id == subject_id,
                AcademicRecord.semester == semester,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_student_and_semester(self, student_id: int, semester: int) -> List[AcademicRecord]:
        result = await self.session.execute(
            select(AcademicRecord).where(
                AcademicRecord.student_id == student_id,
                AcademicRecord.semester == semester,
            ).order_by(AcademicRecord.subject_id)
        )
        return list(result.scalars().all())

    async def create(self, record: AcademicRecord) -> AcademicRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def update(self, record: AcademicRecord) -> AcademicRecord:
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def bulk_upsert(self, records: List[AcademicRecord]) -> List[AcademicRecord]:
        for record in records:
            existing = await self.get_by_student_and_subject(record.student_id, record.subject_id, record.semester)
            if existing:
                existing.internal_marks = record.internal_marks
                existing.max_internal_marks = record.max_internal_marks
                existing.external_marks = record.external_marks
                existing.max_external_marks = record.max_external_marks
                existing.total_marks = record.total_marks
                existing.grade = record.grade
                existing.last_synced_at = record.last_synced_at
                existing.source_sync_run_id = record.source_sync_run_id
            else:
                self.session.add(record)
        await self.session.flush()
        for record in records:
            await self.session.refresh(record)
        return records