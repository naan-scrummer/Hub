from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ReminderTriggerType(str, Enum):
    ASSIGNMENT_DUE = "assignment_due"
    EXAMINATION = "examination"
    CUSTOM = "custom"


class ReminderOrigin(str, Enum):
    AUTOMATIC = "automatic"
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


class ReminderUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    trigger_time: Optional[datetime] = None
    # Note: status is NOT user-updatable. Status transitions are system-managed
    # (PENDING -> PROCESSED via background job, PENDING -> CANCELLED via entity hooks).


class ReminderResponse(BaseModel):
    id: int
    student_id: int
    assignment_id: Optional[int] = None
    examination_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    trigger_type: ReminderTriggerType
    trigger_time: datetime
    origin: ReminderOrigin
    status: ReminderStatus
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # Related entity titles for frontend context badges
    assignment_title: Optional[str] = None
    examination_title: Optional[str] = None

    class Config:
        from_attributes = True
