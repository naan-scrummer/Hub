# AIO Student's Hub
## Final Implementation Decisions & Assigned Work Specification

**Repository:** `naan-scrummer/Hub`  
**Product:** AIO Student's Hub  
**Primary user:** Student  
**Implementation focus:** Assigned Jira work items only, plus the minimum supporting functionality required to complete them correctly.

---

# 1. Purpose of This Document

This document establishes the implementation decisions for the current AIO Student's Hub work based on three sources:

1. The assigned Jira work-item export.
2. The supplied `AIO_Students_Hub_Master_Scaffold_Prompt.md`.
3. The current `naan-scrummer/Hub` repository.

The purpose is to remove ambiguity before implementation and provide a concrete plan for completing the assigned work **without redesigning the architecture already established in the repository**.

The assigned Jira scope currently centers on:

- Reminders
- Notifications
- Their integration
- The Assignment → Reminder → Notification end-to-end workflow
- Authentication test coverage

The assigned CSV contains the following concrete work items:

| Jira ID | Work Item |
|---|---|
| SCRUM03-F010 | Reminders epic |
| SCRUM03-F010-UI-001 | Reminder management |
| SCRUM03-F010-BE-001 | Reminder scheduling workflow |
| SCRUM03-F010-JOB-001 | Reminder background processing |
| SCRUM03-F011 | Notifications epic |
| SCRUM03-F011-UI-001 | Notifications center |
| SCRUM03-F011-BE-001 | Notification generation workflow |
| SCRUM03-F011-JOB-001 | Notification background processing |
| SCRUM03-F011-REL-001 | Reminder-to-notification workflow |
| SCRUM03-E2E-001 | Assignment → Reminder → Notification E2E |
| SCRUM03-T-001 | Authentication unit/integration coverage |

The Jira work items explicitly define the Reminder → Notification workflow as:

```text
Reminder Job
    ↓
Notification
    ↓
Notification Job
    ↓
Student
```

and require the Assignment → Reminder → Notification flow to be testable end-to-end.

This document therefore does **not** introduce additional user-facing features merely because they appear elsewhere in the broader product specification.

---

# 2. Already-Decided Architecture

These decisions are considered settled and are **not open for re-discussion** unless a new requirement forces a change.

## 2.1 Application style

The application remains a **modular monolith**.

There will not be separate network services for:

```text
Assignments
Reminders
Notifications
Authentication
```

The repository already follows this direction with feature modules under:

```text
backend/app/modules/
```

including:

```text
assignments/
reminders/
notifications/
authentication/
```

alongside the other established Hub modules. 

---

## 2.2 Backend

The established stack is:

```text
Python
FastAPI
SQLAlchemy 2.x
Alembic
Pydantic
```

The repository README identifies the backend as FastAPI with SQLAlchemy/Alembic and SQLite for development / PostgreSQL for production. 

No framework replacement is required.

---

## 2.3 Frontend

The current repository has already selected:

```text
React 18
Vite
JavaScript / JSX
React Router
Axios
Lucide React
date-fns
```

This supersedes the scaffold prompt's earlier "React or Vanilla JS" choice.

The current repository is therefore the source of truth:

```text
frontend/
└── src/
```

with pages/components/services organized around the established React implementation. 

---

## 2.4 Persistence

Development:

```text
SQLite
```

Production target:

```text
PostgreSQL
```

Database access goes through:

```text
Repository
    ↓
SQLAlchemy
    ↓
Database
```

rather than direct database access from API handlers.

---

## 2.5 Authentication

Authentication is already a cross-cutting foundation.

The repository uses JWT authentication and the architecture specifies protected resources and secure credential handling.  

The user's product decision further establishes:

> Only student mail is allowed, and every student has a unique Hub password different from the college/portal password.

Therefore:

```text
Student college email
        +
Hub-specific password
        ↓
Hub Authentication
```

The Hub password must **not** be assumed to be the college portal password.

The college identity is used as the student's identity key, while Hub authentication remains a separate security boundary.

---

## 2.6 No faculty

There is **no faculty role or faculty workflow** in the current product.

The only relevant account types for the current work are:

```text
Student
Admin
```

and even Admin functionality is not part of the currently assigned Jira scope unless needed as supporting infrastructure.

Any feature logic that assumes faculty-created assignments, faculty dashboards, faculty grading, or faculty uploads is out of scope.

---

## 2.7 Background jobs

The repository already contains:

```text
backend/app/jobs/scheduler.py
```

with an `AsyncIOScheduler` and periodic jobs for:

```text
process_reminders
process_notifications
```

The current implementation runs reminder processing every minute and notification processing every five minutes. 

This means we **do not introduce Celery, Redis, RabbitMQ, Kafka, or another job infrastructure**.

The existing scheduler is the implementation mechanism for the current project.

---

## 2.8 Notification delivery

The first real notification channel is:

```text
In-app notification
```

External push/email services are **not required for the present implementation**.

The architecture should leave room for external delivery later, but the assigned Jira work can be completed without OneSignal, FCM, Resend, SendGrid, or Twilio.

The assigned Jira item explicitly says delivery-channel details beyond in-app handling are future/implementation dependent.

---

