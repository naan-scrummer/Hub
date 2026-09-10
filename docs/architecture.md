# AIO Student's Hub - Architecture Document

## Overview

AIO Student's Hub is a modular monolith built with FastAPI (Python) backend and React frontend, designed as a centralized student-facing hub for academic information and productivity.

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Database**: SQLite (dev) / PostgreSQL (prod) via SQLAlchemy 2.x
- **Migrations**: Alembic
- **Authentication**: JWT (HS256) with access/refresh tokens
- **Validation**: Pydantic 2.x
- **Background Jobs**: APScheduler
- **Logging**: Structured JSON via structlog
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 18
- **Routing**: React Router 6
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Date Handling**: date-fns
- **Build Tool**: Vite

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/          # API route handlers
│   │   └── dependencies/    # FastAPI dependencies (auth, db)
│   ├── core/                # Configuration, security
│   ├── db/                  # Database base, session management
│   ├── logging/             # Structured logging setup
│   ├── modules/             # Domain modules
│   │   ├── authentication/
│   │   ├── dashboard/
│   │   ├── attendance/
│   │   ├── academics/
│   │   ├── examinations/
│   │   ├── announcements/
│   │   ├── placements/
│   │   ├── study_materials/
│   │   ├── assignments/
│   │   ├── reminders/
│   │   └── notifications/
│   ├── integrations/        # External system integrations
│   │   └── college_portal/
│   ├── jobs/                # Background job definitions
│   ├── schemas/             # Pydantic API schemas
│   └── main.py              # Application entry point
├── migrations/              # Alembic migrations
└── tests/                   # Unit, integration, system tests

frontend/
└── src/
    ├── components/          # Reusable UI components
    ├── pages/               # Page components
    ├── hooks/               # Custom React hooks
    ├── services/            # API service layer
    ├── contexts/            # React contexts (Auth)
    └── utils/               # Utility functions
```

## Architectural Principles

### Layered Architecture
```
Frontend → API Routes → Application Services → Repositories → SQLAlchemy ORM → Database
                    ↓
            Integration Adapters → External Sources
                    ↓
            Background Jobs → Services → Database/Notifications
```

### Module Boundaries
Each domain module owns:
- **Models**: SQLAlchemy ORM entities
- **Repository**: Data access layer
- **Service**: Business logic
- **API Routes**: HTTP endpoints
- **Schemas**: Request/response validation

### Cross-Module Relationships
- **Assignments → Reminders**: Assignment creation triggers reminder scheduling
- **Reminders → Notifications**: Reminder processing generates notifications
- **Assignments → Study Materials**: Materials discoverable by assignment subject
- **Dashboard**: Aggregates from all feature services (no direct DB access)

## Domain Modules

### Authentication
- JWT-based authentication with access/refresh tokens
- bcrypt password hashing
- Role-based access (student, admin)
- Protected route dependencies
- Demo user seeding

### Dashboard
- Aggregation service calling feature services
- Attention-oriented sections (upcoming, overdue, summaries)
- Handles partial failures gracefully

### Attendance
- Subject-based attendance records
- Percentage calculation
- Portal synchronization via adapter pattern
- Unavailable state when sync fails

### Academics
- Subject-based academic records
- Internal/external marks, grades
- Semester tracking
- Portal synchronization

### Examinations
- Exam schedules with dates, venues, types
- Upcoming/past filtering
- Portal synchronization
- Unavailable state when sync fails

### Announcements
- Multi-source feed (portal, department, exam cell)
- Category filtering
- Source/timestamp traceability
- Deduplication

### Placements
- Company opportunities with eligibility, deadlines
- Senior student contributions (interview experiences)
- Contribution approval workflow
- Portal synchronization

### Study Materials
- Subject-associated resources
- Search, filter by type/subject
- Student uploads with approval
- Assignment-context discovery

### Assignments
- Full CRUD with student ownership
- Due date classification (upcoming/overdue/completed)
- Automatic reminder creation (1 day before due)
- Completion cancels pending reminders

### Reminders
- Multiple trigger types (assignment, exam, custom)
- Background processing via APScheduler
- Status tracking (pending/processed/cancelled)
- Notification generation on trigger

### Notifications
- In-app notification center
- Sources: assignment deadlines, reminders, announcements, exams, placements
- Read/unread/archived states
- Mark all read functionality

## Integration Architecture

### Adapter Pattern
```
CollegePortalClient (interface)
    ↓
Domain-specific adapters (AttendancePortalAdapter, etc.)
    ↓
MockCollegePortalClient (development)
    ↓
Deterministic mock data
```

### Synchronization Flow
```
SyncRun created → Adapter.fetch() → Service.upsert() → SyncRun.completed
```
- Each sync tracked with SyncRun entity
- Success/failure/partial states
- Error recording without crashing

## Background Jobs

### JobScheduler (APScheduler)
- **process_reminders**: Every minute, processes due reminders
- **process_notifications**: Every 5 minutes, handles notification delivery

### Job Characteristics
- Independent of API requests
- Uses application services (not direct DB)
- Failure isolation (one job failure doesn't crash app)
- Structured logging

## Database Design

### Key Entities
- **User/StudentProfile**: Authentication + student info
- **Subject**: Academic subjects
- **AttendanceRecord**: Student-subject attendance
- **AcademicRecord**: Marks, grades per semester
- **Examination**: Exam schedules
- **Announcement/AnnouncementSource**: Multi-source feed
- **Company/PlacementOpportunity/PlacementContribution**: Placements
- **StudyMaterial**: Resources with subject association
- **Assignment**: Student tasks with due dates
- **Reminder**: Time-based triggers
- **Notification**: In-app alerts
- **SyncRun**: Synchronization audit trail

### Relationships
- User 1:1 StudentProfile
- StudentProfile 1:N AttendanceRecord, AcademicRecord, Assignment, Reminder, Notification
- Subject 1:N AttendanceRecord, AcademicRecord, Assignment, Examination, StudyMaterial
- Assignment 1:N Reminder
- Reminder → Notification (on processing)

## Security

- Passwords hashed with bcrypt (never plaintext)
- JWT tokens with expiry (access: 60min, refresh: 7 days)
- Secrets via environment variables
- No credentials in logs
- CORS configured for frontend origin
- Protected routes require valid JWT

## Error Handling

- Structured error categories (validation, auth, not found, external unavailable, job failure)
- User-safe messages, detailed logs
- No stack traces to clients
- Graceful degradation for external source failures

## Testing Strategy

### Unit Tests
- Authentication rules
- Assignment status logic
- Reminder processing
- Notification generation

### Integration Tests
- Protected API endpoints
- Repository operations
- Service interactions
- Mock portal synchronization

### System/E2E Tests
- Assignment → Reminder → Notification flow
- Assignment → Materials context
- Portal → Attendance sync
- Portal → Examination sync

## Deployment

### Local Development
```bash
# Backend
cd backend
pip install -e .[dev]
cp ../.env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Production Considerations
- PostgreSQL database
- Environment-specific configuration
- Reverse proxy (nginx)
- Process manager (systemd/supervisor)
- SSL termination
- Monitoring/logging aggregation

## Future Extensibility

The modular architecture supports:
- New domain modules following same pattern
- Real portal adapter implementations
- Additional notification channels (email, push)
- Microservice extraction if needed
- Enhanced background job infrastructure (Celery/Redis)