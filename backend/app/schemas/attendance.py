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

from datetime import date
from app.modules.attendance.models import AttendanceStatus

class DailyAttendanceCreate(BaseModel):
    student_id: int
    date: date
    status: AttendanceStatus

class DailyAttendanceResponse(BaseModel):
    id: int
    student_id: int
    teacher_id: Optional[int]
    date: date
    status: AttendanceStatus
    created_at: datetime

    class Config:
        from_attributes = True

class DailyAttendanceSummary(BaseModel):
    total_classes: int
    present: int
    absent: int
    attendance_percentage: float
    history: List[DailyAttendanceResponse]

class DailyAttendanceStudentResponse(BaseModel):
    student_id: int
    user_id: int
    student_registration_id: str
    name: str
    email: str
    status: Optional[AttendanceStatus] = None

    class Config:
        from_attributes = True