# 3. Product Decisions Made for This Implementation

These are decisions supplied by the product owner/team and therefore must guide implementation.

---

## 3.1 Reminder philosophy

Reminders are **fully user-controlled**.

A student may:

- create a reminder directly;
- create one or more reminders for a project/event;
- create one or more reminders for an assignment;
- create one or more reminders for an examination;
- modify reminder timing later.

The system should not impose a single reminder per event.

For example:

```text
Assignment: DBMS Record

Reminder 1
7 days before

Reminder 2
1 day before

Reminder 3
2 hours before
```

all may coexist.

---

## 3.2 Default reminder

When the system automatically creates a reminder for an event, the default is:

```text
1 week before
```

not one day before.

This is an explicit product decision and therefore supersedes the current repository's simplified one-day-before assignment behavior.

The existing AssignmentService currently creates a reminder one day before an assignment is due. 

That behavior must be changed to use the new default:

```text
due_date - 7 days
```

while still allowing the student to add or alter reminders afterward.

---

## 3.3 Multiple reminders

There is no one-to-one assumption between an event and a reminder.

Conceptually:

```text
Assignment
   │
   ├── Reminder A
   ├── Reminder B
   └── Reminder C
```

Likewise:

```text
Examination
   │
   ├── Reminder A
   └── Reminder B
```

A custom event may have:

```text
Custom Event
   │
   ├── Reminder A
   ├── Reminder B
   └── Reminder C
```

Therefore the reminder model should represent:

```text
Event → 0..N Reminders
```

rather than:

```text
Event → exactly 1 Reminder
```

---

## 3.4 Reminder editing

Students must be able to modify a reminder after creation.

At minimum this includes:

```text
Title
Description
Trigger time
Linked context where applicable
```

A reminder does not become immutable merely because it was automatically created.

---

## 3.5 Examination reminders

Examination reminders are supported.

The initial automatic reminder is:

```text
1 week before the examination
```

Students may add additional reminders or change the timing.

---

## 3.6 Assignment reminders

Assignment-linked reminders are supported.

The automatic default is:

```text
1 week before due date
```

Students may:

```text
edit
reschedule
add additional reminders
```

If the assignment is completed before a pending reminder fires:

```text
Assignment = COMPLETED
        ↓
Pending linked reminders no longer produce stale deadline notifications
```

The assigned E2E Jira story explicitly requires this completion-state behavior.

---

## 3.7 Notification preferences

Advanced per-category notification preferences are not a current requirement.

The project's current decision is intentionally simple:

```text
Qualified event
    ↓
Notification generation
    ↓
In-app notification
```

No complex notification-preference engine is required for the assigned work.

---

## 3.8 Dashboard scope for this work

The Dashboard is **not itself an assigned work item in the CSV**, so it should only be touched where required to expose the completed reminder/notification workflow.

We do not redesign the dashboard.

For the assigned work, it is enough for the dashboard/application shell to provide sensible access to:

```text
Pending reminders
Unread notifications
```

only where that already exists in the established application.

---

# 4. Current Repository Baseline

The existing repository already contains the feature modules expected by the architecture, including Assignments, Reminders, Notifications, Authentication and the other established Hub modules. 

The current AssignmentService already demonstrates cross-module integration:

```text
AssignmentService
    ↓
ReminderRepository
```

and currently:

- creates an assignment-linked reminder;
- updates the linked reminder when the due date changes;
- cancels pending reminders when an assignment is completed;
- cancels linked reminders when an assignment is deleted. 

The current Reminder model already supports:

```text
assignment_id
examination_id
trigger_type
trigger_time
status
processed_at
```

with reminder states:

```text
PENDING
PROCESSED
CANCELLED
```

and the Notification model already supports sources such as:

```text
ASSIGNMENT_DEADLINE
REMINDER_TRIGGER
ANNOUNCEMENT
EXAMINATION
PLACEMENT
```

with:

```text
UNREAD
READ
ARCHIVED
```

states.  

Therefore the assigned work is primarily **completion/refinement of an existing architecture**, not a new architectural build.

---

# 5. Important Current-Code Gap

The repository's current implementation contains an architectural direction that needs refinement.

`ReminderService.process_due_reminders()` currently:

1. finds due reminders;
2. marks each reminder processed;
3. directly constructs a `Notification`;
4. writes it to `NotificationRepository`.

In other words, the current path is effectively:

```text
ReminderService
      ↓
NotificationRepository
```

rather than:

```text
ReminderService
      ↓
NotificationService
      ↓
NotificationRepository
```

The assigned Jira requirements explicitly separate Reminder processing from Notification generation and describe:

```text
Reminder Job → Notification → Notification Job → Student
```

Therefore the implementation should preserve module boundaries by moving notification creation behind the NotificationService boundary. 

This is an implementation correction, not a redesign.

---

# 6. Workstream 1 — Reminders

## Jira scope

```text
SCRUM03-F010
SCRUM03-F010-UI-001
SCRUM03-F010-BE-001
SCRUM03-F010-JOB-001
```

---

## 6.1 What the Reminder feature is

A Reminder is a scheduled request for the application to create a student notification when a particular point in time is reached.

It can be:

```text
Custom
Assignment-linked
Examination-linked
```

