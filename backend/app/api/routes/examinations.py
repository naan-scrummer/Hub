from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.examinations.service import ExaminationService
from app.modules.examinations.repository import ExaminationRepository
from app.modules.attendance.repository import SubjectRepository
from app.schemas.examinations import ExaminationResponse, ExaminationListResponse, ExaminationSyncRequest
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/examinations", tags=["examinations"])
logger = get_logger(__name__)


def get_exam_service(db: AsyncSession = Depends(get_db)) -> ExaminationService:
    exam_repo = ExaminationRepository(db)
    return ExaminationService(exam_repo)


def get_sync_service(db: AsyncSession = Depends(get_db)):
    from app.integrations.college_portal.sync_service import SynchronizationService
    from app.integrations.college_portal.repository import SyncRunRepository
    from app.modules.attendance.service import AttendanceService
    from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
    from app.modules.academics.service import AcademicService
    from app.modules.academics.repository import AcademicRepository
    from app.modules.announcements.service import AnnouncementService
    from app.modules.announcements.repository import AnnouncementSourceRepository, AnnouncementRepository
    from app.modules.placements.service import PlacementService
    from app.modules.placements.repository import CompanyRepository, PlacementOpportunityRepository, PlacementContributionRepository

    sync_run_repo = SyncRunRepository(db)
    subject_repo = SubjectRepository(db)
    attendance_repo = AttendanceRepository(db)
    academic_repo = AcademicRepository(db)
    exam_repo = ExaminationRepository(db)
    ann_source_repo = AnnouncementSourceRepository(db)
    ann_repo = AnnouncementRepository(db)
    company_repo = CompanyRepository(db)
    opp_repo = PlacementOpportunityRepository(db)
    contrib_repo = PlacementContributionRepository(db)

    attendance_service = AttendanceService(subject_repo, attendance_repo)
    academic_service = AcademicService(academic_repo)
    exam_service = ExaminationService(exam_repo)
    announcement_service = AnnouncementService(ann_source_repo, ann_repo)
    placement_service = PlacementService(company_repo, opp_repo, contrib_repo)

    return SynchronizationService(
        sync_run_repo=sync_run_repo,
        attendance_service=attendance_service,
        academic_service=academic_service,
        examination_service=exam_service,
        announcement_service=announcement_service,
        placement_service=placement_service,
    )


@router.get("", response_model=ExaminationListResponse)
async def get_examinations(
    profile: StudentProfile = Depends(get_current_student_profile),
    exam_service: ExaminationService = Depends(get_exam_service),
):
    # Get subject IDs from student's assignments or attendance
    from app.modules.assignments.repository import AssignmentRepository
    assignment_repo = AssignmentRepository(exam_service.exam_repo.session)
    assignments = await assignment_repo.get_by_student(profile.id)
    subject_ids = list(set(a.subject_id for a in assignments))

    exams = await exam_service.get_upcoming_exams(profile.id, subject_ids)

    subject_repo = SubjectRepository(exam_service.exam_repo.session)
    exam_responses = []
    for exam in exams:
        subject = await subject_repo.get_by_id(exam.subject_id)
        exam_responses.append(ExaminationResponse(
            id=exam.id,
            subject_id=exam.subject_id,
            subject_code=subject.code if subject else None,
            subject_name=subject.name if subject else None,
            title=exam.title,
            exam_type=exam.exam_type,
            exam_date=exam.exam_date,
            start_time=exam.start_time,
            end_time=exam.end_time,
            venue=exam.venue,
            description=exam.description,
            last_synced_at=exam.last_synced_at,
            is_unavailable=exam.last_synced_at is None,
        ))

    return ExaminationListResponse(
        examinations=exam_responses,
        is_unavailable=len(exams) == 0,
    )


@router.post("/sync")
async def sync_examinations(
    request: ExaminationSyncRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    sync_service = Depends(get_sync_service),
):
    sync_run = await sync_service.sync_examinations()
    return {"message": "Examinations synchronized", "sync_run_id": sync_run.id, "status": sync_run.status.value}