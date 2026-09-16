from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class AnnouncementSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    base_url: Optional[str]
    is_active: bool
    last_synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class AnnouncementResponse(BaseModel):
    id: int
    source_id: int
    source_name: Optional[str] = None
    source_reference: Optional[str]
    title: str
    content: str
    category: str
    published_at: Optional[datetime]
    is_unavailable: bool = False

    class Config:
        from_attributes = True


class AnnouncementListResponse(BaseModel):
    announcements: List[AnnouncementResponse]
    total: int
    is_unavailable: bool = False


class AnnouncementSyncRequest(BaseModel):
    source_id: int