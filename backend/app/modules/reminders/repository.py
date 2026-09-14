from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reminders.models import Reminder, ReminderStatus


class ReminderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Reminder):
        return select(parameter)

    async def get_by_id(self, reminder_id: int) -> Optional[Reminder]:
        result = await self.session.execute(select(Reminder).where(Reminder.id == reminder_id))
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: int) -> List[Reminder]:
        result = await self.session.execute(
            select(Reminder).where(Reminder.student_id == student_id).order_by(Reminder.trigger_time)
        )
        return list(result.scalars().all())

    async def get_pending_due(self, before_time: datetime) -> List[Reminder]:
        result = await self.session.execute(
            select(Reminder)
            .where(
                Reminder.status == ReminderStatus.PENDING,
                Reminder.trigger_time <= before_time,
            )
            .order_by(Reminder.trigger_time)
        )
        return list(result.scalars().all())

    async def get_by_assignment(self, assignment_id: int) -> List[Reminder]:
        result = await self.session.execute(
            select(Reminder).where(Reminder.assignment_id == assignment_id)
        )
        return list(result.scalars().all())

    async def get_by_examination(self, examination_id: int) -> List[Reminder]:
        result = await self.session.execute(
            select(Reminder).where(Reminder.examination_id == examination_id)
        )
        return list(result.scalars().all())

    async def create(self, reminder: Reminder) -> Reminder:
        self.session.add(reminder)
        await self.session.flush()
        await self.session.refresh(reminder)
        return reminder

    async def update(self, reminder: Reminder) -> Reminder:
        await self.session.flush()
        await self.session.refresh(reminder)
        return reminder

    async def bulk_update_status(self, reminder_ids: List[int], status: ReminderStatus, processed_at: datetime) -> int:
        if not reminder_ids:
            return 0
        result = await self.session.execute(
            select(Reminder).where(Reminder.id.in_(reminder_ids))
        )
        reminders = list(result.scalars().all())
        for reminder in reminders:
            reminder.status = status
            reminder.processed_at = processed_at
        await self.session.flush()
        return len(reminders)