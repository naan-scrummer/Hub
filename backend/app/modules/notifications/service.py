from typing import List, Optional
from datetime import datetime

from app.modules.notifications.models import Notification, NotificationSource, NotificationStatus
from app.modules.notifications.repository import NotificationRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        return await self.notification_repo.get_by_id(notification_id)

    async def get_student_notifications(
        self,
        student_id: int,
        status: Optional[NotificationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        return await self.notification_repo.get_by_student(student_id, status, limit, offset)

    async def get_unread_count(self, student_id: int) -> int:
        return await self.notification_repo.get_unread_count(student_id)

    async def create(
        self,
        student_id: int,
        source: NotificationSource,
        title: str,
        message: str,
        source_id: Optional[int] = None,
    ) -> Notification:
        notification = Notification(
            student_id=student_id,
            source=source,
            source_id=source_id,
            title=title,
            message=message,
            status=NotificationStatus.UNREAD,
        )
        return await self.notification_repo.create(notification)

    async def bulk_create(self, notifications: List[Notification]) -> List[Notification]:
        return await self.notification_repo.bulk_create(notifications)

    async def mark_as_read(self, notification_id: int, student_id: int) -> Optional[Notification]:
        return await self.notification_repo.mark_as_read(notification_id, student_id)

    async def mark_all_as_read(self, student_id: int) -> int:
        return await self.notification_repo.mark_all_as_read(student_id)

    def create_from_assignment_deadline(
        self,
        student_id: int,
        assignment_id: int,
        title: str,
        due_date: datetime,
    ) -> Notification:
        return Notification(
            student_id=student_id,
            source=NotificationSource.ASSIGNMENT_DEADLINE,
            source_id=assignment_id,
            title=f"Assignment Due: {title}",
            message=f"Assignment '{title}' is due on {due_date.strftime('%Y-%m-%d %H:%M')}",
            status=NotificationStatus.UNREAD,
        )

    def create_from_announcement(
        self,
        student_id: int,
        announcement_id: int,
        title: str,
        content: str,
    ) -> Notification:
        return Notification(
            student_id=student_id,
            source=NotificationSource.ANNOUNCEMENT,
            source_id=announcement_id,
            title=f"New Announcement: {title}",
            message=content[:200] + ("..." if len(content) > 200 else ""),
            status=NotificationStatus.UNREAD,
        )