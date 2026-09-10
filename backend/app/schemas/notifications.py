from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class NotificationSource(str, Enum):
    ASSIGNMENT_DEADLINE = "assignment_deadline"
    REMINDER_TRIGGER = "reminder_trigger"
    ANNOUNCEMENT = "announcement"
    EXAMINATION = "examination"
    PLACEMENT = "placement"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class NotificationResponse(BaseModel):
    id: int
    student_id: int
    source: NotificationSource
    source_id: Optional[int]
    title: str
    message: str
    status: NotificationStatus
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int