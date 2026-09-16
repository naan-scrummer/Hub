from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.announcements.models import AnnouncementSource, Announcement


class AnnouncementSourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: AnnouncementSource):
        return select(parameter)

    async def get_by_id(self, source_id: int) -> Optional[AnnouncementSource]:
        result = await self.session.execute(select(AnnouncementSource).where(AnnouncementSource.id == source_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[AnnouncementSource]:
        result = await self.session.execute(select(AnnouncementSource).where(AnnouncementSource.name == name))
        return result.scalar_one_or_none()

    async def get_all_active(self) -> List[AnnouncementSource]:
        result = await self.session.execute(
            select(AnnouncementSource).where(AnnouncementSource.is_active == True)
        )
        return list(result.scalars().all())

    async def create(self, source: AnnouncementSource) -> AnnouncementSource:
        self.session.add(source)
        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def update(self, source: AnnouncementSource) -> AnnouncementSource:
        await self.session.flush()
        await self.session.refresh(source)
        return source


class AnnouncementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Announcement):
        return select(parameter)

    async def get_by_id(self, announcement_id: int) -> Optional[Announcement]:
        result = await self.session.execute(select(Announcement).where(Announcement.id == announcement_id))
        return result.scalar_one_or_none()

    async def get_recent(self, limit: int = 20, offset: int = 0) -> List[Announcement]:
        result = await self.session.execute(
            select(Announcement)
            .order_by(Announcement.published_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_category(self, category: str, limit: int = 20) -> List[Announcement]:
        result = await self.session.execute(
            select(Announcement)
            .where(Announcement.category == category)
            .order_by(Announcement.published_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_source(self, source_id: int, limit: int = 20) -> List[Announcement]:
        result = await self.session.execute(
            select(Announcement)
            .where(Announcement.source_id == source_id)
            .order_by(Announcement.published_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest_per_source(self) -> List[Announcement]:
        subquery = (
            select(
                Announcement.source_id,
                func.max(Announcement.published_at).label("max_published"),
            )
            .group_by(Announcement.source_id)
            .subquery()
        )
        result = await self.session.execute(
            select(Announcement)
            .join(subquery, (Announcement.source_id == subquery.c.source_id) & (Announcement.published_at == subquery.c.max_published))
            .order_by(Announcement.published_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, announcement: Announcement) -> Announcement:
        self.session.add(announcement)
        await self.session.flush()
        await self.session.refresh(announcement)
        return announcement

    async def bulk_upsert(self, announcements: List[Announcement]) -> List[Announcement]:
        saved_announcements = []
        for announcement in announcements:
            existing_ann = None
            if announcement.source_reference:
                existing = await self.session.execute(
                    select(Announcement).where(
                        Announcement.source_id == announcement.source_id,
                        Announcement.source_reference == announcement.source_reference,
                    )
                )
                existing_ann = existing.scalar_one_or_none()
            else:
                # Deterministic fallback when source_reference is missing
                query = select(Announcement).where(
                    Announcement.source_id == announcement.source_id,
                    Announcement.title == announcement.title,
                )
                if announcement.published_at:
                    query = query.where(Announcement.published_at == announcement.published_at)
                else:
                    query = query.where(Announcement.published_at.is_(None))
                
                existing = await self.session.execute(query)
                existing_ann = existing.scalars().first()

            if existing_ann:
                existing_ann.title = announcement.title
                existing_ann.content = announcement.content
                existing_ann.category = announcement.category
                existing_ann.published_at = announcement.published_at
                existing_ann.source_sync_run_id = announcement.source_sync_run_id
                saved_announcements.append(existing_ann)
                continue
            
            self.session.add(announcement)
            saved_announcements.append(announcement)
        await self.session.flush()
        for ann in saved_announcements:
            await self.session.refresh(ann)
        return saved_announcements

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(Announcement.id)))
        return result.scalar_one()