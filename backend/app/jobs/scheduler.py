from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.modules.reminders.service import ReminderService
from app.db.base import async_session_maker
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.repository import NotificationRepository
from app.jobs.notification_job import process_notifications_job
from app.core.config import get_settings
from app.logging.config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class JobScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()

    def _setup_jobs(self):
        self.scheduler.add_job(
            self.process_reminders_job,
            IntervalTrigger(minutes=1),
            id="process_reminders",
            name="Process Due Reminders",
            replace_existing=True,
        )
        self.scheduler.add_job(
            process_notifications_job,
            IntervalTrigger(minutes=settings.NOTIFICATION_JOB_INTERVAL_MINUTES),
            id="process_notifications_job",
            name="Process Pending Notifications",
            replace_existing=True,
        )

    async def process_reminders_job(self):
        logger.info("job_started", job="process_reminders")
        async with async_session_maker() as session:
            try:
                reminder_repo = ReminderRepository(session)
                notification_repo = NotificationRepository(session)
                reminder_service = ReminderService(reminder_repo, notification_repo)

                current_time = datetime.now(timezone.utc)
                processed = await reminder_service.process_due_reminders(current_time)
                await session.commit()

                logger.info("job_completed", job="process_reminders", processed_count=processed)
            except Exception as e:
                logger.error("job_failed", job="process_reminders", error=str(e))
                await session.rollback()

    def start(self):
        self.scheduler.start()
        logger.info("scheduler_started")

    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("scheduler_shutdown")


job_scheduler = JobScheduler()