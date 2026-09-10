from typing import List, Optional
from datetime import datetime

from app.modules.announcements.models import AnnouncementSource, Announcement
from app.modules.announcements.repository import AnnouncementSourceRepository, AnnouncementRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class AnnouncementService:
    def __init__(
        self,
        source_repo: AnnouncementSourceRepository,
        announcement_repo: AnnouncementRepository,
    ):
        self.source_repo = source_repo
        self.announcement_repo = announcement_repo

    async def get_recent_announcements(self, limit: int = 20) -> List[Announcement]:
        return await self.announcement_repo.get_recent(limit=limit)

    async def get_announcements_by_category(self, category: str, limit: int = 20) -> List[Announcement]:
        return await self.announcement_repo.get_by_category(category, limit=limit)

    async def get_latest_per_source(self) -> List[Announcement]:
        return await self.announcement_repo.get_latest_per_source()

    async def get_active_sources(self) -> List[AnnouncementSource]:
        return await self.source_repo.get_all_active()

    async def upsert_announcements(self, announcements: List[Announcement]) -> List[Announcement]:
        return await self.announcement_repo.bulk_upsert(announcements)

    def create_announcement(
        self,
        source_id: int,
        source_reference: Optional[str],
        title: str,
        content: str,
        category: str,
        published_at: datetime,
        sync_run_id: Optional[int] = None,
    ) -> Announcement:
        return Announcement(
            source_id=source_id,
            source_reference=source_reference,
            title=title,
            content=content,
            category=category,
            published_at=published_at,
            source_sync_run_id=sync_run_id,
        )

    def create_source(self, name: str, source_type: str, base_url: Optional[str] = None) -> AnnouncementSource:
        return AnnouncementSource(
            name=name,
            source_type=source_type,
            base_url=base_url,
        )