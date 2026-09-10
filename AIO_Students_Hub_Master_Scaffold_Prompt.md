# AIO STUDENT'S HUB — MASTER SCAFFOLD BUILDER PROMPT

## PURPOSE

Build the **foundation of AIO Student's Hub** from the supplied Jira work-item specification.

This prompt is intentionally project-specific. It is not a generic dashboard-builder prompt.

The objective is to create a **runnable, coherent, extensible scaffold** in which:

- every Jira feature has a defined place in the architecture;
- every cross-module relationship has a defined contract;
- database entities and relationships exist;
- repositories, services, schemas, APIs, UI routes/components, integration adapters, background-job boundaries, and tests are present;
- representative functionality is implemented end-to-end;
- remaining work can be completed later by extending the existing modules rather than redesigning the architecture.

The scaffold must be designed so that the **only significant work remaining later is completion/refinement of final feature functionality**, not restructuring the application.

Do not build a generic admin dashboard and do not replace the Student Hub domain with generic entities such as "Projects", "Reports", or "Revenue".

---

# 1. SOURCE OF TRUTH

Use the supplied Jira work-item list as the **functional source of truth**.

The Jira backlog contains:

- **11 feature epics**
- **48 non-epic work items**
- authentication, dashboard, attendance, academics, examinations, announcements, placements, study materials, assignments, reminders, notifications;
- four explicitly documented end-to-end workflows;
- three explicitly documented test work items.

Requirement IDs must be preserved in implementation notes, tests, comments, or a traceability document where useful.

Do not silently discard a Jira requirement.

Do not invent major user-facing features that are not required by the Jira source.

When an implementation detail is unspecified by Jira, choose the **simplest implementation that preserves the stated behavior and module boundaries**.

When a requirement is genuinely ambiguous and the choice could materially change architecture, stop and use the Decision Gate defined later.

---

# 2. TECHNOLOGY — SOURCE OF TRUTH

The user must choose the frontend before implementation.

```yaml
Backend: Python
API: FastAPI
Frontend: CHOOSE_ONE
  - Vanilla JavaScript
  - React
Frontend Language:
  - JavaScript for both choices
Icons: Lucide Icons only
Database: SQLite for development / PostgreSQL for production
ORM: SQLAlchemy 2.x
Migrations: Alembic
Validation / API Schemas: Pydantic
Repository Pattern: Explicit repository classes
Testing: pytest for backend; browser/system testing appropriate to the chosen frontend
Authentication: Secure session/token mechanism appropriate to the selected stack, with prototype-safe local configuration
Local Execution: Native development environment by default
Logging: Structured JSON application logs to stdout/stderr
```

Rules:

1. The values above are authoritative.
2. Do not silently substitute another framework.
3. Do not add Redux, GraphQL, Django, Flask, another frontend framework, TypeScript, Kafka, Celery, Redis, RabbitMQ, Kubernetes, Terraform, cloud infrastructure, or similar infrastructure unless a real requirement exists and the decision gate permits it.
4. A library may be added when it directly supports an existing requirement and materially reduces implementation complexity.

---

# 3. DEVELOPMENT ROLE

The selected engineering role controls how much implementation ownership the builder takes.

## Junior Software Engineer

- Prefer straightforward, readable code.
- Use existing conventions.
- Avoid unnecessary abstraction.
- Ask before consequential architectural decisions.

## Senior Software Engineer

- Own implementation details.
- Consider maintainability, correctness, testing, security, and failure handling.
- Ask before major product or architecture changes.

## Software Architect

- Explicitly reason about module boundaries, dependencies, data flow, integrations, persistence, testing, and deployment.
- Keep architecture proportional to the project.
- Do not introduce enterprise infrastructure without a requirement.

---

# 4. PROJECT IDENTITY

## Product

**AIO Student's Hub**

## Primary user

Student.

## Product purpose

Provide a centralized student-facing hub that brings together:

- authentication;
- dashboard attention items;
- attendance;
- academic information;
- examinations;
- announcements;
- placements;
- study materials;
- assignments;
- reminders;
- notifications.

The application must behave as **one integrated product**, not as eleven unrelated CRUD pages.

---

# 5. CORE ARCHITECTURAL PRINCIPLE

The architecture must follow:

```text
Frontend
   ↓
API
   ↓
Application Service
   ↓
Repository
   ↓
SQLAlchemy ORM
   ↓
Database
```

For integrations:

```text
Application Service
   ↓
Integration Interface
   ↓
Concrete Portal/Source Adapter
   ↓
External or Mocked Source
```

For background processing:

```text
Domain event / scheduled state
   ↓
Job boundary
   ↓
Application service
   ↓
Persistence / notification result
```

For the Student Hub dashboard:

```text
Dashboard API
   ↓
Dashboard aggregation service
   ↓
Existing feature services
   ↓
Their repositories
   ↓
Database / synchronized source data
```

The Dashboard must **aggregate existing domain modules**. It must not become the owner of attendance, assignments, examinations, notifications, etc.

---

# 6. DOMAIN MODULES

Create explicit modules for:

```text
authentication/
dashboard/
attendance/
academics/
examinations/
announcements/
placements/
study_materials/
assignments/
reminders/
notifications/
integrations/
jobs/
```

Shared infrastructure should live separately:

```text
core/
db/
logging/
schemas/
common/
```

Do not create one huge `models.py`, one huge `services.py`, or one huge route file.

Do not create meaningless generic repositories such as `DashboardRepository` when the dashboard is only an aggregation layer and does not own dashboard data.

---

# 7. DOMAIN MODEL — FOUNDATION

The scaffold must create a coherent relational model.

At minimum model the concepts represented by the Jira requirements.

Recommended foundation entities:

```text
User
StudentProfile

Subject

AttendanceRecord

AcademicRecord
AcademicMark / InternalMark where required by the source

Examination

Announcement
AnnouncementSource

PlacementOpportunity
Company
PlacementContribution

StudyMaterial

Assignment

Reminder

Notification

PortalSource / IntegrationSource
SyncRun
```

Use foreign keys and relationships that reflect the real domain.

Do not create relationships merely to make the ER diagram look impressive.

---

# 8. DOMAIN RELATIONSHIPS

