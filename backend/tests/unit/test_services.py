import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.authentication.service import AuthenticationService
from app.modules.authentication.models import User, UserRole, StudentProfile
from app.modules.authentication.repository import UserRepository, StudentProfileRepository
from app.modules.assignments.service import AssignmentService
from app.modules.assignments.models import Assignment, AssignmentStatus
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.service import ReminderService
from app.modules.reminders.models import Reminder, ReminderTriggerType, ReminderStatus
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.service import NotificationService
from app.modules.notifications.models import Notification, NotificationSource, NotificationStatus
from app.modules.notifications.repository import NotificationRepository


class MockSession:
    def __init__(self):
        self.users = {}
        self.profiles = {}
        self.assignments = {}
        self.reminders = {}
        self.notifications = {}
        self.next_id = 1

    def add(self, obj):
        if not hasattr(obj, 'id') or obj.id is None:
            obj.id = self.next_id
            self.next_id += 1

    async def flush(self):
        pass

    async def refresh(self, obj):
        pass

    async def execute(self, query):
        class MockResult:
            def __init__(self, data):
                self.data = data

            def scalar_one_or_none(self):
                return self.data[0] if self.data else None

            def scalars(self):
                class MockScalars:
                    def __init__(self, data):
                        self.data = data
                    def all(self):
                        return self.data
                return MockScalars(self.data)

            def one(self):
                return self.data[0] if self.data else (None, None, None)

        # Return empty for all queries — tests use mock repos instead
        return MockResult([])


@pytest.fixture
def mock_session():
    return MockSession()


@pytest.fixture
def auth_service(mock_session):
    user_repo = UserRepository(mock_session)
    profile_repo = StudentProfileRepository(mock_session)
    return AuthenticationService(user_repo, profile_repo)


