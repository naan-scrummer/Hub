from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import get_db
from app.api.dependencies.auth import get_current_student_profile, get_current_user
from app.modules.authentication.models import User, UserRole
from app.modules.assignments.service import AssignmentService
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.service import ReminderService
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.service import NotificationService
from app.modules.notifications.repository import NotificationRepository
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
    notification_repo = NotificationRepository(db)
    reminder_service = ReminderService(reminder_repo, notification_repo)
    return AssignmentService(assignment_repo, reminder_service)

def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    repo = NotificationRepository(db)
    return NotificationService(repo)


@router.get("", response_model=AssignmentListResponse)
async def get_assignments(
    user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
):
    from app.modules.authentication.repository import StudentProfileRepository
    
    upcoming = []
    overdue = []
    completed = []

    if user.role == UserRole.TEACHER:
        from sqlalchemy import select
        from app.modules.assignments.models import Assignment, AssignmentStatus
        import datetime
        
        result = await assignment_service.assignment_repo.session.execute(
            select(Assignment).where(Assignment.teacher_id == user.id).order_by(Assignment.due_date)
        )
        all_assignments = list(result.scalars().all())
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        
        for a in all_assignments:
            if a.status == AssignmentStatus.COMPLETED:
                completed.append(a)
            # Ensure safe comparison if due_date is offset-naive or aware
            elif a.due_date.replace(tzinfo=datetime.timezone.utc) < now:
                overdue.append(a)
            else:
                upcoming.append(a)
    else:
        profile_repo = StudentProfileRepository(assignment_service.assignment_repo.session)
        profile = await profile_repo.get_by_user_id(user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")

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
                student_id=a.student_id or 0,
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
    user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    db: AsyncSession = Depends(get_db),
    notification_service: NotificationService = Depends(get_notification_service),
):
    student_id = None
    teacher_id = None
    
    if user.role == UserRole.TEACHER:
        teacher_id = user.id
    else:
        from app.modules.authentication.repository import StudentProfileRepository
        profile_repo = StudentProfileRepository(db)
        profile = await profile_repo.get_by_user_id(user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        student_id = profile.id

    # Add teacher_id to create if we update AssignmentService or just create manually here
    # Actually, AssignmentService.create only takes student_id. Let's just create it directly here
    # or update AssignmentService.
    # It's safer to just set it on the assignment object
    assignment = await assignment_service.create(
        student_id=student_id or 1, # Placeholder, will update below
        subject_id=request.subject_id,
        title=request.title,
        description=request.description,
        due_date=request.due_date,
    )
    
    # Fix the IDs
    assignment.student_id = student_id
    assignment.teacher_id = teacher_id
    await assignment_service.assignment_repo.session.commit()

    if user.role == UserRole.TEACHER:
        # Notify all students
        students = await db.execute(select(StudentProfile))
        for student in students.scalars().all():
            await notification_service.create(
                student_id=student.id,
                source="assignment_deadline",
                source_id=assignment.id,
                title=f"New Assignment: {assignment.title}",
                message=f"A new assignment '{assignment.title}' has been posted."
            )

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(assignment.subject_id)
    return AssignmentResponse(
        id=assignment.id,
        student_id=assignment.student_id or 0,
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
    user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    db: AsyncSession = Depends(get_db),
):
    assignment = await assignment_service.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    if user.role != UserRole.TEACHER:
        from app.modules.authentication.repository import StudentProfileRepository
        profile_repo = StudentProfileRepository(db)
        profile = await profile_repo.get_by_user_id(user.id)
        if assignment.student_id != profile.id:
            raise HTTPException(status_code=404, detail="Assignment not found")
            
    if request.subject_id is not None:
        assignment.subject_id = request.subject_id
    if request.title is not None:
        assignment.title = request.title
    if request.description is not None:
        assignment.description = request.description
    old_due_date = assignment.due_date
    if request.due_date is not None:
        assignment.due_date = request.due_date

    assignment = await assignment_service.update(assignment, old_due_date=old_due_date)

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(assignment.subject_id)
    return AssignmentResponse(
        id=assignment.id,
        student_id=assignment.student_id or 0,
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
    user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    db: AsyncSession = Depends(get_db),
):
    if user.role == UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Teachers cannot complete assignments")
        
    from app.modules.authentication.repository import StudentProfileRepository
    profile_repo = StudentProfileRepository(db)
    profile = await profile_repo.get_by_user_id(user.id)

    assignment = await assignment_service.mark_completed(assignment_id, profile.id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(assignment.subject_id)
    return AssignmentResponse(
        id=assignment.id,
        student_id=assignment.student_id or 0,
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
    user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    db: AsyncSession = Depends(get_db),
):
    assignment = await assignment_service.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    if user.role != UserRole.TEACHER:
        from app.modules.authentication.repository import StudentProfileRepository
        profile_repo = StudentProfileRepository(db)
        profile = await profile_repo.get_by_user_id(user.id)
        if assignment.student_id != profile.id:
            raise HTTPException(status_code=404, detail="Assignment not found")
            
    # Directly delete here to avoid checking student_id in AssignmentService.delete
    await assignment_service.assignment_repo.delete(assignment)
    return {"message": "Assignment deleted"}


@router.get("/subject/{subject_id}", response_model=List[AssignmentResponse])
async def get_assignments_by_subject(
    subject_id: int,
    user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    db: AsyncSession = Depends(get_db),
):
    if user.role == UserRole.TEACHER:
        return []

    from app.modules.authentication.repository import StudentProfileRepository
    profile_repo = StudentProfileRepository(db)
    profile = await profile_repo.get_by_user_id(user.id)

    assignments = await assignment_service.get_by_subject(profile.id, subject_id)

    subject_repo = SubjectRepository(assignment_service.assignment_repo.session)
    subject = await subject_repo.get_by_id(subject_id)

    responses = []
    for a in assignments:
        responses.append(AssignmentResponse(
            id=a.id,
            student_id=a.student_id or 0,
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
    user: User = Depends(get_current_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
    db: AsyncSession = Depends(get_db),
):
    assignment = await assignment_service.get_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    if user.role != UserRole.TEACHER:
        from app.modules.authentication.repository import StudentProfileRepository
        profile_repo = StudentProfileRepository(db)
        profile = await profile_repo.get_by_user_id(user.id)
        if assignment.student_id != profile.id and assignment.student_id is not None:
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


# Coding Assignments Routes

from app.api.dependencies.auth import get_current_teacher, get_current_user
from app.modules.authentication.models import User, UserRole
from app.schemas.assignments import (
    CodingAssignmentCreateRequest,
    CodingAssignmentResponse,
    CodingSubmissionCreateRequest,
    CodingSubmissionResponse,
)
from app.modules.assignments.service import CodingAssignmentService
from app.modules.assignments.repository import CodingAssignmentRepository, TestCaseRepository, CodingSubmissionRepository, SubmissionTestResultRepository
from app.modules.assignments.execution_service import ExecutionService

def get_coding_assignment_service(db: AsyncSession = Depends(get_db)) -> CodingAssignmentService:
    assignment_repo = CodingAssignmentRepository(db)
    test_case_repo = TestCaseRepository(db)
    submission_repo = CodingSubmissionRepository(db)
    test_result_repo = SubmissionTestResultRepository(db)
    execution_service = ExecutionService()
    return CodingAssignmentService(
        assignment_repo, test_case_repo, submission_repo, test_result_repo, execution_service
    )

from app.modules.notifications.service import NotificationService
from app.modules.notifications.repository import NotificationRepository
from app.modules.authentication.models import UserRole, User
from sqlalchemy import select

def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(NotificationRepository(db))

@router.post("/coding", response_model=CodingAssignmentResponse)
async def create_coding_assignment(
    request: CodingAssignmentCreateRequest,
    teacher: User = Depends(get_current_teacher),
    service: CodingAssignmentService = Depends(get_coding_assignment_service),
    db: AsyncSession = Depends(get_db),
    notification_service: NotificationService = Depends(get_notification_service)
):
    assignment_data = request.model_dump(exclude={"test_cases"})
    assignment_data["teacher_id"] = teacher.id
    test_cases_data = [tc.model_dump() for tc in request.test_cases]
    
    assignment = await service.create_coding_assignment(assignment_data, test_cases_data)
    
    # Notify all students
    students = await db.execute(select(StudentProfile))
    for student in students.scalars().all():
        await notification_service.create(
            student_id=student.id,
            source="assignment_deadline",
            source_id=assignment.id,
            title=f"New Coding Assignment: {assignment.title}",
            message=f"A new coding assignment '{assignment.title}' has been posted."
        )
        
    return assignment

@router.delete("/coding/{assignment_id}")
async def delete_coding_assignment(
    assignment_id: int,
    teacher: User = Depends(get_current_teacher),
    service: CodingAssignmentService = Depends(get_coding_assignment_service),
    db: AsyncSession = Depends(get_db)
):
    assignment = await service.get_assignment_with_tests(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Coding assignment not found")
        
    await service.assignment_repo.session.delete(assignment)
    await service.assignment_repo.session.commit()
    return {"message": "Coding assignment deleted"}

@router.get("/coding", response_model=List[CodingAssignmentResponse])
async def get_coding_assignments(
    user: User = Depends(get_current_user),
    service: CodingAssignmentService = Depends(get_coding_assignment_service)
):
    assignments = await service.get_all()
    
    for a in assignments:
        setattr(a, "completed_by_user", False)
        
    if user.role == UserRole.STUDENT:
        from app.modules.authentication.repository import StudentProfileRepository
        profile_repo = StudentProfileRepository(service.assignment_repo.session)
        profile = await profile_repo.get_by_user_id(user.id)
        if profile:
            for a in assignments:
                submissions = await service.get_student_submissions(profile.id, a.id)
                if any(s.score == a.max_points for s in submissions):
                    setattr(a, "completed_by_user", True)
                    
    return assignments

@router.get("/coding/{assignment_id}", response_model=CodingAssignmentResponse)
async def get_coding_assignment(
    assignment_id: int,
    user: User = Depends(get_current_user),
    service: CodingAssignmentService = Depends(get_coding_assignment_service)
):
    assignment = await service.get_assignment_with_tests(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Coding assignment not found")
        
    setattr(assignment, "completed_by_user", False)
        
    if user.role == UserRole.STUDENT:
        from app.modules.authentication.repository import StudentProfileRepository
        profile_repo = StudentProfileRepository(service.assignment_repo.session)
        profile = await profile_repo.get_by_user_id(user.id)
        if profile:
            submissions = await service.get_student_submissions(profile.id, assignment.id)
            if any(s.score == assignment.max_points for s in submissions):
                setattr(assignment, "completed_by_user", True)
                
    return assignment

@router.post("/coding/submit", response_model=CodingSubmissionResponse)
async def submit_coding_assignment(
    request: CodingSubmissionCreateRequest,
    profile: StudentProfile = Depends(get_current_student_profile),
    service: CodingAssignmentService = Depends(get_coding_assignment_service)
):
    try:
        submission = await service.submit_code(
            student_id=profile.id,
            assignment_id=request.assignment_id,
            language=request.language,
            source_code=request.source_code
        )
        
        # Check if the student completed it perfectly
        assignment = await service.get_assignment_with_tests(request.assignment_id)
        if submission.score == assignment.max_points:
            from app.modules.notifications.models import Notification, NotificationSource, NotificationStatus, ProcessingStatus
            from app.modules.authentication.repository import TeacherProfileRepository
            teacher_repo = TeacherProfileRepository(service.assignment_repo.session)
            teacher_profile = await teacher_repo.get_by_user_id(assignment.teacher_id)
            if teacher_profile:
                teacher_notif = Notification(
                    teacher_id=teacher_profile.id,
                    source=NotificationSource.ASSIGNMENT_DEADLINE,
                    source_id=assignment.id,
                    title="Coding Assignment Completed",
                    message=f"Student {profile.student_id} has successfully completed '{assignment.title}' with a score of {submission.score}/{assignment.max_points}.",
                    status=NotificationStatus.UNREAD,
                    processing_status=ProcessingStatus.PENDING,
                )
                service.assignment_repo.session.add(teacher_notif)
                await service.assignment_repo.session.commit()
            
            logger.info(f"[NOTIFY_TEACHER] Student {profile.student_id} has successfully completed '{assignment.title}' with a score of {submission.score}/{assignment.max_points}.")
            
        return submission
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/coding/{assignment_id}/submissions", response_model=List[CodingSubmissionResponse])
async def get_student_submissions(
    assignment_id: int,
    profile: StudentProfile = Depends(get_current_student_profile),
    service: CodingAssignmentService = Depends(get_coding_assignment_service)
):
    return await service.get_student_submissions(profile.id, assignment_id)

@router.get("/teacher/coding/{assignment_id}/submissions", response_model=List[CodingSubmissionResponse])
async def get_all_submissions(
    assignment_id: int,
    teacher: User = Depends(get_current_teacher),
    service: CodingAssignmentService = Depends(get_coding_assignment_service)
):
    return await service.get_all_submissions_for_assignment(assignment_id)