The user may create multiple reminders for the same event.

---

## 6.2 Reminder data model

The existing model should evolve toward:

```text
Reminder
---------
id
student_id
assignment_id      nullable
examination_id     nullable
title
description
trigger_type
trigger_time
status
processed_at
created_at
updated_at
```

This is already close to the existing repository model. 

### Important rule

A reminder belongs to exactly one student.

The student must never be able to read or modify another student's reminders.

---

## 6.3 Reminder types

Use the existing semantic categories:

```text
ASSIGNMENT_DUE
EXAMINATION
CUSTOM
```

Do not introduce "PROJECT", "EVENT", "ASSIGNMENT", "EXAM", etc. as a large collection of unrelated types unless required.

For generic student-created events:

```text
CUSTOM
```

is sufficient.

---

## 6.4 Reminder creation

Example:

```text
POST /api/v1/reminders
```

Request conceptually:

```json
{
  "title": "DBMS project review",
  "description": "Review normalization notes",
  "trigger_time": "2026-10-12T18:00:00+05:30",
  "trigger_type": "custom"
}
```

For an assignment-linked reminder:

```json
{
  "title": "DBMS assignment reminder",
  "trigger_time": "2026-10-10T18:00:00+05:30",
  "trigger_type": "assignment_due",
  "assignment_id": 42
}
```

For an examination:

```json
{
  "title": "DBMS exam preparation",
  "trigger_time": "2026-10-15T18:00:00+05:30",
  "trigger_type": "examination",
  "examination_id": 12
}
```

---

## 6.5 Reminder validation

The service must reject invalid relationships.

For example:

```text
assignment_id = 42
student_id = Student A
```

but Assignment 42 belongs to Student B.

Result:

```text
Reject
```

A student must only be able to create a linked reminder against data they are authorized to use.

Likewise an examination-linked reminder must not silently point to an unrelated record.

---

## 6.6 Automatic reminder creation

When an assignment is created:

```text
Assignment due date
        ↓
Default automatic reminder
        ↓
Trigger = due date - 7 days
```

When an examination is eligible for automatic reminder creation:

```text
Examination date
        ↓
Default automatic reminder
        ↓
Trigger = exam time/date - 7 days
```

This should happen through service logic rather than frontend logic.

The frontend must never calculate and submit an "automatic reminder" merely to simulate backend behavior.

---

## 6.7 Why automatic reminders belong on the backend

Suppose the browser is closed.

The reminder still needs to exist.

Therefore:

```text
Browser
   X
   │
   │ not required
   ▼
Backend
   ↓
Reminder persisted
```

The reminder is persisted independently of whether the UI remains open.

---

# 7. Workstream 2 — Reminder Management UI

## Jira

```text
SCRUM03-F010-UI-001
```

---

## 7.1 Screen responsibility

The Reminder screen should allow a student to:

```text
View reminders
Create reminders
Edit reminders
```

At minimum the UI must display:

```text
Title
Related item/context
Trigger time
Status
```

---

## 7.2 Relationship display

For an assignment-linked reminder:

```text
Assignment
DBMS Record
Due: Oct 20
Reminder: Oct 13
```

For an examination:

```text
Examination
DBMS End Semester
Reminder: Oct 10
```

For a custom reminder:

```text
Custom
Project review
Reminder: Oct 12
```

This directly satisfies the Jira requirement that an associated relationship be visible when viewing a reminder.

---

## 7.3 Suggested UI structure

```text
Reminders
────────────────────────────────

Upcoming
────────────────────────────────
DBMS Project Review
Oct 12 • 6:00 PM
Custom

DBMS Examination
Oct 15 • 6:00 PM
Linked to Examination

Assignment: DBMS Record
Oct 13 • 8:00 AM
Linked to Assignment
```

A clear create action:

```text
+ Add Reminder
```

should open a form.

---

## 7.4 Reminder editing

Editing should call the backend API.

Example:

```text
PATCH /api/v1/reminders/{id}
```

The backend validates:

```text
student ownership
valid trigger time
valid relationship
```

before persistence.

---

# 8. Workstream 3 — Reminder Scheduling Workflow

## Jira

```text
SCRUM03-F010-BE-001
```

---

## 8.1 What the workflow means

The Reminder API creates/persists the scheduled record.

The system does **not** "wait inside the API request".

Instead:

```text
Create Reminder
      ↓
Persist
      ↓
Return response
      ↓
Later...
      ↓
Background job finds reminder when due
```

This directly satisfies the Jira separation between interactive API work and time-based processing.

---

## 8.2 Due determination

Conceptually:

```text
status = PENDING
AND
trigger_time <= current_time
```

means:

```text
ready for processing
```

The repository already has a `get_pending_due()` style operation for this purpose. 

---

## 8.3 Completion-state rule

For assignment-linked reminders:

```text
Assignment incomplete
    +
Reminder due
    ↓
Process reminder
```

but:

```text
Assignment completed
    ↓
Pending linked reminders cancelled
    ↓
Reminder job ignores cancelled reminder
```

This prevents stale assignment notifications.

The existing AssignmentService already cancels pending reminders upon completion, which is the correct direction. 

---

