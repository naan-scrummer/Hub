from typing import List, Optional

from app.modules.academics.models import AcademicRecord
from app.modules.academics.repository import AcademicRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class AcademicService:
    def __init__(self, academic_repo: AcademicRepository):
        self.academic_repo = academic_repo

    async def get_student_academics(self, student_id: int) -> List[AcademicRecord]:
        return await self.academic_repo.get_by_student(student_id)

    async def get_student_semester_academics(self, student_id: int, semester: int) -> List[AcademicRecord]:
        return await self.academic_repo.get_by_student_and_semester(student_id, semester)

    async def get_subject_academic(self, student_id: int, subject_id: int, semester: int) -> Optional[AcademicRecord]:
        return await self.academic_repo.get_by_student_and_subject(student_id, subject_id, semester)

    async def upsert_academic_records(self, records: List[AcademicRecord]) -> List[AcademicRecord]:
        return await self.academic_repo.bulk_upsert(records)