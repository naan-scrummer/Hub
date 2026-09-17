from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.modules.notifications.models import NotificationSource, NotificationStatus, ProcessingStatus


class NotificationCreate(BaseModel):
    student_id: int
    source: NotificationSource
    source_id: Optional[int] = None
    title: str
    message: str


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    source: NotificationSource
    source_id: Optional[int] = None
    title: str
    message: str
    status: NotificationStatus
    processing_status: Optional[ProcessingStatus] = ProcessingStatus.PENDING
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int