# 9. Workstream 4 — Reminder Background Job

## Jira

```text
SCRUM03-F010-JOB-001
```

---

## 9.1 Current scheduler

The repository already has:

```text
JobScheduler
```

using:

```text
AsyncIOScheduler
```

and a reminder job running every minute. 

Keep this.

Do not replace it.

---

## 9.2 Job responsibility

The reminder job should do only orchestration:

```text
Start
 ↓
Open database session
 ↓
Invoke ReminderService.process_due_reminders()
 ↓
Commit on success
 ↓
Log result
```

It should not contain business rules such as:

```text
"If assignment then..."
"If exam then..."
```

Those rules belong in application/domain logic.

---

## 9.3 Failure isolation

If one job run fails:

```text
Job failure
   ↓
Rollback
   ↓
Log error
   ↓
Scheduler stays alive
```

The whole FastAPI process should not terminate.

The current scheduler already follows the intended rollback/logging pattern. 

---

# 10. Workstream 5 — Notifications

## Jira

```text
SCRUM03-F011
SCRUM03-F011-UI-001
SCRUM03-F011-BE-001
SCRUM03-F011-JOB-001
SCRUM03-F011-REL-001
```

---

## 10.1 What a notification is

A Notification is the persistent student-facing result of an event that requires attention.

For the assigned work, the important sources are:

```text
Reminder trigger
Assignment deadline
Important announcement
Relevant examination event
Relevant placement event
```

but only documented/implemented triggers should generate notifications.

The Jira story explicitly says there is no requirement for a large rules engine.

---

## 10.2 Notification data

The current model already has:

```text
student_id
source
source_id
title
message
status
read_at
created_at
```

plus source types and notification states. 

Keep this model.

The `source_id` should retain enough context to trace the originating domain object.

---

## 10.3 Notification source

Example:

```text
source = REMINDER_TRIGGER
source_id = 123
```

means:

```text
Notification came from Reminder #123
```

An assignment-related notification may use:

```text
source = ASSIGNMENT_DEADLINE
source_id = 456
```

This allows the notification UI to explain where the notification came from.

---

# 11. Workstream 6 — Notification Generation Workflow

## Jira

```text
SCRUM03-F011-BE-001
```

---

## 11.1 Correct responsibility boundary

The preferred flow is:

```text
ReminderService
      ↓
NotificationService
      ↓
NotificationRepository
```

not:

```text
ReminderService
      ↓
NotificationRepository
```

The current repository's ReminderService directly writes notifications, so this is one of the implementation areas that should be corrected. 

---

## 11.2 NotificationService responsibilities

`NotificationService` should own operations such as:

```text
create_notification()
get_student_notifications()
mark_read()
mark_all_read()
```

and the generation operation should accept the relevant event/context.

For example:

```text
generate_from_reminder(reminder)
```

Conceptually:

```text
Reminder
  ↓
NotificationService
  ↓
Notification
```

---

## 11.3 Irrelevant event rule

Not every event should automatically create a notification.

The notification generator must respect the supported trigger list.

For example:

```text
Routine database maintenance
    ↓
No student notification
```

while:

```text
Reminder reaches trigger
    ↓
Notification
```

This directly satisfies the Jira acceptance criterion that qualifying events generate notifications while non-qualifying events do not.

---

# 12. Workstream 7 — Notification Center

## Jira

```text
SCRUM03-F011-UI-001
```

---

## 12.1 Notification screen

The notification page should retrieve notifications from the backend.

It should not maintain a hardcoded local list.

Conceptually:

```text
GET /api/v1/notifications
```

returns:

```text
Unread
Read
Archived
```

according to the repository's existing status model. 

---

## 12.2 UI states

The notification page must support at least:

### Notifications exist

```text
Notifications

DBMS assignment reminder
Due tomorrow
2 minutes ago

Exam reminder
DBMS exam next week
1 hour ago
```

### No notifications

```text
You're all caught up.

No notifications right now.
```

This directly satisfies the Jira acceptance criteria.

---

## 12.3 Read state

The repository already supports:

```text
UNREAD
READ
ARCHIVED
```

states. 

For the assigned work, the important behavior is:

```text
Unread notification
      ↓
Student views/marks it
      ↓
READ
```

and:

```text
Mark all as read
```

where the current API already supports this concept.

No elaborate notification-preference system is necessary.

---

# 13. Workstream 8 — Notification Background Job

## Jira

```text
SCRUM03-F011-JOB-001
```

---

## 13.1 Why this job exists

The Notification Job exists to keep notification processing/delivery separate from API requests.

The API should not behave like:

```text
Student requests notifications
       ↓
Generate/send every pending notification
       ↓
Then return response
```

Instead:

```text
Background processing
       ↓
Notification work
       ↓
Persist/process
```

and later:

```text
Student
   ↓
GET /notifications
   ↓
Read already-processed notifications
```

---

## 13.2 Current state

The current repository has the notification job registered, but its implementation is effectively a placeholder: it creates a `NotificationService` and logs that the job ran rather than performing meaningful notification processing. 

This is therefore a real completion item.

---

## 13.3 What it should do now

Because the selected product channel is **in-app notification**, the job should remain intentionally simple.

