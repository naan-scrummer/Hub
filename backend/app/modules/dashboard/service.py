from typing import List

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
        unavailable_sections = []

        # ---------------------------------------------------------
        # ASSIGNMENTS
        # ---------------------------------------------------------
        try:
            assignments = await self.assignment_service.get_by_student(student.id)
            subject_ids = list({assignment.subject_id for assignment in assignments})
        except Exception as exc:
            logger.warning(
                "dashboard_assignments_subjects_unavailable",
                error=str(exc),
            )
            subject_ids = []

        try:
            upcoming_assignments = await self.assignment_service.get_upcoming(
                student.id
            )
        except Exception as exc:
            logger.warning(
                "dashboard_upcoming_assignments_unavailable",
                error=str(exc),
            )
            upcoming_assignments = []
            if "assignments" not in unavailable_sections:
                unavailable_sections.append("assignments")

        try:
            overdue_assignments = await self.assignment_service.get_overdue(
                student.id
            )
        except Exception as exc:
            logger.warning(
                "dashboard_overdue_assignments_unavailable",
                error=str(exc),
            )
            overdue_assignments = []
            if "assignments" not in unavailable_sections:
                unavailable_sections.append("assignments")

        # ---------------------------------------------------------
        # EXAMINATIONS
        # ---------------------------------------------------------
        try:
            upcoming_exams = await self.examination_service.get_upcoming_exams(
                student.id,
                subject_ids,
            )
        except Exception as exc:
            logger.warning(
                "dashboard_examinations_unavailable",
                error=str(exc),
            )
            upcoming_exams = []
            unavailable_sections.append("examinations")

        # ---------------------------------------------------------
        # ANNOUNCEMENTS
        # ---------------------------------------------------------
        try:
            recent_announcements = (
                await self.announcement_service.get_recent_announcements(limit=5)
            )
        except Exception as exc:
            logger.warning(
                "dashboard_announcements_unavailable",
                error=str(exc),
            )
            recent_announcements = []
            unavailable_sections.append("announcements")

        # ---------------------------------------------------------
        # ATTENDANCE
        # ---------------------------------------------------------
        try:
            attendance_summary = (
                await self.attendance_service.get_attendance_summary(student.id)
            )
        except Exception as exc:
            logger.warning(
                "dashboard_attendance_unavailable",
                error=str(exc),
            )

            attendance_summary = {
                "total_classes_attended": 0,
                "total_classes": 0,
                "overall_percentage": 0.0,
                "subjects_count": 0,
                "records": [],
                "is_unavailable": True,
            }

            unavailable_sections.append("attendance")

        # ---------------------------------------------------------
        # ACADEMICS
        # ---------------------------------------------------------
        try:
            academics = await self.academic_service.get_student_academics(
                student.id
            )
        except Exception as exc:
            logger.warning(
                "dashboard_academics_unavailable",
                error=str(exc),
            )
            academics = []
            unavailable_sections.append("academics")

        # ---------------------------------------------------------
        # REMINDERS
        # ---------------------------------------------------------
        try:
            pending_reminders = await self.reminder_service.get_by_student(
                student.id
            )

            pending_reminders = [
                reminder
                for reminder in pending_reminders
                if reminder.status.value == "pending"
            ]
        except Exception as exc:
            logger.warning(
                "dashboard_reminders_unavailable",
                error=str(exc),
            )
            pending_reminders = []
            unavailable_sections.append("reminders")

        # ---------------------------------------------------------
        # NOTIFICATIONS
        # ---------------------------------------------------------
        try:
            unread_notifications = await self.notification_service.get_unread_count(
                student.id
            )
        except Exception as exc:
            logger.warning(
                "dashboard_notifications_unavailable",
                error=str(exc),
            )
            unread_notifications = 0
            unavailable_sections.append("notifications")

        # ---------------------------------------------------------
        # PLACEMENTS
        # ---------------------------------------------------------
        try:
            placement_opportunities = (
                await self.placement_service.get_open_opportunities()
            )
        except Exception as exc:
            logger.warning(
                "dashboard_placements_unavailable",
                error=str(exc),
            )
            placement_opportunities = []
            unavailable_sections.append("placements")

        # Remove duplicate section names.
        unavailable_sections = list(dict.fromkeys(unavailable_sections))

        # ---------------------------------------------------------
        # FINAL DASHBOARD RESPONSE
        # ---------------------------------------------------------
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
            "unavailable_sections": unavailable_sections,
        }

    async def get_widgets(self, student_id: int) -> List[DashboardWidget]:
        return await self.widget_repo.get_by_student(student_id)

    async def update_widget(self, widget: DashboardWidget) -> DashboardWidget:
        return await self.widget_repo.update(widget)