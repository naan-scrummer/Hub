from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assignments.models import Assignment, AssignmentStatus


class AssignmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Assignment):
        return select(parameter)

    async def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        result = await self.session.execute(select(Assignment).where(Assignment.id == assignment_id))
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment).where(Assignment.student_id == student_id).order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def get_upcoming(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                Assignment.student_id == student_id,
                Assignment.due_date >= datetime.utcnow(),
                Assignment.status != AssignmentStatus.COMPLETED,
            )
            .order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def get_overdue(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                Assignment.student_id == student_id,
                Assignment.due_date < datetime.utcnow(),
                Assignment.status != AssignmentStatus.COMPLETED,
            )
            .order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def get_completed(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                Assignment.student_id == student_id,
                Assignment.status == AssignmentStatus.COMPLETED,
            )
            .order_by(Assignment.completed_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def get_by_subject(self, student_id: int, subject_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                Assignment.student_id == student_id,
                Assignment.subject_id == subject_id,
            )
            .order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def create(self, assignment: Assignment) -> Assignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def update(self, assignment: Assignment) -> Assignment:
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def delete(self, assignment: Assignment) -> None:
        await self.session.delete(assignment)
        await self.session.flush()