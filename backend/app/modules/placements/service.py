from typing import List, Optional
from datetime import datetime

from app.modules.placements.models import Company, PlacementOpportunity, PlacementContribution
from app.modules.placements.repository import CompanyRepository, PlacementOpportunityRepository, PlacementContributionRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class PlacementService:
    def __init__(
        self,
        company_repo: CompanyRepository,
        opportunity_repo: PlacementOpportunityRepository,
        contribution_repo: PlacementContributionRepository,
    ):
        self.company_repo = company_repo
        self.opportunity_repo = opportunity_repo
        self.contribution_repo = contribution_repo

    async def get_open_opportunities(self) -> List[PlacementOpportunity]:
        return await self.opportunity_repo.get_all_open()

    async def get_recent_opportunities(self, limit: int = 20) -> List[PlacementOpportunity]:
        return await self.opportunity_repo.get_recent(limit)

    async def get_published_contributions(self) -> List[PlacementContribution]:
        return await self.contribution_repo.get_published()

    async def get_student_contributions(self, student_id: int) -> List[PlacementContribution]:
        return await self.contribution_repo.get_by_student(student_id)

    async def get_or_create_company(self, name: str) -> Company:
        return await self.company_repo.get_or_create(name)

    async def create_opportunity(self, opportunity: PlacementOpportunity) -> PlacementOpportunity:
        return await self.opportunity_repo.create(opportunity)

    async def upsert_opportunities(self, opportunities: List[PlacementOpportunity]) -> List[PlacementOpportunity]:
        return await self.opportunity_repo.bulk_upsert(opportunities)

    async def create_contribution(self, contribution: PlacementContribution) -> PlacementContribution:
        return await self.contribution_repo.create(contribution)

    async def update_contribution(self, contribution: PlacementContribution) -> PlacementContribution:
        return await self.contribution_repo.update(contribution)

    def create_opportunity_from_data(
        self,
        company_id: int,
        title: str,
        description: Optional[str],
        eligibility_criteria: Optional[str],
        location: Optional[str],
        package_details: Optional[str],
        application_deadline: Optional[datetime],
        recruitment_status: str = "open",
        sync_run_id: Optional[int] = None,
    ) -> PlacementOpportunity:
        return PlacementOpportunity(
            company_id=company_id,
            title=title,
            description=description,
            eligibility_criteria=eligibility_criteria,
            location=location,
            package_details=package_details,
            application_deadline=application_deadline,
            recruitment_status=recruitment_status,
            source_sync_run_id=sync_run_id,
        )

    def create_contribution_from_data(
        self,
        student_id: int,
        company_id: int,
        title: str,
        content: str,
        contribution_type: str,
        is_published: bool = False,
    ) -> PlacementContribution:
        return PlacementContribution(
            student_id=student_id,
            company_id=company_id,
            title=title,
            content=content,
            contribution_type=contribution_type,
            is_published=is_published,
        )