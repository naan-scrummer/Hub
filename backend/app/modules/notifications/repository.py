from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification, NotificationStatus


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Notification):
        return select(parameter)

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        result = await self.session.execute(select(Notification).where(Notification.id == notification_id))
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
        return result.scalar_one()

    async def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification

    async def bulk_create(self, notifications: List[Notification]) -> List[Notification]:
        self.session.add_all(notifications)
        await self.session.flush()
        for n in notifications:
            await self.session.refresh(n)
        return notifications

    async def mark_as_read(self, notification_id: int, student_id: int) -> Optional[Notification]:
        notification = await self.get_by_id(notification_id)
        if notification and notification.student_id == student_id:
            notification.status = NotificationStatus.READ
            from datetime import datetime
            notification.read_at = datetime.utcnow()
            await self.session.flush()
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
        for n in notifications:
            n.status = NotificationStatus.READ
            n.read_at = datetime.utcnow()
        await self.session.flush()
        return len(notifications)