At minimum support these relationships:

```text
User
  └── StudentProfile

StudentProfile
  ├── Assignments
  ├── Reminders
  ├── Notifications
  ├── Attendance records
  ├── Academic records
  ├── Examination information
  └── placement-related information where applicable

Subject
  ├── Attendance records
  ├── Academic records
  ├── Assignments
  └── Study materials
```

Documented cross-module relationships:

```text
Assignment
   ↓
Reminder
   ↓
Notification
```

```text
Assignment
   ↓
Subject / academic context
   ↓
Study Materials
```

```text
Portal Source
   ↓
Integration Adapter
   ↓
Synchronization
   ↓
Domain Service
   ↓
Persistence
   ↓
API
   ↓
Student UI
```

The specific portal workflows explicitly required are:

```text
Portal → Attendance → Student
Portal → Examinations → Student
Portal → Academics → Student
Portal → Announcements → Student
Portal → Placements → Student
```

Not every module needs a real external portal implementation in the scaffold. The integration boundary must exist, and the testable/mock adapter must make the flow demonstrable.

---

# 9. DATA OWNERSHIP RULE

Each module owns its own domain behavior.

Examples:

```text
Assignments
    owns:
    - assignment fields
    - completion status
    - due-date classification

Reminders
    owns:
    - trigger time
    - reminder scheduling/processing

Notifications
    owns:
    - notification records
    - notification generation rules
    - notification retrieval
```

Never move reminder processing into assignment routes.

Never move notification generation into the assignment UI.

Never make the Dashboard directly query every table when existing services can provide the required information.

---

# 10. API CONTRACT PRINCIPLES

The frontend must communicate through API contracts.

Do not hardcode feature results into the frontend.

API routes should handle:

- HTTP concerns;
- validation;
- authentication/authorization;
- calling application services;
- returning response schemas.

Routes must not contain substantial SQL or business logic.

Use request/response Pydantic schemas.

Keep internal ORM models separate from external API schemas where appropriate.

---

# 11. AUTHENTICATION FOUNDATION

Authentication is a foundational cross-cutting concern.

Required foundation:

```text
Login
Authentication state
Logout
Protected resources
Authorization checks
Secure credential handling
```

The scaffold must support:

```text
Unauthenticated user
       ↓
Login
       ↓
Authenticated session
       ↓
Protected application
       ↓
Logout
       ↓
Unauthenticated state
```

The current project is a student-facing prototype, but credentials must still be handled safely.

Never:

- store plaintext passwords;
- log passwords;
- log access tokens;
- expose secrets to the frontend unnecessarily;
- put authentication logic into arbitrary feature modules.

Provide a clear authentication service and protected-route/API dependency mechanism.

Seed a deterministic demo student account through development configuration.

Document the demo credentials safely in development documentation only; never treat them as production credentials.

---

# 12. APPLICATION SHELL

After successful authentication, provide the student application shell.

Required structural areas:

```text
Sidebar
Header / top navigation
Main content area
```

Primary navigation must cover:

```text
Dashboard
Attendance
Academics
Examinations
Announcements
Placements
Study Materials
Assignments
Reminders
Notifications
```

Settings may exist only when supported by the implementation; do not create an empty settings feature merely for visual completeness.

Use Lucide icons only.

Never use emoji in the interface.

---

# 13. DASHBOARD

The Dashboard is an aggregation/presentation layer.

It must expose a consolidated student overview containing relevant information from:

- assignments;
- examinations;
- announcements;
- attendance;
- academic information;
- reminders;
- notifications;
- placement information.

The Dashboard must not duplicate business logic from these modules.

Implement:

```text
Dashboard aggregation service
        ↓
feature-specific services
        ↓
feature repositories
```

The initial scaffold should expose deterministic seeded data so the dashboard is meaningful immediately.

The dashboard must include useful attention-oriented sections rather than generic business KPIs such as Revenue or Conversion Rate.

Appropriate examples:

```text
Upcoming assignments
Overdue assignments
Upcoming examinations
Recent announcements
Attendance summary
Academic summary
Pending reminders
Unread notifications
Placement updates
```

Charts may be used when they communicate student data meaningfully, but charts are not a requirement by themselves.

---

# 14. ATTENDANCE

Required capability:

- view attendance by subject;
- show classes attended;
- show total classes;
- show attendance percentage;
- process synchronized source data;
- expose unavailable state when synchronization/source retrieval fails.

Architectural flow:

```text
Portal Adapter
   ↓
Attendance Synchronization Service
   ↓
Attendance Application Service
   ↓
Attendance Repository
   ↓
AttendanceRecord
   ↓
Attendance API
   ↓
Student UI
```

Do not put portal-specific parsing into the Attendance UI.

Use representative/mock source data for the scaffold and tests.

---

# 15. ACADEMICS

Required capability:

- subject information;
- internal marks / academic performance information;
- other academic records required by the source;
- source synchronization boundary.

Architectural flow:

```text
Portal Adapter
   ↓
Academic Synchronization Service
   ↓
Academic Application Service
   ↓
Academic Repository
   ↓
Academic Records
   ↓
API
   ↓
UI
```

Keep source-specific logic inside integrations.

---

# 16. EXAMINATIONS

Required capability:

- examination schedule;
- examination dates;
- examination-related information;
- synchronized examination information;
- unavailable state when synchronization fails.

Architectural flow:

```text
Portal Adapter
   ↓
Examination Synchronization Service
   ↓
Examination Service
   ↓
Repository
   ↓
Examination records
   ↓
API
   ↓
UI
```

Do not couple the UI directly to portal-specific implementations.

---

# 17. ANNOUNCEMENTS

Required capability:

- unified announcement feed;
- college notices;
- department announcements;
- examination notices;
- academic deadlines;
- events;
- administrative updates;
- source traceability;
- timestamp traceability.

Model source/timestamp metadata explicitly.

A useful conceptual model is:

```text
Announcement
 ├── title
 ├── content
 ├── published_at
 ├── source
 └── source_reference / source identifier where appropriate
```

The final schema may differ, but source and timestamp traceability must remain available.

Architecture:

