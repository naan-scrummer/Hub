import pytest
from datetime import datetime, timedelta
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
        service = AssignmentService(assignment_repo, reminder_repo)

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
        service = AssignmentService(assignment_repo, reminder_repo)

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
        service = AssignmentService(assignment_repo, reminder_repo)

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

        processed = await service.process_due_reminders(datetime.utcnow())
        assert processed == 1
        assert reminder.status == ReminderStatus.PROCESSED
        assert len(session.notifications) == 1

    @pytest.mark.asyncio
    async def test_process_due_reminders_skips_future(self):
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

        processed = await service.process_due_reminders(datetime.utcnow())
        assert processed == 0
        assert reminder.status == ReminderStatus.PENDING
        assert len(session.notifications) == 0


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

        result = await service.mark_as_read(1, 1)
        assert result is None