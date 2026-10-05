# AIO Student's Hub: Notification Pipeline Implementation Guide

**Target Work Items:** `SCRUM-33` (Epic), `SCRUM-82` (UI Center), `SCRUM-83` (Backend Generation), `SCRUM-84` (Background Job)

---

## 1. Scope & Objective

This implementation guide outlines the exact, step-by-step build instructions for isolating and completing the Notification system for AIO Student's Hub without touching unrelated modules or implementing full end-to-end flows (`SCRUM03-E2E-001` is out of scope).

### 1.1 Included Jira Work Items

| Issue Key | Summary | Component | Description |
| --- | --- | --- | --- |
| **SCRUM-33** | `[SCRUM03-F011]` Notifications Epic | Core Architecture | Overall notifications feature container. |
| **SCRUM-82** | `[SCRUM03-F011-UI-001]` Notifications center | Frontend UI | Student notification center with read/unread, filters, and empty state. |
| **SCRUM-83** | `[SCRUM03-F011-BE-001]` Notification generation workflow | Backend Service | Service-layer generation of notification records with source context. |
| **SCRUM-84** | `[SCRUM03-F011-JOB-001]` Notification background processing | Background Job | Decoupled background task execution for processing notification delivery states. |

---

## 2. Explicit Boundaries & Isolation Guardrails

An AI execution agent **must** strictly adhere to the following file modification rules:

* **Strict Prohibition:** Do NOT create, alter, or delete any files in `backend/app/modules/assignments/`, `backend/app/modules/reminders/`, `backend/app/modules/auth/`, `backend/app/modules/examinations/`, or any unrelated frontend pages (`AssignmentsPage.jsx`, `RemindersPage.jsx`, etc.).
* **Cautionary Modifications (Shared Registration Points):** The only existing core files permitted for minimal, surgical additions are:
* `backend/app/main.py` (to register `notifications_router`)
* `backend/app/jobs/scheduler.py` (to register `process_notifications_job`)
* `backend/scripts/seed.py` (to invoke `seed_notifications()`)
* `frontend/src/App.jsx` (to mount the `/notifications` route)
* `.env.example` (to add notification configuration variables)


* **Primary Domain Boundaries:** All code changes must be isolated to:
* `backend/app/modules/notifications/`
* `backend/app/jobs/notification_job.py`
* `backend/alembic/versions/*_notifications_schema.py`
* `backend/scripts/seed_notifications.py`
* `frontend/src/pages/NotificationsPage.jsx`
* `frontend/src/services/notificationsService.js`



---

## 3. Subagent Task Delegation Matrix

The implementation is executed by five specialized AI subagent roles:

```text
 ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
 │ explorer.md  │ ───► │  planner.md  │ ───► │   build.md   │ ───► │ reviewer.md  │ ───► │  tester.md   │
 └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘

```

1. **`explorer.md`**: Scans existing repository file structure and schema baseline.
2. **`planner.md`**: Defines database deltas, API contracts, environment updates, and seeding structures.
3. **`build.md`**: Writes database migrations, backend services, jobs, routes, frontend services, and UI components.
4. **`reviewer.md`**: Enforces strict non-contamination rules and verifies architectural compliance.
5. **`tester.md`**: Implements and executes unit and integration tests.

---

## 4. Phase 1 — Explorer Agent Tasks (`explorer.md`)

Execute initial directory inspection to verify the baseline structure:

1. Confirm existence of `backend/app/modules/notifications/`:
* `models.py`
* `schemas.py`
* `repository.py`
* `service.py`
* `router.py`


2. Verify scheduler setup in `backend/app/jobs/scheduler.py`.
3. Check `frontend/src/services/` and `frontend/src/pages/` conventions.

---

## 5. Phase 2 — Planner Agent Architecture Blueprint (`planner.md`)

### 5.1 Database Modification Blueprint

Modify or ensure the existence of the `notifications` table schema with appropriate processing statuses.

```sql
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    source VARCHAR(50) NOT NULL, -- ASSIGNMENT_DEADLINE, REMINDER_TRIGGER, ANNOUNCEMENT, EXAMINATION, PLACEMENT
    source_id INTEGER NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'UNREAD', -- UNREAD, READ, ARCHIVED
    processing_status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSED, FAILED
    read_at TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_notifications_student_status ON notifications(student_id, status);
CREATE INDEX idx_notifications_processing_status ON notifications(processing_status);

```