```text
Source / Portal
   ↓
Announcement Adapter
   ↓
Aggregation + Normalization Service
   ↓
Repository
   ↓
Announcement
   ↓
API
   ↓
Feed UI
```

Do not require a live external portal for tests.

Use deterministic mock source data.

---

# 18. PLACEMENTS

Required capability:

- placement opportunities;
- company information;
- eligibility requirements;
- recruitment updates;
- important dates;
- preparation resources;
- interview experiences;
- placement-system synchronization;
- senior-student contributions.

Model the distinction between synchronized placement information and student-contributed experiences/resources.

Do not assume every student can modify synchronized company records.

The scaffold should support contribution boundaries and authorization.

---

# 19. STUDY MATERIALS

Required capability:

- browse materials;
- search materials;
- filter materials;
- associate materials with subjects/academic context;
- permitted contributions/uploads;
- discover related materials from assignment context.

Important relationship:

```text
Assignment
   ↓
Subject / academic context
   ↓
Related Study Materials
```

Do not hardcode a special assignment-to-materials path that bypasses the Study Materials service.

The relation should be queryable through the materials domain/application layer.

For the scaffold, file upload may be represented by a storage abstraction and local development implementation. Do not introduce cloud storage unless requested.

---

# 20. ASSIGNMENTS

Assignments are a central student-owned domain.

Required capability:

```text
Create
Read
Update
Delete
```

Store at minimum:

```text
due date
subject
description
completion status
student ownership
```

Support state classification:

```text
Upcoming
Overdue
Completed
```

Do not duplicate reminder rules in assignment UI code.

Assignment owns assignment state.

Reminder processing owns time-based reminder behavior.

Important integration:

```text
Create assignment
    ↓
Persist assignment
    ↓
Create/update reminder relationship
```

When due date changes:

```text
Assignment update
    ↓
Reminder relationship update
```

When assignment is completed:

```text
Assignment completed
    ↓
Reminder processing respects completion state
```

Exact cancellation/rescheduling implementation may be chosen by the builder, but module boundaries must remain intact.

---

# 21. REMINDERS

Required capability:

- create reminders;
- view reminders;
- associate reminders with supported entities;
- schedule/recognize trigger time;
- process reminders independently from API requests.

Reminder may be directly student-created or associated with:

- assignments;
- examinations;
- important deadlines;
- other student-created events supported by the source.

Do not force unrelated fields into the reminder model.

Background work belongs to the Jobs boundary.

---

# 22. NOTIFICATIONS

Required capability:

- notification records;
- notification center;
- empty state;
- notification generation from supported academic events;
- reminder-to-notification flow;
- background processing boundary.

Documented notification sources include:

```text
Assignment deadlines
Reminder triggers
Important announcements
Other relevant documented academic events
```

Do not build a large rules engine unless required.

The important flow is:

```text
Reminder Job
     ↓
Notification generation
     ↓
Notification record
     ↓
Notification Job / processing boundary
     ↓
Student retrieves notification
```

For the initial scaffold, the student-facing delivery channel is **in-app notification**.

Do not invent email/SMS/push infrastructure.

---

# 23. BACKGROUND JOB ARCHITECTURE

The requirements explicitly call for reminder and notification background processing.

The builder must therefore create a **job boundary**, while keeping infrastructure minimal.

Required logical jobs:

```text
process_due_reminders()
process_pending_notifications()
```

Jobs must:

- run independently of an API request;
- be testable;
- handle individual failures without crashing the whole application;
- emit useful structured logs;
- use application services rather than duplicating domain logic.

The exact scheduler mechanism is implementation-specific.

For the scaffold, prefer the simplest local approach that demonstrates the architecture.

Do not introduce Redis/Celery/RabbitMQ/Kafka merely because the project has background work.

Design job functions/classes so a production scheduler can invoke them later without changing domain logic.

---

# 24. PORTAL INTEGRATION ARCHITECTURE

All external college-system access must go through explicit integration boundaries.

Create an interface/protocol/abstract adapter concept such as:

```text
CollegePortalClient
```

and separate adapters for domains as needed:

```text
AttendancePortalAdapter
AcademicPortalAdapter
ExaminationPortalAdapter
AnnouncementPortalAdapter
PlacementPortalAdapter
```

These may share a lower-level client only when that reduces duplication without coupling domain logic.

For development and testing:

```text
MockCollegePortalAdapter
```

must provide deterministic representative data.

Do not make the core application depend directly on HTTP calls to a real college portal.

Portal-specific details must remain in infrastructure/integration code.

---

# 25. SYNCHRONIZATION MODEL

Provide a synchronization abstraction.

Conceptually:

```text
Source
  ↓
Fetch
  ↓
Validate
  ↓
Normalize
  ↓
Persist
  ↓
Record SyncRun
```

A `SyncRun` should make it possible to understand:

```text
what source was synchronized
when it ran
whether it succeeded
whether it failed
basic result/error information
```

Do not store secrets or raw credentials in logs.

The scaffold must support an unavailable/failure state in UI for source-dependent features.

---

# 26. DATABASE RULES

Use:

```text
SQLite
```

for development.

Use:

```text
PostgreSQL
```

for production configuration.

Use:

```text
DATABASE_URL
```

for configuration.

Never hardcode database credentials.

Use SQLAlchemy 2.x typed declarative models.

Use Alembic migrations.

Do not use `create_all()` as the production schema migration strategy.

The business/service/repository layers must remain portable between SQLite and PostgreSQL as far as practical.

Do not add PostgreSQL infrastructure to local development unless requested.

---

# 27. REPOSITORY RULES

Every persistent domain must expose repository classes.

Examples:

```text
UserRepository
AttendanceRepository
AcademicRepository
ExaminationRepository
AnnouncementRepository
PlacementRepository
StudyMaterialRepository
AssignmentRepository
ReminderRepository
NotificationRepository
SyncRunRepository
```

Use the actual domain names.

Repositories own:

- persistence operations;
- queries;
- filtering;
- loading relationships where appropriate;
- transaction-aware database operations.

Repositories do not own:

- HTTP;
- UI;
- authentication screens;
- cross-module business orchestration.

Services own business/application rules.

---

# 28. SERVICE RULES

Services orchestrate business behavior.

Examples:

