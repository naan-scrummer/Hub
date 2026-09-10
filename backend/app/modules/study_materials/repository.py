from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.study_materials.models import StudyMaterial


class StudyMaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, material_id: int) -> Optional[StudyMaterial]:
        result = await self.session.execute(select(StudyMaterial).where(StudyMaterial.id == material_id))
        return result.scalar_one_or_none()

    async def get_by_subject(self, subject_id: int) -> List[StudyMaterial]:
        result = await self.session.execute(
            select(StudyMaterial).where(StudyMaterial.subject_id == subject_id).order_by(StudyMaterial.title)
        )
        return list(result.scalars().all())

    async def search(self, query: str, subject_id: Optional[int] = None, material_type: Optional[str] = None, limit: int = 50) -> List[StudyMaterial]:
        stmt = select(StudyMaterial).where(StudyMaterial.is_approved == True)
        if query:
            stmt = stmt.where(
                or_(
                    StudyMaterial.title.ilike(f"%{query}%"),
                    StudyMaterial.description.ilike(f"%{query}%"),
                )
            )
        if subject_id:
            stmt = stmt.where(StudyMaterial.subject_id == subject_id)
        if material_type:
            stmt = stmt.where(StudyMaterial.material_type == material_type)
        stmt = stmt.order_by(StudyMaterial.title).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self, limit: int = 50, offset: int = 0) -> List[StudyMaterial]:
        result = await self.session.execute(
            select(StudyMaterial).where(StudyMaterial.is_approved == True).order_by(StudyMaterial.title).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_student_uploads(self, student_id: int) -> List[StudyMaterial]:
        result = await self.session.execute(
            select(StudyMaterial).where(StudyMaterial.uploaded_by_student_id == student_id).order_by(StudyMaterial.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, material: StudyMaterial) -> StudyMaterial:
        self.session.add(material)
        await self.session.flush()
        await self.session.refresh(material)
        return material

    async def update(self, material: StudyMaterial) -> StudyMaterial:
        await self.session.flush()
        await self.session.refresh(material)
        return material