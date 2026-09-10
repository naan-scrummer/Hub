from typing import List
from datetime import datetime, timedelta
from decimal import Decimal

from app.integrations.college_portal.interface import (
    CollegePortalClient,
    AttendancePortalAdapter,
    AcademicPortalAdapter,
    ExaminationPortalAdapter,
    AnnouncementPortalAdapter,
    PlacementPortalAdapter,
)
from app.modules.attendance.models import AttendanceRecord, Subject
from app.modules.academics.models import AcademicRecord
from app.modules.examinations.models import Examination
from app.modules.announcements.models import Announcement, AnnouncementSource
from app.modules.placements.models import Company, PlacementOpportunity
from app.logging.config import get_logger


logger = get_logger(__name__)


class MockCollegePortalClient(CollegePortalClient):
    async def fetch_attendance(self, student_id: str) -> List[dict]:
        return [
            {"subject_code": "CS301", "classes_attended": 38, "total_classes": 42},
            {"subject_code": "CS302", "classes_attended": 35, "total_classes": 40},
            {"subject_code": "CS303", "classes_attended": 30, "total_classes": 38},
            {"subject_code": "MA201", "classes_attended": 28, "total_classes": 35},
        ]

    async def fetch_academics(self, student_id: str) -> List[dict]:
        return [
            {"subject_code": "CS301", "internal_marks": 42, "max_internal": 50, "external_marks": 78, "max_external": 100, "semester": 6},
            {"subject_code": "CS302", "internal_marks": 38, "max_internal": 50, "external_marks": 72, "max_external": 100, "semester": 6},
            {"subject_code": "CS303", "internal_marks": 45, "max_internal": 50, "external_marks": 85, "max_external": 100, "semester": 6},
            {"subject_code": "MA201", "internal_marks": 40, "max_internal": 50, "external_marks": 68, "max_external": 100, "semester": 6},
        ]

    async def fetch_examinations(self) -> List[dict]:
        now = datetime.utcnow()
        return [
            {
                "subject_code": "CS301",
                "title": "Database Systems - Midterm",
                "exam_type": "midterm",
                "exam_date": now + timedelta(days=7),
                "venue": "Room 101",
            },
            {
                "subject_code": "CS302",
                "title": "Computer Networks - Final",
                "exam_type": "final",
                "exam_date": now + timedelta(days=14),
                "venue": "Room 205",
            },
            {
                "subject_code": "CS303",
                "title": "Operating Systems - Quiz",
                "exam_type": "quiz",
                "exam_date": now + timedelta(days=3),
                "venue": "Lab 3",
            },
        ]

    async def fetch_announcements(self, source: AnnouncementSource) -> List[dict]:
        now = datetime.utcnow()
        return [
            {
                "source_reference": f"{source.name}-001",
                "title": "Midterm Exam Schedule Released",
                "content": "The midterm examination schedule for the current semester has been published. Please check the examination portal for details.",
                "category": "examination",
                "published_at": now - timedelta(days=2),
            },
            {
                "source_reference": f"{source.name}-002",
                "title": "Library Extended Hours",
                "content": "The central library will remain open until 11 PM during the examination period starting next week.",
                "category": "administrative",
                "published_at": now - timedelta(days=5),
            },
            {
                "source_reference": f"{source.name}-003",
                "title": "Department Tech Fest Registration Open",
                "content": "Registration for the annual department technical festival is now open. Visit the student portal to register.",
                "category": "event",
                "published_at": now - timedelta(days=10),
            },
        ]

    async def fetch_placements(self) -> List[dict]:
        now = datetime.utcnow()
        return [
            {
                "company_name": "TechCorp Solutions",
                "title": "Software Engineer Intern",
                "description": "Summer internship program for CS students",
                "eligibility": "CGPA >= 7.0, no active backlogs",
                "location": "Bangalore",
                "package": "₹40,000/month",
                "deadline": now + timedelta(days=30),
                "status": "open",
            },
            {
                "company_name": "DataFlow Analytics",
                "title": "Data Analyst Trainee",
                "description": "Entry-level position for recent graduates",
                "eligibility": "Graduation in 2024, Statistics/CS background",
                "location": "Hyderabad",
                "package": "₹6,00,000/annum",
                "deadline": now + timedelta(days=45),
                "status": "open",
            },
            {
                "company_name": "CloudNine Systems",
                "title": "DevOps Engineer",
                "description": "Cloud infrastructure and automation role",
                "eligibility": "Experience with AWS/Docker/Kubernetes",
                "location": "Pune",
                "package": "₹12,00,000/annum",
                "deadline": now + timedelta(days=60),
                "status": "open",
            },
        ]