```text
AuthenticationService
DashboardService
AttendanceService
AcademicService
ExaminationService
AnnouncementService
PlacementService
StudyMaterialService
AssignmentService
ReminderService
NotificationService
SynchronizationService
```

Cross-module workflows must be orchestrated here or in clearly named application services.

Examples:

```text
AssignmentService
    → ReminderService

ReminderJob
    → ReminderService
    → NotificationService

DashboardService
    → AssignmentService
    → ExaminationService
    → AnnouncementService
    → AttendanceService
    → AcademicService
    → ReminderService
    → NotificationService
    → PlacementService
```

Avoid circular dependencies.

Do not let domain modules import each other's implementation details arbitrarily.

---

# 29. SCHEMAS

Separate:

```text
ORM entities
```

from:

```text
API request/response schemas
```

Use Pydantic schemas for API boundaries.

Examples:

```text
LoginRequest
LoginResponse
StudentDashboardResponse

AttendanceResponse
AcademicRecordResponse
ExaminationResponse
AnnouncementResponse
PlacementResponse
StudyMaterialResponse

AssignmentCreateRequest
AssignmentUpdateRequest
AssignmentResponse

ReminderCreateRequest
ReminderResponse

NotificationResponse
```

The exact schema names may vary, but the separation must remain.

---

# 30. FRONTEND ARCHITECTURE

## Vanilla JavaScript

Use:

```text
HTML
CSS
JavaScript
```

Organize code by feature rather than one giant script.

Example:

```text
frontend/
  pages/
  components/
  services/
  state/
  features/
```

## React

Use:

```text
React
JavaScript / JSX
```

Use:

```text
components
pages
hooks
services
feature modules
routing
```

Do not add global-state tooling unless a real requirement appears.

The frontend must have a clean API/service layer.

---

# 31. UI STATES

Every feature that loads data must account for:

```text
Loading
Success
Empty
Error
Unavailable
```

Do not show a permanently blank panel when an API fails.

For synchronized external data, distinguish:

```text
No data
```

from:

```text
Data temporarily unavailable because synchronization/source retrieval failed
```

This distinction is explicitly required for Attendance and Examinations and should be reused sensibly elsewhere.

---

# 32. SEED DATA

Create deterministic, realistic Student Hub seed data.

Seed enough data to demonstrate:

```text
1+ student account

multiple subjects

attendance across several subjects

academic/internal marks

upcoming examinations

past/upcoming announcements

placement opportunities

study materials

assignments:
  - upcoming
  - overdue
  - completed

reminders:
  - direct student reminder
  - assignment-linked reminder

notifications:
  - at least one relevant notification
```

Do not generate different random data every startup.

Provide a command such as:

```bash
python -m app.seed
```

or a project-equivalent command.

Seed data must exercise cross-module relationships.

---

# 33. DATE/TIME RULES

Use timezone-aware application logic where appropriate.

Centralize application date/time behavior enough that tests can use controlled time.

This is especially important for:

```text
upcoming assignments
overdue assignments
reminder triggers
notification generation
examination dates
announcement timestamps
```

Do not scatter direct calls to system time throughout business logic if doing so makes deterministic testing difficult.

---

# 34. TESTING STRATEGY

Tests are not an afterthought.

Create at least:

```text
tests/
  unit/
  integration/
  system/
```

The exact structure may be adapted to the framework.

## Unit tests

Cover:

- authentication rules;
- assignment status logic;
- reminder processing logic;
- notification generation;
- relevant aggregation logic.

## Integration tests

Cover:

- protected APIs;
- repositories against a test database;
- announcement aggregation;
- mock portal synchronization;
- relevant service/API boundaries.

## System / E2E tests

Cover the explicitly required end-to-end flows.

Tests must exercise public behavior rather than internal implementation details whenever possible.

---

# 35. REQUIRED END-TO-END WORKFLOWS

These are not optional examples. They are project requirements.

## E2E-001 — Assignment → Reminder → Notification

```text
Student logs in
   ↓
Creates assignment
   ↓
Due date stored
   ↓
Reminder created/scheduled
   ↓
Controlled test time reaches trigger
   ↓
Reminder background processor runs
   ↓
Notification generated
   ↓
Student retrieves notification
```

Also test:

```text
Assignment completed before trigger
   ↓
Reminder processing
   ↓
No stale notification generated
```

## E2E-002 — Assignment → Materials context

```text
Student views assignment
   ↓
Assignment has subject/academic context
   ↓
Related materials requested
   ↓
Relevant materials returned
```

Also test:

```text
No related material
   ↓
Clear empty result
```

## E2E-003 — Portal → Attendance → Student

```text
Mock portal returns attendance
   ↓
Attendance synchronization
   ↓
Validation/normalization
   ↓
Persistence
   ↓
Attendance API
   ↓
Student sees attendance
```

Also test source failure:

```text
Portal retrieval fails
   ↓
Attendance UI
   ↓
Clear unavailable state
```

## E2E-004 — Portal → Examination view

```text
Mock portal returns examination data
   ↓
Synchronization
   ↓
Persistence
   ↓
Examination API
   ↓
Student sees synchronized schedule/date data
```

Also test synchronization failure with a clear unavailable state.

---

# 36. REQUIRED TEST WORK ITEMS

Implement and pass the following source requirements:

```text
SCRUM03-T-001
Authentication unit and integration test coverage

SCRUM03-T-002
Assignments/reminders/notifications system test coverage

SCRUM03-T-003
Announcement feed integration test coverage
```

Do not satisfy these by merely creating empty test files.

Execute the tests.

Report failures clearly.

---

# 37. LOGGING

Implement application-level structured JSON logging even when no external observability platform is installed.

At minimum support:

```text
timestamp
level
service
environment
request_id
session_id where applicable
user_id where safe
method
path
status_code
duration_ms
event
message
exception information
```

Never log:

```text
passwords
tokens
secrets
full authentication credentials
unnecessary sensitive personal data
```

Request logging must not expose credential payloads.

---

# 38. ERROR HANDLING

Create consistent application error handling.

Support meaningful categories such as:

```text
validation error
authentication failure
authorization failure
not found
conflict
external-source unavailable
background-job failure
unexpected internal error
```

Do not leak stack traces or secrets to normal users.

