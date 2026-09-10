from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ExaminationResponse(BaseModel):
    id: int
    subject_id: int
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    title: str
    exam_type: str
    exam_date: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    venue: Optional[str]
    description: Optional[str]
    last_synced_at: Optional[datetime]
    is_unavailable: bool = False

    class Config:
        from_attributes = True


class ExaminationListResponse(BaseModel):
    examinations: List[ExaminationResponse]
    is_unavailable: bool = False


class ExaminationSyncRequest(BaseModel):
    pass