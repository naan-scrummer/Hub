# Implementation Specification: Reminders Module (SCRUM 32, 79, 80, 81)

**Repository:** `naan-scrummer/Hub`

**Product:** AIO Student's Hub

**Primary User:** Student

**Target Scope:** Reminders Module only (SCRUM 32 Epic, SCRUM 79 UI, SCRUM 80 Backend API/Workflow, SCRUM 81 Background Processing). End-to-End (E2E) workflow integration and external notification deliverability are explicitly excluded from this specification.

---

# 1. Scope & Ticket Mapping

| Ticket ID | Work Item | Focus Area | Core Responsibility |
| --- | --- | --- | --- |
| **SCRUM 32** | Reminders Epic | Domain / Architecture | Defines the overall module scope, entity semantics, default 7-day rules, origin tracking (`AUTOMATIC` vs `CUSTOM`), and data isolation rules. |
| **SCRUM 79** | Reminder Management UI | Frontend (`frontend/src/`) | UI components, management page, creation/edit modals, visual relationship tagging, and frontend API service wrappers. |
| **SCRUM 80** | Reminder Scheduling Workflow | Backend API (`backend/app/modules/reminders/`) | REST API routes, Pydantic schemas, SQLAlchemy models, service CRUD operations, authorization validations, and default trigger calculations. |
| **SCRUM 81** | Background Reminder Processing | Background Jobs (`backend/app/jobs/`) | Scheduler job definition, periodic polling of due `PENDING` reminders, status transition state machine, and atomic transaction handling. |

---

# 2. Strict Modification Rules & Guardrails

To prevent regression and unintended side effects, any agent or developer executing this guide must adhere to the following rules:

## 2.1 Unrelated Files (STRICT DO NOT MODIFY)

The following directories and files must **not** be modified under any circumstances:

* `backend/app/modules/notifications/`
* `backend/app/modules/authentication/` (except reading auth context/tokens)
* `backend/app/modules/assignments/` (except invocation hooks explicitly defined in Section 6.1)
* `backend/app/modules/examinations/`
* `frontend/src/pages/NotificationsPage.jsx`
* `frontend/src/pages/DashboardPage.jsx` (unless adding a minimal link to the Reminders page in navigation)
* any file that does not involve in the reminder pipeline

## 2.2 Related Files (MODIFY WITH CAUTION)

The following shared infrastructure files may be touched **only** to register the Reminders module:

* `backend/app/main.py` or API Router index: Only to include `reminders_router`.
* Database Base / Alembic Metadata: Only to register the `Reminder` SQLAlchemy model for migrations.
* `frontend/src/App.jsx` or main Navigation component: Only to add the client-side route `/reminders` and nav link.

---

# 3. Architecture & Data Model (SCRUM 32)

## 3.1 Entity Model: `Reminder`

The `Reminder` model must be placed in `backend/app/modules/reminders/models.py`.

```text
Reminder
-------------------------------------------------------------------
id              : Integer (Primary Key, Autoincrement)
student_id      : Integer (Foreign Key -> StudentProfile.id, Indexed)
assignment_id   : Integer (Foreign Key -> Assignment.id, Nullable, Indexed)
examination_id  : Integer (Foreign Key -> Examination.id, Nullable, Indexed)
title           : String(255) (Required)
description     : Text (Nullable)
trigger_type    : Enum ('ASSIGNMENT_DUE', 'EXAMINATION', 'CUSTOM')
trigger_time    : DateTime(timezone=True) (Indexed)
origin          : Enum ('AUTOMATIC', 'CUSTOM') (Default: 'CUSTOM')
status          : Enum ('PENDING', 'PROCESSED', 'CANCELLED') (Default: 'PENDING')
processed_at    : DateTime(timezone=True) (Nullable)
created_at      : DateTime(timezone=True) (Server Default: utcnow)
updated_at      : DateTime(timezone=True) (Server Default: utcnow, OnUpdate: utcnow)

```

## 3.2 Business Rules & Constraints

* **Student Ownership Boundary:** A student can only access, view, modify, or delete reminders where `student_id == current_user.student_id`. Attempting to access or link against another student's assignment/exam must return HTTP 403 / HTTP 404.
* **Multiple Reminders:** A single assignment or examination can have multiple linked reminders (1-to-N relationship).
* **Default Trigger Calculation:** System-generated reminders for assignments or exams default to `event_time - 7 days`.
* **Origin Integrity:** `origin = 'AUTOMATIC'` designates system-generated defaults (re-calculated if due dates shift). `origin = 'CUSTOM'` designates user-created reminders (immutable trigger times unless explicitly edited by user).

