from typing import List, Optional
from datetime import datetime

from app.modules.reminders.models import Reminder, ReminderTriggerType, ReminderStatus
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.models import Notification, NotificationSource
from app.modules.notifications.repository import NotificationRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class ReminderService:
    def __init__(
        self,
        reminder_repo: ReminderRepository,
        notification_repo: NotificationRepository,
    ):
        self.reminder_repo = reminder_repo
        self.notification_repo = notification_repo

    async def get_by_id(self, reminder_id: int) -> Optional[Reminder]:
        return await self.reminder_repo.get_by_id(reminder_id)

    async def get_by_student(self, student_id: int) -> List[Reminder]:
        return await self.reminder_repo.get_by_student(student_id)

    async def get_pending_due(self, before_time: datetime) -> List[Reminder]:
        return await self.reminder_repo.get_pending_due(before_time)

    async def create(
        self,
        student_id: int,
        title: str,
        trigger_time: datetime,
        description: Optional[str] = None,
        trigger_type: ReminderTriggerType = ReminderTriggerType.CUSTOM,
        assignment_id: Optional[int] = None,
        examination_id: Optional[int] = None,
    ) -> Reminder:
        reminder = Reminder(
            student_id=student_id,
            assignment_id=assignment_id,
            examination_id=examination_id,
            title=title,
            description=description,
            trigger_type=trigger_type,
            trigger_time=trigger_time,
            status=ReminderStatus.PENDING,
        )
        return await self.reminder_repo.create(reminder)

    async def process_due_reminders(self, current_time: datetime) -> int:
        due_reminders = await self.reminder_repo.get_pending_due(current_time)
        processed_count = 0

        for reminder in due_reminders:
            reminder.status = ReminderStatus.PROCESSED
            reminder.processed_at = current_time
            await self.reminder_repo.update(reminder)

            # Generate notification
            notification = Notification(
                student_id=reminder.student_id,
                source=NotificationSource.REMINDER_TRIGGER,
                source_id=reminder.id,
                title=reminder.title,
                message=reminder.description or f"Reminder triggered at {current_time.strftime('%Y-%m-%d %H:%M')}",
                status=NotificationStatus.UNREAD,
            )
            await self.notification_repo.create(notification)
            processed_count += 1

            logger.info("reminder_processed", reminder_id=reminder.id, student_id=reminder.student_id)

        return processed_count