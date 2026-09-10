from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SubjectResponse(BaseModel):
    id: int
    code: str
    name: str
    department: Optional[str]
    credits: Optional[int]

    class Config:
        from_attributes = True


class AttendanceRecordResponse(BaseModel):
    id: int
    subject_id: int
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    classes_attended: int
    total_classes: int
    attendance_percentage: float
    last_synced_at: Optional[datetime]
    is_unavailable: bool = False

    class Config:
        from_attributes = True


class AttendanceSummaryResponse(BaseModel):
    total_classes_attended: int
    total_classes: int
    overall_percentage: float
    subjects_count: int
    records: List[AttendanceRecordResponse]
    is_unavailable: bool = False


class AttendanceSyncRequest(BaseModel):
    student_id: int