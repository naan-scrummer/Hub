import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.db.base import Base
from app.modules.announcements.models import Announcement, AnnouncementSource
from app.modules.announcements.repository import AnnouncementRepository

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session

@pytest.fixture
def mock_source():
    return AnnouncementSource(id=1, name="Mock Source", source_type="api", is_active=True)

@pytest.mark.asyncio
async def test_bulk_upsert_deduplicates_by_source_reference(db_session: AsyncSession, mock_source):
    repo = AnnouncementRepository(db_session)
    db_session.add(mock_source)
    await db_session.flush()

    ann1 = Announcement(source_id=1, source_reference="ref1", title="Title 1", content="Content 1", category="event")
    ann2 = Announcement(source_id=1, source_reference="ref1", title="Title 1 Updated", content="Content 1 Updated", category="event")

    # Insert first
    await repo.bulk_upsert([ann1])
    count = await repo.count_total()
    assert count == 1

    # Upsert with same ref, should update, not create new
    await repo.bulk_upsert([ann2])
    count = await repo.count_total()
    assert count == 1

    saved = await repo.get_by_source(1)
    assert saved[0].title == "Title 1 Updated"

@pytest.mark.asyncio
async def test_bulk_upsert_deduplicates_without_reference(db_session: AsyncSession, mock_source):
    repo = AnnouncementRepository(db_session)
    db_session.add(mock_source)
    await db_session.flush()

    # Same title, same source_id, missing reference
    ann1 = Announcement(source_id=1, title="No Ref Notice", content="Content 1", category="event", published_at=None)
    ann2 = Announcement(source_id=1, title="No Ref Notice", content="Content 1 Updated", category="event", published_at=None)

    await repo.bulk_upsert([ann1])
    assert await repo.count_total() == 1

    await repo.bulk_upsert([ann2])
    assert await repo.count_total() == 1

    saved = await repo.get_by_source(1)
    assert saved[0].content == "Content 1 Updated"

@pytest.mark.asyncio
async def test_bulk_upsert_adds_multiple(db_session: AsyncSession, mock_source):
    repo = AnnouncementRepository(db_session)
    db_session.add(mock_source)
    await db_session.flush()

    ann1 = Announcement(source_id=1, source_reference="ref1", title="Title 1", content="Content 1", category="event")
    ann2 = Announcement(source_id=1, source_reference="ref2", title="Title 2", content="Content 2", category="event")

    await repo.bulk_upsert([ann1, ann2])
    assert await repo.count_total() == 2
