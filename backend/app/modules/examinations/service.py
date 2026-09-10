from typing import List, Optional
from datetime import datetime

from app.modules.examinations.models import Examination
from app.modules.examinations.repository import ExaminationRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class ExaminationService:
    def __init__(self, exam_repo: ExaminationRepository):
        self.exam_repo = exam_repo

    async def get_upcoming_exams(self, student_id: int, subject_ids: List[int]) -> List[Examination]:
        return await self.exam_repo.get_upcoming_for_student(student_id, subject_ids)

    async def get_all_exams_for_subjects(self, subject_ids: List[int]) -> List[Examination]:
        return await self.exam_repo.get_all_for_subjects(subject_ids)

    async def upsert_examinations(self, exams: List[Examination]) -> List[Examination]:
        return await self.exam_repo.bulk_upsert(exams)

    def create_examination(
        self,
        subject_id: int,
        title: str,
        exam_type: str,
        exam_date: datetime,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        venue: Optional[str] = None,
        description: Optional[str] = None,
        sync_run_id: Optional[int] = None,
    ) -> Examination:
        return Examination(
            subject_id=subject_id,
            title=title,
            exam_type=exam_type,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            venue=venue,
            description=description,
            last_synced_at=datetime.utcnow(),
            source_sync_run_id=sync_run_id,
        )