The pipeline can be:

```text
Notification generated
       ↓
Notification persisted
       ↓
Notification Job
       ↓
Process pending notification state
       ↓
Mark delivery-processing state complete
```

The exact persistence state may be implemented minimally.

Do not manufacture a complicated external delivery subsystem when the current requirement is in-app.

---

# 14. Workstream 9 — Reminder → Notification Relationship

## Jira

```text
SCRUM03-F011-REL-001
```

---

## 14.1 Required behavior

When a reminder becomes due:

```text
Reminder status = PENDING
trigger_time <= now
```

then:

```text
Reminder Job
   ↓
ReminderService
   ↓
NotificationService
   ↓
Notification record
```

After processing:

```text
Reminder status = PROCESSED
```

and the student can retrieve the notification.

This exactly corresponds to the Jira acceptance criteria.

---

## 14.2 Recommended implementation sequence

```text
1. Find due reminders
2. For each valid reminder:
      a. verify it is still actionable
      b. generate notification
      c. mark reminder processed
3. Commit transaction
```

The transaction boundary should ensure that the application does not end up with an impossible half-state such as:

```text
Reminder processed
but
Notification never created
```

for a successful workflow.

---

# 15. Workstream 10 — Assignment → Reminder → Notification E2E

## Jira

```text
SCRUM03-E2E-001
```

This is the most important demonstration workflow in the assigned work.

---

## 15.1 Successful scenario

```text
Student
  ↓
Create Assignment
  ↓
Assignment persisted
  ↓
Default reminder scheduled for 1 week before
  ↓
Controlled time reaches trigger
  ↓
Reminder job executes
  ↓
Reminder found as due
  ↓
Notification generated
  ↓
Notification persisted
  ↓
Notification job processes it
  ↓
Student opens Notifications
  ↓
Notification visible
```

---

## 15.2 Completion scenario

Second scenario:

```text
Student creates assignment
      ↓
Reminder created
      ↓
Student marks assignment completed
      ↓
Pending linked reminder cancelled
      ↓
Reminder processing runs
      ↓
No stale deadline notification
```

The Jira E2E story explicitly requires this second behavior.

---

## 15.3 Controlled time

Do not wait a week in a real test.

Use dependency-injected/application-controlled time:

```text
now = controlled test timestamp
```

Example:

```text
Assignment due:
2026-10-20 10:00

Default reminder:
2026-10-13 10:00
```

Test advances logical current time to:

```text
2026-10-13 10:01
```

Then invokes:

```text
process_reminders_job()
```

and verifies the notification.

This makes the test deterministic and fast.

---

# 16. Workstream 11 — Authentication Test Coverage

## Jira

```text
SCRUM03-T-001
```

This work item exists specifically because authentication is foundational to the rest of the application.

---

## 16.1 Unit test coverage

Test authentication logic for:

```text
Valid password
Invalid password
Unknown student email
Expired authentication
Invalid token
```

The exact internal cases can follow the current auth implementation.

---

## 16.2 Protected-resource integration tests

Test that:

```text
No authentication
    ↓
401/appropriate authentication failure
```

and:

```text
Valid student authentication
    ↓
Protected reminder API accessible
```

and:

```text
Student A token
    ↓
Attempt to retrieve Student B reminder
    ↓
Rejected
```

This last case is especially important because reminders and notifications are student-owned records.

---

## 16.3 Student-email restriction

The authentication tests should also verify the product rule:

```text
allowed student email
      ↓
accepted
```

while:

```text
non-student email
      ↓
rejected
```

provided this restriction has been encoded in the chosen registration/authentication flow.

---

# 17. Reminder and Notification API Responsibilities

The exact API routes may remain consistent with the existing repository.

## Reminder APIs

Current documented shape includes:

```text
GET  /api/v1/reminders
POST /api/v1/reminders
POST /api/v1/reminders/process
```

The internal/manual processing endpoint exists in the repository README and can remain useful for development/demo. 

For production-like behavior, however:

```text
scheduler
```

should be the normal execution mechanism.

---

## Notification APIs

Current documented shape includes:

```text
GET  /api/v1/notifications
POST /api/v1/notifications/{id}/read
POST /api/v1/notifications/read-all
```

These align naturally with the notification-center requirement. 

---

# 18. Data Flow

## Create reminder

```text
React Reminder Form
      ↓
Axios API Service
      ↓
POST /reminders
      ↓
Reminder Route
      ↓
ReminderService
      ↓
ReminderRepository
      ↓
SQLite/PostgreSQL
```

---

## Process reminder

```text
APScheduler
      ↓
process_reminders_job
      ↓
ReminderService
      ↓
ReminderRepository
      ↓
Find due reminders
      ↓
NotificationService
      ↓
NotificationRepository
      ↓
Notification record
```

---

## Read notifications

```text
React NotificationsPage
      ↓
Axios
      ↓
GET /notifications
      ↓
Notification Route
      ↓
NotificationService
      ↓
NotificationRepository
      ↓
Response
      ↓
React UI
```

---

# 19. Entity Relationship Decisions

For the assigned scope:

```text
StudentProfile
    │
    ├──────────────< Reminder
    │                  │
    │                  ├── assignment_id
    │                  └── examination_id
    │
    └──────────────< Notification
```