class TestAuthenticationService:
    @pytest.mark.asyncio
    async def test_password_hashing(self, auth_service):
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrongpassword", hashed)

    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service):
        token = auth_service.create_access_token({"sub": "1", "email": "test@test.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_decode_token(self, auth_service):
        token = auth_service.create_access_token({"sub": "1", "email": "test@test.com"})
        payload = auth_service.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["email"] == "test@test.com"

    @pytest.mark.asyncio
    async def test_decode_invalid_token(self, auth_service):
        payload = auth_service.decode_token("invalid.token.here")
        assert payload is None


class TestAssignmentService:
    @pytest.mark.asyncio
    async def test_classify_upcoming(self):
        session = MockSession()
        assignment_repo = AssignmentRepository(session)
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        reminder_service = ReminderService(reminder_repo, notification_repo)
        service = AssignmentService(assignment_repo, reminder_service)

        assignment = Assignment(
            id=1,
            student_id=1,
            subject_id=1,
            title="Test Assignment",
            due_date=datetime.utcnow() + timedelta(days=2),
            status=AssignmentStatus.UPCOMING,
        )

        status = service.classify_status(assignment)
        assert status == AssignmentStatus.UPCOMING

    @pytest.mark.asyncio
    async def test_classify_overdue(self):
        session = MockSession()
        assignment_repo = AssignmentRepository(session)
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        reminder_service = ReminderService(reminder_repo, notification_repo)
        service = AssignmentService(assignment_repo, reminder_service)

        assignment = Assignment(
            id=1,
            student_id=1,
            subject_id=1,
            title="Test Assignment",
            due_date=datetime.utcnow() - timedelta(days=1),
            status=AssignmentStatus.UPCOMING,
        )

        status = service.classify_status(assignment)
        assert status == AssignmentStatus.OVERDUE

    @pytest.mark.asyncio
    async def test_classify_completed(self):
        session = MockSession()
        assignment_repo = AssignmentRepository(session)
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        reminder_service = ReminderService(reminder_repo, notification_repo)
        service = AssignmentService(assignment_repo, reminder_service)

        assignment = Assignment(
            id=1,
            student_id=1,
            subject_id=1,
            title="Test Assignment",
            due_date=datetime.utcnow() - timedelta(days=1),
            status=AssignmentStatus.COMPLETED,
            completed_at=datetime.utcnow(),
        )

        status = service.classify_status(assignment)
        assert status == AssignmentStatus.COMPLETED


class TestReminderService:
    @pytest.mark.asyncio
    async def test_process_due_reminders_creates_notifications(self):
        """Test that processing due reminders creates notifications."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        reminder = Reminder(
            id=1,
            student_id=1,
            title="Test Reminder",
            trigger_time=datetime.utcnow() - timedelta(minutes=5),
            trigger_type=ReminderTriggerType.CUSTOM,
            status=ReminderStatus.PENDING,
        )
        session.reminders[1] = reminder

        # Mock the repository methods to return the test data
        reminder_repo.get_pending_due = AsyncMock(return_value=[reminder])
        reminder_repo.update = AsyncMock(return_value=reminder)
        notification_repo.create = AsyncMock(return_value=MagicMock())

        processed = await service.process_due_reminders(datetime.utcnow())
        assert processed == 1
        assert reminder.status == ReminderStatus.PROCESSED
        assert reminder.processed_at is not None
        notification_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_due_reminders_skips_future(self):
        """Test that future reminders are not processed."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        reminder = Reminder(
            id=1,
            student_id=1,
            title="Future Reminder",
            trigger_time=datetime.utcnow() + timedelta(days=1),
            trigger_type=ReminderTriggerType.CUSTOM,
            status=ReminderStatus.PENDING,
        )
        session.reminders[1] = reminder

        # Mock get_pending_due to return empty (no due reminders)
        reminder_repo.get_pending_due = AsyncMock(return_value=[])

        processed = await service.process_due_reminders(datetime.utcnow())
        assert processed == 0
        assert reminder.status == ReminderStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_automatic_reminder(self):
        """Test automatic reminder creation with 7-day trigger."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        created_reminder = Reminder(
            id=1,
            student_id=1,
            assignment_id=42,
            title="Due soon: Test",
            trigger_time=datetime.utcnow() + timedelta(days=3),
            trigger_type=ReminderTriggerType.ASSIGNMENT_DUE,
            status=ReminderStatus.PENDING,
        )

        # Mock the create method
        async def mock_create(reminder):
            reminder.id = 1
            return reminder
        reminder_repo.create = mock_create

        event_time = datetime.utcnow() + timedelta(days=10)
        result = await service.create_automatic_reminder(
            student_id=1,
            entity_type="assignment",
            entity_id=42,
            event_time=event_time,
            title="Due soon: Test",
        )

        assert result is not None
        assert result.student_id == 1
        assert result.assignment_id == 42
        assert result.origin.value == "automatic"
        assert result.status == ReminderStatus.PENDING
        # trigger_time should be event_time - 7 days
        expected_trigger = event_time - timedelta(days=7)
        assert abs((result.trigger_time - expected_trigger).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_create_automatic_reminder_past_event(self):
        """Test that automatic reminders are not created for past events."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        event_time = datetime.utcnow() + timedelta(days=3)  # Only 3 days away, trigger would be in past
        result = await service.create_automatic_reminder(
            student_id=1,
            entity_type="assignment",
            entity_id=42,
            event_time=event_time,
            title="Due soon: Test",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_linked_reminders(self):
        """Test that linked reminders are cancelled."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        # Mock cancel_by_entity
        reminder_repo.cancel_by_entity = AsyncMock(return_value=2)

        count = await service.cancel_linked_reminders(
            student_id=1,
            entity_type="assignment",
            entity_id=42,
        )

        assert count == 2
        reminder_repo.cancel_by_entity.assert_called_once_with(
            1, "assignment", 42
        )

    @pytest.mark.asyncio
    async def test_update_reminder(self):
        """Test updating a reminder."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        from app.schemas.reminders import ReminderUpdateRequest

        reminder = Reminder(
            id=1,
            student_id=1,
            title="Original Title",
            trigger_time=datetime.utcnow() + timedelta(days=1),
            trigger_type=ReminderTriggerType.CUSTOM,
            status=ReminderStatus.PENDING,
        )

        # Mock get_by_student_and_id to return the reminder
        reminder_repo.get_by_student_and_id = AsyncMock(return_value=reminder)
        reminder_repo.update = AsyncMock(return_value=reminder)

        update_data = ReminderUpdateRequest(title="Updated Title")
        result = await service.update_reminder(student_id=1, reminder_id=1, data=update_data)

        assert result is not None
        assert result.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_reminder(self):
        """Test deleting a reminder."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        reminder = Reminder(
            id=1,
            student_id=1,
            title="To Delete",
            trigger_time=datetime.utcnow() + timedelta(days=1),
            trigger_type=ReminderTriggerType.CUSTOM,
            status=ReminderStatus.PENDING,
        )

        # Mock get_by_student_and_id and delete
        reminder_repo.get_by_student_and_id = AsyncMock(return_value=reminder)
        reminder_repo.delete = AsyncMock(return_value=None)

        result = await service.delete_reminder(student_id=1, reminder_id=1)

        assert result is True
        reminder_repo.delete.assert_called_once_with(reminder)

    @pytest.mark.asyncio
    async def test_delete_reminder_not_found(self):
        """Test deleting a non-existent reminder returns False."""
        session = MockSession()
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)
        service = ReminderService(reminder_repo, notification_repo)

        reminder_repo.get_by_student_and_id = AsyncMock(return_value=None)

        result = await service.delete_reminder(student_id=1, reminder_id=999)

        assert result is False


class TestNotificationService:
    @pytest.mark.asyncio
    async def test_create_notification(self):
        session = MockSession()
        notification_repo = NotificationRepository(session)
        service = NotificationService(notification_repo)

        notification = await service.create(
            student_id=1,
            source=NotificationSource.ASSIGNMENT_DEADLINE,
            title="Test",
            message="Test message",
        )

        assert notification.id == 1
        assert notification.student_id == 1
        assert notification.source == NotificationSource.ASSIGNMENT_DEADLINE
        assert notification.status == NotificationStatus.UNREAD

    @pytest.mark.asyncio
    async def test_mark_as_read(self):
        session = MockSession()
        notification_repo = NotificationRepository(session)
        service = NotificationService(notification_repo)

        notification = Notification(
            id=1,
            student_id=1,
            source=NotificationSource.ASSIGNMENT_DEADLINE,
            title="Test",
            message="Test",
            status=NotificationStatus.UNREAD,
        )
        session.notifications[1] = notification

        # Mock the repo methods
        notification_repo.get_by_id = AsyncMock(return_value=notification)
        notification_repo.update = AsyncMock(return_value=notification)

        result = await service.mark_as_read(1, 1)
        assert result is not None
        assert result.status == NotificationStatus.READ
        assert result.read_at is not None

    @pytest.mark.asyncio
    async def test_mark_as_read_wrong_student(self):
        session = MockSession()
        notification_repo = NotificationRepository(session)
        service = NotificationService(notification_repo)

        notification = Notification(
            id=1,
            student_id=2,
            source=NotificationSource.ASSIGNMENT_DEADLINE,
            title="Test",
            message="Test",
            status=NotificationStatus.UNREAD,
        )
        session.notifications[1] = notification

        # Mock the repo to return the notification
        notification_repo.get_by_id = AsyncMock(return_value=notification)

        result = await service.mark_as_read(1, 1)
        assert result is None
