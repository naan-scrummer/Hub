from typing import List, Optional, Union
from datetime import datetime
import logging

from app.modules.notifications.models import (
    Notification,
    NotificationSource,
    NotificationStatus,
    ProcessingStatus,
)
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import NotificationCreate
from app.logging.config import get_logger

logger = get_logger(__name__)


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def generate_notification(self, data: NotificationCreate) -> Notification:
        """
        Generate a notification from an academic event (SCRUM-83).
        Validates the event source against supported sources and logs appropriately.
        """
        # Validate supported sources (SCRUM-83 AC1/AC2)
        try:
            if isinstance(data.source, NotificationSource):
                source_enum = data.source
            else:
                source_enum = NotificationSource(data.source)
        except (ValueError, KeyError, TypeError):
            logger.warning("unsupported_notification_source", source=str(data.source))
            raise ValueError(f"Unsupported notification source: {data.source}")

        logger.info(
            "generating_notification",
            student_id=data.student_id,
            source=source_enum.value,
            title=data.title,
        )

        notification = Notification(
            student_id=data.student_id,
            source=source_enum,
            source_id=data.source_id,
            title=data.title,
            message=data.message,
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PENDING,
        )
        return await self.notification_repo.create(notification)

    async def create(
        self,
        student_id: int,
        source: Union[NotificationSource, str],
        title: str,
        message: str,
        source_id: Optional[int] = None,
        processing_status: ProcessingStatus = ProcessingStatus.PENDING,
    ) -> Notification:
        payload = NotificationCreate(
            student_id=student_id,
            source=NotificationSource(source) if isinstance(source, str) else source,
            source_id=source_id,
            title=title,
            message=message,
        )
        return await self.generate_notification(payload)

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        return await self.notification_repo.get_by_id(notification_id)

    async def get_student_notifications(
        self,
        student_id: int,
        status: Optional[Union[NotificationStatus, str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        status_enum = None
        if status:
            if isinstance(status, NotificationStatus):
                status_enum = status
            elif isinstance(status, str) and status.lower() != "all":
                try:
                    status_enum = NotificationStatus(status)
                except ValueError:
                    status_enum = None
        return await self.notification_repo.get_by_student(
            student_id=student_id, status=status_enum, limit=limit, offset=offset
        )

    async def get_unread_count(self, student_id: int) -> int:
        return await self.notification_repo.get_unread_count(student_id)

    async def mark_as_read(self, notification_id: int, student_id: int) -> Optional[Notification]:
        return await self.notification_repo.mark_as_read(notification_id, student_id)

    async def mark_notification_read(self, notification_id: int, student_id: int) -> Optional[Notification]:
        return await self.mark_as_read(notification_id, student_id)

    async def mark_all_as_read(self, student_id: int) -> int:
        return await self.notification_repo.mark_all_as_read(student_id)

    async def mark_all_notifications_read(self, student_id: int) -> int:
        return await self.mark_all_as_read(student_id)

    async def process_pending_notifications_batch(self, limit: int = 100) -> int:
        """
        Processes a batch of pending notifications for delivery state updating (SCRUM-84).
        """
        pending = await self.notification_repo.get_pending_processing(limit=limit)
        processed_count = 0
        for item in pending:
            try:
                await self.notification_repo.mark_processed(item.id)
                processed_count += 1
            except Exception as e:
                logger.error("notification_processing_failed", notification_id=item.id, error=str(e))
        return processed_count

    async def bulk_create(self, notifications: List[Notification]) -> List[Notification]:
        return await self.notification_repo.bulk_create(notifications)

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
            processing_status=ProcessingStatus.PENDING,
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
            processing_status=ProcessingStatus.PENDING,
        )

    def create_from_reminder(
        self,
        student_id: int,
        reminder_id: int,
        title: str,
        description: Optional[str] = None,
    ) -> Notification:
        return Notification(
            student_id=student_id,
            source=NotificationSource.REMINDER_TRIGGER,
            source_id=reminder_id,
            title=f"Reminder: {title}",
            message=description or f"Reminder scheduled: {title}",
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PENDING,
        )

    def create_from_examination(
        self,
        student_id: int,
        exam_id: int,
        title: str,
        exam_date: datetime,
    ) -> Notification:
        return Notification(
            student_id=student_id,
            source=NotificationSource.EXAMINATION,
            source_id=exam_id,
            title=f"Exam Alert: {title}",
            message=f"Examination '{title}' scheduled for {exam_date.strftime('%Y-%m-%d %H:%M')}",
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PENDING,
        )

    def create_from_placement(
        self,
        student_id: int,
        opp_id: int,
        title: str,
        description: str,
    ) -> Notification:
        return Notification(
            student_id=student_id,
            source=NotificationSource.PLACEMENT,
            source_id=opp_id,
            title=f"Placement Alert: {title}",
            message=description[:200] + ("..." if len(description) > 200 else ""),
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PENDING,
        )