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
    subject_id: Optional[int] = None
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


class TestCaseCreate(BaseModel):
    input_data: str
    expected_output: str
    points: int
    order_index: int

class TestCaseResponse(BaseModel):
    id: int
    input_data: str
    expected_output: str
    points: int
    order_index: int

    class Config:
        from_attributes = True


class CodingAssignmentCreateRequest(BaseModel):
    title: str
    description: str
    difficulty: str
    allowed_languages: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    time_limit: float = 1.0
    memory_limit: int = 128
    max_points: int = 100
    due_date: datetime
    test_cases: List[TestCaseCreate]


class CodingAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    title: str
    description: str
    difficulty: str
    allowed_languages: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    time_limit: float
    memory_limit: int
    max_points: int
    due_date: datetime
    test_cases: List[TestCaseResponse]
    completed_by_user: Optional[bool] = False

    class Config:
        from_attributes = True


class CodingSubmissionCreateRequest(BaseModel):
    assignment_id: int
    language: str
    source_code: str


class SubmissionTestResultResponse(BaseModel):
    id: int
    test_case_id: int
    status: str
    actual_output: Optional[str] = None
    execution_time: Optional[float] = None
    points_awarded: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class CodingSubmissionResponse(BaseModel):
    id: int
    student_id: int
    assignment_id: int
    language: str
    source_code: str
    score: int
    status: str
    execution_time: Optional[float] = None
    passed_tests: int
    total_tests: int
    created_at: datetime
    test_results: List[SubmissionTestResultResponse] = []

    class Config:
        from_attributes = True