And:

```text
Assignment
    │
    └──────────────< Reminder
```

The current repository already models Assignment → Reminder as a one-to-many relationship. 

This is correct and should be preserved.

---

# 20. Important Reminder Relationship Decision

A custom event/project is currently **not a separate domain module**.

Therefore:

```text
Custom Reminder
```

does not require a new `Project` or `Event` entity unless another assigned Jira requirement introduces one.

This follows the instruction to avoid inventing major user-facing features outside the assigned scope.

For now:

```text
trigger_type = CUSTOM
assignment_id = NULL
examination_id = NULL
```

is sufficient.

---

# 21. Default-vs-Custom Reminder Behavior

The distinction should be explicit.

## Automatically created

```text
Assignment created
       ↓
Default reminder:
due date - 7 days
```

## Student-created

```text
Student chooses:
trigger date/time
```

## Multiple reminders

```text
Student adds more
```

This results in:

```text
Automatic reminder
+
Zero or more user-created reminders
```

The system must **not delete the automatic reminder simply because the student creates another reminder**, unless the student explicitly edits/deletes it.

---

# 22. Reminder Update Rules

## Assignment due date changes

If the automatically associated reminder is still pending and is still recognized as the automatic/default reminder:

```text
old due date
      ↓
new due date
      ↓
recalculate default reminder
```

However, a student-created custom reminder should **not automatically move just because the assignment due date changes** unless the product explicitly treats it as tied to the due date.

This means we should distinguish automatic/default reminders from independently customized reminders.

A practical implementation is to add a field such as:

```text
origin
```

or equivalent semantic metadata:

```text
AUTOMATIC
CUSTOM
```

This is a small model refinement justified by your requirement for editable/customizable reminders.

---

# 23. Why Reminder Origin Matters

Consider:

```text
Assignment due Oct 20

Automatic reminder:
Oct 13

Student custom reminder:
Oct 17
```

If the assignment changes to Oct 25:

The correct behavior is likely:

```text
Automatic reminder:
→ Oct 18

Custom reminder:
→ remains Oct 17
```

Otherwise the user loses control of their explicitly chosen schedule.

Therefore the implementation must distinguish:

```text
system-generated reminder
```

from:

```text
student-created reminder
```

---

# 24. Notification Idempotency

The reminder processor must not generate duplicate notifications if the same reminder is encountered more than once.

Example failure:

```text
Job run 1
Reminder found
Notification created

Job run 2
Reminder accidentally still appears due
Notification created again
```

Result:

```text
Duplicate notifications
```

The reminder state transition:

```text
PENDING → PROCESSED
```

must therefore be reliable and atomic enough for the current single-application scheduler.

At minimum, notification generation should occur only for actionable pending reminders.

---

# 25. Transaction Boundary

For the reminder→notification operation:

```text
begin transaction

load pending reminder

generate notification

mark reminder processed

commit
```

On failure:

```text
rollback
```

This is preferable to:

```text
mark processed
commit

then create notification
```

because the latter can lose the notification if notification creation fails.

The current scheduler already uses a database session and rollback on job failure. 

The service-level transaction design should align with that pattern.

---

# 26. Error Handling

## Reminder creation errors

Examples:

```text
Invalid trigger time
Invalid linked assignment
Invalid linked examination
Unauthorized linked resource
```

return safe client-facing errors.

---

## Reminder processing error

A job failure should:

```text
log structured error
rollback transaction
keep scheduler alive
```

not crash the application.

This is explicitly required by the Jira work item.

---

## Notification generation error

If notification creation fails:

```text
Do not silently mark the reminder processed.
```

The system should preserve enough state for the next job execution to retry safely.

---

# 27. Notification Job Strategy

Since the current channel is in-app only, the second-stage notification job should remain simple.

Possible state progression:

```text
Notification
status = UNREAD
```

For the current project, this is enough for the student-facing state.

The "notification job" can be interpreted as the separate background-processing boundary required by Jira rather than a complex third-party delivery queue.

This keeps:

```text
notification generation
```

separate from:

```text
background notification processing
```

without adding unnecessary infrastructure.

---

# 28. Manual Processing for Demonstration

The existing system has manual processing API endpoints such as:

```text
POST /api/v1/reminders/process
```

These are useful for development and demonstration.

They should remain available only as an explicit processing hook, while the normal production-like flow remains:

```text
APScheduler
```

This is particularly useful for demonstrating the assigned E2E story:

```text
Create assignment
   ↓
Set test/demo reminder to near-current time
   ↓
Trigger processing
   ↓
Notification appears
```

No need to wait for the real scheduler interval during a classroom demonstration.

---

# 29. Testing Matrix

## Reminder UI

Test:

```text
Create reminder
Display reminder
Display relationship
Edit reminder
```

---

## Reminder service

Test:

```text
Create custom reminder
Create assignment-linked reminder
Create examination-linked reminder
Find pending due reminders
Reject unauthorized relationships
```

---

## Assignment/reminder relationship

Test:

```text
Create assignment
→ default reminder exists

Change assignment due date
→ automatic reminder adjusts

Complete assignment
→ pending reminder is cancelled
```

