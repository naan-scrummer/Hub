from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.placements.models import Company, PlacementOpportunity, PlacementContribution


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Company):
        return select(parameter)

    async def get_by_id(self, company_id: int) -> Optional[Company]:
        result = await self.session.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Company]:
        result = await self.session.execute(select(Company).where(Company.name == name))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Company]:
        result = await self.session.execute(select(Company).order_by(Company.name))
        return list(result.scalars().all())

    async def create(self, company: Company) -> Company:
        self.session.add(company)
        await self.session.flush()
        await self.session.refresh(company)
        return company

    async def get_or_create(self, name: str) -> Company:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        company = Company(name=name)
        return await self.create(company)


class PlacementOpportunityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: PlacementOpportunity):
        return select(parameter)

    async def get_by_id(self, opportunity_id: int) -> Optional[PlacementOpportunity]:
        result = await self.session.execute(select(PlacementOpportunity).where(PlacementOpportunity.id == opportunity_id))
        return result.scalar_one_or_none()

    async def get_all_open(self) -> List[PlacementOpportunity]:
        result = await self.session.execute(
            select(PlacementOpportunity)
            .where(PlacementOpportunity.recruitment_status == "open")
            .order_by(PlacementOpportunity.application_deadline.asc().nullslast())
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 20) -> List[PlacementOpportunity]:
        result = await self.session.execute(
            select(PlacementOpportunity)
            .order_by(PlacementOpportunity.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, opportunity: PlacementOpportunity) -> PlacementOpportunity:
        self.session.add(opportunity)
        await self.session.flush()
        await self.session.refresh(opportunity)
        return opportunity

    async def bulk_upsert(self, opportunities: List[PlacementOpportunity]) -> List[PlacementOpportunity]:
        for opp in opportunities:
            existing = await self.get_by_id(opp.id) if opp.id else None
            if existing:
                existing.title = opp.title
                existing.description = opp.description
                existing.eligibility_criteria = opp.eligibility_criteria
                existing.location = opp.location
                existing.package_details = opp.package_details
                existing.application_deadline = opp.application_deadline
                existing.recruitment_status = opp.recruitment_status
                existing.source_sync_run_id = opp.source_sync_run_id
            else:
                self.session.add(opp)
        await self.session.flush()
        for opp in opportunities:
            await self.session.refresh(opp)
        return opportunities


class PlacementContributionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: PlacementContribution):
        return select(parameter)

    async def get_by_id(self, contribution_id: int) -> Optional[PlacementContribution]:
        result = await self.session.execute(select(PlacementContribution).where(PlacementContribution.id == contribution_id))
        return result.scalar_one_or_none()

    async def get_published(self) -> List[PlacementContribution]:
        result = await self.session.execute(
            select(PlacementContribution)
            .where(PlacementContribution.is_published == True)
            .order_by(PlacementContribution.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_student(self, student_id: int) -> List[PlacementContribution]:
        result = await self.session.execute(
            select(PlacementContribution)
            .where(PlacementContribution.student_id == student_id)
            .order_by(PlacementContribution.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, contribution: PlacementContribution) -> PlacementContribution:
        self.session.add(contribution)
        await self.session.flush()
        await self.session.refresh(contribution)
        return contribution

    async def update(self, contribution: PlacementContribution) -> PlacementContribution:
        await self.session.flush()
        await self.session.refresh(contribution)
        return contribution