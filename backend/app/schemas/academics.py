from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class AcademicRecordResponse(BaseModel):
    id: int
    subject_id: int
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    internal_marks: Optional[int]
    max_internal_marks: Optional[int]
    external_marks: Optional[int]
    max_external_marks: Optional[int]
    total_marks: Optional[int]
    grade: Optional[str]
    semester: int
    last_synced_at: Optional[datetime]
    is_unavailable: bool = False

    class Config:
        from_attributes = True


class AcademicSummaryResponse(BaseModel):
    records: List[AcademicRecordResponse]
    is_unavailable: bool = False


class AcademicSyncRequest(BaseModel):
    student_id: int