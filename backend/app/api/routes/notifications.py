from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.notifications.service import NotificationService
from app.modules.notifications.repository import NotificationRepository
from app.schemas.notifications import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCreate,
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


from app.api.dependencies.auth import get_current_user
from app.modules.authentication.models import User, UserRole

@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    status: Optional[str] = Query(None, description="Filter by status: all, unread, read, archived"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    profile_id = None
    if user.role == UserRole.STUDENT:
        from app.modules.authentication.repository import StudentProfileRepository
        repo = StudentProfileRepository(notification_service.notification_repo.session)
        profile = await repo.get_by_user_id(user.id)
        if profile:
            profile_id = profile.id
    elif user.role == UserRole.TEACHER:
        from app.modules.authentication.repository import TeacherProfileRepository
        repo = TeacherProfileRepository(notification_service.notification_repo.session)
        profile = await repo.get_by_user_id(user.id)
        if profile:
            profile_id = profile.id

    if not profile_id:
        return NotificationListResponse(notifications=[], unread_count=0)

    if user.role == UserRole.TEACHER:
        # For now, teachers use same repository method, but we should make sure it filters correctly
        notifications = await notification_service.get_teacher_notifications(profile_id, status, limit, offset)
        unread_count = await notification_service.get_teacher_unread_count(profile_id)
    else:
        notifications = await notification_service.get_student_notifications(profile_id, status, limit, offset)
        unread_count = await notification_service.get_unread_count(profile_id)

    responses = [NotificationResponse.model_validate(n) for n in notifications]

    return NotificationListResponse(
        notifications=responses,
        unread_count=unread_count,
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    profile_id = None
    if user.role == UserRole.STUDENT:
        from app.modules.authentication.repository import StudentProfileRepository
        repo = StudentProfileRepository(notification_service.notification_repo.session)
        profile = await repo.get_by_user_id(user.id)
        if profile:
            profile_id = profile.id
    elif user.role == UserRole.TEACHER:
        from app.modules.authentication.repository import TeacherProfileRepository
        repo = TeacherProfileRepository(notification_service.notification_repo.session)
        profile = await repo.get_by_user_id(user.id)
        if profile:
            profile_id = profile.id

    if not profile_id:
        raise HTTPException(status_code=404, detail="Profile not found")

    notification = await notification_service.mark_as_read(
        notification_id, profile_id, user.role == UserRole.TEACHER
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationResponse.model_validate(notification)


@router.post("/read-all")
async def mark_all_read(
    user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    profile_id = None
    if user.role == UserRole.STUDENT:
        from app.modules.authentication.repository import StudentProfileRepository
        repo = StudentProfileRepository(notification_service.notification_repo.session)
        profile = await repo.get_by_user_id(user.id)
        if profile:
            profile_id = profile.id
    elif user.role == UserRole.TEACHER:
        from app.modules.authentication.repository import TeacherProfileRepository
        repo = TeacherProfileRepository(notification_service.notification_repo.session)
        profile = await repo.get_by_user_id(user.id)
        if profile:
            profile_id = profile.id
            
    if not profile_id:
        return {"message": "Profile not found", "updated_count": 0}

    count = await notification_service.mark_all_as_read(
        profile_id, user.role == UserRole.TEACHER
    )
    return {"message": f"Marked {count} notifications as read", "updated_count": count}


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    payload: NotificationCreate,
    profile: StudentProfile = Depends(get_current_student_profile),
    notification_service: NotificationService = Depends(get_notification_service),
):
    if payload.student_id != profile.id:
        raise HTTPException(status_code=403, detail="Cannot generate notification for another student")
    try:
        notification = await notification_service.generate_notification(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return NotificationResponse.model_validate(notification)