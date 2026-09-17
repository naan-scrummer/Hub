from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.assignments import AssignmentResponse
from app.schemas.examinations import ExaminationResponse
from app.schemas.announcements import AnnouncementResponse
from app.schemas.attendance import AttendanceSummaryResponse
from app.schemas.academics import AcademicRecordResponse
from app.schemas.reminders import ReminderResponse
from app.schemas.placements import PlacementOpportunityResponse


class DashboardWidgetResponse(BaseModel):
    id: int
    widget_type: str
    position: int
    is_visible: bool
    config: Optional[str]

    class Config:
        from_attributes = True


class DashboardDataResponse(BaseModel):
    upcoming_assignments: List[AssignmentResponse]
    overdue_assignments: List[AssignmentResponse]
    upcoming_examinations: List[ExaminationResponse]
    recent_announcements: List[AnnouncementResponse]
    attendance_summary: AttendanceSummaryResponse
    academic_summary: List[AcademicRecordResponse]
    pending_reminders: List[ReminderResponse]
    unread_notifications_count: int
    placement_opportunities: List[PlacementOpportunityResponse]
    unavailable_sections: List[str] = []