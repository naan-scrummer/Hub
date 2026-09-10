from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.dashboard.service import DashboardService
from app.modules.dashboard.repository import DashboardWidgetRepository
from app.modules.assignments.service import AssignmentService
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.repository import ReminderRepository
from app.modules.examinations.service import ExaminationService
from app.modules.examinations.repository import ExaminationRepository
from app.modules.announcements.service import AnnouncementService
from app.modules.announcements.repository import AnnouncementSourceRepository, AnnouncementRepository
from app.modules.attendance.service import AttendanceService
from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
from app.modules.academics.service import AcademicService
from app.modules.academics.repository import AcademicRepository
from app.modules.reminders.service import ReminderService
from app.modules.notifications.service import NotificationService
from app.modules.notifications.repository import NotificationRepository
from app.modules.placements.service import PlacementService
from app.modules.placements.repository import CompanyRepository, PlacementOpportunityRepository, PlacementContributionRepository
from app.schemas.dashboard import DashboardDataResponse
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = get_logger(__name__)


def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> DashboardService:
    # Create all required services
    assignment_repo = AssignmentRepository(db)
    reminder_repo = ReminderRepository(db)
    assignment_service = AssignmentService(assignment_repo, reminder_repo)

    exam_repo = ExaminationRepository(db)
    exam_service = ExaminationService(exam_repo)

    ann_source_repo = AnnouncementSourceRepository(db)
    ann_repo = AnnouncementRepository(db)
    announcement_service = AnnouncementService(ann_source_repo, ann_repo)

    subject_repo = SubjectRepository(db)
    attendance_repo = AttendanceRepository(db)
    attendance_service = AttendanceService(subject_repo, attendance_repo)

    academic_repo = AcademicRepository(db)
    academic_service = AcademicService(academic_repo)

    notification_repo = NotificationRepository(db)
    reminder_service = ReminderService(reminder_repo, notification_repo)
    notification_service = NotificationService(notification_repo)

    company_repo = CompanyRepository(db)
    opp_repo = PlacementOpportunityRepository(db)
    contrib_repo = PlacementContributionRepository(db)
    placement_service = PlacementService(company_repo, opp_repo, contrib_repo)

    widget_repo = DashboardWidgetRepository(db)

    return DashboardService(
        assignment_service=assignment_service,
        examination_service=exam_service,
        announcement_service=announcement_service,
        attendance_service=attendance_service,
        academic_service=academic_service,
        reminder_service=reminder_service,
        notification_service=notification_service,
        placement_service=placement_service,
        widget_repo=widget_repo,
    )


@router.get("", response_model=DashboardDataResponse)
async def get_dashboard(
    profile: StudentProfile = Depends(get_current_student_profile),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
):
    data = await dashboard_service.get_dashboard_data(profile)
    return DashboardDataResponse(**data)