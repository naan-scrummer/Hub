from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.academics.service import AcademicService
from app.modules.academics.repository import AcademicRepository
from app.schemas.academics import AcademicRecordResponse, AcademicSummaryResponse, AcademicSyncRequest
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/academics", tags=["academics"])
logger = get_logger(__name__)


def get_academic_service(db: AsyncSession = Depends(get_db)) -> AcademicService:
    academic_repo = AcademicRepository(db)
    return AcademicService(academic_repo)


def get_sync_service(db: AsyncSession = Depends(get_db)):
    from app.integrations.college_portal.sync_service import SynchronizationService
    from app.integrations.college_portal.repository import SyncRunRepository
    from app.modules.attendance.service import AttendanceService
    from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
    from app.modules.examinations.service import ExaminationService
    from app.modules.examinations.repository import ExaminationRepository
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


@router.get("", response_model=AcademicSummaryResponse)
async def get_academics(
    profile: StudentProfile = Depends(get_current_student_profile),
    academic_service: AcademicService = Depends(get_academic_service),
):
    records = await academic_service.get_student_academics(profile.id)

    from app.modules.attendance.repository import SubjectRepository
    subject_repo = SubjectRepository(academic_service.academic_repo.session)

    record_responses = []
    for record in records:
        subject = await subject_repo.get_by_id(record.subject_id)
        record_responses.append(AcademicRecordResponse(
            id=record.id,
            subject_id=record.subject_id,
            subject_code=subject.code if subject else None,
            subject_name=subject.name if subject else None,
            internal_marks=record.internal_marks,
            max_internal_marks=record.max_internal_marks,
            external_marks=record.external_marks,
            max_external_marks=record.max_external_marks,
            total_marks=record.total_marks,
            grade=record.grade,
            semester=record.semester,
            last_synced_at=record.last_synced_at,
            is_unavailable=record.last_synced_at is None,
        ))

    return AcademicSummaryResponse(
        records=record_responses,
        is_unavailable=len(records) == 0,
    )


@router.post("/sync")
async def sync_academics(
    request: AcademicSyncRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    sync_service = Depends(get_sync_service),
):
    if request.student_id != profile.id:
        raise HTTPException(status_code=403, detail="Cannot sync academics for another student")

    sync_run = await sync_service.sync_academics(profile.id)
    return {"message": "Academics synchronized", "sync_run_id": sync_run.id, "status": sync_run.status.value}