class MockAttendancePortalAdapter(AttendancePortalAdapter):
    def __init__(self, client: CollegePortalClient):
        self.client = client

    async def sync(self, student_id: int, sync_run_id: int) -> List[AttendanceRecord]:
        # In a real implementation, we'd map student_id to portal student_id
        portal_student_id = f"STU{student_id:06d}"
        raw_data = await self.client.fetch_attendance(portal_student_id)

        records = []
        for item in raw_data:
            # Subject lookup would happen here; for mock we create records with subject_id from code mapping
            records.append(
                AttendanceRecord(
                    student_id=student_id,
                    subject_id=self._get_subject_id(item["subject_code"]),
                    classes_attended=item["classes_attended"],
                    total_classes=item["total_classes"],
                    attendance_percentage=round((item["classes_attended"] / item["total_classes"]) * 100, 2) if item["total_classes"] > 0 else 0,
                    last_synced_at=datetime.utcnow(),
                    source_sync_run_id=sync_run_id,
                )
            )
        logger.info("mock_attendance_synced", student_id=student_id, count=len(records))
        return records

    def _get_subject_id(self, code: str) -> int:
        # Mock mapping - in real impl would query Subject table
        mapping = {"CS301": 1, "CS302": 2, "CS303": 3, "MA201": 4}
        return mapping.get(code, 1)


class MockAcademicPortalAdapter(AcademicPortalAdapter):
    def __init__(self, client: CollegePortalClient):
        self.client = client

    async def sync(self, student_id: int, sync_run_id: int) -> List[AcademicRecord]:
        portal_student_id = f"STU{student_id:06d}"
        raw_data = await self.client.fetch_academics(portal_student_id)

        records = []
        for item in raw_data:
            total = (item["internal_marks"] or 0) + (item["external_marks"] or 0)
            max_total = (item["max_internal"] or 0) + (item["max_external"] or 0)
            grade = self._calculate_grade(total, max_total)

            records.append(
                AcademicRecord(
                    student_id=student_id,
                    subject_id=self._get_subject_id(item["subject_code"]),
                    internal_marks=item["internal_marks"],
                    max_internal_marks=item["max_internal"],
                    external_marks=item["external_marks"],
                    max_external_marks=item["max_external"],
                    total_marks=total,
                    grade=grade,
                    semester=item["semester"],
                    last_synced_at=datetime.utcnow(),
                    source_sync_run_id=sync_run_id,
                )
            )
        logger.info("mock_academics_synced", student_id=student_id, count=len(records))
        return records

    def _get_subject_id(self, code: str) -> int:
        mapping = {"CS301": 1, "CS302": 2, "CS303": 3, "MA201": 4}
        return mapping.get(code, 1)

    def _calculate_grade(self, total: int, max_total: int) -> str:
        if max_total == 0:
            return "N/A"
        pct = (total / max_total) * 100
        if pct >= 90: return "A+"
        if pct >= 80: return "A"
        if pct >= 70: return "B+"
        if pct >= 60: return "B"
        if pct >= 50: return "C"
        return "F"


class MockExaminationPortalAdapter(ExaminationPortalAdapter):
    def __init__(self, client: CollegePortalClient):
        self.client = client

    async def sync(self, sync_run_id: int) -> List[Examination]:
        raw_data = await self.client.fetch_examinations()

        exams = []
        for item in raw_data:
            exams.append(
                Examination(
                    subject_id=self._get_subject_id(item["subject_code"]),
                    title=item["title"],
                    exam_type=item["exam_type"],
                    exam_date=item["exam_date"],
                    venue=item.get("venue"),
                    last_synced_at=datetime.utcnow(),
                    source_sync_run_id=sync_run_id,
                )
            )
        logger.info("mock_examinations_synced", count=len(exams))
        return exams

    def _get_subject_id(self, code: str) -> int:
        mapping = {"CS301": 1, "CS302": 2, "CS303": 3, "MA201": 4}
        return mapping.get(code, 1)


class MockAnnouncementPortalAdapter(AnnouncementPortalAdapter):
    def __init__(self, client: CollegePortalClient):
        self.client = client

    async def sync(self, source: AnnouncementSource, sync_run_id: int) -> List[Announcement]:
        raw_data = await self.client.fetch_announcements(source)

        announcements = []
        for item in raw_data:
            announcements.append(
                Announcement(
                    source_id=source.id,
                    source_reference=item["source_reference"],
                    title=item["title"],
                    content=item["content"],
                    category=item["category"],
                    published_at=item["published_at"],
                    source_sync_run_id=sync_run_id,
                )
            )
        logger.info("mock_announcements_synced", source=source.name, count=len(announcements))
        return announcements


class MockPlacementPortalAdapter(PlacementPortalAdapter):
    def __init__(self, client: CollegePortalClient):
        self.client = client

    async def sync(self, sync_run_id: int) -> List[PlacementOpportunity]:
        raw_data = await self.client.fetch_placements()

        opportunities = []
        for item in raw_data:
            opportunities.append(
                PlacementOpportunity(
                    company_id=self._get_company_id(item["company_name"]),
                    title=item["title"],
                    description=item["description"],
                    eligibility_criteria=item["eligibility"],
                    location=item["location"],
                    package_details=item["package"],
                    application_deadline=item["deadline"],
                    recruitment_status=item["status"],
                    source_sync_run_id=sync_run_id,
                )
            )
        logger.info("mock_placements_synced", count=len(opportunities))
        return opportunities

    def _get_company_id(self, name: str) -> int:
        mapping = {
            "TechCorp Solutions": 1,
            "DataFlow Analytics": 2,
            "CloudNine Systems": 3,
        }
        return mapping.get(name, 1)