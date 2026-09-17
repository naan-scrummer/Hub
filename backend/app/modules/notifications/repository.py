from typing import Optional, List, Union
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import (
    Notification,
    NotificationStatus,
    ProcessingStatus,
    NotificationSource,
)


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Notification):
        return select(parameter)

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student(
        self,
        student_id: int,
        status: Optional[NotificationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        stmt = select(Notification).where(Notification.student_id == student_id)
        if status:
            stmt = stmt.where(Notification.status == status)
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_unread_count(self, student_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Notification.id)).where(
                Notification.student_id == student_id,
                Notification.status == NotificationStatus.UNREAD,
            )
        )
        return result.scalar_one() or 0

    async def get_pending_processing(self, limit: int = 100) -> List[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.processing_status == ProcessingStatus.PENDING)
            .order_by(Notification.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_processed(self, notification_id: int) -> Optional[Notification]:
        notification = await self.get_by_id(notification_id)
        if notification:
            notification.processing_status = ProcessingStatus.PROCESSED
            notification.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
            try:
                await self.session.commit()
            except Exception:
                pass
            await self.session.refresh(notification)
            return notification
        return None

    async def create(
        self,
        notification_or_student_id: Union[Notification, int],
        source: Optional[NotificationSource] = None,
        title: Optional[str] = None,
        message: Optional[str] = None,
        source_id: Optional[int] = None,
        processing_status: ProcessingStatus = ProcessingStatus.PENDING,
    ) -> Notification:
        if isinstance(notification_or_student_id, Notification):
            notification = notification_or_student_id
        else:
            notification = Notification(
                student_id=notification_or_student_id,
                source=source,
                source_id=source_id,
                title=title,
                message=message,
                status=NotificationStatus.UNREAD,
                processing_status=processing_status,
            )
        self.session.add(notification)
        await self.session.flush()
        try:
            await self.session.commit()
        except Exception:
            pass
        await self.session.refresh(notification)
        return notification

    async def bulk_create(self, notifications: List[Notification]) -> List[Notification]:
        self.session.add_all(notifications)
        await self.session.flush()
        try:
            await self.session.commit()
        except Exception:
            pass
        for n in notifications:
            await self.session.refresh(n)
        return notifications

    async def mark_as_read(self, notification_id: int, student_id: int) -> Optional[Notification]:
        notification = await self.get_by_id(notification_id)
        if notification and notification.student_id == student_id:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.now(timezone.utc)
            notification.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
            try:
                await self.session.commit()
            except Exception:
                pass
            return notification
        return None

    async def mark_all_as_read(self, student_id: int) -> int:
        result = await self.session.execute(
            select(Notification).where(
                Notification.student_id == student_id,
                Notification.status == NotificationStatus.UNREAD,
            )
        )
        notifications = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        for n in notifications:
            n.status = NotificationStatus.READ
            n.read_at = now
            n.updated_at = now
        await self.session.flush()
        try:
            await self.session.commit()
        except Exception:
            pass
        return len(notifications)

    async def delete(self, notification_id: int, student_id: int) -> bool:
        notification = await self.get_by_id(notification_id)
        if notification and notification.student_id == student_id:
            await self.session.delete(notification)
            await self.session.flush()
            try:
                await self.session.commit()
            except Exception:
                pass
            return True
        return False