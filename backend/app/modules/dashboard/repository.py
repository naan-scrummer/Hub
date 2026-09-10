from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard.models import DashboardWidget


class DashboardWidgetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_student(self, student_id: int) -> List[DashboardWidget]:
        result = await self.session.execute(
            select(DashboardWidget).where(DashboardWidget.student_id == student_id).order_by(DashboardWidget.position)
        )
        return list(result.scalars().all())

    async def create(self, widget: DashboardWidget) -> DashboardWidget:
        self.session.add(widget)
        await self.session.flush()
        await self.session.refresh(widget)
        return widget

    async def update(self, widget: DashboardWidget) -> DashboardWidget:
        await self.session.flush()
        await self.session.refresh(widget)
        return widget