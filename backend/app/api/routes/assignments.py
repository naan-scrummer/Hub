from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile
from app.modules.assignments.service import AssignmentService
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.repository import ReminderRepository
from app.modules.attendance.repository import SubjectRepository
from app.modules.study_materials.service import StudyMaterialService
from app.modules.study_materials.repository import StudyMaterialRepository
from app.schemas.study_materials import StudyMaterialListResponse, StudyMaterialResponse
from app.schemas.assignments import (
    AssignmentCreateRequest,
    AssignmentUpdateRequest,
    AssignmentResponse,
    AssignmentListResponse,
)
from app.modules.authentication.models import StudentProfile
from app.logging.config import get_logger


router = APIRouter(prefix="/assignments", tags=["assignments"])
logger = get_logger(__name__)


def get_assignment_service(db: AsyncSession = Depends(get_db)) -> AssignmentService:
    assignment_repo = AssignmentRepository(db)
    reminder_repo = ReminderRepository(db)
    return AssignmentService(assignment_repo, reminder_repo)


@router.get("", response_model=AssignmentListResponse)
async def get_assignments(
    profile: StudentProfile = Depends(get_current_student_profile),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    upcoming = await assignment_service.get_upcoming(profile.id)
    overdue = await assignment_service.get_overdue(profile.id)
    completed = await assignment_service.get_completed(profile.id)

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)

    async def to_response(assignments: List) -> List[AssignmentResponse]:
        responses = []
        for a in assignments:
            subject = await subject_repo.get_by_id(a.subject_id)
            responses.append(AssignmentResponse(
                id=a.id,
                student_id=a.student_id,
                subject_id=a.subject_id,
                subject_code=subject.code if subject else None,
                subject_name=subject.name if subject else None,
                title=a.title,
                description=a.description,
                due_date=a.due_date,
                status=assignment_service.classify_status(a),
                completed_at=a.completed_at,
                created_at=a.created_at,
                updated_at=a.updated_at,
            ))
        return responses

    return AssignmentListResponse(
        upcoming=await to_response(upcoming),
        overdue=await to_response(overdue),
        completed=await to_response(completed),
    )


@router.post("", response_model=AssignmentResponse)
async def create_assignment(
    request: AssignmentCreateRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    assignment = await assignment_service.create(
        student_id=profile.id,
        subject_id=request.subject_id,
        title=request.title,
        description=request.description,
        due_date=request.due_date,
    )

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(assignment.subject_id)
    return AssignmentResponse(
        id=assignment.id,
        student_id=assignment.student_id,
        subject_id=assignment.subject_id,
        subject_code=subject.code if subject else None,
        subject_name=subject.name if subject else None,
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date,
        status=assignment_service.classify_status(assignment),
        completed_at=assignment.completed_at,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    request: AssignmentUpdateRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    assignment = await assignment_service.get_by_id(assignment_id)
    if not assignment or assignment.student_id != profile.id:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if request.title is not None:
        assignment.title = request.title
    if request.description is not None:
        assignment.description = request.description
    if request.due_date is not None:
        assignment.due_date = request.due_date

    assignment = await assignment_service.update(assignment)

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(assignment.subject_id)
    return AssignmentResponse(
        id=assignment.id,
        student_id=assignment.student_id,
        subject_id=assignment.subject_id,
        subject_code=subject.code if subject else None,
        subject_name=subject.name if subject else None,
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date,
        status=assignment_service.classify_status(assignment),
        completed_at=assignment.completed_at,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


@router.post("/{assignment_id}/complete", response_model=AssignmentResponse)
async def complete_assignment(
    assignment_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    assignment = await assignment_service.mark_completed(assignment_id, profile.id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(assignment.subject_id)
    return AssignmentResponse(
        id=assignment.id,
        student_id=assignment.student_id,
        subject_id=assignment.subject_id,
        subject_code=subject.code if subject else None,
        subject_name=subject.name if subject else None,
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date,
        status=assignment_service.classify_status(assignment),
        completed_at=assignment.completed_at,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    success = await assignment_service.delete(assignment_id, profile.id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"message": "Assignment deleted"}


@router.get("/subject/{subject_id}", response_model=List[AssignmentResponse])
async def get_assignments_by_subject(
    subject_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    assignments = await assignment_service.get_by_subject(profile.id, subject_id)

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(subject_id)

    responses = []
    for a in assignments:
        responses.append(AssignmentResponse(
            id=a.id,
            student_id=a.student_id,
            subject_id=a.subject_id,
            subject_code=subject.code if subject else None,
            subject_name=subject.name if subject else None,
            title=a.title,
            description=a.description,
            due_date=a.due_date,
            status=assignment_service.classify_status(a),
            completed_at=a.completed_at,
            created_at=a.created_at,
            updated_at=a.updated_at,
        ))
    return responses


@router.get("/{assignment_id}/materials", response_model=StudyMaterialListResponse)
async def get_assignment_materials(
    assignment_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    db: AsyncSession = Depends(get_db),
):
    assignment = await assignment_service.get_by_id(assignment_id)
    if not assignment or assignment.student_id != profile.id:
        raise HTTPException(status_code=404, detail="Assignment not found")

    material_repo = StudyMaterialRepository(db)
    material_service = StudyMaterialService(material_repo)
    materials = await material_service.get_by_subject(assignment.subject_id)

    subject_repo = SubjectRepository(db)
    subject = await subject_repo.get_by_id(assignment.subject_id)

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