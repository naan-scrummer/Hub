from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.attendance.service import AttendanceService
from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
from app.schemas.attendance import (
    SubjectResponse,
    AttendanceRecordResponse,
    AttendanceSummaryResponse,
    AttendanceSyncRequest,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/attendance", tags=["attendance"])
logger = get_logger(__name__)


def get_attendance_service(db: AsyncSession = Depends(get_db)) -> AttendanceService:
    subject_repo = SubjectRepository(db)
    attendance_repo = AttendanceRepository(db)
    return AttendanceService(subject_repo, attendance_repo)


def get_sync_service(db: AsyncSession = Depends(get_db)):
    from app.integrations.college_portal.sync_service import SynchronizationService
    from app.integrations.college_portal.repository import SyncRunRepository
    from app.modules.academics.service import AcademicService
    from app.modules.academics.repository import AcademicRepository
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


@router.get("/subjects", response_model=List[SubjectResponse])
async def get_subjects(
    attendance_service: AttendanceService = Depends(get_attendance_service),
):
    subjects = await attendance_service.get_subjects()
    return [SubjectResponse.model_validate(s) for s in subjects]


@router.get("/summary", response_model=AttendanceSummaryResponse)
async def get_attendance_summary(
    profile: StudentProfile = Depends(get_current_student_profile),
    attendance_service: AttendanceService = Depends(get_attendance_service),
):
    summary = await attendance_service.get_attendance_summary(profile.id)
    records = await attendance_service.get_student_attendance(profile.id)

    subject_repo = SubjectRepository(attendance_service.attendance_repo.session)
    record_responses = []
    for record in records:
        subject = await subject_repo.get_by_id(record.subject_id)
        record_responses.append(AttendanceRecordResponse(
            id=record.id,
            subject_id=record.subject_id,
            subject_code=subject.code if subject else None,
            subject_name=subject.name if subject else None,
            classes_attended=record.classes_attended,
            total_classes=record.total_classes,
            attendance_percentage=record.attendance_percentage,
            last_synced_at=record.last_synced_at,
            is_unavailable=record.last_synced_at is None,
        ))

    return AttendanceSummaryResponse(
        total_classes_attended=summary["total_classes_attended"],
        total_classes=summary["total_classes"],
        overall_percentage=summary["overall_percentage"],
        subjects_count=summary["subjects_count"],
        records=record_responses,
        is_unavailable=len(records) == 0,
    )


@router.get("/{subject_id}", response_model=AttendanceRecordResponse)
async def get_subject_attendance(
    subject_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    attendance_service: AttendanceService = Depends(get_attendance_service),
):
    record = await attendance_service.get_subject_attendance(profile.id, subject_id)
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    subject_repo = SubjectRepository(attendance_service.attendance_repo.session)
    subject = await subject_repo.get_by_id(subject_id)

    return AttendanceRecordResponse(
        id=record.id,
        subject_id=record.subject_id,
        subject_code=subject.code if subject else None,
        subject_name=subject.name if subject else None,
        classes_attended=record.classes_attended,
        total_classes=record.total_classes,
        attendance_percentage=record.attendance_percentage,
        last_synced_at=record.last_synced_at,
        is_unavailable=record.last_synced_at is None,
    )


@router.post("/sync")
async def sync_attendance(
    request: AttendanceSyncRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    sync_service = Depends(get_sync_service),
):
    if request.student_id != profile.id:
        raise HTTPException(status_code=403, detail="Cannot sync attendance for another student")

    sync_run = await sync_service.sync_attendance(profile.id)
    return {"message": "Attendance synchronized", "sync_run_id": sync_run.id, "status": sync_run.status.value}