# AIO Student's Hub

A centralized student-facing hub that brings together authentication, dashboard, attendance, academics, examinations, announcements, placements, study materials, assignments, reminders, and notifications.

## Features

- **Authentication**: Secure JWT-based login with access/refresh tokens
- **Dashboard**: Consolidated overview of attention items across all modules
- **Attendance**: Subject-wise attendance with percentage tracking
- **Academics**: Academic records, marks, and grades per semester
- **Examinations**: Exam schedules with dates, venues, and types
- **Announcements**: Multi-source feed with source/timestamp traceability
- **Placements**: Opportunities, company info, and peer contributions
- **Study Materials**: Browse, search, filter resources by subject
- **Assignments**: Full CRUD with due dates and status classification
- **Reminders**: Time-based triggers with background processing
- **Notifications**: In-app notification center with read/unread states

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- SQLAlchemy 2.x with Alembic migrations
- SQLite (dev) / PostgreSQL (prod)
- JWT authentication with bcrypt
- APScheduler for background jobs
- Structured JSON logging

### Frontend
- React 18 with Vite
- React Router 6
- Axios for API calls
- Lucide React icons
- date-fns for date formatting

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Copy environment file
cp ../.env.example .env

# Run migrations
alembic upgrade head

# Seed database with demo data
python -m app.seed

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

### Demo Credentials
- **Email**: student@demo.edu
- **Password**: demo123

## Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Config, security
│   │   ├── db/                  # Database setup
│   │   ├── logging/             # Structured logging
│   │   ├── modules/             # Domain modules
│   │   ├── integrations/        # Portal adapters
│   │   ├── jobs/                # Background jobs
│   │   ├── schemas/             # Pydantic schemas
│   │   └── main.py              # FastAPI app
│   ├── migrations/              # Alembic migrations
│   └── tests/                   # Unit/integration/system tests
├── frontend/
│   └── src/
│       ├── components/          # React components
│       ├── pages/               # Page components
│       ├── services/            # API services
│       ├── contexts/            # React contexts
│       └── hooks/               # Custom hooks
├── docs/
│   ├── architecture.md          # Architecture documentation
│   ├── api.md                   # API documentation
│   └── jira-traceability.md     # Requirements traceability
└── .env.example                 # Environment template
```

## Running Tests

### Backend Tests
```bash
cd backend
pytest                    # All tests
pytest tests/unit         # Unit tests
pytest tests/integration  # Integration tests
pytest tests/system       # System/E2E tests
pytest -v --cov=app      # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run test              # When implemented
npm run lint              # ESLint
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Current user
- `GET /api/v1/auth/profile` - Student profile

### Dashboard
- `GET /api/v1/dashboard` - Aggregated dashboard data

### Attendance
- `GET /api/v1/attendance/subjects` - All subjects
- `GET /api/v1/attendance/summary` - Attendance summary
- `GET /api/v1/attendance/{subject_id}` - Subject attendance
- `POST /api/v1/attendance/sync` - Sync from portal

### Academics
- `GET /api/v1/academics` - Academic records
- `POST /api/v1/academics/sync` - Sync from portal

### Examinations
- `GET /api/v1/examinations` - Exam schedule
- `POST /api/v1/examinations/sync` - Sync from portal

### Announcements
- `GET /api/v1/announcements` - Announcements feed
- `GET /api/v1/announcements/sources` - Announcement sources
- `POST /api/v1/announcements/sync` - Sync from source

### Placements
- `GET /api/v1/placements/opportunities` - Open opportunities
- `GET /api/v1/placements/contributions` - Published contributions
- `GET /api/v1/placements/my-contributions` - My contributions
- `POST /api/v1/placements/contributions` - Create contribution
- `POST /api/v1/placements/sync` - Sync from portal

### Study Materials
- `GET /api/v1/materials` - Search/filter materials
- `GET /api/v1/materials/subject/{subject_id}` - Materials by subject
- `GET /api/v1/materials/{material_id}` - Material details
- `POST /api/v1/materials` - Create material
- `GET /api/v1/materials/my-uploads` - My uploads

### Assignments
- `GET /api/v1/assignments` - All assignments (upcoming/overdue/completed)
- `GET /api/v1/assignments/subject/{subject_id}` - By subject
- `POST /api/v1/assignments` - Create assignment
- `PATCH /api/v1/assignments/{id}` - Update assignment
- `POST /api/v1/assignments/{id}/complete` - Mark complete
- `DELETE /api/v1/assignments/{id}` - Delete assignment

### Reminders
- `GET /api/v1/reminders` - All reminders
- `POST /api/v1/reminders` - Create reminder
- `POST /api/v1/reminders/process` - Process due reminders

### Notifications
- `GET /api/v1/notifications` - Notifications (with filter)
- `POST /api/v1/notifications/{id}/read` - Mark read
- `POST /api/v1/notifications/read-all` - Mark all read

## Background Jobs

- **Reminder Processor**: Runs every minute, processes due reminders, generates notifications
- **Notification Processor**: Runs every 5 minutes, handles notification delivery

## Development

### Adding a New Module
1. Create module directory in `backend/app/modules/`
2. Add models, repository, service, schemas, routes
3. Register routes in `main.py`
4. Create frontend page in `frontend/src/pages/`
5. Add navigation item in `Layout.jsx`
6. Write tests

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Seeding Data
```bash
cd backend
python -m app.seed
```

## Configuration

Key environment variables (see `.env.example`):
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key (min 32 chars)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token lifetime
- `FRONTEND_URL`: CORS origin

## Architecture

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Requirements Traceability

See [docs/jira-traceability.md](docs/jira-traceability.md) for Jira requirement mapping.

## License

MIT License - see LICENSE file for details.