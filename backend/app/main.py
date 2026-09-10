from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.base import init_db, close_db
from app.logging.config import setup_logging, get_logger
from app.jobs.scheduler import job_scheduler
from app.api.routes import (
    auth,
    dashboard,
    attendance,
    academics,
    examinations,
    announcements,
    placements,
    study_materials,
    assignments,
    reminders,
    notifications,
)


settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("application_starting", env=settings.APP_ENV)

    await init_db()
    logger.info("database_initialized")

    job_scheduler.start()

    yield

    job_scheduler.shutdown()
    await close_db()
    logger.info("application_shutdown")


app = FastAPI(
    title="AIO Student's Hub",
    description="Centralized student-facing hub for academic information and productivity",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aio-students-hub"}


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")
app.include_router(academics.router, prefix="/api/v1")
app.include_router(examinations.router, prefix="/api/v1")
app.include_router(announcements.router, prefix="/api/v1")
app.include_router(placements.router, prefix="/api/v1")
app.include_router(study_materials.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")
app.include_router(reminders.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)