### 5.2 Environment Variables Update (`.env.example`)

Add the following environment variables to `.env.example`:

```env
# Notification Pipeline Settings
NOTIFICATION_JOB_INTERVAL_MINUTES=5
NOTIFICATION_RETENTION_DAYS=30
NOTIFICATION_BATCH_SIZE=100
ENABLE_BACKGROUND_NOTIFICATIONS=true

```

### 5.3 Notification Data Seed Specification

Notification seeding must append demo notification data without wiping existing users or assignments.

* **Demo Categories:** `ASSIGNMENT_DEADLINE`, `REMINDER_TRIGGER`, `ANNOUNCEMENT`, `EXAMINATION`, `PLACEMENT`.
* **States:** `UNREAD`, `READ`, `ARCHIVED`.
* **Processing States:** `PROCESSED`.

---

## 6. Phase 3 — Build Agent Implementation (`build.md`)

### 6.1 Database Migration Script

**Path:** `backend/alembic/versions/20260917_001_notifications_schema.py`

```python
"""Notification schema refinement

Revision ID: 20260917_001
Revises: 
Create Date: 2026-09-17 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20260917_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='UNREAD', nullable=False),
        sa.Column('processing_status', sa.String(length=20), server_default='PENDING', nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_student_status', 'notifications', ['student_id', 'status'])
    op.create_index('idx_notifications_processing_status', 'notifications', ['processing_status'])

def downgrade():
    op.drop_index('idx_notifications_processing_status', table_name='notifications')
    op.drop_index('idx_notifications_student_status', table_name='notifications')
    op.drop_table('notifications')

```

### 6.2 Backend Data Models & Schemas

**Path:** `backend/app/modules/notifications/models.py`

```python
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from app.db.base import Base

class NotificationSource(str, enum.Enum):
    ASSIGNMENT_DEADLINE = "ASSIGNMENT_DEADLINE"
    REMINDER_TRIGGER = "REMINDER_TRIGGER"
    ANNOUNCEMENT = "ANNOUNCEMENT"
    EXAMINATION = "EXAMINATION"
    PLACEMENT = "PLACEMENT"

class NotificationStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    ARCHIVED = "ARCHIVED"

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    source = Column(SQLEnum(NotificationSource), nullable=False)
    source_id = Column(Integer, nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.UNREAD, nullable=False, index=True)
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

```

**Path:** `backend/app/modules/notifications/schemas.py`

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.modules.notifications.models import NotificationSource, NotificationStatus, ProcessingStatus

class NotificationCreate(BaseModel):
    student_id: int
    source: NotificationSource
    source_id: Optional[int] = None
    title: str
    message: str

class NotificationResponse(BaseModel):
    id: int
    student_id: int
    source: NotificationSource
    source_id: Optional[int]
    title: str
    message: str
    status: NotificationStatus
    processing_status: ProcessingStatus
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

```

### 6.3 Repository Layer

**Path:** `backend/app/modules/notifications/repository.py`

```python
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.modules.notifications.models import Notification, NotificationStatus, ProcessingStatus, NotificationSource

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, student_id: int, source: NotificationSource, title: str, message: str, source_id: Optional[int] = None) -> Notification:
        notification = Notification(
            student_id=student_id,
            source=source,
            source_id=source_id,
            title=title,
            message=message,
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PENDING
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_student(self, student_id: int, status: Optional[NotificationStatus] = None) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.student_id == student_id)
        if status:
            query = query.filter(Notification.status == status)
        return query.order_by(Notification.created_at.desc()).all()

    def get_pending_processing(self, limit: int = 100) -> List[Notification]:
        return self.db.query(Notification).filter(
            Notification.processing_status == ProcessingStatus.PENDING
        ).limit(limit).all()

    def mark_processed(self, notification_id: int) -> Optional[Notification]:
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.processing_status = ProcessingStatus.PROCESSED
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_as_read(self, notification_id: int, student_id: int) -> Optional[Notification]:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.student_id == student_id
        ).first()
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, student_id: int) -> int:
        count = self.db.query(Notification).filter(
            Notification.student_id == student_id,
            Notification.status == NotificationStatus.UNREAD
        ).update({
            Notification.status: NotificationStatus.READ,
            Notification.read_at: datetime.now(timezone.utc)
        }, synchronize_session=False)
        self.db.commit()
        return count

