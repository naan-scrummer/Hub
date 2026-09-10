from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.college_portal.models import SyncRun, SyncSourceType, SyncStatus


class SyncRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, sync_run_id: int) -> Optional[SyncRun]:
        result = await self.session.execute(select(SyncRun).where(SyncRun.id == sync_run_id))
        return result.scalar_one_or_none()

    async def get_recent(self, source_type: Optional[SyncSourceType] = None, limit: int = 20) -> List[SyncRun]:
        stmt = select(SyncRun).order_by(SyncRun.started_at.desc()).limit(limit)
        if source_type:
            stmt = stmt.where(SyncRun.source_type == source_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_source(self, source_type: SyncSourceType, source_name: str) -> Optional[SyncRun]:
        result = await self.session.execute(
            select(SyncRun)
            .where(SyncRun.source_type == source_type, SyncRun.source_name == source_name)
            .order_by(SyncRun.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, sync_run: SyncRun) -> SyncRun:
        self.session.add(sync_run)
        await self.session.flush()
        await self.session.refresh(sync_run)
        return sync_run

    async def update(self, sync_run: SyncRun) -> SyncRun:
        await self.session.flush()
        await self.session.refresh(sync_run)
        return sync_run

    async def mark_running(self, sync_run_id: int) -> Optional[SyncRun]:
        sync_run = await self.get_by_id(sync_run_id)
        if sync_run:
            sync_run.status = SyncStatus.RUNNING
            await self.session.flush()
            await self.session.refresh(sync_run)
        return sync_run

    async def mark_completed(
        self,
        sync_run_id: int,
        status: SyncStatus,
        records_processed: int,
        records_created: int,
        records_updated: int,
        records_failed: int,
        error_message: Optional[str] = None,
        error_details: Optional[str] = None,
    ) -> Optional[SyncRun]:
        sync_run = await self.get_by_id(sync_run_id)
        if sync_run:
            sync_run.status = status
            sync_run.completed_at = datetime.utcnow()
            sync_run.records_processed = records_processed
            sync_run.records_created = records_created
            sync_run.records_updated = records_updated
            sync_run.records_failed = records_failed
            sync_run.error_message = error_message
            sync_run.error_details = error_details
            await self.session.flush()
            await self.session.refresh(sync_run)
        return sync_run