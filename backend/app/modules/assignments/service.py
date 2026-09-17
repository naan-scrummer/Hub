from typing import List, Optional
from datetime import datetime

from app.modules.assignments.models import Assignment, AssignmentStatus
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.service import ReminderService
from app.logging.config import get_logger


logger = get_logger(__name__)


class AssignmentService:
    def __init__(
        self,
        assignment_repo: AssignmentRepository,
        reminder_service: ReminderService,
    ):
        self.assignment_repo = assignment_repo
        self.reminder_service = reminder_service

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

        # Create automatic reminder 7 days before due date (SCRUM 32 spec)
        await self.reminder_service.create_automatic_reminder(
            student_id=student_id,
            entity_type="assignment",
            entity_id=assignment.id,
            event_time=due_date,
            title=f"Due soon: {title}",
        )

        logger.info("assignment_created", assignment_id=assignment.id, student_id=student_id)
        return assignment

    async def update(self, assignment: Assignment, old_due_date: Optional[datetime] = None) -> Assignment:
        if old_due_date is None:
            old_due_date = assignment.due_date
        assignment = await self.assignment_repo.update(assignment)

        # Update automatic reminders if due date shifted (SCRUM 32 spec)
        if assignment.due_date != old_due_date:
            await self.reminder_service.update_automatic_reminders_on_due_date_shift(
                student_id=assignment.student_id,
                entity_type="assignment",
                entity_id=assignment.id,
                new_event_time=assignment.due_date,
            )

        return assignment

    async def mark_completed(self, assignment_id: int, student_id: int) -> Optional[Assignment]:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.student_id != student_id:
            return None

        assignment.status = AssignmentStatus.COMPLETED
        assignment.completed_at = datetime.utcnow()
        assignment = await self.assignment_repo.update(assignment)

        # Cancel associated pending reminders (SCRUM 32 spec)
        await self.reminder_service.cancel_linked_reminders(
            student_id=student_id,
            entity_type="assignment",
            entity_id=assignment.id,
        )

        logger.info("assignment_completed", assignment_id=assignment.id, student_id=student_id)
        return assignment

    async def delete(self, assignment_id: int, student_id: int) -> bool:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.student_id != student_id:
            return False

        # Cancel associated reminders before deleting
        await self.reminder_service.cancel_linked_reminders(
            student_id=student_id,
            entity_type="assignment",
            entity_id=assignment.id,
        )

        await self.assignment_repo.delete(assignment)
        logger.info("assignment_deleted", assignment_id=assignment_id, student_id=student_id)
        return True

    def classify_status(self, assignment: Assignment) -> AssignmentStatus:
        if assignment.status == AssignmentStatus.COMPLETED:
            return AssignmentStatus.COMPLETED
        if assignment.due_date < datetime.utcnow():
            return AssignmentStatus.OVERDUE
        return AssignmentStatus.UPCOMING