```

### 6.4 Notification Service (`SCRUM-83`)

**Path:** `backend/app/modules/notifications/service.py`

```python
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.models import Notification, NotificationStatus, NotificationSource, ProcessingStatus
from app.modules.notifications.schemas import NotificationCreate

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.repo = NotificationRepository(db)

    def generate_notification(self, data: NotificationCreate) -> Notification:
        # Validate supported sources (SCRUM-83 AC1/AC2)
        if data.source not in NotificationSource:
            logger.warning(f"Discarding event from unsupported source: {data.source}")
            raise ValueError(f"Unsupported notification source: {data.source}")

        logger.info(f"Generating notification for student={data.student_id}, source={data.source}")
        return self.repo.create(
            student_id=data.student_id,
            source=data.source,
            source_id=data.source_id,
            title=data.title,
            message=data.message
        )

    def get_student_notifications(self, student_id: int, status: Optional[str] = None) -> List[Notification]:
        enum_status = NotificationStatus(status) if status else None
        return self.repo.get_by_student(student_id=student_id, status=enum_status)

    def mark_notification_read(self, notification_id: int, student_id: int) -> Optional[Notification]:
        return self.repo.mark_as_read(notification_id=notification_id, student_id=student_id)

    def mark_all_notifications_read(self, student_id: int) -> int:
        return self.repo.mark_all_as_read(student_id=student_id)

    def process_pending_notifications_batch(self, limit: int = 100) -> int:
        pending = self.repo.get_pending_processing(limit=limit)
        processed_count = 0
        for item in pending:
            try:
                # Process in-app delivery state
                self.repo.mark_processed(item.id)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed processing notification id={item.id}: {str(e)}")
        return processed_count

```

### 6.5 Background Job Implementation (`SCRUM-84`)

**Path:** `backend/app/jobs/notification_job.py`

```python
import logging
from app.db.session import SessionLocal
from app.modules.notifications.service import NotificationService

logger = logging.getLogger(__name__)

def process_notifications_job():
    """
    Background job handling notification delivery and state processing independently of API requests (SCRUM-84).
    """
    db = SessionLocal()
    try:
        logger.info("Starting background notification processing job...")
        service = NotificationService(db)
        count = service.process_pending_notifications_batch(limit=100)
        logger.info(f"Notification processing job completed. Successfully processed {count} notifications.")
    except Exception as exc:
        logger.error(f"Notification job encountered an error: {str(exc)}", exc_info=True)
        db.rollback()
    finally:
        db.close()

```

Register job in `backend/app/jobs/scheduler.py` (CAUTION: modify only scheduler setup):

```python
from app.jobs.notification_job import process_notifications_job

def start_scheduler(scheduler):
    # Existing jobs retained...
    scheduler.add_job(
        process_notifications_job,
        'interval',
        minutes=5,
        id='process_notifications_job',
        replace_existing=True
    )

```

### 6.6 API Router Setup

**Path:** `backend/app/modules/notifications/router.py`

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_student
from app.modules.notifications.schemas import NotificationResponse, NotificationCreate
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    status: Optional[str] = Query(None, description="Filter by status: UNREAD, READ, ARCHIVED"),
    current_student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    return service.get_student_notifications(student_id=current_student.id, status=status)

@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    current_student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    updated = service.mark_notification_read(notification_id=notification_id, student_id=current_student.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Notification not found")
    return updated

@router.post("/read-all")
def mark_all_read(
    current_student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    service = NotificationService(db)
    count = service.mark_all_notifications_read(student_id=current_student.id)
    return {"message": "Notifications updated", "updated_count": count}

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreate,
    current_student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    if payload.student_id != current_student.id:
        raise HTTPException(status_code=403, detail="Cannot generate notification for another student")
    service = NotificationService(db)
    return service.generate_notification(payload)

```

### 6.7 Data Seeding Script

**Path:** `backend/scripts/seed_notifications.py`

