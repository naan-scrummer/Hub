from typing import List, Optional
from datetime import datetime

from app.modules.assignments.models import Assignment, AssignmentStatus
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.models import Reminder, ReminderTriggerType, ReminderStatus
from app.modules.reminders.repository import ReminderRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class AssignmentService:
    def __init__(
        self,
        assignment_repo: AssignmentRepository,
        reminder_repo: ReminderRepository,
    ):
        self.assignment_repo = assignment_repo
        self.reminder_repo = reminder_repo

    async def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        return await self.assignment_repo.get_by_id(assignment_id)

    async def get_by_student(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_by_student(student_id)

    async def get_upcoming(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_upcoming(student_id)

    async def get_overdue(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_overdue(student_id)

    async def get_completed(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_completed(student_id)

    async def get_by_subject(self, student_id: int, subject_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_by_subject(student_id, subject_id)

    async def create(
        self,
        student_id: int,
        subject_id: int,
        title: str,
        description: Optional[str],
        due_date: datetime,
    ) -> Assignment:
        assignment = Assignment(
            student_id=student_id,
            subject_id=subject_id,
            title=title,
            description=description,
            due_date=due_date,
            status=AssignmentStatus.UPCOMING,
        )
        assignment = await self.assignment_repo.create(assignment)

        # Create associated reminder (1 day before due date)
        from datetime import timedelta
        trigger_time = due_date - timedelta(days=1)
        if trigger_time > datetime.utcnow():
            reminder = Reminder(
                student_id=student_id,
                assignment_id=assignment.id,
                title=f"Assignment due: {title}",
                description=f"Reminder for assignment '{title}' due on {due_date.strftime('%Y-%m-%d %H:%M')}",
                trigger_type=ReminderTriggerType.ASSIGNMENT_DUE,
                trigger_time=trigger_time,
                status=ReminderStatus.PENDING,
            )
            await self.reminder_repo.create(reminder)

        logger.info("assignment_created", assignment_id=assignment.id, student_id=student_id)
        return assignment

    async def update(self, assignment: Assignment) -> Assignment:
        old_due_date = assignment.due_date
        assignment = await self.assignment_repo.update(assignment)

        # Update associated reminder if due date changed
        if assignment.due_date != old_due_date:
            reminders = await self.reminder_repo.get_by_assignment(assignment.id)
            from datetime import timedelta
            new_trigger_time = assignment.due_date - timedelta(days=1)
            for reminder in reminders:
                if reminder.status == ReminderStatus.PENDING and new_trigger_time > datetime.utcnow():
                    reminder.trigger_time = new_trigger_time
                    reminder.description = f"Reminder for assignment '{assignment.title}' due on {assignment.due_date.strftime('%Y-%m-%d %H:%M')}"
                    await self.reminder_repo.update(reminder)

        return assignment

    async def mark_completed(self, assignment_id: int, student_id: int) -> Optional[Assignment]:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.student_id != student_id:
            return None

        assignment.status = AssignmentStatus.COMPLETED
        assignment.completed_at = datetime.utcnow()
        assignment = await self.assignment_repo.update(assignment)

        # Cancel associated pending reminders
        reminders = await self.reminder_repo.get_by_assignment(assignment.id)
        for reminder in reminders:
            if reminder.status == ReminderStatus.PENDING:
                reminder.status = ReminderStatus.CANCELLED
                reminder.processed_at = datetime.utcnow()
                await self.reminder_repo.update(reminder)

        logger.info("assignment_completed", assignment_id=assignment.id, student_id=student_id)
        return assignment

    async def delete(self, assignment_id: int, student_id: int) -> bool:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.student_id != student_id:
            return False

        # Delete associated reminders
        reminders = await self.reminder_repo.get_by_assignment(assignment.id)
        for reminder in reminders:
            await self.reminder_repo.delete(reminder)

        await self.assignment_repo.delete(assignment)
        logger.info("assignment_deleted", assignment_id=assignment_id, student_id=student_id)
        return True

    def classify_status(self, assignment: Assignment) -> AssignmentStatus:
        if assignment.status == AssignmentStatus.COMPLETED:
            return AssignmentStatus.COMPLETED
        if assignment.due_date < datetime.utcnow():
            return AssignmentStatus.OVERDUE
        return AssignmentStatus.UPCOMING