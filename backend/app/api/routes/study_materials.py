from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
import os
import uuid
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.study_materials.service import StudyMaterialService
from app.modules.study_materials.repository import StudyMaterialRepository
from app.modules.attendance.repository import SubjectRepository
from app.schemas.study_materials import (
    StudyMaterialResponse,
    StudyMaterialListResponse,
    StudyMaterialCreateRequest,
    StudyMaterialSearchRequest,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/materials", tags=["study-materials"])
logger = get_logger(__name__)


def get_material_service(db: AsyncSession = Depends(get_db)) -> StudyMaterialService:
    material_repo = StudyMaterialRepository(db)
    return StudyMaterialService(material_repo)


@router.get("", response_model=StudyMaterialListResponse)
async def get_materials(
    query: Optional[str] = None,
    subject_id: Optional[int] = None,
    material_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    profile: StudentProfile = Depends(get_current_student_profile),
    material_service: StudyMaterialService = Depends(get_material_service),
):
    materials = await material_service.search(query or "", subject_id, material_type, limit)

    subject_repo = SubjectRepository(material_service.material_repo.session)
    material_responses = []
    for material in materials:
        subject = await subject_repo.get_by_id(material.subject_id)
        material_responses.append(StudyMaterialResponse(
            id=material.id,
            subject_id=material.subject_id,
            subject_code=subject.code if subject else None,
            subject_name=subject.name if subject else None,
            title=material.title,
            description=material.description,
            material_type=material.material_type,
            file_path=material.file_path,
            external_url=material.external_url,
            uploaded_by_student_id=material.uploaded_by_student_id,
            is_approved=material.is_approved,
            created_at=material.created_at,
        ))

    return StudyMaterialListResponse(materials=material_responses, total=len(material_responses))


@router.get("/{material_id}", response_model=StudyMaterialResponse)
async def get_material(
    material_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    material_service: StudyMaterialService = Depends(get_material_service),
):
    material = await material_service.get_by_id(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Study material not found")

    subject_repo = SubjectRepository(material_service.material_repo.session)
    subject = await subject_repo.get_by_id(material.subject_id)
    return StudyMaterialResponse(
        id=material.id,
        subject_id=material.subject_id,
        subject_code=subject.code if subject else None,
        subject_name=subject.name if subject else None,
        title=material.title,
        description=material.description,
        material_type=material.material_type,
        file_path=material.file_path,
        external_url=material.external_url,
        uploaded_by_student_id=material.uploaded_by_student_id,
        is_approved=material.is_approved,
        created_at=material.created_at,
    )


@router.get("/subject/{subject_id}", response_model=StudyMaterialListResponse)
async def get_materials_by_subject(
    subject_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    material_service: StudyMaterialService = Depends(get_material_service),
):
    materials = await material_service.get_by_subject(subject_id)

    subject_repo = SubjectRepository(material_service.material_repo.session)
    subject = await subject_repo.get_by_id(subject_id)
    material_responses = []
    for material in materials:
        material_responses.append(StudyMaterialResponse(
            id=material.id,
            subject_id=material.subject_id,
            subject_code=subject.code if subject else None,
            subject_name=subject.name if subject else None,
            title=material.title,
            description=material.description,
            material_type=material.material_type,
            file_path=material.file_path,
            external_url=material.external_url,
            uploaded_by_student_id=material.uploaded_by_student_id,
            is_approved=material.is_approved,
            created_at=material.created_at,
        ))

    return StudyMaterialListResponse(materials=material_responses, total=len(material_responses))


UPLOAD_DIR = "uploads/materials"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("", response_model=StudyMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    subject_id: int = Form(...),
    title: str = Form(...),
    material_type: str = Form(...),
    description: Optional[str] = Form(None),
    external_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    profile: StudentProfile = Depends(get_current_student_profile),
    material_service: StudyMaterialService = Depends(get_material_service),
):
    if not file and not external_url:
        raise HTTPException(status_code=400, detail="Either file or external_url must be provided")

    file_path = None
    if file:
        allowed_extensions = {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".jpg", ".png", ".zip"}
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        safe_filename = f"{uuid.uuid4()}{ext}"
        local_path = os.path.join(UPLOAD_DIR, safe_filename).replace("\\", "/")
        try:
            async with aiofiles.open(local_path, 'wb') as out_file:
                content = await file.read()
                if len(content) > 10 * 1024 * 1024:
                    raise HTTPException(status_code=400, detail="File too large (max 10MB)")
                await out_file.write(content)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

        file_path = f"/static/materials/{safe_filename}"

    material = material_service.create_material(
        subject_id=subject_id,
        title=title,
        material_type=material_type,
        description=description,
        file_path=file_path,
        external_url=external_url,
        uploaded_by_student_id=profile.id,
        is_approved=True,
    )
    material = await material_service.create(material)

    subject_repo = SubjectRepository(material_service.material_repo.session)
    subject = await subject_repo.get_by_id(material.subject_id)
    return StudyMaterialResponse(
        id=material.id,
        subject_id=material.subject_id,
        subject_code=subject.code if subject else None,
        subject_name=subject.name if subject else None,
        title=material.title,
        description=material.description,
        material_type=material.material_type,
        file_path=material.file_path,
        external_url=material.external_url,
        uploaded_by_student_id=material.uploaded_by_student_id,
        is_approved=material.is_approved,
        created_at=material.created_at,
    )


@router.get("/my-uploads", response_model=StudyMaterialListResponse)
async def get_my_uploads(
    profile: StudentProfile = Depends(get_current_student_profile),
    material_service: StudyMaterialService = Depends(get_material_service),
):
    materials = await material_service.get_student_uploads(profile.id)

    subject_repo = SubjectRepository(material_service.material_repo.session)
    material_responses = []
    for material in materials:
        subject = await subject_repo.get_by_id(material.subject_id)
        material_responses.append(StudyMaterialResponse(
            id=material.id,
            subject_id=material.subject_id,
            subject_code=subject.code if subject else None,
            subject_name=subject.name if subject else None,
            title=material.title,
            description=material.description,
            material_type=material.material_type,
            file_path=material.file_path,
            external_url=material.external_url,
            uploaded_by_student_id=material.uploaded_by_student_id,
            is_approved=material.is_approved,
            created_at=material.created_at,
        ))

    return StudyMaterialListResponse(materials=material_responses, total=len(material_responses))