```python
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.modules.notifications.models import Notification, NotificationSource, NotificationStatus, ProcessingStatus

logger = logging.getLogger(__name__)

def seed_notifications(db: Session, student_id: int):
    logger.info(f"Seeding notifications for student_id={student_id}...")
    
    existing = db.query(Notification).filter(Notification.student_id == student_id).first()
    if existing:
        logger.info("Notifications already seeded. Skipping.")
        return

    sample_notifications = [
        Notification(
            student_id=student_id,
            source=NotificationSource.ASSIGNMENT_DEADLINE,
            source_id=101,
            title="Assignment Due Soon: DBMS Record",
            message="Your DBMS Lab Record submission is due in 24 hours.",
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PROCESSED,
            created_at=datetime.now(timezone.utc)
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.REMINDER_TRIGGER,
            source_id=202,
            title="Reminder: Study for Computer Networks",
            message="Custom reminder: Chapter 4 revision scheduled now.",
            status=NotificationStatus.UNREAD,
            processing_status=ProcessingStatus.PROCESSED,
            created_at=datetime.now(timezone.utc)
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.ANNOUNCEMENT,
            source_id=303,
            title="Campus Placement Drive",
            message="Registration for the upcoming tech drive closes this Friday.",
            status=NotificationStatus.READ,
            processing_status=ProcessingStatus.PROCESSED,
            read_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        ),
        Notification(
            student_id=student_id,
            source=NotificationSource.EXAMINATION,
            source_id=404,
            title="Mid-Semester Exam Schedule Released",
            message="The timetable for Mid-Sem 2 examinations is now live.",
            status=NotificationStatus.READ,
            processing_status=ProcessingStatus.PROCESSED,
            read_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
    ]

    db.add_all(sample_notifications)
    db.commit()
    logger.info("Notification seeding completed.")

```

Integrate into `backend/scripts/seed.py`:

```python
from scripts.seed_notifications import seed_notifications

def run_seed():
    # Existing demo seed logic
    db = SessionLocal()
    try:
        demo_student_id = 1 # Retrieve or reference standard demo student
        seed_notifications(db, student_id=demo_student_id)
    finally:
        db.close()

```

### 6.8 Frontend Service Layer

**Path:** `frontend/src/services/notificationsService.js`

```javascript
import api from './api';

export const notificationsService = {
  async getNotifications(status = null) {
    const params = status ? { status } : {};
    const response = await api.get('/notifications', { params });
    return response.data;
  },

  async markAsRead(id) {
    const response = await api.post(`/notifications/${id}/read`);
    return response.data;
  },

  async markAllAsRead() {
    const response = await api.post('/notifications/read-all');
    return response.data;
  }
};

```

### 6.9 Frontend Notifications Center (`SCRUM-82`)

**Path:** `frontend/src/pages/NotificationsPage.jsx`

