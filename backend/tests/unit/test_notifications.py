import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.notifications.service import NotificationService
from app.modules.notifications.models import (
    Notification,
    NotificationSource,
    NotificationStatus,
    ProcessingStatus,
)
from app.modules.notifications.schemas import NotificationCreate
from app.modules.notifications.repository import NotificationRepository
from app.jobs.notification_job import process_notifications_job


class MockNotificationSession:
    def __init__(self):
        self.notifications = {}
        self.next_id = 1

    def add(self, obj):
        if not hasattr(obj, 'id') or obj.id is None:
            obj.id = self.next_id
            self.next_id += 1
        self.notifications[obj.id] = obj

    def add_all(self, objs):
        for o in objs:
            self.add(o)

    async def flush(self):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def refresh(self, obj):
        pass

    async def execute(self, query):
        class MockResult:
            def __init__(self, data):
                self.data = data

            def scalar_one_or_none(self):
                return self.data[0] if self.data else None

            def scalar_one(self):
                return self.data[0] if self.data else 0

            def scalars(self):
                class MockScalars:
                    def __init__(self, data):
                        self.data = data
                    def all(self):
                        return self.data
                    def first(self):
                        return self.data[0] if self.data else None
                return MockScalars(self.data)

        return MockResult(list(self.notifications.values()))


@pytest.fixture
def mock_session():
    return MockNotificationSession()


@pytest.fixture
def notification_repo(mock_session):
    return NotificationRepository(mock_session)


@pytest.fixture
def notification_service(notification_repo):
    return NotificationService(notification_repo)


class TestNotificationService:
    @pytest.mark.asyncio
    async def test_generate_notification_success(self, notification_service):
        payload = NotificationCreate(
            student_id=1,
            source=NotificationSource.ANNOUNCEMENT,
            source_id=10,
            title="Test Announcement",
            message="This is a test notification.",
        )
        notification = await notification_service.generate_notification(payload)

        assert notification.id is not None
        assert notification.student_id == 1
        assert notification.source == NotificationSource.ANNOUNCEMENT
        assert notification.title == "Test Announcement"
        assert notification.status == NotificationStatus.UNREAD
        assert notification.processing_status == ProcessingStatus.PENDING

    @pytest.mark.asyncio
    async def test_unsupported_notification_source(self, notification_service):
        with pytest.raises(ValueError):
            await notification_service.generate_notification(
                NotificationCreate(
                    student_id=1,
                    source="INVALID_SOURCE",  # type: ignore
                    title="Invalid",
                    message="Should fail",
                )
            )

    @pytest.mark.asyncio
    async def test_mark_as_read(self, notification_service, mock_session, notification_repo):
        payload = NotificationCreate(
            student_id=1,
            source=NotificationSource.EXAMINATION,
            title="Exam Alert",
            message="Exam schedule",
        )
        created = await notification_service.generate_notification(payload)
        
        # Mock get_by_id on repo to return the created object
        notification_repo.get_by_id = AsyncMock(return_value=created)
        
        updated = await notification_service.mark_as_read(created.id, student_id=1)
        assert updated is not None
        assert updated.status == NotificationStatus.READ
        assert updated.read_at is not None

    @pytest.mark.asyncio
    async def test_mark_as_read_wrong_student(self, notification_service, notification_repo):
        notification = Notification(
            id=10,
            student_id=2,
            source=NotificationSource.PLACEMENT,
            title="Placement Shortlist",
            message="You are shortlisted",
            status=NotificationStatus.UNREAD,
        )
        notification_repo.get_by_id = AsyncMock(return_value=notification)

        result = await notification_service.mark_as_read(10, student_id=1)
        assert result is None

    @pytest.mark.asyncio
    async def test_mark_all_as_read(self, notification_service, notification_repo):
        notification_repo.mark_all_as_read = AsyncMock(return_value=3)
        count = await notification_service.mark_all_as_read(student_id=1)
        assert count == 3

    @pytest.mark.asyncio
    async def test_process_pending_notifications_batch(self, notification_service, notification_repo):
        n1 = Notification(
            id=1,
            student_id=1,
            source=NotificationSource.ASSIGNMENT_DEADLINE,
            title="Due Soon",
            message="Due in 24h",
            processing_status=ProcessingStatus.PENDING,
        )
        n2 = Notification(
            id=2,
            student_id=1,
            source=NotificationSource.REMINDER_TRIGGER,
            title="Reminder",
            message="Reminder trigger",
            processing_status=ProcessingStatus.PENDING,
        )
        notification_repo.get_pending_processing = AsyncMock(return_value=[n1, n2])
        notification_repo.mark_processed = AsyncMock(return_value=True)

        count = await notification_service.process_pending_notifications_batch(limit=10)
        assert count == 2
        assert notification_repo.mark_processed.call_count == 2

    @pytest.mark.asyncio
    async def test_helper_factories(self, notification_service):
        now = datetime.now(timezone.utc)
        n_assign = notification_service.create_from_assignment_deadline(1, 10, "Math HW", now)
        assert n_assign.source == NotificationSource.ASSIGNMENT_DEADLINE
        assert "Math HW" in n_assign.title

        n_rem = notification_service.create_from_reminder(1, 20, "Study CS", "Revision")
        assert n_rem.source == NotificationSource.REMINDER_TRIGGER

        n_ann = notification_service.create_from_announcement(1, 30, "Tech Fest", "Details")
        assert n_ann.source == NotificationSource.ANNOUNCEMENT

        n_exam = notification_service.create_from_examination(1, 40, "Midterm", now)
        assert n_exam.source == NotificationSource.EXAMINATION

        n_place = notification_service.create_from_placement(1, 50, "Google", "Interview")
        assert n_place.source == NotificationSource.PLACEMENT


class TestNotificationJob:
    @pytest.mark.asyncio
    async def test_notification_job_resilience(self, monkeypatch):
        """
        Background job execution should catch exceptions internally and log them without crashing caller thread (SCRUM-84).
        """
        async def mock_failure(*args, **kwargs):
            raise RuntimeError("Simulated Database Drop")

        monkeypatch.setattr(
            "app.modules.notifications.service.NotificationService.process_pending_notifications_batch",
            mock_failure,
        )

        # Job execution must not throw
        try:
            await process_notifications_job()
        except Exception as exc:
            pytest.fail(f"Background job crashed caller thread: {str(exc)}")
