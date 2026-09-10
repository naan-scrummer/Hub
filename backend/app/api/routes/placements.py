from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.placements.service import PlacementService
from app.modules.placements.repository import CompanyRepository, PlacementOpportunityRepository, PlacementContributionRepository
from app.schemas.placements import (
    CompanyResponse,
    PlacementOpportunityResponse,
    PlacementOpportunityListResponse,
    PlacementContributionResponse,
    PlacementContributionListResponse,
    PlacementContributionCreateRequest,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/placements", tags=["placements"])
logger = get_logger(__name__)


def get_placement_service(db: AsyncSession = Depends(get_db)) -> PlacementService:
    company_repo = CompanyRepository(db)
    opp_repo = PlacementOpportunityRepository(db)
    contrib_repo = PlacementContributionRepository(db)
    return PlacementService(company_repo, opp_repo, contrib_repo)


def get_sync_service(db: AsyncSession = Depends(get_db)):
    from app.integrations.college_portal.sync_service import SynchronizationService
    from app.integrations.college_portal.repository import SyncRunRepository
    from app.modules.attendance.service import AttendanceService
    from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
    from app.modules.academics.service import AcademicService
    from app.modules.academics.repository import AcademicRepository
    from app.modules.examinations.service import ExaminationService
    from app.modules.examinations.repository import ExaminationRepository
    from app.modules.announcements.service import AnnouncementService
    from app.modules.announcements.repository import AnnouncementSourceRepository, AnnouncementRepository

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


@router.get("/opportunities", response_model=PlacementOpportunityListResponse)
async def get_opportunities(
    profile: StudentProfile = Depends(get_current_student_profile),
    placement_service: PlacementService = Depends(get_placement_service),
):
    opportunities = await placement_service.get_open_opportunities()

    opp_responses = []
    for opp in opportunities:
        company = await placement_service.company_repo.get_by_id(opp.company_id)
        opp_responses.append(PlacementOpportunityResponse(
            id=opp.id,
            company_id=opp.company_id,
            company_name=company.name if company else None,
            title=opp.title,
            description=opp.description,
            eligibility_criteria=opp.eligibility_criteria,
            location=opp.location,
            package_details=opp.package_details,
            application_deadline=opp.application_deadline,
            recruitment_status=opp.recruitment_status,
            created_at=opp.created_at,
        ))

    return PlacementOpportunityListResponse(opportunities=opp_responses)


@router.get("/contributions", response_model=PlacementContributionListResponse)
async def get_contributions(
    profile: StudentProfile = Depends(get_current_student_profile),
    placement_service: PlacementService = Depends(get_placement_service),
):
    contributions = await placement_service.get_published_contributions()

    contrib_responses = []
    for contrib in contributions:
        company = await placement_service.company_repo.get_by_id(contrib.company_id)
        contrib_responses.append(PlacementContributionResponse(
            id=contrib.id,
            student_id=contrib.student_id,
            company_id=contrib.company_id,
            company_name=company.name if company else None,
            title=contrib.title,
            content=contrib.content,
            contribution_type=contrib.contribution_type,
            is_published=contrib.is_published,
            created_at=contrib.created_at,
        ))

    return PlacementContributionListResponse(contributions=contrib_responses)


@router.get("/my-contributions", response_model=PlacementContributionListResponse)
async def get_my_contributions(
    profile: StudentProfile = Depends(get_current_student_profile),
    placement_service: PlacementService = Depends(get_placement_service),
):
    contributions = await placement_service.get_student_contributions(profile.id)

    contrib_responses = []
    for contrib in contributions:
        company = await placement_service.company_repo.get_by_id(contrib.company_id)
        contrib_responses.append(PlacementContributionResponse(
            id=contrib.id,
            student_id=contrib.student_id,
            company_id=contrib.company_id,
            company_name=company.name if company else None,
            title=contrib.title,
            content=contrib.content,
            contribution_type=contrib.contribution_type,
            is_published=contrib.is_published,
            created_at=contrib.created_at,
        ))

    return PlacementContributionListResponse(contributions=contrib_responses)


@router.post("/contributions", response_model=PlacementContributionResponse)
async def create_contribution(
    request: PlacementContributionCreateRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    placement_service: PlacementService = Depends(get_placement_service),
):
    contribution = placement_service.create_contribution_from_data(
        student_id=profile.id,
        company_id=request.company_id,
        title=request.title,
        content=request.content,
        contribution_type=request.contribution_type,
    )
    contribution = await placement_service.create_contribution(contribution)

    company = await placement_service.company_repo.get_by_id(contribution.company_id)
    return PlacementContributionResponse(
        id=contribution.id,
        student_id=contribution.student_id,
        company_id=contribution.company_id,
        company_name=company.name if company else None,
        title=contribution.title,
        content=contribution.content,
        contribution_type=contribution.contribution_type,
        is_published=contribution.is_published,
        created_at=contribution.created_at,
    )


@router.post("/sync")
async def sync_placements(
    profile: StudentProfile = Depends(get_current_student_profile),
    sync_service = Depends(get_sync_service),
):
    sync_run = await sync_service.sync_placements()
    return {"message": "Placements synchronized", "sync_run_id": sync_run.id, "status": sync_run.status.value}