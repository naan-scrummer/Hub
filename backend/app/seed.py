import asyncio
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session_maker, init_db
from app.modules.authentication.models import User, StudentProfile, UserRole
from app.modules.authentication.repository import UserRepository, StudentProfileRepository
from app.modules.authentication.service import AuthenticationService
from app.modules.attendance.models import Subject, AttendanceRecord
from app.modules.attendance.repository import SubjectRepository, AttendanceRepository
from app.modules.academics.models import AcademicRecord
from app.modules.academics.repository import AcademicRepository
from app.modules.examinations.models import Examination
from app.modules.examinations.repository import ExaminationRepository
from app.modules.announcements.models import AnnouncementSource, Announcement
from app.modules.announcements.repository import AnnouncementSourceRepository, AnnouncementRepository
from app.modules.placements.models import Company, PlacementOpportunity, PlacementContribution
from app.modules.placements.repository import CompanyRepository, PlacementOpportunityRepository, PlacementContributionRepository
from app.modules.study_materials.models import StudyMaterial
from app.modules.study_materials.repository import StudyMaterialRepository
from app.modules.assignments.models import Assignment, AssignmentStatus
from app.modules.assignments.repository import AssignmentRepository
from app.modules.reminders.models import Reminder, ReminderTriggerType, ReminderOrigin, ReminderStatus
from app.modules.reminders.repository import ReminderRepository
from app.modules.notifications.models import (
    Notification,
    NotificationSource,
    NotificationStatus,
    ProcessingStatus,
)
from app.modules.notifications.repository import NotificationRepository
from app.logging.config import get_logger


logger = get_logger(__name__)


@asynccontextmanager
async def _get_session(session: AsyncSession | None):
    if session is not None:
        yield session
    else:
        async with async_session_maker() as s:
            yield s


