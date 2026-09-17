import logging
from datetime import datetime, timezone, timedelta
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.modules.notifications.models import (
    Notification,
    NotificationSource,
    NotificationStatus,
    ProcessingStatus,
)
from app.logging.config import get_logger

logger = get_logger(__name__)


async def seed_notifications(session: Union[AsyncSession, Session], student_id: int):
    """
    Seed notification demo data across all supported categories and statuses (SCRUM-83/SCRUM-84).
    """
    logger.info("seeding_notifications_start", student_id=student_id)

    # Check if already seeded
    if isinstance(session, AsyncSession):
        res = await session.execute(
            select(Notification).where(Notification.student_id == student_id)
        )
        existing = res.scalars().first()
    else:
        existing = session.query(Notification).filter(Notification.student_id == student_id).first()

    if existing:
        logger.info("notifications_already_seeded", student_id=student_id)
        return

    now = datetime.now(timezone.utc)

    sample_notifications = [
        Notification(
            student_id=student_id,
            source=NotificationSource.ASSIGNMENT_DEADLINE,
            source_id=101,
            title="Assignment Due Soon: DBMS Record",
            message="Your DBMS Lab Record submission is due in 24 hours.",
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PROCESSED,
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=2),
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.REMINDER_TRIGGER,
            source_id=202,
            title="Reminder: Study for Computer Networks",
            message="Custom reminder: Chapter 4 revision scheduled now.",
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PROCESSED,
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=5),
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.ANNOUNCEMENT,
            source_id=303,
            title="Campus Placement Drive",
            message="Registration for the upcoming tech drive closes this Friday.",
            status=NotificationStatus.READ,
            processing_status=ProcessingStatus.PROCESSED,
            read_at=now - timedelta(hours=10),
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(hours=10),
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.EXAMINATION,
            source_id=404,
            title="Mid-Semester Exam Schedule Released",
            message="The timetable for Mid-Sem 2 examinations is now live on the student portal.",
            status=NotificationStatus.READ,
            processing_status=ProcessingStatus.PROCESSED,
            read_at=now - timedelta(days=1),
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(days=1),
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.PLACEMENT,
            source_id=505,
            title="Interview Shortlist Announced: TechCorp",
            message="You have been shortlisted for the technical interview with TechCorp Solutions.",
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PROCESSED,
            created_at=now - timedelta(minutes=30),
            updated_at=now - timedelta(minutes=30),
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.ANNOUNCEMENT,
            source_id=304,
            title="Annual Sports Day Schedule",
            message="Annual sports day registrations and event schedules are archived.",
            status=NotificationStatus.ARCHIVED,
            processing_status=ProcessingStatus.PROCESSED,
            read_at=now - timedelta(days=15),
            created_at=now - timedelta(days=20),
            updated_at=now - timedelta(days=15),
        ),
    ]

    if isinstance(session, AsyncSession):
        session.add_all(sample_notifications)
        await session.flush()
        await session.commit()
    else:
        session.add_all(sample_notifications)
        session.commit()

    logger.info("notifications_seeded_successfully", count=len(sample_notifications))