Detailed errors belong in logs.

User-facing messages should be safe and understandable.

---

# 39. HEALTH ENDPOINT

Provide:

```text
GET /health
```

It should be lightweight.

Do not create Kubernetes-specific readiness/liveness infrastructure.

The health endpoint must not require authentication.

---

# 40. PROJECT STRUCTURE

A recommended foundation:

```text
project-root/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   └── dependencies/
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── logging/
│   │   │
│   │   ├── modules/
│   │   │   ├── authentication/
│   │   │   ├── dashboard/
│   │   │   ├── attendance/
│   │   │   ├── academics/
│   │   │   ├── examinations/
│   │   │   ├── announcements/
│   │   │   ├── placements/
│   │   │   ├── study_materials/
│   │   │   ├── assignments/
│   │   │   ├── reminders/
│   │   │   └── notifications/
│   │   │
│   │   ├── integrations/
│   │   │   └── college_portal/
│   │   │
│   │   ├── jobs/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   ├── migrations/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── system/
│   └── pyproject.toml / requirements files
│
├── frontend/
│   └── [chosen frontend structure]
│
├── .env.example
├── README.md
└── docs/
    ├── architecture.md
    ├── api.md
    └── jira-traceability.md
```

Adapt rather than blindly overwrite an existing repository.

---

# 41. JIRA TRACEABILITY

Create:

```text
docs/jira-traceability.md
```

Map every Jira requirement to implementation artifacts.

Recommended columns:

```text
Requirement ID
Feature
Layer
Implementation
Test
Status
```

Example:

```text
SCRUM03-F009-UI-001
Assignments
Frontend + API
Assignment CRUD page + endpoints
Assignment integration tests
Implemented
```

The traceability document is part of the scaffold.

---

# 42. SCAFFOLD DEPTH REQUIREMENT

The scaffold must go deeper than empty folders and placeholder files.

For every major module, provide:

```text
Model
Repository
Service
API route(s)
API schema(s)
Frontend entry/page/component
Seed data
Relevant tests
```

For integration-backed modules additionally provide:

```text
Integration interface
Mock adapter
Synchronization service/path
Synchronization test
```

For job-backed modules additionally provide:

```text
Job entry point
Service call
Failure handling
Job test
```

For cross-module workflows additionally provide:

```text
relationship
orchestration path
integration/system test
```

The scaffold must compile/run.

---

# 43. WHAT "SCAFFOLD" MEANS HERE

The initial generated system must be a **vertical, runnable foundation**.

It is acceptable for some deep final behavior to remain simplified, mocked, or development-only.

It is NOT acceptable for the following to be missing:

```text
database entities
relationships
API contracts
module boundaries
frontend routes/pages
integration interfaces
job boundaries
authentication foundation
seed data
tests
traceability
```

The architecture should allow later work to implement the final real functionality **inside the existing boundaries**.

Do not leave structural work for later.

---

# 44. WHAT MAY REMAIN SIMPLIFIED

The following may use development implementations:

```text
College portal
External placement system
External announcement sources
Material file storage
Background scheduler
Notification delivery infrastructure
```

The scaffold must make the boundary explicit.

Use deterministic mock adapters and local implementations.

Do not fake a successful external integration by hardcoding results directly into UI components.

---

# 45. DO NOT BUILD

Unless explicitly requested, do not add:

```text
Kubernetes
Helm
Terraform
Cloud deployment
Service mesh
Kafka
RabbitMQ
Redis
Celery
Prometheus
Grafana
Loki
Elasticsearch
Kibana
OpenTelemetry
CI/CD
Load balancers
Auto-scaling
Microservices
GraphQL
```

Do not introduce these technologies simply because they are common in enterprise systems.

A modular monolith is the preferred architecture for this project unless the user explicitly requests otherwise.

---

# 46. DEPLOYMENT

The first milestone is local execution.

Preferred:

```text
Frontend
   ↓
Python/FastAPI backend
   ↓
SQLite
```

The application should work without containers.

If the application genuinely contains multiple local services later, Docker Compose may be introduced.

Do not create deployment infrastructure merely because production might eventually need it.

---

# 47. NO PREMATURE MICROservices

The project should initially be one deployable application with clear internal module boundaries.

Use:

```text
modular monolith
```

rather than:

```text
authentication service
attendance service
academics service
...
```

as separate network services.

The internal boundaries must be strong enough that a future extraction would be possible, but service extraction is not a current requirement.

---

# 48. DECISION GATE

Stop only for decisions that materially alter the product or architecture.

Use:

```text
Decision required

Context:
...

Option A:
...

Option B:
...

Recommendation:
...

Why this matters:
...
```

Examples:

- changing frontend technology;
- changing authentication architecture;
- changing database technology;
- introducing distributed infrastructure;
- changing a documented module relationship;
- changing an important data model relationship;
- introducing a new external dependency with substantial architectural impact.

Do not interrupt for ordinary implementation choices.

---

# 49. IMPLEMENTATION ORDER

Use this order:

```text
1. Inspect existing repository
        ↓
2. Read and map Jira requirements
        ↓
3. Establish project structure
        ↓
4. Configure application/runtime
        ↓
5. Create database base + models
        ↓
6. Create Alembic migration
        ↓
7. Implement repositories
        ↓
8. Implement services
        ↓
9. Implement authentication
        ↓
10. Implement integrations/interfaces
        ↓
11. Implement jobs
        ↓
12. Implement APIs
        ↓
13. Implement frontend shell
        ↓
14. Implement feature pages/components
        ↓
15. Seed deterministic data
        ↓
16. Implement cross-module workflows
        ↓
17. Implement unit/integration/system tests
        ↓
18. Implement structured logging
        ↓
19. Run application
        ↓
20. Run migrations
        ↓
21. Seed database
        ↓
22. Run automated tests
        ↓
23. Manually exercise critical workflows
        ↓
24. Produce traceability + README
```

Do not reverse this order merely to make the UI look complete sooner.

---

# 50. VALIDATION LOOP

After meaningful implementation steps:

```text
Build/run
   ↓
Check errors
   ↓
Fix
   ↓
Run tests
   ↓
Fix
   ↓
Re-test
```