---

# 4. Backend Implementation — Workflow & APIs (SCRUM 80)

## 4.1 Directory Structure

```text
backend/app/modules/reminders/
├── __init__.py
├── models.py
├── schemas.py
├── repository.py
├── service.py
└── router.py

```

## 4.2 Schemas (`schemas.py`)

* `ReminderBase`: `title` (str), `description` (optional str), `trigger_time` (datetime), `trigger_type` (Enum).
* `ReminderCreate(ReminderBase)`: `assignment_id` (optional int), `examination_id` (optional int).
* `ReminderUpdate`: `title` (optional str), `description` (optional str), `trigger_time` (optional datetime), `status` (optional Enum).
* `ReminderResponse(ReminderBase)`: `id`, `student_id`, `assignment_id`, `examination_id`, `origin`, `status`, `processed_at`, `created_at`, `updated_at`.

## 4.3 Service Layer (`service.py`)

Implement the following methods in `ReminderService`:

1. `create_reminder(student_id: int, data: ReminderCreate) -> Reminder`
* Validates that `assignment_id` or `examination_id` (if supplied) belongs to `student_id`.
* Sets `origin = CUSTOM` for API requests.


2. `create_automatic_reminder(student_id: int, entity_type: str, entity_id: int, event_time: datetime, title: str) -> Reminder`
* Calculates `trigger_time = event_time - timedelta(days=7)`.
* Sets `origin = AUTOMATIC`.


3. `get_student_reminders(student_id: int, status_filter: Optional[str]) -> List[Reminder]`
* Returns reminders owned by `student_id` ordered by `trigger_time ASC`.


4. `update_reminder(student_id: int, reminder_id: int, data: ReminderUpdate) -> Reminder`
* Ensures reminder exists and belongs to `student_id`.
* Updates fields and saves.


5. `cancel_linked_reminders(student_id: int, entity_type: str, entity_id: int)`
* Sets status of all `PENDING` linked reminders to `CANCELLED`.


6. `process_due_reminders() -> List[Reminder]`
* Queries all `PENDING` reminders where `trigger_time <= current_utc_time()`.
* Updates status to `PROCESSED` and sets `processed_at = current_utc_time()`.



## 4.4 API Endpoints (`router.py`)

All endpoints require active JWT authentication (`get_current_student`).

| Method | Endpoint | Description | Status Code |
| --- | --- | --- | --- |
| `GET` | `/api/v1/reminders` | Fetch all reminders for logged-in student (optional query `?status=PENDING`) | 200 OK |
| `GET` | `/api/v1/reminders/{id}` | Fetch specific reminder by ID | 200 OK / 404 |
| `POST` | `/api/v1/reminders` | Create custom or linked reminder | 201 Created |
| `PATCH` | `/api/v1/reminders/{id}` | Update title, description, or trigger time | 200 OK / 403 / 404 |
| `DELETE` | `/api/v1/reminders/{id}` | Delete a reminder | 204 No Content |
| `POST` | `/api/v1/reminders/process` | Dev/Demo trigger endpoint to process due reminders manually | 200 OK |

---

# 5. Background Processing Job Implementation (SCRUM 81)

## 5.1 Scheduler File Touchpoint

Location: `backend/app/jobs/scheduler.py` (or `backend/app/jobs/reminder_job.py`).

## 5.2 Job logic

```python
async def process_reminders_job():
    """
    Periodic job executing every 60 seconds.
    Polls pending due reminders and transitions their state atomically.
    """
    db = SessionLocal()
    try:
        service = ReminderService(db)
        processed_count = service.process_due_reminders()
        db.commit()
        logger.info(f"[ReminderJob] Successfully processed {processed_count} due reminders.")
    except Exception as e:
        db.rollback()
        logger.error(f"[ReminderJob] Error during background processing: {str(e)}", exc_info=True)
    finally:
        db.close()

```

## 5.3 Reliability & Isolation Rules

* **No Crash Principle:** Exceptions must be caught, logged, and trigger a database rollback so the FastAPI process and scheduler remain running.
* **Idempotency:** Reminders must transition from `PENDING` to `PROCESSED` in a single transaction to avoid duplicate processing in subsequent runs.

---

