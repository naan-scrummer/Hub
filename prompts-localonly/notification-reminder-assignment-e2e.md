# AI Agent Implementation Guide: Reminders, Notifications & Auth Coverage

This document provides operational instructions for an AI agent to implement the assigned feature slice in the `naan-scrummer/Hub` modular monolith repository.

---

## 1. Scope & Ticket Routing

High-level Epics (`SCRUM-32`, `SCRUM-33`) and E2E workflow specifications (`SCRUM-85`, `SCRUM-86`) are extracted out of the direct coding checklist. Implementation is strictly focused on component and integration tasks:

| Jira Ticket | Component | Primary Focus |
| --- | --- | --- |
| **SCRUM-79** (`SCRUM03-F010-UI-001`) | Frontend | Reminder management screen, relationship badges, creation/edit modals |
| **SCRUM-80** (`SCRUM03-F010-BE-001`) | Backend | Reminder scheduling workflow, student ownership validation, API endpoints |
| **SCRUM-81** (`SCRUM03-F010-JOB-001`) | Background Jobs | Periodic due-reminder polling, error isolation, transaction rollback |
| **SCRUM-82** (`SCRUM03-F011-UI-001`) | Frontend | Notification center UI, read/unread status toggles, empty state handling |
| **SCRUM-83** (`SCRUM03-F011-BE-001`) | Backend | Notification generation workflow & domain event dispatching |
| **SCRUM-84** (`SCRUM03-F011-JOB-001`) | Background Jobs | Asynchronous notification status processing |
| **SCRUM-90** (`SCRUM03-T-001`) | Testing | Auth unit & protected resource integration coverage |

---

## 2. File Modification & Isolation Rules

To prevent scope creep and maintain repository integrity, strictly observe the following boundaries:

* **Strictly Untouched**: Any directory or file outside the notification, reminder, assignment integration, and auth pipelines must remain completely untouched (e.g., predicted question papers, course catalogs, external material storage, third-party push integrations).
* **Allowed Modifications**:
* `backend/app/modules/reminders/`
* `backend/app/modules/notifications/`
* `backend/app/modules/assignments/` (Integration touchpoints only: default reminder trigger, due-date updates, completion state handling)
* `backend/app/jobs/scheduler.py`
* `backend/migrations/versions/` (New schema migration)
* `backend/app/seed.py` (Demo seed updates)
* `.env.example`
* `frontend/src/pages/RemindersPage.jsx` & `frontend/src/pages/NotificationsPage.jsx`
* `frontend/src/services/reminders.js` & `frontend/src/services/notifications.js`
* `backend/tests/integration/` (`test_reminders.py`, `test_notifications.py`, `test_auth.py`)



---

## 3. Subagent Execution Strategy

Execute tasks sequentially using dedicated subagents:

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ explorer.md  │───>│  planner.md  │───>│   build.md   │───>│ reviewer.md  │───>│  tester.md   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

