from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.reminders.service import ReminderService
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.repository import NotificationRepository
from app.schemas.reminders import (
    ReminderCreateRequest,
    ReminderResponse,
    ReminderTriggerType,
    ReminderStatus,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/reminders", tags=["reminders"])
logger = get_logger(__name__)


def get_reminder_service(db: AsyncSession = Depends(get_db)) -> ReminderService:
    reminder_repo = ReminderRepository(db)
    notification_repo = NotificationRepository(db)
    return ReminderService(reminder_repo, notification_repo)


@router.get("", response_model=List[ReminderResponse])
async def get_reminders(
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    reminders = await reminder_service.get_by_student(profile.id)

    responses = []
    for r in reminders:
        responses.append(ReminderResponse(
            id=r.id,
            student_id=r.student_id,
            assignment_id=r.assignment_id,
            examination_id=r.examination_id,
            title=r.title,
            description=r.description,
            trigger_type=r.trigger_type,
            trigger_time=r.trigger_time,
            status=r.status,
            processed_at=r.processed_at,
            created_at=r.created_at,
            updated_at=r.updated_at,
        ))
    return responses


@router.post("", response_model=ReminderResponse)
async def create_reminder(
    request: ReminderCreateRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    reminder = await reminder_service.create(
        student_id=profile.id,
        title=request.title,
        trigger_time=request.trigger_time,
        description=request.description,
        trigger_type=request.trigger_type,
        assignment_id=request.assignment_id,
        examination_id=request.examination_id,
    )

    return ReminderResponse(
        id=reminder.id,
        student_id=reminder.student_id,
        assignment_id=reminder.assignment_id,
        examination_id=reminder.examination_id,
        title=reminder.title,
        description=reminder.description,
        trigger_type=reminder.trigger_type,
        trigger_time=reminder.trigger_time,
        status=reminder.status,
        processed_at=reminder.processed_at,
        created_at=reminder.created_at,
        updated_at=reminder.updated_at,
    )


@router.post("/process")
async def process_reminders(
    profile: StudentProfile = Depends(get_current_student_profile),
    reminder_service: ReminderService = Depends(get_reminder_service),
):
    from datetime import datetime
    processed = await reminder_service.process_due_reminders(datetime.utcnow())
    return {"message": f"Processed {processed} reminders"}