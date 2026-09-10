from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class StudyMaterialResponse(BaseModel):
    id: int
    subject_id: int
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    title: str
    description: Optional[str]
    material_type: str
    file_path: Optional[str]
    external_url: Optional[str]
    uploaded_by_student_id: Optional[int]
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StudyMaterialListResponse(BaseModel):
    materials: List[StudyMaterialResponse]
    total: int


class StudyMaterialCreateRequest(BaseModel):
    subject_id: int
    title: str
    material_type: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    external_url: Optional[str] = None


class StudyMaterialSearchRequest(BaseModel):
    query: Optional[str] = None
    subject_id: Optional[int] = None
    material_type: Optional[str] = None
    limit: int = 50