from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ReminderTriggerType(str, Enum):
    ASSIGNMENT_DUE = "assignment_due"
    EXAMINATION = "examination"
    CUSTOM = "custom"


class ReminderStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


class ReminderCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    trigger_type: ReminderTriggerType = ReminderTriggerType.CUSTOM
    trigger_time: datetime
    assignment_id: Optional[int] = None
    examination_id: Optional[int] = None


class ReminderResponse(BaseModel):
    id: int
    student_id: int
    assignment_id: Optional[int]
    examination_id: Optional[int]
    title: str
    description: Optional[str]
    trigger_type: ReminderTriggerType
    trigger_time: datetime
    status: ReminderStatus
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True