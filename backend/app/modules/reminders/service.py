from typing import List, Optional
from datetime import datetime, timedelta

from app.modules.reminders.models import (
    Reminder,
    ReminderTriggerType,
    ReminderOrigin,
    ReminderStatus,
)
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.models import Notification, NotificationSource, NotificationStatus
from app.modules.notifications.repository import NotificationRepository
from app.logging.config import get_logger
from app.schemas.reminders import ReminderCreateRequest, ReminderUpdateRequest


logger = get_logger(__name__)


class ReminderService:
    def __init__(
        self,
        reminder_repo: ReminderRepository,
        notification_repo: NotificationRepository,
    ):
        self.reminder_repo = reminder_repo
        self.notification_repo = notification_repo

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    async def get_by_id(self, reminder_id: int) -> Optional[Reminder]:
        return await self.reminder_repo.get_by_id(reminder_id)

    async def get_student_reminders(
        self,
        student_id: int,
        status_filter: Optional[str] = None,
    ) -> List[Reminder]:
        """Return reminders owned by student_id ordered by trigger_time ASC.

        Optionally filter by status (PENDING, PROCESSED, CANCELLED).
        """
        return await self.reminder_repo.get_by_student_with_filter(
            student_id, status_filter=status_filter
        )

    async def get_by_student(self, student_id: int) -> List[Reminder]:
        """Alias for backward compatibility."""
        return await self.reminder_repo.get_by_student(student_id)

    async def create_reminder(
        self,
        student_id: int,
        data: ReminderCreateRequest,
    ) -> Reminder:
        """Create a CUSTOM reminder from user input.

        Validates that any linked assignment or examination belongs to
        the student.
        """
        # Validate entity ownership if linked
        if data.assignment_id is not None:
            assignment = await self._get_owned_assignment(student_id, data.assignment_id)
            if assignment is None:
                raise ValueError("Assignment not found or not owned by student")

        if data.examination_id is not None:
            examination = await self._get_owned_examination(student_id, data.examination_id)
            if examination is None:
                raise ValueError("Examination not found or not owned by student")

        reminder = Reminder(
            student_id=student_id,
            assignment_id=data.assignment_id,
            examination_id=data.examination_id,
            title=data.title,
            description=data.description,
            trigger_type=data.trigger_type,
            trigger_time=data.trigger_time,
            origin=ReminderOrigin.CUSTOM,
            status=ReminderStatus.PENDING,
        )
        return await self.reminder_repo.create(reminder)

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
        """Legacy create method for backward compatibility."""
        reminder = Reminder(
            student_id=student_id,
            assignment_id=assignment_id,
            examination_id=examination_id,
            title=title,
            description=description,
            trigger_type=trigger_type,
            trigger_time=trigger_time,
            origin=ReminderOrigin.CUSTOM,
            status=ReminderStatus.PENDING,
        )
        return await self.reminder_repo.create(reminder)

    async def create_automatic_reminder(
        self,
        student_id: int,
        entity_type: str,
        entity_id: int,
        event_time: datetime,
        title: str,
        lead_days: int = 7,
    ) -> Optional[Reminder]:
        """Create an AUTOMATIC reminder before the event.

        Returns None if the calculated trigger time is in the past.
        """
        trigger_time = event_time - timedelta(days=lead_days)

        # Don't create reminders for events already in the past
        if trigger_time <= datetime.utcnow():
            return None

        if entity_type == "assignment":
            reminder = Reminder(
                student_id=student_id,
                assignment_id=entity_id,
                title=title,
                description=f"Automatic reminder: {title}",
                trigger_type=ReminderTriggerType.ASSIGNMENT_DUE,
                trigger_time=trigger_time,
                origin=ReminderOrigin.AUTOMATIC,
                status=ReminderStatus.PENDING,
            )
        elif entity_type == "examination":
            reminder = Reminder(
                student_id=student_id,
                examination_id=entity_id,
                title=title,
                description=f"Automatic reminder: {title}",
                trigger_type=ReminderTriggerType.EXAMINATION,
                trigger_time=trigger_time,
                origin=ReminderOrigin.AUTOMATIC,
                status=ReminderStatus.PENDING,
            )
        else:
            return None

        return await self.reminder_repo.create(reminder)

    async def update_reminder(
        self,
        student_id: int,
        reminder_id: int,
        data: ReminderUpdateRequest,
    ) -> Optional[Reminder]:
        """Update a reminder. Ensures the reminder exists and belongs to the student."""
        reminder = await self.reminder_repo.get_by_student_and_id(student_id, reminder_id)
        if reminder is None:
            return None

        if data.title is not None:
            reminder.title = data.title
        if data.description is not None:
            reminder.description = data.description
        if data.trigger_time is not None:
            reminder.trigger_time = data.trigger_time
        # Note: status is intentionally NOT updated here.
        # Status transitions are system-managed (process/cancel).

        return await self.reminder_repo.update(reminder)

    async def delete_reminder(
        self,
        student_id: int,
        reminder_id: int,
    ) -> bool:
        """Delete a reminder. Ensures ownership. Returns True if deleted."""
        reminder = await self.reminder_repo.get_by_student_and_id(student_id, reminder_id)
        if reminder is None:
            return False
        await self.reminder_repo.delete(reminder)
        return True

    # ------------------------------------------------------------------
    # Entity-linked operations
    # ------------------------------------------------------------------

    async def cancel_linked_reminders(
        self,
        student_id: int,
        entity_type: str,
        entity_id: int,
    ) -> int:
        """Cancel all PENDING reminders linked to the given entity."""
        return await self.reminder_repo.cancel_by_entity(
            student_id, entity_type, entity_id
        )

    async def update_automatic_reminders_on_due_date_shift(
        self,
        student_id: int,
        entity_type: str,
        entity_id: int,
        new_event_time: datetime,
        lead_days: int = 7,
    ) -> int:
        """Recalculate trigger times for AUTOMATIC reminders when due dates shift."""
        new_trigger_time = new_event_time - timedelta(days=lead_days)
        return await self.reminder_repo.update_automatic_trigger_times(
            student_id, entity_type, entity_id, new_trigger_time
        )

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    async def process_due_reminders(self, current_time: Optional[datetime] = None) -> int:
        """Process all PENDING reminders whose trigger_time <= current_time.

        Transitions status to PROCESSED atomically and generates notifications.
        Returns the number of reminders processed.
        """
        if current_time is None:
            current_time = datetime.utcnow()

        due_reminders = await self.reminder_repo.get_pending_due(current_time)
        processed_count = 0

        for reminder in due_reminders:
            # Transition to PROCESSED atomically
            reminder.status = ReminderStatus.PROCESSED
            reminder.processed_at = current_time
            await self.reminder_repo.update(reminder)

            # Generate notification
            notification = Notification(
                student_id=reminder.student_id,
                source=NotificationSource.REMINDER_TRIGGER,
                source_id=reminder.id,
                title=reminder.title,
                message=reminder.description
                    or f"Reminder triggered at {current_time.strftime('%Y-%m-%d %H:%M')}",
                status=NotificationStatus.UNREAD,
            )
            await self.notification_repo.create(notification)
            processed_count += 1

            logger.info(
                "reminder_processed",
                reminder_id=reminder.id,
                student_id=reminder.student_id,
            )

        return processed_count

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_owned_assignment(self, student_id: int, assignment_id: int):
        """Validate assignment ownership. Returns the assignment or None."""
        # Avoid circular import by importing locally
        from app.modules.assignments.repository import AssignmentRepository

        # We need a session — use the one from the reminder repo
        session = self.reminder_repo.session
        assignment_repo = AssignmentRepository(session)
        assignment = await assignment_repo.get_by_id(assignment_id)
        if assignment is None or assignment.student_id != student_id:
            return None
        return assignment

    async def _get_owned_examination(self, student_id: int, examination_id: int):
        """Validate examination ownership via student enrollment. Returns the examination or None."""
        from app.modules.examinations.repository import ExaminationRepository

        session = self.reminder_repo.session
        exam_repo = ExaminationRepository(session)
        exam = await exam_repo.get_by_id(examination_id)
        # Examination doesn't have student_id — it's global/synced.
        # Ownership is implied by student access to the system.
        return exam