```jsx
import React, { useEffect, useState } from 'react';
import { notificationsService } from '../services/notificationsService';
import { Bell, CheckCircle, Info, Calendar, AlertCircle, Bookmark } from 'lucide-react';

export const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const statusParam = filter === 'ALL' ? null : filter;
      const data = await notificationsService.getNotifications(statusParam);
      setNotifications(data);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const handleMarkAsRead = async (id) => {
    try {
      await notificationsService.markAsRead(id);
      fetchNotifications();
    } catch (err) {
      console.error('Error marking as read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationsService.markAllAsRead();
      fetchNotifications();
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'ASSIGNMENT_DEADLINE': return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'REMINDER_TRIGGER': return <Calendar className="w-5 h-5 text-blue-500" />;
      case 'ANNOUNCEMENT': return <Info className="w-5 h-5 text-yellow-500" />;
      case 'EXAMINATION': return <Bookmark className="w-5 h-5 text-purple-500" />;
      default: return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-sm text-gray-500">Stay updated with academic events and deadline alerts.</p>
        </div>
        {notifications.some(n => n.status === 'UNREAD') && (
          <button
            onClick={handleMarkAllRead}
            className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            <CheckCircle className="w-4 h-4" /> Mark all as read
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-4 border-b border-gray-200 mb-6">
        {['ALL', 'UNREAD', 'READ'].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`pb-2 text-sm font-medium capitalize ${
              filter === tab
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.toLowerCase()}
          </button>
        ))}
      </div>

      {/* Notification List & Empty State (SCRUM-82 AC1/AC2) */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading notifications...</div>
      ) : notifications.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-200 rounded-lg">
          <Bell className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-base font-medium text-gray-900">You're all caught up!</h3>
          <p className="text-sm text-gray-500 mt-1">No notifications found in this view.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((item) => (
            <div
              key={item.id}
              className={`flex items-start justify-between p-4 rounded-lg border ${
                item.status === 'UNREAD' ? 'bg-blue-50/50 border-blue-200' : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">{getSourceIcon(item.source)}</div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">{item.title}</h4>
                  <p className="text-sm text-gray-600 mt-0.5">{item.message}</p>
                  <span className="text-xs text-gray-400 mt-2 block">
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
              {item.status === 'UNREAD' && (
                <button
                  onClick={() => handleMarkAsRead(item.id)}
                  className="text-xs font-medium text-blue-600 hover:text-blue-800"
                >
                  Mark read
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

```

---

## 7. Phase 4 — Reviewer Agent Verification (`reviewer.md`)

Before proceeding to testing, `reviewer.md` performs a file integrity check:

* [x] **No Unrelated Touches:** Verify zero modifications made in `assignments/`, `reminders/`, `auth/` (excluding router mounting).
* [x] **Correct Model References:** Ensure `NotificationSource` enums cover documented sources.
* [x] **Job Isolation:** Ensure `process_notifications_job` handles exceptions gracefully without aborting the main application thread.
* [x] **Separation of Concerns:** Confirm UI reads state strictly from `notificationsService.js` and does not call database models or external hooks directly.

---

## 8. Phase 5 — Tester Agent Task Suite (`tester.md`)

### 8.1 Backend Unit & Integration Tests

**Path:** `backend/tests/test_notifications.py`

```python
import pytest
from app.modules.notifications.service import NotificationService
from app.modules.notifications.schemas import NotificationCreate
from app.modules.notifications.models import NotificationSource, NotificationStatus

def test_generate_notification_success(db_session):
    service = NotificationService(db_session)
    payload = NotificationCreate(
        student_id=1,
        source=NotificationSource.ANNOUNCEMENT,
        source_id=10,
        title="Test Announcement",
        message="This is a test notification."
    )
    notification = service.generate_notification(payload)
    assert notification.id is not None
    assert notification.status == NotificationStatus.UNREAD
    assert notification.title == "Test Announcement"

def test_unsupported_notification_source(db_session):
    service = NotificationService(db_session)
    with pytest.raises(ValueError):
        service.generate_notification(
            NotificationCreate(
                student_id=1,
                source="INVALID_SOURCE",
                title="Invalid",
                message="Should fail"
            )
        )

def test_mark_as_read(db_session):
    service = NotificationService(db_session)
    payload = NotificationCreate(
        student_id=1,
        source=NotificationSource.EXAMINATION,
        title="Exam Alert",
        message="Exam schedule"
    )
    created = service.generate_notification(payload)
    updated = service.mark_notification_read(created.id, student_id=1)
    assert updated.status == NotificationStatus.READ
    assert updated.read_at is not None

```

### 8.2 Background Job Failure Resilience Test

**Path:** `backend/tests/test_notification_job.py`

```python
from app.jobs.notification_job import process_notifications_job

def test_notification_job_resilience(monkeypatch):
    def mock_failure(*args, **kwargs):
        raise RuntimeError("Simulated Database Drop")

    monkeypatch.setattr("app.modules.notifications.service.NotificationService.process_pending_notifications_batch", mock_failure)

    # Job execution should catch the exception internally and log it without crashing
    try:
        process_notifications_job()
    except Exception as exc:
        pytest.fail(f"Background job crashed caller thread: {str(exc)}")

```

---

## 9. Verification Summary for AI Implementation Agent

An AI agent reading this guide can execute the features using this step sequence:

1. **Environment Setup:** Append key values to `.env.example`.
2. **Database:** Execute Alembic migration `20260917_001_notifications_schema.py`.
3. **Backend Logic:** Create `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py` in `backend/app/modules/notifications/`.
4. **Job Decoupling:** Write `backend/app/jobs/notification_job.py` and register it in `scheduler.py`.
5. **Seeding:** Add `seed_notifications.py` and trigger it in `seed.py`.
6. **Frontend UI:** Build `notificationsService.js` and `NotificationsPage.jsx`.
7. **Automated Testing:** Run `pytest backend/tests/test_notifications.py` and verify all tests pass.