from typing import List, Optional

from app.modules.study_materials.models import StudyMaterial
from app.modules.study_materials.repository import StudyMaterialRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


class StudyMaterialService:
    def __init__(self, material_repo: StudyMaterialRepository):
        self.material_repo = material_repo

    async def get_by_subject(self, subject_id: int) -> List[StudyMaterial]:
        return await self.material_repo.get_by_subject(subject_id)

    async def search(
        self,
        query: str,
        subject_id: Optional[int] = None,
        material_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[StudyMaterial]:
        return await self.material_repo.search(query, subject_id, material_type, limit)

    async def get_all(self, limit: int = 50, offset: int = 0) -> List[StudyMaterial]:
        return await self.material_repo.get_all(limit, offset)

    async def get_student_uploads(self, student_id: int) -> List[StudyMaterial]:
        return await self.material_repo.get_by_student_uploads(student_id)

    async def get_by_id(self, material_id: int) -> Optional[StudyMaterial]:
        return await self.material_repo.get_by_id(material_id)

    async def create(self, material: StudyMaterial) -> StudyMaterial:
        return await self.material_repo.create(material)

    async def update(self, material: StudyMaterial) -> StudyMaterial:
        return await self.material_repo.update(material)

    def create_material(
        self,
        subject_id: int,
        title: str,
        material_type: str,
        description: Optional[str] = None,
        file_path: Optional[str] = None,
        external_url: Optional[str] = None,
        uploaded_by_student_id: Optional[int] = None,
        is_approved: bool = True,
    ) -> StudyMaterial:
        return StudyMaterial(
            subject_id=subject_id,
            title=title,
            description=description,
            material_type=material_type,
            file_path=file_path,
            external_url=external_url,
            uploaded_by_student_id=uploaded_by_student_id,
            is_approved=is_approved,
        )