async def seed_data(session: AsyncSession | None = None):
    async with _get_session(session) as session:
        # Initialize repositories
        user_repo = UserRepository(session)
        profile_repo = StudentProfileRepository(session)
        auth_service = AuthenticationService(user_repo, profile_repo)

        subject_repo = SubjectRepository(session)
        attendance_repo = AttendanceRepository(session)
        academic_repo = AcademicRepository(session)
        exam_repo = ExaminationRepository(session)
        ann_source_repo = AnnouncementSourceRepository(session)
        ann_repo = AnnouncementRepository(session)
        company_repo = CompanyRepository(session)
        opp_repo = PlacementOpportunityRepository(session)
        contrib_repo = PlacementContributionRepository(session)
        material_repo = StudyMaterialRepository(session)
        assignment_repo = AssignmentRepository(session)
        reminder_repo = ReminderRepository(session)
        notification_repo = NotificationRepository(session)

        # Create demo user
        demo_user = await auth_service.create_demo_user()
        demo_profile = await profile_repo.get_by_user_id(demo_user.id)
        logger.info("demo_user_ready", user_id=demo_user.id, profile_id=demo_profile.id)

        # Create subjects
        subjects_data = [
            {"code": "CS301", "name": "Database Systems", "department": "Computer Science", "credits": 4},
            {"code": "CS302", "name": "Computer Networks", "department": "Computer Science", "credits": 4},
            {"code": "CS303", "name": "Operating Systems", "department": "Computer Science", "credits": 4},
            {"code": "MA201", "name": "Discrete Mathematics", "department": "Mathematics", "credits": 3},
            {"code": "CS304", "name": "Software Engineering", "department": "Computer Science", "credits": 3},
        ]

        subjects = []
        for s_data in subjects_data:
            existing = await subject_repo.get_by_code(s_data["code"])
            if not existing:
                subject = Subject(**s_data)
                subject = await subject_repo.create(subject)
                subjects.append(subject)
            else:
                subjects.append(existing)

        logger.info("subjects_seeded", count=len(subjects))

        # Create attendance records
        attendance_data = [
            (subjects[0].id, 38, 42),
            (subjects[1].id, 35, 40),
            (subjects[2].id, 30, 38),
            (subjects[3].id, 28, 35),
            (subjects[4].id, 25, 30),
        ]

        for subject_id, attended, total in attendance_data:
            existing = await attendance_repo.get_by_student_and_subject(demo_profile.id, subject_id)
            if not existing:
                percentage = round((attended / total) * 100, 2) if total > 0 else 0
                record = AttendanceRecord(
                    student_id=demo_profile.id,
                    subject_id=subject_id,
                    classes_attended=attended,
                    total_classes=total,
                    attendance_percentage=percentage,
                    last_synced_at=datetime.utcnow(),
                )
                await attendance_repo.create(record)

        logger.info("attendance_seeded", count=len(attendance_data))

        # Create academic records
        academic_data = [
            (subjects[0].id, 42, 50, 78, 100, 6),
            (subjects[1].id, 38, 50, 72, 100, 6),
            (subjects[2].id, 45, 50, 85, 100, 6),
            (subjects[3].id, 40, 50, 68, 100, 6),
            (subjects[4].id, 35, 50, 70, 100, 6),
        ]

        for subject_id, internal, max_internal, external, max_external, semester in academic_data:
            existing = await academic_repo.get_by_student_and_subject(demo_profile.id, subject_id, semester)
            if not existing:
                total = internal + external
                max_total = max_internal + max_external
                pct = (total / max_total) * 100 if max_total > 0 else 0
                grade = "A+" if pct >= 90 else "A" if pct >= 80 else "B+" if pct >= 70 else "B" if pct >= 60 else "C" if pct >= 50 else "F"

                record = AcademicRecord(
                    student_id=demo_profile.id,
                    subject_id=subject_id,
                    internal_marks=internal,
                    max_internal_marks=max_internal,
                    external_marks=external,
                    max_external_marks=max_external,
                    total_marks=total,
                    grade=grade,
                    semester=semester,
                    last_synced_at=datetime.utcnow(),
                )
                await academic_repo.create(record)

        logger.info("academics_seeded", count=len(academic_data))

        # Create examinations
        now = datetime.utcnow()
        exam_data = [
            (subjects[0].id, "Database Systems - Midterm", "midterm", now + timedelta(days=7), now + timedelta(days=7, hours=2), "Room 101"),
            (subjects[1].id, "Computer Networks - Final", "final", now + timedelta(days=14), now + timedelta(days=14, hours=3), "Room 205"),
            (subjects[2].id, "Operating Systems - Quiz", "quiz", now + timedelta(days=3), now + timedelta(days=3, hours=1), "Lab 3"),
            (subjects[3].id, "Discrete Mathematics - Midterm", "midterm", now + timedelta(days=10), now + timedelta(days=10, hours=2), "Room 301"),
        ]

        for subject_id, title, exam_type, exam_date, end_time, venue in exam_data:
            existing = await session.execute(
                exam_repo.select(Examination).where(
                    Examination.subject_id == subject_id,
                    Examination.title == title,
                )
            )
            if not existing.scalar_one_or_none():
                exam = Examination(
                    subject_id=subject_id,
                    title=title,
                    exam_type=exam_type,
                    exam_date=exam_date,
                    start_time=exam_date,
                    end_time=end_time,
                    venue=venue,
                    last_synced_at=datetime.utcnow(),
                )
                await exam_repo.create(exam)

        logger.info("examinations_seeded", count=len(exam_data))

        # Create announcement sources
        sources_data = [
            {"name": "College Portal", "source_type": "portal", "base_url": "https://college.edu/portal"},
            {"name": "Department CS", "source_type": "department", "base_url": "https://cs.college.edu"},
            {"name": "Examination Cell", "source_type": "examination", "base_url": "https://exam.college.edu"},
        ]

        sources = []
        for s_data in sources_data:
            existing = await ann_source_repo.get_by_name(s_data["name"])
            if not existing:
                source = AnnouncementSource(**s_data)
                source = await ann_source_repo.create(source)
                sources.append(source)
            else:
                sources.append(existing)

        # Create announcements
        now = datetime.utcnow()
        announcements_data = [
            (sources[0].id, "portal-001", "Midterm Exam Schedule Released", "The midterm examination schedule for the current semester has been published. Please check the examination portal for details.", "examination", now - timedelta(days=2)),
            (sources[1].id, "cs-001", "Department Tech Fest Registration Open", "Registration for the annual department technical festival is now open. Visit the student portal to register.", "event", now - timedelta(days=5)),
            (sources[0].id, "portal-002", "Library Extended Hours", "The central library will remain open until 11 PM during the examination period starting next week.", "administrative", now - timedelta(days=8)),
            (sources[2].id, "exam-001", "Supplementary Exam Applications Open", "Applications for supplementary exams are now open. Last date to apply is next Friday.", "examination", now - timedelta(days=12)),
            (sources[1].id, "cs-002", "Guest Lecture on AI/ML", "A guest lecture on Artificial Intelligence and Machine Learning will be held this Friday at 2 PM in Auditorium.", "event", now - timedelta(days=1)),
        ]

        for source_id, ref, title, content, category, published_at in announcements_data:
            existing = await session.execute(
                ann_repo.select(Announcement).where(
                    Announcement.source_id == source_id,
                    Announcement.source_reference == ref,
                )
            )
            if not existing.scalar_one_or_none():
                ann = Announcement(
                    source_id=source_id,
                    source_reference=ref,
                    title=title,
                    content=content,
                    category=category,
                    published_at=published_at,
                )
                await ann_repo.create(ann)

        logger.info("announcements_seeded", count=len(announcements_data))

        # Create companies
        companies_data = [
            {"name": "TechCorp Solutions", "description": "Leading software solutions provider", "website": "https://techcorp.com", "industry": "Software"},
            {"name": "DataFlow Analytics", "description": "Data analytics and business intelligence", "website": "https://dataflow.com", "industry": "Analytics"},
            {"name": "CloudNine Systems", "description": "Cloud infrastructure and DevOps", "website": "https://cloudnine.com", "industry": "Cloud Computing"},
        ]

        companies = []
        for c_data in companies_data:
            existing = await company_repo.get_by_name(c_data["name"])
            if not existing:
                company = Company(**c_data)
                company = await company_repo.create(company)
                companies.append(company)
            else:
                companies.append(existing)

        # Create placement opportunities
        now = datetime.utcnow()
        opportunities_data = [
            (companies[0].id, "Software Engineer Intern", "Summer internship program for CS students", "CGPA >= 7.0, no active backlogs", "Bangalore", "₹40,000/month", now + timedelta(days=30), "open"),
            (companies[1].id, "Data Analyst Trainee", "Entry-level position for recent graduates", "Graduation in 2024, Statistics/CS background", "Hyderabad", "₹6,00,000/annum", now + timedelta(days=45), "open"),
            (companies[2].id, "DevOps Engineer", "Cloud infrastructure and automation role", "Experience with AWS/Docker/Kubernetes", "Pune", "₹12,00,000/annum", now + timedelta(days=60), "open"),
        ]

        for company_id, title, desc, eligibility, location, package, deadline, status in opportunities_data:
            existing = await session.execute(
                opp_repo.select(PlacementOpportunity).where(
                    PlacementOpportunity.company_id == company_id,
                    PlacementOpportunity.title == title,
                )
            )
            if not existing.scalar_one_or_none():
                opp = PlacementOpportunity(
                    company_id=company_id,
                    title=title,
                    description=desc,
                    eligibility_criteria=eligibility,
                    location=location,
                    package_details=package,
                    application_deadline=deadline,
                    recruitment_status=status,
                )
                await opp_repo.create(opp)

        logger.info("placements_seeded", count=len(opportunities_data))

        # Create study materials
        materials_data = [
            (subjects[0].id, "Database Systems - Lecture Notes", "Complete lecture notes for Database Systems course", "notes", None, "https://example.com/db-notes.pdf"),
            (subjects[0].id, "SQL Practice Problems", "Collection of SQL practice problems with solutions", "practice", None, "https://example.com/sql-practice.pdf"),
            (subjects[1].id, "Computer Networks - Textbook", "Reference textbook for Computer Networks", "textbook", None, "https://example.com/cn-textbook.pdf"),
            (subjects[2].id, "OS Lab Manual", "Operating Systems laboratory manual", "lab_manual", None, "https://example.com/os-lab.pdf"),
            (subjects[3].id, "Discrete Math - Previous Year Papers", "Previous year question papers for Discrete Mathematics", "question_paper", None, "https://example.com/ma201-papers.pdf"),
        ]

        for subject_id, title, desc, m_type, file_path, url in materials_data:
            existing = await session.execute(
                material_repo.select(StudyMaterial).where(
                    StudyMaterial.subject_id == subject_id,
                    StudyMaterial.title == title,
                )
            )
            if not existing.scalar_one_or_none():
                material = StudyMaterial(
                    subject_id=subject_id,
                    title=title,
                    description=desc,
                    material_type=m_type,
                    file_path=file_path,
                    external_url=url,
                    is_approved=True,
                )
                await material_repo.create(material)

        logger.info("study_materials_seeded", count=len(materials_data))

        # Create assignments
        now = datetime.utcnow()
        assignments_data = [
            (subjects[0].id, "Database Design Project", "Design a normalized database schema for a library management system", now + timedelta(days=5), AssignmentStatus.UPCOMING),
            (subjects[1].id, "Network Simulation Lab", "Complete the network simulation using Cisco Packet Tracer", now - timedelta(days=2), AssignmentStatus.OVERDUE),
            (subjects[2].id, "OS Process Scheduling", "Implement round-robin and priority scheduling algorithms", now + timedelta(days=10), AssignmentStatus.UPCOMING),
            (subjects[3].id, "Graph Theory Problems", "Solve problems on graph coloring and spanning trees", now - timedelta(days=10), AssignmentStatus.COMPLETED),
        ]

        assignments = []
        for subject_id, title, desc, due_date, status in assignments_data:
            assignment = Assignment(
                student_id=demo_profile.id,
                subject_id=subject_id,
                title=title,
                description=desc,
                due_date=due_date,
                status=status,
                completed_at=datetime.utcnow() - timedelta(days=12) if status == AssignmentStatus.COMPLETED else None,
            )
            assignment = await assignment_repo.create(assignment)
            assignments.append(assignment)

        logger.info("assignments_seeded", count=len(assignments))

        # Fetch exams for reminder references
        exams_result = await session.execute(
            exam_repo.select(Examination).where(Examination.subject_id == subjects[0].id)
        )
        exams_list = list(exams_result.scalars().all())

        # Create reminders — mix of AUTOMATIC and CUSTOM origins, different statuses
        reminders_data = [
            # AUTOMATIC reminders (system-generated, 7 days before event)
            {
                "assignment_id": assignments[0].id,
                "examination_id": None,
                "title": "Due soon: Database Design Project",
                "description": "Automatic reminder: Database Design Project due in 5 days",
                "trigger_type": ReminderTriggerType.ASSIGNMENT_DUE,
                "trigger_time": assignments[0].due_date - timedelta(days=7),
                "origin": ReminderOrigin.AUTOMATIC,
                "status": ReminderStatus.PENDING,
            },
            {
                "assignment_id": assignments[2].id,
                "examination_id": None,
                "title": "Due soon: OS Process Scheduling",
                "description": "Automatic reminder: OS Process Scheduling due in 10 days",
                "trigger_type": ReminderTriggerType.ASSIGNMENT_DUE,
                "trigger_time": assignments[2].due_date - timedelta(days=7),
                "origin": ReminderOrigin.AUTOMATIC,
                "status": ReminderStatus.PENDING,
            },
            {
                "assignment_id": None,
                "examination_id": exams_list[0].id if exams_list else None,
                "title": "Exam soon: Database Systems - Midterm",
                "description": "Automatic reminder: Database Systems - Midterm in 7 days",
                "trigger_type": ReminderTriggerType.EXAMINATION,
                "trigger_time": (now + timedelta(days=7)) - timedelta(days=7),
                "origin": ReminderOrigin.AUTOMATIC,
                "status": ReminderStatus.PENDING,
            },
            # AUTOMATIC reminder that was already processed (for completed assignment)
            {
                "assignment_id": assignments[1].id,
                "examination_id": None,
                "title": "Due soon: Network Simulation Lab",
                "description": "Automatic reminder: Network Simulation Lab (already overdue)",
                "trigger_type": ReminderTriggerType.ASSIGNMENT_DUE,
                "trigger_time": assignments[1].due_date - timedelta(days=7),
                "origin": ReminderOrigin.AUTOMATIC,
                "status": ReminderStatus.PROCESSED,
                "processed_at": now - timedelta(days=3),
            },
            # CUSTOM reminders (user-created)
            {
                "assignment_id": None,
                "examination_id": None,
                "title": "Study Group Meeting",
                "description": "Weekly study group meeting at library — bring notes",
                "trigger_type": ReminderTriggerType.CUSTOM,
                "trigger_time": now + timedelta(days=2, hours=14),
                "origin": ReminderOrigin.CUSTOM,
                "status": ReminderStatus.PENDING,
            },
            {
                "assignment_id": None,
                "examination_id": None,
                "title": "Submit internship application",
                "description": "Deadline for TechCorp summer internship application",
                "trigger_type": ReminderTriggerType.CUSTOM,
                "trigger_time": now + timedelta(days=7, hours=9),
                "origin": ReminderOrigin.CUSTOM,
                "status": ReminderStatus.PENDING,
            },
            {
                "assignment_id": assignments[3].id,
                "examination_id": None,
                "title": "Review Graph Theory solutions",
                "description": "Review solutions for completed Graph Theory assignment",
                "trigger_type": ReminderTriggerType.ASSIGNMENT_DUE,
                "trigger_time": now - timedelta(days=5),
                "origin": ReminderOrigin.CUSTOM,
                "status": ReminderStatus.CANCELLED,
            },
            {
                "assignment_id": None,
                "examination_id": exams_list[0].id if exams_list else None,
                "title": "Pre-exam prep: Database Systems",
                "description": "Start preparing for Database Systems midterm",
                "trigger_type": ReminderTriggerType.EXAMINATION,
                "trigger_time": now - timedelta(days=1),
                "origin": ReminderOrigin.CUSTOM,
                "status": ReminderStatus.PROCESSED,
                "processed_at": now - timedelta(days=1),
            },
        ]

        for data in reminders_data:
            reminder = Reminder(
                student_id=demo_profile.id,
                assignment_id=data["assignment_id"],
                examination_id=data["examination_id"],
                title=data["title"],
                description=data["description"],
                trigger_type=data["trigger_type"],
                trigger_time=data["trigger_time"],
                origin=data["origin"],
                status=data["status"],
                processed_at=data.get("processed_at"),
            )
            await reminder_repo.create(reminder)

        logger.info("reminders_seeded", count=len(reminders_data))

        # Create notifications covering all supported sources and statuses (SCRUM-83/SCRUM-84)
        notifications_data = [
            (
                NotificationSource.ASSIGNMENT_DEADLINE,
                assignments[0].id if assignments else 101,
                "Assignment Due Soon: Database Design Project",
                "Your DBMS project submission is due in 24 hours. Ensure all diagrams and schema SQL are included.",
                NotificationStatus.UNREAD,
                ProcessingStatus.PROCESSED,
                None,
                now - timedelta(hours=2),
            ),
            (
                NotificationSource.REMINDER_TRIGGER,
                None,
                "Reminder: Study for Computer Networks",
                "Custom study reminder: Chapter 4 packet routing revision scheduled now.",
                NotificationStatus.UNREAD,
                ProcessingStatus.PROCESSED,
                None,
                now - timedelta(hours=5),
            ),
            (
                NotificationSource.ANNOUNCEMENT,
                None,
                "Campus Placement Drive: Registration Open",
                "Registration for the upcoming technology recruitment drive closes this Friday at 5 PM.",
                NotificationStatus.READ,
                ProcessingStatus.PROCESSED,
                now - timedelta(hours=8),
                now - timedelta(days=1),
            ),
            (
                NotificationSource.EXAMINATION,
                exams_list[0].id if exams_list else 404,
                "Mid-Semester Examination Schedule Live",
                "The official timetable for Mid-Sem 2 examinations has been published on the academic portal.",
                NotificationStatus.READ,
                ProcessingStatus.PROCESSED,
                now - timedelta(days=1),
                now - timedelta(days=2),
            ),
            (
                NotificationSource.PLACEMENT,
                None,
                "Placement Shortlist: TechCorp Solutions",
                "You have been shortlisted for the initial technical evaluation round with TechCorp Solutions.",
                NotificationStatus.UNREAD,
                ProcessingStatus.PROCESSED,
                None,
                now - timedelta(minutes=45),
            ),
            (
                NotificationSource.ANNOUNCEMENT,
                None,
                "Annual Sports Day Archived Information",
                "Annual sports day track events timetable and venue details.",
                NotificationStatus.ARCHIVED,
                ProcessingStatus.PROCESSED,
                now - timedelta(days=12),
                now - timedelta(days=15),
            ),
        ]

        for source, source_id, title, message, status, p_status, read_at, created_at in notifications_data:
            notification = Notification(
                student_id=demo_profile.id,
                source=source,
                source_id=source_id,
                title=title,
                message=message,
                status=status,
                processing_status=p_status,
                read_at=read_at,
                created_at=created_at,
                updated_at=created_at,
            )
            await notification_repo.create(notification)

        logger.info("notifications_seeded", count=len(notifications_data))

        await session.commit()
        logger.info("seed_completed")


if __name__ == "__main__":
    asyncio.run(seed_data())