```

* **`explorer.md`**: Inspect `backend/app/modules/`, `frontend/src/`, `backend/migrations/`, and `backend/tests/`. Locate existing schema definitions for `Reminder`, `Notification`, and `Assignment`.
* **`planner.md`**: Formulate the step-by-step code modification diffs, database migration plan, service decoupled calls, and test cases.
* **`build.md`**: Perform model modifications, Alembic migration generation, `.env.example` updates, service refactoring, frontend view creation, and seed data expansion.
* **`reviewer.md`**: Audit changes against file-isolation rules, module boundary hygiene (no direct repository cross-imports), and validation logic.
* **`tester.md`**: Execute unit and integration tests (`pytest`), verify auth enforcement, job error isolation, and database seed execution.

---

## 4. Database Schema, `.env.example`, and Seed Updates

### 4.1 Data Model Refinement (`Reminder`)

Add an `origin` column to distinguish automatic system-generated reminders from student-defined custom reminders.

* **File**: `backend/app/modules/reminders/models.py`
* **Column**: `origin = Column(String(20), nullable=False, default="CUSTOM")` (Values: `'AUTOMATIC'`, `'CUSTOM'`)
* **Foreign Keys**: Ensure `assignment_id` and `examination_id` are nullable.

### 4.2 Alembic Migration

Generate a new migration script under `backend/migrations/versions/`:

```python
"""add_origin_to_reminders

Revision ID: 002_add_reminder_origin
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('reminders', sa.Column('origin', sa.String(length=20), nullable=False, server_default='CUSTOM'))

def downgrade():
    op.drop_column('reminders', 'origin')

```

### 4.3 `.env.example` Update

Add configuration values for background job polling intervals and default reminder offsets:

```env
# Background Job Schedules
REMINDER_JOB_INTERVAL_MINUTES=1
NOTIFICATION_JOB_INTERVAL_MINUTES=5

# Default Reminder Settings
DEFAULT_REMINDER_OFFSET_DAYS=7

```

### 4.4 Demo Seed Extension (`backend/app/seed.py`)

Update seed data to include realistic reminders and notifications along with existing assignments:

```python
# Sample Seed Data Injection
demo_student_email = "student@college.edu"

# Assignment with Automatic 7-Day Reminder
assignment = Assignment(
    title="DBMS Record Submission",
    due_date=datetime.now(timezone.utc) + timedelta(days=10),
    student_id=student.id
)

auto_reminder = Reminder(
    student_id=student.id,
    assignment_id=assignment.id,
    title="DBMS Record Submission - Reminder",
    trigger_time=assignment.due_date - timedelta(days=7),
    trigger_type="ASSIGNMENT_DUE",
    origin="AUTOMATIC",
    status="PENDING"
)

custom_reminder = Reminder(
    student_id=student.id,
    title="Study Group Review",
    trigger_time=datetime.now(timezone.utc) + timedelta(days=2),
    trigger_type="CUSTOM",
    origin="CUSTOM",
    status="PENDING"
)

# In-App Notification Seed
notification = Notification(
    student_id=student.id,
    source="REMINDER_TRIGGER",
    source_id=custom_reminder.id,
    title="Study Group Review",
    message="Your study group reminder is active.",
    status="UNREAD"
)

```

---

## 5. Implementation Roadmap

### Phase 1: Assignment ↔ Reminder Business Rules (`SCRUM-80`)

1. **Default Offset**: Modify `AssignmentService.create()` to calculate default reminder trigger as `due_date - timedelta(days=7)`. Set `origin = "AUTOMATIC"`.
2. **Due Date Updates**: When an assignment due date updates, recalculate trigger times **only** for linked reminders where `origin == "AUTOMATIC"` and `status == "PENDING"`. Leave custom reminders untouched.
3. **Completion Cancellation**: When an assignment is marked `COMPLETED`, transition all linked pending reminders to `CANCELLED`.

### Phase 2: Service Decoupling & Notification Generation (`SCRUM-83`)

Refactor boundary violation in `ReminderService`:

```text
[ INCORRECT ]  ReminderService  ──> NotificationRepository
[ CORRECT ]    ReminderService  ──> NotificationService  ──> NotificationRepository

```

1. Modify `ReminderService.process_due_reminders()` to iterate over `PENDING` reminders where `trigger_time <= now`.
2. Generate and persist the corresponding notification through `NotificationService.create(...)`, which delegates persistence to `NotificationRepository`.
3. Update reminder status to `PROCESSED` within a single database transaction.

### Phase 3: Background Jobs Decoupling (`SCRUM-81`, `SCRUM-84`)

Update `backend/app/jobs/scheduler.py`:

```python
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
        async with async_session_maker() as session:
            try:
                reminder_repo = ReminderRepository(session)
                notification_repo = NotificationRepository(session)
                reminder_service = ReminderService(reminder_repo, notification_repo)
                current_time = datetime.now(timezone.utc)
                await reminder_service.process_due_reminders(current_time)
                await session.commit()
            except Exception:
                await session.rollback()

```

### Phase 4: Frontend UI Components (`SCRUM-79`, `SCRUM-82`)

#### 4.1 Reminder Management (`frontend/src/pages/RemindersPage.jsx`)

* Render list of upcoming and past reminders.
* Display contextual badges based on link (`Assignment`, `Examination`, or `Custom`).
* Include modal for creating custom reminders and editing existing reminder times.

#### 4.2 Notification Center (`frontend/src/pages/NotificationsPage.jsx`)

* Display notification stream sorted by timestamp.
* Provide "Mark as Read" and "Mark All as Read" actions using `notificationsService`.
* Display standard empty state ("You're all caught up. No notifications right now.") when list is empty.

### Phase 5: Authentication & Protection Test Suite (`SCRUM-90`)

Create/extend `backend/tests/integration/test_auth.py` and `backend/tests/integration/test_reminders.py`:

* **Unit Coverage**: Test token verification, password hashing, and email validation (accept student emails, reject invalid formats).
* **Resource Protection**: Verify HTTP 401 when accessing `/api/v1/reminders` or `/api/v1/notifications` without a Bearer token.
* **Student Data Isolation**: Verify that Student A receives HTTP 403 / empty response when attempting to access or modify Student B's reminders/notifications.

---

## 6. Execution Verification Checklist

Before marking the implementation complete, verify the following checklist:

* [ ] **Data Isolation**: Verify Student A cannot fetch or update Student B's reminders/notifications.
* [ ] **7-Day Default**: Verify creating an assignment automatically creates a reminder set 7 days prior to due date.
* [ ] **Custom Reminders**: Verify students can add multiple custom reminders to assignments or standalone events without overriding automatic defaults.
* [ ] **Completion Logic**: Verify completing an assignment cancels pending reminders and prevents stale notifications.
* [ ] **Service Decoupling**: Verify `ReminderService` calls `NotificationService` (not `NotificationRepository`).
* [ ] **Job Stability**: Verify job execution failure triggers rollback without crashing the FastAPI process.
* [ ] **Auth Tests**: Run `pytest backend/tests/integration/test_auth.py` and ensure 100% pass rate.
* [ ] **Seed Validation**: Run `cd backend && python -m app.seed` and verify database populates cleanly.