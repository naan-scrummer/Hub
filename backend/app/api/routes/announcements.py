from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.announcements.service import AnnouncementService
from app.modules.announcements.repository import AnnouncementSourceRepository, AnnouncementRepository
from app.schemas.announcements import (
    AnnouncementSourceResponse,
    AnnouncementResponse,
    AnnouncementListResponse,
    AnnouncementSyncRequest,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/announcements", tags=["announcements"])
logger = get_logger(__name__)


def get_announcement_service(db: AsyncSession = Depends(get_db)) -> AnnouncementService:
    source_repo = AnnouncementSourceRepository(db)
    announcement_repo = AnnouncementRepository(db)
    return AnnouncementService(source_repo, announcement_repo)


def get_sync_service(db: AsyncSession = Depends(get_db)):
    from app.integrations.college_portal.sync_service import SynchronizationService
    from app.integrations.college_portal.repository import SyncRunRepository
    from app.modules.attendance.service import AttendanceService
    from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
    from app.modules.academics.service import AcademicService
    from app.modules.academics.repository import AcademicRepository
    from app.modules.examinations.service import ExaminationService
    from app.modules.examinations.repository import ExaminationRepository
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


from app.api.dependencies.auth import get_current_user, get_current_teacher_profile
from app.modules.authentication.models import User, TeacherProfile
from pydantic import BaseModel, Field

class AnnouncementCreateRequest(BaseModel):
    title: str
    content: str
    category: str = Field(..., description="e.g. academic, event, placement")
    source_id: Optional[int] = None

@router.get("", response_model=AnnouncementListResponse)
async def get_announcements(
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    if category:
        announcements = await announcement_service.get_announcements_by_category(category, limit=limit)
    else:
        announcements = await announcement_service.get_recent_announcements(limit=limit)

    total = await announcement_service.announcement_repo.count_total()

    ann_responses = []
    for ann in announcements:
        source = await announcement_service.source_repo.get_by_id(ann.source_id) if ann.source_id else None
        ann_responses.append(AnnouncementResponse(
            id=ann.id,
            source_id=ann.source_id,
            source_name=source.name if source else None,
            source_reference=ann.source_reference,
            title=ann.title,
            content=ann.content,
            category=ann.category,
            published_at=ann.published_at,
            is_unavailable=False,
        ))

    return AnnouncementListResponse(
        announcements=ann_responses,
        total=total,
        is_unavailable=len(announcements) == 0,
    )


@router.get("/sources", response_model=List[AnnouncementSourceResponse])
async def get_announcement_sources(
    current_user: User = Depends(get_current_user),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    sources = await announcement_service.get_active_sources()
    return [AnnouncementSourceResponse.model_validate(s) for s in sources]


@router.post("/sync")
async def sync_announcements(
    request: AnnouncementSyncRequest,
    current_user: User = Depends(get_current_user),
    sync_service = Depends(get_sync_service),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    source = await announcement_service.source_repo.get_by_id(request.source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Announcement source not found")

    sync_run = await sync_service.sync_announcements(source)
    return {"message": "Announcements synchronized", "sync_run_id": sync_run.id, "status": sync_run.status.value}


@router.post("", response_model=AnnouncementResponse)
async def create_announcement(
    request: AnnouncementCreateRequest,
    profile: TeacherProfile = Depends(get_current_teacher_profile),
    announcement_service: AnnouncementService = Depends(get_announcement_service),
):
    from app.modules.announcements.models import Announcement
    from datetime import datetime, UTC
    
    announcement = Announcement(
        title=request.title,
        content=request.content,
        category=request.category,
        source_id=request.source_id,
        published_at=datetime.now(UTC),
    )
    
    saved_ann = await announcement_service.announcement_repo.create(announcement)
    
    source = await announcement_service.source_repo.get_by_id(saved_ann.source_id) if saved_ann.source_id else None
    
    return AnnouncementResponse(
        id=saved_ann.id,
        source_id=saved_ann.source_id,
        source_name=source.name if source else "Teacher Announcement",
        source_reference=saved_ann.source_reference,
        title=saved_ann.title,
        content=saved_ann.content,
        category=saved_ann.category,
        published_at=saved_ann.published_at,
        is_unavailable=False,
    )