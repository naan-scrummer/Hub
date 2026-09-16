import pytest
from app.modules.announcements.models import AnnouncementSource
from app.integrations.college_portal.mock_adapters import MockAnnouncementPortalAdapter, MockCollegePortalClient
from app.modules.announcements.repository import AnnouncementRepository
from app.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session

@pytest.mark.asyncio
async def test_announcements_sync_missing_metadata(db_session):
    repo = AnnouncementRepository(db_session)
    source = AnnouncementSource(name="Test Source", source_type="api", is_active=True)
    db_session.add(source)
    await db_session.flush()

    client = MockCollegePortalClient()
    adapter = MockAnnouncementPortalAdapter(client)
    
    announcements = await adapter.sync(source, sync_run_id=1)
    
    # Check that we have a notice without reference and timestamp
    missing_meta = next((a for a in announcements if a.source_reference is None), None)
    assert missing_meta is not None
    assert missing_meta.published_at is None
    assert missing_meta.title == "Unreferenced Notice without Timestamp"

    await repo.bulk_upsert(announcements)
    
    count = await repo.count_total()
    assert count == 4 # 3 standard + 1 missing metadata from mock_adapters