---

## Reminder job

Test:

```text
Due reminder
→ processed

Future reminder
→ not processed

Cancelled reminder
→ not processed

Job failure
→ rollback + scheduler remains stable
```

---

## Notification service

Test:

```text
Generate reminder notification
Retrieve student notifications
Mark one read
Mark all read
```

---

## Notification job

Test:

```text
Job executes independently of API request
Job failure does not crash application
```

---

## E2E

Test:

```text
Assignment
→ Reminder
→ Reminder Job
→ Notification
→ Notification Job
→ Notification Center
```

and:

```text
Assignment
→ Reminder
→ Assignment completed
→ No notification
```

---

## Authentication

Test:

```text
Valid student
Invalid password
Unknown email
Protected API
Unauthorized resource
```

The latter is important because reminder/notification data is student-private.

---

# 30. Frontend API Separation

React components should not directly build URLs throughout the UI.

Use the existing service layer:

```text
frontend/src/services/
```

and feature-specific API functions.

Conceptually:

```text
remindersService
notificationsService
authService
```

Then:

```text
RemindersPage
   ↓
remindersService
   ↓
Axios
   ↓
FastAPI
```

This matches the scaffold's API service-layer principle and the current repository organization. 

---

# 31. Frontend State

Do not introduce Redux merely for reminders/notifications.

For this scope:

```text
React component state
+
existing auth context
+
API service calls
```

is enough.

Notification unread count can be refreshed from the existing notification API when required.

A global notification state architecture is not necessary unless the existing application already implements one.

---

# 32. Notification Center UX

The UI should visually distinguish:

```text
Unread
```

from:

```text
Read
```

but should remain simple.

Suggested structure:

```text
Notifications

[Unread]
Assignment due tomorrow
DBMS Record
Today, 10:30 AM

[Read]
Exam reminder
DBMS End Semester
Yesterday
```

A global:

```text
Mark all as read
```

action can remain available.

---

# 33. Reminder UI UX

Suggested structure:

```text
Reminders

Upcoming
───────────────────────
DBMS Record
Oct 13, 8:00 AM
Assignment

DBMS Exam
Oct 15, 6:00 PM
Examination

Project Review
Oct 18, 4:00 PM
Custom
```

Add:

```text
+ Add reminder
```

and edit capability.

The relationship should be human-readable rather than exposing raw IDs.

---

# 34. Time and Timezone

The project decision is:

```text
Backend
    ↓
UTC-oriented persistence where appropriate

Frontend
    ↓
Convert/display in India Standard Time / application local time
```

The current test and application logic should use timezone-aware timestamps where practical.

For the assigned feature, the main requirement is **deterministic time handling**, particularly for reminder processing tests.

Avoid scattering:

```text
datetime.utcnow()
```

through every service.

The existing code currently does this in both assignment and reminder services, so this should be gradually centralized during implementation.  

---

# 35. Staleness

Your decision applies to synchronized college data generally:

```text
Show cached data
+
show last-sync timestamp
+
use a configured staleness threshold
```

This is not directly part of the assigned Reminder/Notification work and therefore does not require implementation here except where existing application infrastructure is touched.

No new sync architecture should be introduced as part of these Jira stories.

---

# 36. College Portal Links

You decided that external portal functionality can initially be represented by routing the relevant site inside the frontend section rather than implementing real backend synchronization.

That applies to the broader product.

It does **not** become part of the assigned Reminder/Notification work unless an assigned item explicitly depends on it.

Therefore do not introduce new portal integration work into these Jira stories.

---

# 37. Admin

Admin is a supporting role, not part of the assigned feature scope.

Do not create a broad admin dashboard simply because an admin role exists.

Admin APIs can exist where needed for future moderation/management, but they should not absorb implementation time from the assigned stories.

---

# 38. Out-of-Scope for This Work

Explicitly excluded unless an assigned Jira dependency forces them:

```text
Faculty workflows
Faculty assignment creation
Faculty portals
AI features
Question-paper prediction
Email delivery
SMS delivery
Push delivery
OneSignal integration
FCM integration
Resend integration
SendGrid integration
Twilio integration
Redis
Celery
Kafka
RabbitMQ
Microservices
Cloud storage
Complex notification preference engine
New project-management module
Generic event-management module
```

These are intentionally not introduced merely for completeness.

---

# 39. Safe Implementation Choices

The following are implementation details that can be chosen without reopening product architecture.

## 39.1 Reminder origin

Add:

```text
AUTOMATIC
CUSTOM
```

or equivalent metadata.

Reason:

Your product requires both automatic defaults and user-defined custom reminders.

---

## 39.2 Notification delivery state

A minimal internal state can be added if needed to distinguish:

```text
generated
processed
```

without introducing external delivery services.

---

## 39.3 Repository query methods

Add methods such as:

```text
get_pending_due()
get_by_assignment()
get_by_examination()
get_by_student()
```

where needed.

The repository pattern is already established.

---

## 39.4 Service dependency direction

Prefer:

```text
ReminderService
      ↓
NotificationService
```

and avoid direct use of another module's repository from the ReminderService.

This is a safe architectural refinement within the existing design.

---

# 40. Recommended Completion Order

