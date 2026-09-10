from typing import List
from datetime import datetime

from app.integrations.college_portal.models import SyncRun, SyncSourceType, SyncStatus
from app.integrations.college_portal.repository import SyncRunRepository
from app.integrations.college_portal.mock_adapters import (
    MockCollegePortalClient,
    MockAttendancePortalAdapter,
    MockAcademicPortalAdapter,
    MockExaminationPortalAdapter,
    MockAnnouncementPortalAdapter,
    MockPlacementPortalAdapter,
)
from app.modules.attendance.service import AttendanceService
from app.modules.academics.service import AcademicService
from app.modules.examinations.service import ExaminationService
from app.modules.announcements.service import AnnouncementService
from app.modules.placements.service import PlacementService
from app.modules.announcements.models import AnnouncementSource
from app.logging.config import get_logger


logger = get_logger(__name__)


class SynchronizationService:
    def __init__(
        self,
        sync_run_repo: SyncRunRepository,
        attendance_service: AttendanceService,
        academic_service: AcademicService,
        examination_service: ExaminationService,
        announcement_service: AnnouncementService,
        placement_service: PlacementService,
    ):
        self.sync_run_repo = sync_run_repo
        self.attendance_service = attendance_service
        self.academic_service = academic_service
        self.examination_service = examination_service
        self.announcement_service = announcement_service
        self.placement_service = placement_service

        # Initialize mock adapters
        self.client = MockCollegePortalClient()
        self.attendance_adapter = MockAttendancePortalAdapter(self.client)
        self.academic_adapter = MockAcademicPortalAdapter(self.client)
        self.examination_adapter = MockExaminationPortalAdapter(self.client)
        self.announcement_adapter = MockAnnouncementPortalAdapter(self.client)
        self.placement_adapter = MockPlacementPortalAdapter(self.client)

    async def sync_attendance(self, student_id: int) -> SyncRun:
        sync_run = SyncRun(
            source_type=SyncSourceType.ATTENDANCE,
            source_name="mock_college_portal",
            status=SyncStatus.RUNNING,
        )
        sync_run = await self.sync_run_repo.create(sync_run)

        try:
            records = await self.attendance_adapter.sync(student_id, sync_run.id)
            if records:
                await self.attendance_service.upsert_attendance_records(records)

            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.SUCCESS,
                records_processed=len(records),
                records_created=len(records),
                records_updated=0,
                records_failed=0,
            )
        except Exception as e:
            logger.error("attendance_sync_failed", student_id=student_id, error=str(e))
            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.FAILED,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                error_message=str(e),
            )
            raise

        return await self.sync_run_repo.get_by_id(sync_run.id)

    async def sync_academics(self, student_id: int) -> SyncRun:
        sync_run = SyncRun(
            source_type=SyncSourceType.ACADEMICS,
            source_name="mock_college_portal",
            status=SyncStatus.RUNNING,
        )
        sync_run = await self.sync_run_repo.create(sync_run)

        try:
            records = await self.academic_adapter.sync(student_id, sync_run.id)
            if records:
                await self.academic_service.upsert_academic_records(records)

            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.SUCCESS,
                records_processed=len(records),
                records_created=len(records),
                records_updated=0,
                records_failed=0,
            )
        except Exception as e:
            logger.error("academics_sync_failed", student_id=student_id, error=str(e))
            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.FAILED,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                error_message=str(e),
            )
            raise

        return await self.sync_run_repo.get_by_id(sync_run.id)

    async def sync_examinations(self) -> SyncRun:
        sync_run = SyncRun(
            source_type=SyncSourceType.EXAMINATIONS,
            source_name="mock_college_portal",
            status=SyncStatus.RUNNING,
        )
        sync_run = await self.sync_run_repo.create(sync_run)

        try:
            exams = await self.examination_adapter.sync(sync_run.id)
            if exams:
                await self.examination_service.upsert_examinations(exams)

            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.SUCCESS,
                records_processed=len(exams),
                records_created=len(exams),
                records_updated=0,
                records_failed=0,
            )
        except Exception as e:
            logger.error("examinations_sync_failed", error=str(e))
            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.FAILED,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                error_message=str(e),
            )
            raise

        return await self.sync_run_repo.get_by_id(sync_run.id)

    async def sync_announcements(self, source: AnnouncementSource) -> SyncRun:
        sync_run = SyncRun(
            source_type=SyncSourceType.ANNOUNCEMENTS,
            source_name=source.name,
            status=SyncStatus.RUNNING,
        )
        sync_run = await self.sync_run_repo.create(sync_run)

        try:
            announcements = await self.announcement_adapter.sync(source, sync_run.id)
            if announcements:
                await self.announcement_service.upsert_announcements(announcements)

            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.SUCCESS,
                records_processed=len(announcements),
                records_created=len(announcements),
                records_updated=0,
                records_failed=0,
            )
        except Exception as e:
            logger.error("announcements_sync_failed", source=source.name, error=str(e))
            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.FAILED,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                error_message=str(e),
            )
            raise

        return await self.sync_run_repo.get_by_id(sync_run.id)

    async def sync_placements(self) -> SyncRun:
        sync_run = SyncRun(
            source_type=SyncSourceType.PLACEMENTS,
            source_name="mock_college_portal",
            status=SyncStatus.RUNNING,
        )
        sync_run = await self.sync_run_repo.create(sync_run)

        try:
            opportunities = await self.placement_adapter.sync(sync_run.id)
            if opportunities:
                await self.placement_service.upsert_opportunities(opportunities)

            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.SUCCESS,
                records_processed=len(opportunities),
                records_created=len(opportunities),
                records_updated=0,
                records_failed=0,
            )
        except Exception as e:
            logger.error("placements_sync_failed", error=str(e))
            await self.sync_run_repo.mark_completed(
                sync_run.id,
                SyncStatus.FAILED,
                records_processed=0,
                records_created=0,
                records_updated=0,
                records_failed=0,
                error_message=str(e),
            )
            raise

        return await self.sync_run_repo.get_by_id(sync_run.id)

    async def sync_all_for_student(self, student_id: int) -> List[SyncRun]:
        runs = []
        runs.append(await self.sync_attendance(student_id))
        runs.append(await self.sync_academics(student_id))
        runs.append(await self.sync_examinations())
        runs.append(await self.sync_placements())

        sources = await self.announcement_service.get_active_sources()
        for source in sources:
            runs.append(await self.sync_announcements(source))

        return runs