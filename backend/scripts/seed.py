import asyncio
from app.db.base import async_session_maker
from app.seed import seed_data
from scripts.seed_notifications import seed_notifications
from app.modules.authentication.models import User, StudentProfile
from sqlalchemy import select


async def run_seed():
    await seed_data()


if __name__ == "__main__":
    asyncio.run(run_seed())
