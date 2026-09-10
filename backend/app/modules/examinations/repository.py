from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.examinations.models import Examination


class ExaminationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, exam_id: int) -> Optional[Examination]:
        result = await self.session.execute(select(Examination).where(Examination.id == exam_id))
        return result.scalar_one_or_none()

    async def get_upcoming_for_student(self, student_id: int, subject_ids: List[int]) -> List[Examination]:
        result = await self.session.execute(
            select(Examination)
            .where(
                Examination.subject_id.in_(subject_ids),
                Examination.exam_date >= datetime.utcnow(),
            )
            .order_by(Examination.exam_date)
        )
        return list(result.scalars().all())

    async def get_all_for_subjects(self, subject_ids: List[int]) -> List[Examination]:
        result = await self.session.execute(
            select(Examination).where(Examination.subject_id.in_(subject_ids)).order_by(Examination.exam_date)
        )
        return list(result.scalars().all())

    async def create(self, exam: Examination) -> Examination:
        self.session.add(exam)
        await self.session.flush()
        await self.session.refresh(exam)
        return exam

    async def bulk_upsert(self, exams: List[Examination]) -> List[Examination]:
        for exam in exams:
            existing = await self.get_by_id(exam.id) if exam.id else None
            if existing:
                existing.title = exam.title
                existing.exam_type = exam.exam_type
                existing.exam_date = exam.exam_date
                existing.start_time = exam.start_time
                existing.end_time = exam.end_time
                existing.venue = exam.venue
                existing.description = exam.description
                existing.last_synced_at = exam.last_synced_at
                existing.source_sync_run_id = exam.source_sync_run_id
            else:
                self.session.add(exam)
        await self.session.flush()
        for exam in exams:
            await self.session.refresh(exam)
        return exams