# 6. Reminder Integration & Hooks (SCRUM 32)

To satisfy automatic reminder requirements without breaking module boundaries, the `AssignmentService` (or examination module) may invoke `ReminderService` methods using cautious integration points:

## 6.1 Assignment Creation Hook

When an assignment is created:

```python
# In AssignmentService.create_assignment
reminder_service.create_automatic_reminder(
    student_id=student.id,
    entity_type="assignment",
    entity_id=assignment.id,
    event_time=assignment.due_date,
    title=f"Due soon: {assignment.title}"
)

```

## 6.2 Assignment Completion Hook

When an assignment status changes to `COMPLETED`:

```python
# In AssignmentService.mark_completed
reminder_service.cancel_linked_reminders(
    student_id=student.id,
    entity_type="assignment",
    entity_id=assignment.id
)

```

## 6.3 Assignment Due Date Shift

When an assignment due date is modified:

* Update only linked reminders where `origin == AUTOMATIC` and `status == PENDING` to `new_due_date - 7 days`.
* Do **not** modify reminders where `origin == CUSTOM`.

---

# 7. Frontend Implementation — Management UI (SCRUM 79)

## 7.1 Directory Structure

```text
frontend/src/
├── services/
│   └── remindersService.js
└── pages/
    ├── RemindersPage.jsx
    └── components/
        ├── ReminderCard.jsx
        ├── ReminderFormModal.jsx
        └── ReminderList.jsx

```

## 7.2 Service Layer (`remindersService.js`)

```javascript
import api from './api';

export const remindersService = {
  getReminders: async (status = null) => {
    const params = status ? { status } : {};
    const response = await api.get('/api/v1/reminders', { params });
    return response.data;
  },
  
  createReminder: async (reminderData) => {
    const response = await api.post('/api/v1/reminders', reminderData);
    return response.data;
  },

  updateReminder: async (id, updateData) => {
    const response = await api.patch(`/api/v1/reminders/${id}`, updateData);
    return response.data;
  },

  deleteReminder: async (id) => {
    const response = await api.delete(`/api/v1/reminders/${id}`);
    return response.data;
  }
};

```

## 7.3 Page Specification (`RemindersPage.jsx`)

The UI must present a clean, structured interface for student reminder management:

### Core Visual Sections

1. **Header Section:** Title ("Reminders"), total count badge, and `+ Add Reminder` primary button.
2. **Tab / Filter Control:** Filter by `Upcoming` (PENDING), `Processed`, or `All`.
3. **List View (`ReminderList` & `ReminderCard`):**
* **Title & Description:** Clean typography with description text.
* **Trigger Date & Time:** Formatted in local time (e.g., using `date-fns` format `MMM dd, yyyy - hh:mm a`).
* **Context Badge:** Explicit visual tag showing relationship:
* `Assignment: <Title>` (Blue badge)
* `Examination: <Title>` (Purple badge)
* `Custom` (Gray badge)


* **Status Badge:** `Pending` (Yellow), `Processed` (Green), `Cancelled` (Red strikethrough).
* **Actions Menu:** Edit (opens modal) and Delete buttons.


4. **Modal Component (`ReminderFormModal.jsx`):**
* Fields: Title (Input), Description (Textarea), Trigger Date & Time (Datetime picker), Type Selection (`Custom`, `Assignment`, `Examination`).
* Handles both Create (POST) and Edit (PATCH) operations.



---

# 8. AI Agent Self-Verification Checklist

Before submitting code, an AI agent or developer must perform the following self-checks against the repository:

* [ ] **File Isolation:** Did I limit backend creations to `backend/app/modules/reminders/` and frontend creations to `RemindersPage.jsx` and `remindersService.js`?
* [ ] **Model Check:** Is `origin` ('AUTOMATIC' vs 'CUSTOM') included in the SQLAlchemy model and Pydantic schemas?
* [ ] **Default Timing Rule:** Does automatic creation set trigger time to `due_date - 7 days` (not 1 day)?
* [ ] **Ownership Isolation:** Does every query filter by `student_id = current_user.student_id`?
* [ ] **Job Stability:** Does `process_reminders_job` catch all generic exceptions, log errors, rollback the DB session, and leave the app running?
* [ ] **No Notification / E2E Contamination:** Have notification module files and end-to-end integration test suites been kept untouched as instructed?
* [ ] **UI Usability:** Does every reminder item display its associated relationship (Assignment / Examination / Custom) in readable text?