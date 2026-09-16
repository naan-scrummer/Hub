from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.reminders.service import ReminderService
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.repository import NotificationRepository
from app.modules.assignments.repository import AssignmentRepository
from app.modules.examinations.repository import ExaminationRepository
from app.schemas.reminders import (
    ReminderCreateRequest,
    ReminderUpdateRequest,
    ReminderResponse,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/reminders", tags=["reminders"])
logger = get_logger(__name__)


def get_reminder_service(db: AsyncSession = Depends(get_db)) -> ReminderService:
    reminder_repo = ReminderRepository(db)
    notification_repo = NotificationRepository(db)
    return ReminderService(reminder_repo, notification_repo)


async def _enrich_reminder_response(
    reminder,
    assignment_repo: AssignmentRepository,
    exam_repo: ExaminationRepository,
) -> ReminderResponse:
    """Build a ReminderResponse with optional related entity titles."""
    assignment_title = None
    examination_title = None

    if reminder.assignment_id is not None:
        assignment = await assignment_repo.get_by_id(reminder.assignment_id)
        if assignment:
            assignment_title = assignment.title

    if reminder.examination_id is not None:
        exam = await exam_repo.get_by_id(reminder.examination_id)
        if exam:
            examination_title = exam.title

    return ReminderResponse(
        id=reminder.id,
        student_id=reminder.student_id,
        assignment_id=reminder.assignment_id,
        examination_id=reminder.examination_id,
        title=reminder.title,
        description=reminder.description,
        trigger_type=reminder.trigger_type,
        trigger_time=reminder.trigger_time,
        origin=reminder.origin,
        status=reminder.status,
        processed_at=reminder.processed_at,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at,
        assignment_title=assignment_title,
        examination_title=examination_title,
    )


# ------------------------------------------------------------------
# GET /api/v1/reminders — List all reminders (optional status filter)
# ------------------------------------------------------------------
@router.get("", response_model=List[ReminderResponse])
async def get_reminders(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, PROCESSED, CANCELLED"),
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
    db: AsyncSession = Depends(get_db),
):
    # Normalize status filter — enum values are lowercase
    status_filter = status.lower() if status else None

    reminders = await reminder_service.get_student_reminders(
        profile.id, status_filter=status_filter
    )

    assignment_repo = AssignmentRepository(db)
    exam_repo = ExaminationRepository(db)

    responses = []
    for r in reminders:
        responses.append(await _enrich_reminder_response(r, assignment_repo, exam_repo))
    return responses


# ------------------------------------------------------------------
# GET /api/v1/reminders/{reminder_id} — Fetch specific reminder
# ------------------------------------------------------------------
@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
    db: AsyncSession = Depends(get_db),
):
    reminder = await reminder_service.reminder_repo.get_by_student_and_id(
        profile.id, reminder_id
    )
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")

    assignment_repo = AssignmentRepository(db)
    exam_repo = ExaminationRepository(db)
    return await _enrich_reminder_response(reminder, assignment_repo, exam_repo)


# ------------------------------------------------------------------
# POST /api/v1/reminders — Create custom reminder
# ------------------------------------------------------------------
@router.post("", response_model=ReminderResponse, status_code=201)
async def create_reminder(
    request: ReminderCreateRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
    db: AsyncSession = Depends(get_db),
):
    try:
        reminder = await reminder_service.create_reminder(profile.id, request)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    assignment_repo = AssignmentRepository(db)
    exam_repo = ExaminationRepository(db)
    return await _enrich_reminder_response(reminder, assignment_repo, exam_repo)


# ------------------------------------------------------------------
# PATCH /api/v1/reminders/{reminder_id} — Update reminder
# ------------------------------------------------------------------
@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    request: ReminderUpdateRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
    db: AsyncSession = Depends(get_db),
):
    reminder = await reminder_service.update_reminder(profile.id, reminder_id, request)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")

    assignment_repo = AssignmentRepository(db)
    exam_repo = ExaminationRepository(db)
    return await _enrich_reminder_response(reminder, assignment_repo, exam_repo)


# ------------------------------------------------------------------
# DELETE /api/v1/reminders/{reminder_id} — Delete reminder
# ------------------------------------------------------------------
@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    deleted = await reminder_service.delete_reminder(profile.id, reminder_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return None


# ------------------------------------------------------------------
# POST /api/v1/reminders/process — Dev/Demo manual processing trigger
# ------------------------------------------------------------------
@router.post("/process")
async def process_reminders(
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    from datetime import datetime

    processed = await reminder_service.process_due_reminders(datetime.utcnow())
    return {"message": f"Processed {processed} reminders"}
