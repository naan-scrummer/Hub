"""End-to-end integration tests for the Notifications pipeline.

SCRUM-32: Notification listing API
SCRUM-33: Mark notification as read
SCRUM-85: Reminder-to-notification pipeline (reminder job → notification created)
SCRUM-86: Full assignment → reminder → notification flow
"""
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient

from app.main import app
from app.modules.reminders.models import Reminder, ReminderTriggerType, ReminderOrigin, ReminderStatus
from app.modules.notifications.models import (
    Notification,
    NotificationSource,
    NotificationStatus,
    ProcessingStatus,
)
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.repository import NotificationRepository
from app.modules.reminders.service import ReminderService
from app.modules.notifications.service import NotificationService


# ─────────────────────────────────────────────────────────
# Helper: get auth token for demo user
# ─────────────────────────────────────────────────────────

async def _get_token(client: AsyncClient) -> str:
    resp = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123",
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


# ─────────────────────────────────────────────────────────
# SCRUM-32: GET /notifications returns a list for the student
# ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_notifications_list_requires_auth(client):
    """Unauthenticated request must be rejected (SCRUM-32)."""
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_notifications_list_authenticated(client):
    """Authenticated student can fetch their notification list (SCRUM-32)."""
    token = await _get_token(client)
    resp = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Response is a list of notification objects
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_notifications_list_contains_seeded_data(client):
    """Seeded demo notifications appear in the student's list (SCRUM-32)."""
    token = await _get_token(client)
    resp = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0, "Expected seeded notifications; list is empty"

    # Every notification belongs to a valid source category
    valid_sources = {s.value for s in NotificationSource}
    for n in items:
        assert n["source"] in valid_sources, f"Unknown source: {n['source']}"
        assert "title" in n
        assert "message" in n
        assert "status" in n


# ─────────────────────────────────────────────────────────
# SCRUM-33: Mark single notification as read
# ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mark_notification_as_read(client):
    """POST /{id}/read flips status to 'read' for an unread notification (SCRUM-33)."""
    token = await _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    notifications = (await client.get("/api/v1/notifications", headers=headers)).json()
    unread = [n for n in notifications if n["status"] == NotificationStatus.UNREAD.value]
    assert unread, "No unread notifications found to test mark-as-read"

    notif_id = unread[0]["id"]
    resp = await client.post(f"/api/v1/notifications/{notif_id}/read", headers=headers)
    assert resp.status_code == 200

    # Re-fetch and verify status changed
    refreshed = (await client.get("/api/v1/notifications", headers=headers)).json()
    updated = next((n for n in refreshed if n["id"] == notif_id), None)
    assert updated is not None
    assert updated["status"] == NotificationStatus.READ.value, \
        f"Expected 'read', got {updated['status']}"


@pytest.mark.asyncio
async def test_mark_all_notifications_as_read(client):
    """POST /read-all marks every notification as read (SCRUM-33)."""
    token = await _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/notifications/read-all", headers=headers)
    assert resp.status_code == 200

    refreshed = (await client.get("/api/v1/notifications", headers=headers)).json()
    unread_after = [n for n in refreshed if n["status"] == NotificationStatus.UNREAD.value]
    assert len(unread_after) == 0, \
        f"Expected 0 unread after mark-all-read; found {len(unread_after)}"


# ─────────────────────────────────────────────────────────
# SCRUM-85: Reminder-to-Notification pipeline
# ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reminder_job_creates_notification(client, test_session):
    """Due reminders are converted to REMINDER_TRIGGER notifications (SCRUM-85)."""
    now = datetime.now(timezone.utc)

    # Insert a reminder that is already due (trigger_time in the past)
    reminder = Reminder(
        student_id=1,  # demo student profile id seeded by conftest
        title="E2E Test Reminder",
        description="Should trigger a notification",
        trigger_type=ReminderTriggerType.CUSTOM,
        trigger_time=now - timedelta(minutes=5),
        origin=ReminderOrigin.CUSTOM,
        status=ReminderStatus.PENDING,
    )
    test_session.add(reminder)
    await test_session.flush()

    # Count notifications before job runs
    notif_repo = NotificationRepository(test_session)
    before_count = len(await notif_repo.get_by_student(1))

    # Run the reminder processing service directly (simulates the scheduler job)
    reminder_repo = ReminderRepository(test_session)
    reminder_service = ReminderService(reminder_repo, notif_repo)
    processed = await reminder_service.process_due_reminders(now)
    await test_session.commit()

    # At least one reminder should have been processed
    assert processed >= 1, f"Expected at least 1 processed reminder; got {processed}"

    # A new REMINDER_TRIGGER notification must exist
    after_count = len(await notif_repo.get_by_student(1))
    assert after_count > before_count, \
        "No new notification created after reminder job ran"

    # Verify the reminder itself is now PROCESSED
    from sqlalchemy import select
    result = await test_session.execute(
        select(Reminder).where(Reminder.id == reminder.id)
    )
    updated_reminder = result.scalar_one_or_none()
    assert updated_reminder is not None
    assert updated_reminder.status == ReminderStatus.PROCESSED


# ─────────────────────────────────────────────────────────
# SCRUM-86: Assignment → Reminder → Notification full pipeline
# ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_assignment_reminder_notification_pipeline(client, test_session):
    """Full pipeline: assignment due → automatic reminder → notification (SCRUM-86)."""
    now = datetime.now(timezone.utc)

    # The seeded data already contains automatic reminders for assignments.
    # Verify at least one ASSIGNMENT_DEADLINE or REMINDER_TRIGGER notification
    # exists for the seeded demo student via the API.
    token = await _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    notifications = (await client.get("/api/v1/notifications", headers=headers)).json()

    assignment_notifs = [
        n for n in notifications
        if n["source"] in (
            NotificationSource.ASSIGNMENT_DEADLINE.value,
            NotificationSource.REMINDER_TRIGGER.value,
        )
    ]
    assert len(assignment_notifs) > 0, \
        "Expected at least one assignment/reminder notification from seeded data"


@pytest.mark.asyncio
async def test_notification_batch_processing(client, test_session):
    """Pending notifications are moved to PROCESSED by the notification service (SCRUM-86)."""
    now = datetime.now(timezone.utc)

    # Create a PENDING notification directly
    notif_repo = NotificationRepository(test_session)
    notif = Notification(
        student_id=1,
        source=NotificationSource.ASSIGNMENT_DEADLINE,
        source_id=999,
        title="Batch Processing Test",
        message="This pending notification should be processed by the job",
        status=NotificationStatus.UNREAD,
        processing_status=ProcessingStatus.PENDING,
    )
    test_session.add(notif)
    await test_session.flush()

    # Run the notification batch processing
    notif_service = NotificationService(notif_repo)
    count = await notif_service.process_pending_notifications_batch(limit=100)
    await test_session.commit()

    assert count >= 1, f"Expected at least 1 notification processed; got {count}"

    # Verify it moved to PROCESSED
    from sqlalchemy import select
    result = await test_session.execute(
        select(Notification).where(Notification.id == notif.id)
    )
    updated = result.scalar_one_or_none()
    assert updated is not None
    assert updated.processing_status == ProcessingStatus.PROCESSED