Never declare the scaffold complete solely because files were created.

---

# 51. DEFINITION OF A SUCCESSFUL FIRST BUILD

The scaffold is considered successfully built only when:

1. The backend starts.
2. The frontend starts.
3. The database can be initialized.
4. Alembic migrations execute.
5. Deterministic seed data can be loaded.
6. Login works.
7. Protected resources are actually protected.
8. Logout works.
9. The authenticated shell loads.
10. Navigation reaches the major feature areas.
11. Feature APIs return database-backed data.
12. Dashboard data is aggregated from feature services.
13. Assignment CRUD works.
14. Upcoming/overdue/completed assignment classification works.
15. Assignment-to-reminder relationship exists.
16. Reminder processing can be executed independently.
17. Reminder-to-notification flow can be exercised.
18. Notifications are retrievable in-app.
19. Study materials can be discovered by assignment context.
20. Mock portal synchronization can populate Attendance.
21. Mock portal synchronization can populate Examinations.
22. Announcement source/timestamp traceability exists.
23. Placement information and permitted contributions have defined boundaries.
24. Required unit/integration/system tests run.
25. Required E2E workflows can be demonstrated.
26. Structured logs are produced.
27. No secrets or passwords are exposed in logs.
28. README explains local setup and architecture.
29. Jira traceability exists.
30. The application remains understandable without requiring an external observability or deployment platform.

---

# 52. FINAL ARCHITECTURAL PRINCIPLE

Build:

```text
                  AIO STUDENT'S HUB
                          │
                ┌─────────┴─────────┐
                │    Application    │
                │    Shell + Auth   │
                └─────────┬─────────┘
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
   Student Data       Academic Core     Productivity
       │                  │                  │
 Attendance           Academics        Assignments
 Profile              Examinations     Reminders
                      Announcements     Notifications
                      Placements
                      Materials
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                 Application Services
                          │
                    Repositories
                          │
                    SQLAlchemy ORM
                          │
                       SQLite
```

Integrations:

```text
College systems
      ↓
Integration adapters
      ↓
Synchronization services
      ↓
Domain persistence
```

Background processing:

```text
Reminder state
      ↓
Reminder Job
      ↓
Notification generation
      ↓
Notification Job boundary
      ↓
Student notification center
```

Do not collapse these boundaries.

Do not duplicate business logic across layers.

Do not build the project as a collection of disconnected screens.

---

# 53. IMPORTANT BUILDER BEHAVIOR

Before coding:

1. inspect the existing repository;
2. inspect the supplied Jira requirements;
3. derive the domain model;
4. derive cross-module dependencies;
5. identify the minimum scaffold required to satisfy those dependencies;
6. implement the architecture before polishing visuals.

While coding:

- preserve the established architecture;
- keep business logic out of API route handlers;
- keep database access out of frontend code;
- keep portal-specific logic out of domain modules;
- keep background work out of interactive request handlers;
- keep dashboard aggregation out of individual domain ownership.

After coding:

- run migrations;
- seed data;
- start the application;
- execute tests;
- exercise the four required E2E flows;
- fix discovered failures;
- verify logs;
- update traceability;
- document local setup.

Do not claim completion when the system has not been executed and validated.

---

# 54. FUNCTIONAL REQUIREMENTS — JIRA SOURCE

The following section is a normalized copy of the supplied Jira requirements. Preserve every requirement ID.


### SCRUM03-F001 — Authentication
Feature: Authentication Description: Secure access to AIO Student's Hub through login, logout, authentication state, protected resources, authorization, and secure credential handling. Source basis: README Core Features — Authentication.

- **SCRUM03-F001-UI-001 — Login screen**
  - Dependencies: Authentication mechanism implementation.
  - Technical: Keep credential handling on the appropriate client/server boundary and never expose secrets in client configuration.
  - Done: Login UI implemented and tested with success and failure cases.
- **SCRUM03-F001-FLOW-001 — Authentication state and logout**
  - Dependencies: Login authentication flow.
  - Technical: Authentication state belongs to the client/server authentication boundary, not to domain modules.
  - Done: State transitions and logout are implemented and tested.
- **SCRUM03-F001-SEC-001 — Protected resources and authorization**
  - Dependencies: Authentication state and protected API endpoints.
  - Technical: Server-side authorization must not depend only on client-side route hiding.
  - Done: Protected resources and authorization checks are tested.
- **SCRUM03-F001-SEC-002 — Secure credential handling**
  - Dependencies: Selected authentication mechanism.
  - Technical: Passwords must never be stored in plain text; external service credentials remain server-side.
  - Done: Security review completed for authentication handling.
- **SCRUM03-T-001 — Authentication unit and integration test coverage**
  - Dependencies: Authentication implementation.
  - Technical: The README defines unit and integration testing; exact framework is not specified.
  - Done: Relevant unit/integration tests implemented and passing.

### SCRUM03-F002 — Dashboard
Feature: Dashboard Description: A consolidated student-facing overview of upcoming assignments, examinations, recent announcements, attendance, academic information, pending reminders, notifications, and placement updates. The Dashboard acts as a presentation and aggregation layer rather than owning the business logic of other modules. Source basis: README — Dashboard.

- **SCRUM03-F002-UI-001 — Student dashboard overview**
  - Dependencies: Feature APIs/data services for the dashboard content.
  - Technical: Business logic remains in the relevant feature modules.
  - Done: Dashboard implemented and tested with representative feature data.
- **SCRUM03-F002-BE-001 — Dashboard aggregation workflow**
  - Dependencies: Availability of feature application services/APIs.
  - Technical: Keep aggregation separate from feature-specific domain logic.
  - Done: Aggregation workflow implemented and tested.
- **SCRUM03-F002-E2E-001 — Dashboard end-to-end attention view**
  - Dependencies: Completion of the participating feature workflows.
  - Technical: Do not duplicate feature business logic in the dashboard test.
  - Done: End-to-end workflow verified.

### SCRUM03-F003 — Attendance
Feature: Attendance Description: Student access to attendance information including subject, classes attended, total classes, and attendance percentage. Where applicable, attendance can be synchronized from an existing college portal through the portal integration infrastructure. Source basis: README — Attendance.

