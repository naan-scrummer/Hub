from datetime import datetime, timezone

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    future=True,
)


if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine.sync_engine, "connect")
    def register_sqlite_now_function(dbapi_connection, _connection_record):
        dbapi_connection.run_async(
            lambda connection: connection.create_function(
                "now",
                0,
                lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


# Register every model before SQLAlchemy configures relationships.
from app.integrations.college_portal.models import SyncRun  # noqa: E402,F401
from app.modules.academics.models import AcademicRecord  # noqa: E402,F401
from app.modules.announcements.models import Announcement, AnnouncementSource  # noqa: E402,F401
from app.modules.assignments.models import Assignment  # noqa: E402,F401
from app.modules.attendance.models import AttendanceRecord, Subject  # noqa: E402,F401
from app.modules.authentication.models import StudentProfile, User  # noqa: E402,F401
from app.modules.dashboard.models import DashboardWidget  # noqa: E402,F401
from app.modules.examinations.models import Examination  # noqa: E402,F401
from app.modules.notifications.models import Notification  # noqa: E402,F401
from app.modules.placements.models import Company, PlacementContribution, PlacementOpportunity  # noqa: E402,F401
from app.modules.reminders.models import Reminder  # noqa: E402,F401
from app.modules.study_materials.models import StudyMaterial  # noqa: E402,F401


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()