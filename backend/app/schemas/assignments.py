from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class AssignmentStatus(str, Enum):
    UPCOMING = "upcoming"
    OVERDUE = "overdue"
    COMPLETED = "completed"


class AssignmentCreateRequest(BaseModel):
    subject_id: int
    title: str
    description: Optional[str] = None
    due_date: datetime


class AssignmentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    


class AssignmentResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    title: str
    description: Optional[str]
    due_date: datetime
    status: AssignmentStatus
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignmentListResponse(BaseModel):
    upcoming: List[AssignmentResponse]
    overdue: List[AssignmentResponse]
    completed: List[AssignmentResponse]