- **SCRUM03-F003-UI-001 — Attendance view by subject**
  - Dependencies: Attendance data service.
  - Technical: Use the latest synchronized values available to the application.
  - Done: Attendance screen implemented and tested.
- **SCRUM03-F003-BE-001 — Attendance application processing**
  - Dependencies: Portal integration or source data.
  - Technical: Attendance business behavior should not depend directly on portal-specific details.
  - Done: Processing implemented and tested with representative data.
- **SCRUM03-F003-INT-001 — College portal attendance synchronization**
  - Dependencies: Supported college portal integration availability.
  - Technical: The README does not specify an exact portal or API contract.
  - Done: Synchronization implemented against the available integration boundary and verified.
- **SCRUM03-E2E-003 — Portal → Attendance → Student workflow**
  - Dependencies: Attendance portal integration.
  - Technical: Portal-specific details remain in infrastructure.
  - Done: End-to-end synchronization workflow verified.

### SCRUM03-F004 — Academics
Feature: Academics Description: General academic information including subject information, internal marks, academic performance information, and other academic records. Information may be retrieved from existing college systems through the portal integration layer. Source basis: README — Academics.

- **SCRUM03-F004-UI-001 — Academic information view**
  - Dependencies: Academic application service/data.
  - Technical: Do not add student-editing behavior not stated in the README.
  - Done: Academic information view implemented and tested.
- **SCRUM03-F004-BE-001 — Academic information processing**
  - Dependencies: College academic source/integration.
  - Technical: Keep portal-specific details outside core domain logic.
  - Done: Processing implemented and tested.
- **SCRUM03-F004-INT-001 — College portal academics synchronization**
  - Dependencies: Supported college system integration.
  - Technical: Portal-specific implementation stays isolated from the academic domain.
  - Done: Integration verified with representative source data.

### SCRUM03-F005 — Examinations
Feature: Examinations Description: Examination-related information including examination schedules, examination dates, examination-related announcements, and other relevant examination information. Supported college portals may supply synchronized examination information. Source basis: README — Examinations.

- **SCRUM03-F005-UI-001 — Examination schedule view**
  - Dependencies: Examination application data.
  - Technical: Keep exam-specific business rules separate from portal integration details.
  - Done: Examination view implemented and tested.
- **SCRUM03-F005-BE-001 — Examination information processing**
  - Dependencies: Examination source data/integration.
  - Technical: Portal-specific details remain outside the domain layer.
  - Done: Processing implemented and tested.
- **SCRUM03-F005-INT-001 — College portal examination synchronization**
  - Dependencies: Supported college portal integration.
  - Technical: Keep portal-specific communication in the integration boundary.
  - Done: Integration verified with representative data.
- **SCRUM03-E2E-004 — Portal synchronization to examination view**
  - Dependencies: Examination portal integration.
  - Technical: Do not couple the UI directly to portal-specific implementations.
  - Done: End-to-end examination synchronization verified.

### SCRUM03-F006 — Announcements
Feature: Announcements Description: Centralized access to college notices, department announcements, examination notices, academic deadlines, events, and administrative updates, with source and timestamp traceability. Announcements may originate from supported college portals or other configured sources. Source basis: README — Announcements.

- **SCRUM03-F006-UI-001 — Announcements feed**
  - Dependencies: Announcement aggregation service.
  - Technical: Each announcement should retain source and timestamp information for traceability.
  - Done: Announcements feed implemented and tested.
- **SCRUM03-F006-BE-001 — Announcement aggregation and normalization**
  - Dependencies: Source integrations/configured sources.
  - Technical: Keep source-specific communication outside the announcement domain.
  - Done: Aggregation implemented and tested.
- **SCRUM03-F006-INT-001 — College portal announcement synchronization**
  - Dependencies: Supported source availability.
  - Technical: Portal-specific communication belongs in integration infrastructure.
  - Done: Synchronization verified with representative source data.
- **SCRUM03-F006-DATA-001 — Announcement traceability data**
  - Dependencies: Announcement source data.
  - Technical: Metadata should remain tied to the source record.
  - Done: Traceability fields are implemented and tested.
- **SCRUM03-T-003 — Announcement feed integration test coverage**
  - Dependencies: Announcement aggregation and integration implementation.
  - Technical: No live external portal dependency is required for the test itself.
  - Done: Relevant integration tests implemented and passing.

### SCRUM03-F007 — Placements
Feature: Placements Description: Centralized placement information including placement opportunities, company information, eligibility requirements, recruitment updates, important dates, preparation resources, and interview experiences. Placement information may come from supported college placement systems, and senior students can contribute experiences and preparation information. Source basis: README — Placements.

- **SCRUM03-F007-UI-001 — Placement opportunities view**
  - Dependencies: Placement application data.
  - Technical: Keep source-system details outside the placement domain.
  - Done: Placement view implemented and tested.
- **SCRUM03-F007-BE-001 — Placement information processing**
  - Dependencies: Placement source/integration.
  - Technical: Keep source-specific fields isolated from core placement concepts.
  - Done: Processing implemented and tested.
- **SCRUM03-F007-INT-001 — College placement-system synchronization**
  - Dependencies: Supported college placement system.
  - Technical: Source-specific logic remains in infrastructure.
  - Done: Integration verified with representative data.
- **SCRUM03-F007-CON-001 — Senior placement contributions**
  - Dependencies: Placement contribution capability.
  - Technical: Do not invent a moderation model; use the product workflow chosen by the team.
  - Done: Contribution workflow implemented and tested.

### SCRUM03-F008 — Study Materials
Feature: Study Materials Description: Centralized academic-resource access supporting browsing, searching, filtering, subject-related resources, and permitted uploads/contributions. Resources may include notes, PDFs, reference documents, subject materials, and previous academic resources. Materials are connected with Assignments through subject or relevant academic context. Source basis: README — Materials.

- **SCRUM03-F008-UI-001 — Study materials browse and access**
  - Dependencies: Materials data/storage service.
  - Technical: Uploaded files must be validated.
  - Done: Browse/access UI implemented and tested.
- **SCRUM03-F008-UI-002 — Study materials search and filtering**
  - Dependencies: Materials listing.
  - Technical: Feature-specific logic should remain within the Materials module.
  - Done: Search/filter behavior implemented and tested.
