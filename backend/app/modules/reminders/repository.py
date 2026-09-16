from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reminders.models import Reminder, ReminderStatus, ReminderOrigin


class ReminderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, reminder_id: int) -> Optional[Reminder]:
        result = await self.session.execute(select(Reminder).where(Reminder.id == reminder_id))
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: int) -> List[Reminder]:
        result = await self.session.execute(
            select(Reminder).where(Reminder.student_id == student_id).order_by(Reminder.trigger_time)
        )
        return list(result.scalars().all())

    async def get_by_student_with_filter(
        self, student_id: int, status_filter: Optional[str] = None
    ) -> List[Reminder]:
        query = select(Reminder).where(Reminder.student_id == student_id)
        if status_filter:
            query = query.where(Reminder.status == status_filter)
        query = query.order_by(Reminder.trigger_time)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_student_and_id(
        self, student_id: int, reminder_id: int
    ) -> Optional[Reminder]:
        result = await self.session.execute(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.student_id == student_id,
            )
        )
        return result.scalar_one_or_none()

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

    async def delete(self, reminder: Reminder) -> None:
        await self.session.delete(reminder)
        await self.session.flush()

    async def cancel_by_entity(
        self,
        student_id: int,
        entity_type: str,
        entity_id: int,
    ) -> int:
        """Cancel all PENDING reminders linked to the given entity.
        Returns the number of reminders cancelled."""
        if entity_type == "assignment":
            col = Reminder.assignment_id
        elif entity_type == "examination":
            col = Reminder.examination_id
        else:
            return 0

        result = await self.session.execute(
            select(Reminder).where(
                Reminder.student_id == student_id,
                col == entity_id,
                Reminder.status == ReminderStatus.PENDING,
            )
        )
        reminders = list(result.scalars().all())
        now = datetime.utcnow()
        for reminder in reminders:
            reminder.status = ReminderStatus.CANCELLED
            reminder.processed_at = now
        await self.session.flush()
        return len(reminders)

    async def update_automatic_trigger_times(
        self,
        student_id: int,
        entity_type: str,
        entity_id: int,
        new_trigger_time: datetime,
    ) -> int:
        """Update trigger time for AUTOMATIC + PENDING reminders linked to an entity.
        Returns the number of reminders updated."""
        if entity_type == "assignment":
            col = Reminder.assignment_id
        elif entity_type == "examination":
            col = Reminder.examination_id
        else:
            return 0

        result = await self.session.execute(
            select(Reminder).where(
                Reminder.student_id == student_id,
                col == entity_id,
                Reminder.origin == ReminderOrigin.AUTOMATIC,
                Reminder.status == ReminderStatus.PENDING,
            )
        )
        reminders = list(result.scalars().all())
        for reminder in reminders:
            reminder.trigger_time = new_trigger_time
        await self.session.flush()
        return len(reminders)

    async def bulk_update_status(
        self, reminder_ids: List[int], status: ReminderStatus, processed_at: datetime
    ) -> int:
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
