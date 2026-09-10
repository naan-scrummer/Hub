from typing import List, Optional
from datetime import datetime

from app.modules.dashboard.models import DashboardWidget
from app.modules.dashboard.repository import DashboardWidgetRepository
from app.modules.assignments.service import AssignmentService
from app.modules.examinations.service import ExaminationService
from app.modules.announcements.service import AnnouncementService
from app.modules.attendance.service import AttendanceService
from app.modules.academics.service import AcademicService
from app.modules.reminders.service import ReminderService
from app.modules.notifications.service import NotificationService
from app.modules.placements.service import PlacementService
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


logger = get_logger(__name__)


class DashboardService:
    def __init__(
        self,
        assignment_service: AssignmentService,
        examination_service: ExaminationService,
        announcement_service: AnnouncementService,
        attendance_service: AttendanceService,
        academic_service: AcademicService,
        reminder_service: ReminderService,
        notification_service: NotificationService,
        placement_service: PlacementService,
        widget_repo: DashboardWidgetRepository,
    ):
        self.assignment_service = assignment_service
        self.examination_service = examination_service
        self.announcement_service = announcement_service
        self.attendance_service = attendance_service
        self.academic_service = academic_service
        self.reminder_service = reminder_service
        self.notification_service = notification_service
        self.placement_service = placement_service
        self.widget_repo = widget_repo

    async def get_dashboard_data(self, student: StudentProfile) -> dict:
        subject_ids = [a.subject_id for a in await self.assignment_service.get_by_student(student.id)]
        subject_ids = list(set(subject_ids))

        upcoming_assignments = await self.assignment_service.get_upcoming(student.id)
        overdue_assignments = await self.assignment_service.get_overdue(student.id)
        upcoming_exams = await self.examination_service.get_upcoming_exams(student.id, subject_ids)
        recent_announcements = await self.announcement_service.get_recent_announcements(limit=5)
        attendance_summary = await self.attendance_service.get_attendance_summary(student.id)
        academics = await self.academic_service.get_student_academics(student.id)
        pending_reminders = await self.reminder_service.get_by_student(student.id)
        unread_notifications = await self.notification_service.get_unread_count(student.id)
        placement_opportunities = await self.placement_service.get_open_opportunities()

        pending_reminders = [r for r in pending_reminders if r.status.value == "pending"]

        return {
            "upcoming_assignments": upcoming_assignments[:5],
            "overdue_assignments": overdue_assignments[:5],
            "upcoming_examinations": upcoming_exams[:5],
            "recent_announcements": recent_announcements,
            "attendance_summary": attendance_summary,
            "academic_summary": academics[:5],
            "pending_reminders": pending_reminders[:5],
            "unread_notifications_count": unread_notifications,
            "placement_opportunities": placement_opportunities[:5],
        }

    async def get_widgets(self, student_id: int) -> List[DashboardWidget]:
        return await self.widget_repo.get_by_student(student_id)

    async def update_widget(self, widget: DashboardWidget) -> DashboardWidget:
        return await self.widget_repo.update(widget)