- **SCRUM03-F008-BE-001 — Study materials catalog service**
  - Dependencies: Material storage/data.
  - Technical: Keep storage-specific implementation outside core material concepts.
  - Done: Catalog service implemented and tested.
- **SCRUM03-F008-CON-001 — Permitted material contributions**
  - Dependencies: File storage and material catalog.
  - Technical: Uploaded files must be validated; secrets and credentials are not stored in client configuration.
  - Done: Contribution flow implemented and tested.
- **SCRUM03-F008-REL-001 — Assignment-related material context**
  - Dependencies: Assignments module and material metadata.
  - Technical: Do not create unrelated cross-module coupling.
  - Done: Relationship is implemented and tested.
- **SCRUM03-E2E-002 — Assignment → Materials context workflow**
  - Dependencies: Assignments and Materials.
  - Technical: Do not introduce unrelated cross-module dependencies.
  - Done: End-to-end workflow verified.

### SCRUM03-F009 — Assignments
Feature: Assignments Description: Student task management supporting creation, viewing, editing, deletion, due dates, subject association, descriptions, completion status, upcoming assignments, and overdue identification. Assignments interact with Reminders, Notifications, and Study Materials. Source basis: README — Assignments.

- **SCRUM03-F009-UI-001 — Assignment CRUD screen**
  - Dependencies: Assignment application service and persistence.
  - Technical: Use protected resources so students can access only authorized assignment data.
  - Done: CRUD flow implemented and tested.
- **SCRUM03-F009-DATA-001 — Assignment details and status**
  - Dependencies: Assignment persistence.
  - Technical: Do not infer additional task fields beyond the README unless needed by the implementation.
  - Done: Assignment data model and status behavior implemented and tested.
- **SCRUM03-F009-UI-002 — Upcoming and overdue assignment views**
  - Dependencies: Assignment due dates and completion state.
  - Technical: Do not duplicate reminder logic in the Assignment UI.
  - Done: Upcoming/overdue behavior implemented and tested.
- **SCRUM03-F009-REL-001 — Assignment to reminder integration**
  - Dependencies: Reminder module and scheduled processing.
  - Technical: Keep reminder processing in the Reminders/Jobs responsibilities.
  - Done: Integration behavior implemented and tested.
- **SCRUM03-F009-REL-002 — Assignment completion and reminder behavior**
  - Dependencies: Assignment state and Reminder processing.
  - Technical: Keep business state in Assignments and time-based processing in Reminders/Jobs.
  - Done: Behavior verified with representative workflow tests.
- **SCRUM03-E2E-001 — Assignment → Reminder → Notification end-to-end workflow**
  - Dependencies: Assignments, Reminders, Notifications.
  - Technical: Follow the module boundaries stated in the README rather than moving job logic into the API.
  - Done: End-to-end workflow tested.
- **SCRUM03-T-002 — Assignments/reminders/notifications system test coverage**
  - Dependencies: Implemented Assignment, Reminder, and Notification modules.
  - Technical: System tests should exercise the public feature workflow rather than internal implementation details.
  - Done: System test scenarios implemented and passing.

### SCRUM03-F010 — Reminders
Feature: Reminders Description: Time-sensitive student reminders associated with assignments, examinations, important deadlines, and other student-created events. Reminders may be created directly, created by other modules, and processed by background jobs. Source basis: README — Reminders.

- **SCRUM03-F010-UI-001 — Reminder management**
  - Dependencies: Reminder application service.
  - Technical: Avoid duplicating notification delivery logic in the reminder UI.
  - Done: Reminder management implemented and tested.
- **SCRUM03-F010-BE-001 — Reminder scheduling workflow**
  - Dependencies: Background job processing.
  - Technical: Time-based work belongs in Jobs rather than API request handling.
  - Done: Reminder scheduling workflow implemented and tested.
- **SCRUM03-F010-JOB-001 — Reminder background processing**
  - Dependencies: Reminder persistence and notification workflow.
  - Technical: Keep background job responsibilities separate from API request handling.
  - Done: Reminder job behavior implemented and tested.

### SCRUM03-F011 — Notifications
Feature: Notifications Description: Notifications that inform students about upcoming assignment deadlines, reminder triggers, important announcements, and other relevant academic events. Notification delivery and processing are separated from core domain logic. Source basis: README — Notifications.

- **SCRUM03-F011-UI-001 — Notifications center**
  - Dependencies: Notification application/data service.
  - Technical: Keep delivery infrastructure separate from notification domain behavior.
  - Done: Notification center implemented and tested.
- **SCRUM03-F011-BE-001 — Notification generation workflow**
  - Dependencies: Assignments, Reminders, Announcements, and other supported event sources.
  - Technical: Keep event-specific source logic outside notification delivery infrastructure.
  - Done: Generation workflow implemented and tested.
- **SCRUM03-F011-JOB-001 — Notification background processing**
  - Dependencies: Notification generation workflow.
  - Technical: Notification delivery infrastructure and job processing should remain outside domain rules.
  - Done: Notification job implemented and tested.
- **SCRUM03-F011-REL-001 — Reminder-to-notification workflow**
  - Dependencies: Reminder processing and notification generation.
  - Technical: Follow the README workflow: Reminder Job → Notification → Notification Job → Student.
  - Done: End-to-end reminder-to-notification workflow verified.


---

# 55. FINAL INSTRUCTION TO THE BUILDER

Build the **AIO Student's Hub scaffold**, not a generic sample application.

The generated repository must have a real domain model, real persistence, real module boundaries, real APIs, a real authenticated shell, deterministic seed data, mockable integration boundaries, independently invokable job boundaries, automated tests, and demonstrable cross-feature workflows.

The remaining future work should be primarily:

```text
Replace/extend simplified development implementations
+
Complete final business functionality
+
Connect real external systems where required
+
Refine UX and production deployment
```

It must NOT be:

```text
rewrite architecture
add missing domain models
invent module relationships
move business logic out of routes
replace hardcoded frontend data
create integration architecture from scratch
create job architecture from scratch
add foundational tests from scratch
```

Build the foundation so thoroughly that future work occurs **inside the existing architecture**, not around it.