The assigned work should be implemented in this order:

```text
1. Verify authentication foundation
        ↓
2. Add/adjust reminder data semantics
        ↓
3. Complete ReminderService
        ↓
4. Complete Reminder API
        ↓
5. Complete Reminder UI
        ↓
6. Implement default 7-day reminder behavior
        ↓
7. Support custom/multiple reminders
        ↓
8. Correct Assignment ↔ Reminder integration
        ↓
9. Complete reminder background job
        ↓
10. Refine NotificationService
        ↓
11. Refactor Reminder → Notification through service boundary
        ↓
12. Complete Notification API/UI
        ↓
13. Complete notification background job
        ↓
14. Implement reminder → notification workflow test
        ↓
15. Implement Assignment → Reminder → Notification E2E
        ↓
16. Implement authentication tests
        ↓
17. Run full test suite
        ↓
18. Run manual demo
```

---

# 41. Definition of Done for the Assigned Scope

The assigned work is complete only when the following are true.

## Reminders

- A student can create a reminder.
- A student can see reminders.
- A student can edit a reminder.
- Multiple reminders can exist for the same event.
- Assignment-linked reminders work.
- Examination-linked reminders work.
- Custom reminders work.
- Reminder relationships are visible.
- Default automatic reminders use one week before.
- Custom reminder timings remain user-controlled.

## Reminder jobs

- Due reminders are processed by background work.
- Future reminders remain pending.
- Cancelled reminders are ignored.
- Job failures do not crash the application.
- Job failures are logged.

## Notifications

- Qualified events produce notifications.
- Notifications contain source/event context.
- Students can retrieve notifications.
- Read/unread behavior works.
- Empty notification state works.
- Notification background processing is separate from API requests.

## Integration

The following must be demonstrable:

```text
Assignment
   ↓
Reminder
   ↓
Reminder Job
   ↓
Notification
   ↓
Notification Job
   ↓
Notification Center
```

## Authentication

- Valid student authentication works.
- Invalid authentication fails safely.
- Protected reminder/notification resources require authentication.
- Students cannot access another student's private reminder/notification data.
- Authentication unit/integration tests pass.

---

# 42. Final Architecture for the Assigned Work

The final intended flow is:

```text
                         STUDENT
                            │
                            ▼
                     React Frontend
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
          Reminder UI              Notification UI
                │                       │
                ▼                       ▼
         Reminder API             Notification API
                │                       │
                ▼                       ▼
        ReminderService         NotificationService
                │                       │
                ▼                       ▼
        ReminderRepository       NotificationRepository
                │                       │
                └──────────┬────────────┘
                           ▼
                         Database
```

Background processing:

```text
                    APScheduler
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      Reminder Job             Notification Job
             │
             ▼
      ReminderService
             │
             ▼
     NotificationService
             │
             ▼
     NotificationRepository
```

Assignment integration:

```text
AssignmentService
        │
        ▼
ReminderService
        │
        ▼
ReminderRepository
```

Important architectural rule:

```text
API
 ↓
Service
 ↓
Repository
```

and:

```text
Job
 ↓
Service
```

not:

```text
API
 ↓
SQL

Job
 ↓
SQL
```

and not:

```text
ReminderService
 ↓
NotificationRepository
```

when NotificationService is the established application boundary.

---

# 43. Final Decision Summary

## Already decided

```text
FastAPI
React + JavaScript
SQLAlchemy
Alembic
SQLite dev
PostgreSQL prod
Modular monolith
Repository pattern
Service layer
APScheduler
In-app notification
Student-first product
No faculty
No unnecessary infrastructure
Current repository is authoritative
```

## Product decisions

```text
Student college email is the identity
Hub password is unique/different from portal password
Students own their reminders
Students may create multiple reminders
Students may modify reminder timing
Default automatic reminder = 1 week before
Exam reminders supported
Assignment reminders supported
Custom reminders supported
In-app notifications first
External notification providers later
Browser/site routing may be used for portal access
Local file storage
Simple material search
No faculty involvement
No additional broad feature scope
Primary optimization = convincing working demo
```

## Safe implementation decisions

```text
Separate automatic vs custom reminder origin
Use service-to-service orchestration
Keep notification generation inside NotificationService
Use transaction-safe reminder → notification processing
Use controlled application time in tests
Keep APScheduler
Keep manual process hooks for demonstration
Preserve current module/folder architecture
Add only the minimal model/query methods required
```

---

# 44. Implementation Principle Going Forward

For these Jira items, the objective is not to build a larger system.

The objective is to make the **existing AIO Student's Hub architecture behave correctly**.

The most important demonstrable slice is therefore:

```text
Student logs in
      ↓
Creates assignment
      ↓
Automatic one-week reminder exists
      ↓
Student can add/edit additional reminders
      ↓
Reminder reaches trigger time
      ↓
Background job processes reminder
      ↓
NotificationService creates notification
      ↓
Notification job processes it
      ↓
Student opens Notifications
      ↓
Notification is visible
```

and:

```text
Student completes assignment first
      ↓
Reminder is cancelled
      ↓
Reminder job does not generate stale notification
```

That is the implementation spine around which the currently assigned Jira work should be completed.