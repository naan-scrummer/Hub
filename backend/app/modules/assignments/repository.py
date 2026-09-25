from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assignments.models import Assignment, AssignmentStatus


class AssignmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def select(self, parameter: Assignment):
        return select(parameter)

    async def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        result = await self.session.execute(select(Assignment).where(Assignment.id == assignment_id))
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment).where(Assignment.student_id == student_id).order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def get_upcoming(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                or_(Assignment.student_id == student_id, Assignment.student_id.is_(None)),
                Assignment.due_date >= datetime.utcnow(),
                Assignment.status != AssignmentStatus.COMPLETED,
            )
            .order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def get_overdue(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                or_(Assignment.student_id == student_id, Assignment.student_id.is_(None)),
                Assignment.due_date < datetime.utcnow(),
                Assignment.status != AssignmentStatus.COMPLETED,
            )
            .order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def get_completed(self, student_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                or_(Assignment.student_id == student_id, Assignment.student_id.is_(None)),
                Assignment.status == AssignmentStatus.COMPLETED,
            )
            .order_by(Assignment.completed_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def get_by_subject(self, student_id: int, subject_id: int) -> List[Assignment]:
        result = await self.session.execute(
            select(Assignment)
            .where(
                Assignment.student_id == student_id,
                Assignment.subject_id == subject_id,
            )
            .order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def create(self, assignment: Assignment) -> Assignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def update(self, assignment: Assignment) -> Assignment:
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def delete(self, assignment: Assignment) -> None:
        await self.session.delete(assignment)
        await self.session.flush()

from sqlalchemy.orm import selectinload
from app.modules.assignments.models import CodingAssignment, TestCase, CodingSubmission, SubmissionTestResult

class CodingAssignmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, assignment_id: int) -> Optional[CodingAssignment]:
        result = await self.session.execute(
            select(CodingAssignment)
            .options(selectinload(CodingAssignment.test_cases))
            .where(CodingAssignment.id == assignment_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[CodingAssignment]:
        result = await self.session.execute(
            select(CodingAssignment)
            .options(selectinload(CodingAssignment.test_cases))
            .order_by(CodingAssignment.due_date)
        )
        return list(result.scalars().all())

    async def get_by_teacher(self, teacher_id: int) -> List[CodingAssignment]:
        result = await self.session.execute(
            select(CodingAssignment)
            .options(selectinload(CodingAssignment.test_cases))
            .where(CodingAssignment.teacher_id == teacher_id)
            .order_by(CodingAssignment.due_date.desc())
        )
        return list(result.scalars().all())

    async def create(self, assignment: CodingAssignment) -> CodingAssignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

class TestCaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_assignment(self, assignment_id: int) -> List[TestCase]:
        result = await self.session.execute(select(TestCase).where(TestCase.assignment_id == assignment_id).order_by(TestCase.order_index))
        return list(result.scalars().all())

    async def create(self, test_case: TestCase) -> TestCase:
        self.session.add(test_case)
        await self.session.flush()
        await self.session.refresh(test_case)
        return test_case

class CodingSubmissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, submission_id: int) -> Optional[CodingSubmission]:
        result = await self.session.execute(select(CodingSubmission).where(CodingSubmission.id == submission_id))
        return result.scalar_one_or_none()

    async def get_by_id_with_results(self, submission_id: int) -> Optional[CodingSubmission]:
        result = await self.session.execute(
            select(CodingSubmission)
            .options(selectinload(CodingSubmission.test_results))
            .where(CodingSubmission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student_and_assignment(self, student_id: int, assignment_id: int) -> List[CodingSubmission]:
        result = await self.session.execute(
            select(CodingSubmission)
            .options(selectinload(CodingSubmission.test_results))
            .where(CodingSubmission.student_id == student_id, CodingSubmission.assignment_id == assignment_id)
            .order_by(CodingSubmission.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, submission: CodingSubmission) -> CodingSubmission:
        self.session.add(submission)
        await self.session.flush()
        await self.session.refresh(submission)
        return submission
        
    async def update(self, submission: CodingSubmission) -> CodingSubmission:
        await self.session.flush()
        await self.session.refresh(submission)
        return submission

    async def get_by_assignment(self, assignment_id: int) -> List[CodingSubmission]:
        result = await self.session.execute(
            select(CodingSubmission)
            .options(selectinload(CodingSubmission.test_results))
            .where(CodingSubmission.assignment_id == assignment_id)
            .order_by(CodingSubmission.created_at.desc())
        )
        return list(result.scalars().all())


class SubmissionTestResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_submission(self, submission_id: int) -> List[SubmissionTestResult]:
        result = await self.session.execute(select(SubmissionTestResult).where(SubmissionTestResult.submission_id == submission_id))
        return list(result.scalars().all())

    async def create(self, result: SubmissionTestResult) -> SubmissionTestResult:
        self.session.add(result)
        await self.session.flush()
        await self.session.refresh(result)
        return result