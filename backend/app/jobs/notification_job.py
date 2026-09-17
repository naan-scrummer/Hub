import logging
from app.db.base import async_session_maker
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.service import NotificationService
from app.core.config import get_settings
from app.logging.config import get_logger

logger = get_logger(__name__)


async def process_notifications_job():
    """
    Background job handling notification delivery and state processing independently of API requests (SCRUM-84).
    Processes pending notifications into PROCESSED state with full error handling and resilience.
    """
    settings = get_settings()
    if not settings.ENABLE_BACKGROUND_NOTIFICATIONS:
        logger.info("background_notifications_disabled")
        return

    logger.info("job_started", job="process_notifications")
    async with async_session_maker() as session:
        try:
            repo = NotificationRepository(session)
            service = NotificationService(repo)
            count = await service.process_pending_notifications_batch(
                limit=settings.NOTIFICATION_BATCH_SIZE
            )
            await session.commit()
            logger.info("job_completed", job="process_notifications", processed_count=count)
        except Exception as exc:
            logger.error(
                "job_failed",
                job="process_notifications",
                error=str(exc),
            )
            await session.rollback()
