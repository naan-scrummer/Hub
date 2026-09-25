from typing import List, Optional
from datetime import datetime

from app.modules.assignments.models import Assignment, AssignmentStatus
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.service import ReminderService
from app.logging.config import get_logger


logger = get_logger(__name__)


class AssignmentService:
    def __init__(
        self,
        assignment_repo: AssignmentRepository,
        reminder_service: ReminderService,
    ):
        self.assignment_repo = assignment_repo
        self.reminder_service = reminder_service

    async def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        return await self.assignment_repo.get_by_id(assignment_id)

    async def get_by_student(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_by_student(student_id)

    async def get_upcoming(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_upcoming(student_id)

    async def get_overdue(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_overdue(student_id)

    async def get_completed(self, student_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_completed(student_id)

    async def get_by_subject(self, student_id: int, subject_id: int) -> List[Assignment]:
        return await self.assignment_repo.get_by_subject(student_id, subject_id)

    async def create(
        self,
        student_id: int,
        subject_id: int,
        title: str,
        description: Optional[str],
        due_date: datetime,
    ) -> Assignment:
        assignment = Assignment(
            student_id=student_id,
            subject_id=subject_id,
            title=title,
            description=description,
            due_date=due_date,
            status=AssignmentStatus.UPCOMING,
        )
        assignment = await self.assignment_repo.create(assignment)

        # Create the assignment reminder one day before the due date.
        await self.reminder_service.create_automatic_reminder(
            student_id=student_id,
            entity_type="assignment",
            entity_id=assignment.id,
            event_time=due_date,
            title=f"Due soon: {title}",
            lead_days=1,
        )

        logger.info("assignment_created", assignment_id=assignment.id, student_id=student_id)
        return assignment

    async def update(self, assignment: Assignment, old_due_date: Optional[datetime] = None) -> Assignment:
        if old_due_date is None:
            old_due_date = assignment.due_date
        assignment = await self.assignment_repo.update(assignment)

        # Keep the assignment reminder one day before the shifted due date.
        if assignment.due_date != old_due_date:
            await self.reminder_service.update_automatic_reminders_on_due_date_shift(
                student_id=assignment.student_id,
                entity_type="assignment",
                entity_id=assignment.id,
                new_event_time=assignment.due_date,
                lead_days=1,
            )

        return assignment

    async def mark_completed(self, assignment_id: int, student_id: int) -> Optional[Assignment]:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.student_id != student_id:
            return None

        assignment.status = AssignmentStatus.COMPLETED
        assignment.completed_at = datetime.utcnow()
        assignment = await self.assignment_repo.update(assignment)

        # Cancel associated pending reminders (SCRUM 32 spec)
        await self.reminder_service.cancel_linked_reminders(
            student_id=student_id,
            entity_type="assignment",
            entity_id=assignment.id,
        )

        logger.info("assignment_completed", assignment_id=assignment.id, student_id=student_id)
        return assignment

    async def delete(self, assignment_id: int, student_id: int) -> bool:
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.student_id != student_id:
            return False

        # Cancel associated reminders before deleting
        await self.reminder_service.cancel_linked_reminders(
            student_id=student_id,
            entity_type="assignment",
            entity_id=assignment.id,
        )

        await self.assignment_repo.delete(assignment)
        logger.info("assignment_deleted", assignment_id=assignment_id, student_id=student_id)
        return True

    def classify_status(self, assignment: Assignment) -> AssignmentStatus:
        if assignment.status == AssignmentStatus.COMPLETED:
            return AssignmentStatus.COMPLETED
        if assignment.due_date < datetime.utcnow():
            return AssignmentStatus.OVERDUE
        return AssignmentStatus.UPCOMING


from app.modules.assignments.models import CodingAssignment, TestCase, CodingSubmission, SubmissionTestResult
from app.modules.assignments.repository import CodingAssignmentRepository, TestCaseRepository, CodingSubmissionRepository, SubmissionTestResultRepository
from app.modules.assignments.execution_service import ExecutionService

class CodingAssignmentService:
    def __init__(
        self,
        assignment_repo: CodingAssignmentRepository,
        test_case_repo: TestCaseRepository,
        submission_repo: CodingSubmissionRepository,
        test_result_repo: SubmissionTestResultRepository,
        execution_service: ExecutionService,
    ):
        self.assignment_repo = assignment_repo
        self.test_case_repo = test_case_repo
        self.submission_repo = submission_repo
        self.test_result_repo = test_result_repo
        self.execution_service = execution_service
        
    async def get_by_teacher(self, teacher_id: int) -> List[CodingAssignment]:
        # test_cases are eagerly loaded by the repository
        return await self.assignment_repo.get_by_teacher(teacher_id)

    async def get_all(self) -> List[CodingAssignment]:
        # test_cases are eagerly loaded by the repository
        return await self.assignment_repo.get_all()
        
    async def create_coding_assignment(self, assignment_data: dict, test_cases_data: list) -> CodingAssignment:
        assignment = CodingAssignment(**assignment_data)
        assignment = await self.assignment_repo.create(assignment)
        
        for tc_data in test_cases_data:
            tc = TestCase(**tc_data, assignment_id=assignment.id)
            await self.test_case_repo.create(tc)
            
        # Fetch the assignment with test cases eagerly loaded
        return await self.get_assignment_with_tests(assignment.id)
        
    async def get_assignment_with_tests(self, assignment_id: int) -> Optional[CodingAssignment]:
        # test_cases are eagerly loaded by the repository
        return await self.assignment_repo.get_by_id(assignment_id)
        
    async def submit_code(self, student_id: int, assignment_id: int, language: str, source_code: str) -> CodingSubmission:
        assignment = await self.get_assignment_with_tests(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
            
        submission = CodingSubmission(
            student_id=student_id,
            assignment_id=assignment_id,
            language=language,
            source_code=source_code,
            score=0,
            status="PENDING",
            passed_tests=0,
            total_tests=len(assignment.test_cases)
        )
        submission = await self.submission_repo.create(submission)
        
        passed = 0
        total_points = 0
        total_exec_time = 0.0
        max_possible_points = sum(tc.points for tc in assignment.test_cases)
        
        for tc in assignment.test_cases:
            stdout, stderr, exec_time = await self.execution_service.execute_code(
                language=language,
                source_code=source_code,
                input_data=tc.input_data,
                time_limit=assignment.time_limit,
                memory_limit=assignment.memory_limit
            )
            total_exec_time += exec_time
            
            actual_output = stdout.strip()
            expected_output = tc.expected_output.strip()
            
            if stderr:
                status = "ERROR"
                points_awarded = 0
                error_message = stderr
            elif actual_output == expected_output:
                status = "PASSED"
                points_awarded = tc.points
                passed += 1
                error_message = None
            else:
                status = "FAILED"
                points_awarded = 0
                error_message = None
                
            result = SubmissionTestResult(
                submission_id=submission.id,
                test_case_id=tc.id,
                status=status,
                actual_output=actual_output,
                execution_time=exec_time,
                points_awarded=points_awarded,
                error_message=error_message
            )
            await self.test_result_repo.create(result)
            total_points += points_awarded
            
        if max_possible_points > 0:
            submission.score = int((total_points / max_possible_points) * assignment.max_points)
        else:
            submission.score = 0
        submission.passed_tests = passed
        submission.execution_time = total_exec_time
        submission.status = "COMPLETED"
        await self.submission_repo.update(submission)
        
        # Load the submission with its test results to prevent lazy loading errors
        submission_with_results = await self.submission_repo.get_by_id_with_results(submission.id)
        
        return submission_with_results
        
    async def get_student_submissions(self, student_id: int, assignment_id: int) -> List[CodingSubmission]:
        submissions = await self.submission_repo.get_by_student_and_assignment(student_id, assignment_id)
        return submissions

    async def get_all_submissions_for_assignment(self, assignment_id: int) -> List[CodingSubmission]:
        submissions = await self.submission_repo.get_by_assignment(assignment_id)
        return submissions
