from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.notifications.service import NotificationService
from app.modules.notifications.repository import NotificationRepository
from app.schemas.notifications import (
    NotificationResponse,
    NotificationListResponse,
    NotificationStatus,
    NotificationSource,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = get_logger(__name__)


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    notification_repo = NotificationRepository(db)
    return NotificationService(notification_repo)


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    status: Optional[NotificationStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    profile: StudentProfile = Depends(get_current_student_profile),
    notification_service: NotificationService = Depends(get_notification_service),
):
    notifications = await notification_service.get_student_notifications(
        profile.id, status, limit, offset
    )
    unread_count = await notification_service.get_unread_count(profile.id)

    responses = []
    for n in notifications:
        responses.append(NotificationResponse(
            id=n.id,
            student_id=n.student_id,
            source=n.source,
            source_id=n.source_id,
            title=n.title,
            message=n.message,
            status=n.status,
            read_at=n.read_at,
            created_at=n.created_at,
        ))

    return NotificationListResponse(
        notifications=responses,
        unread_count=unread_count,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    notification_service: NotificationService = Depends(get_notification_service),
):
    notification = await notification_service.mark_as_read(notification_id, profile.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationResponse(
        id=notification.id,
        student_id=notification.student_id,
        source=notification.source,
        source_id=notification.source_id,
        title=notification.title,
        message=notification.message,
        status=notification.status,
        read_at=notification.read_at,
        created_at=notification.created_at,
    )


@router.post("/read-all")
async def mark_all_read(
    profile: StudentProfile = Depends(get_current_student_profile),
    notification_service: NotificationService = Depends(get_notification_service),
):
    count = await notification_service.mark_all_as_read(profile.id)
    return {"message": f"Marked {count} notifications as read"}