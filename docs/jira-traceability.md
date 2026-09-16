# Jira Traceability Matrix

| Requirement ID | Feature | Layer | Implementation | Test | Status |
|----------------|---------|-------|----------------|------|--------|
| SCRUM03-F001 | Authentication | Backend | AuthService, UserRepository, JWT tokens | test_services.py, test_api.py | Implemented |
| SCRUM03-F001-UI-001 | Login screen | Frontend | LoginPage component | Manual | Implemented |
| SCRUM03-F001-FLOW-001 | Auth state & logout | Backend + Frontend | JWT refresh, AuthContext | test_api.py | Implemented |
| SCRUM03-F001-SEC-001 | Protected resources | Backend | Auth dependency, route guards | test_api.py | Implemented |
| SCRUM03-F001-SEC-002 | Secure credential handling | Backend | bcrypt, env config, no logging | test_services.py | Implemented |
| SCRUM03-F002 | Dashboard | Backend | DashboardService, aggregation | test_api.py | Implemented |
| SCRUM03-F002-UI-001 | Dashboard overview | Frontend | DashboardPage component | Manual | Implemented |
| SCRUM03-F002-BE-001 | Dashboard aggregation | Backend | DashboardService | test_services.py | Implemented |
| SCRUM03-F002-E2E-001 | Dashboard E2E | System | test_e2e_workflows.py | test_e2e_workflows.py | Implemented |
| SCRUM03-F003 | Attendance | Backend | AttendanceService, SubjectRepository | test_api.py | Implemented |
| SCRUM03-F003-UI-001 | Attendance view | Frontend | AttendancePage component | Manual | Implemented |
| SCRUM03-F003-BE-001 | Attendance processing | Backend | AttendanceService | test_services.py | Implemented |
| SCRUM03-F003-INT-001 | Portal sync | Backend | MockAttendancePortalAdapter, SyncService | test_e2e_workflows.py | Implemented |
| SCRUM03-F004 | Academics | Backend | AcademicService, AcademicRepository | test_api.py | Implemented |
| SCRUM03-F004-UI-001 | Academic view | Frontend | AcademicsPage component | Manual | Implemented |
| SCRUM03-F004-BE-001 | Academic processing | Backend | AcademicService | test_services.py | Implemented |
| SCRUM03-F004-INT-001 | Portal sync | Backend | MockAcademicPortalAdapter, SyncService | - | Implemented |
| SCRUM03-F005 | Examinations | Backend | ExaminationService, ExaminationRepository | test_api.py | Implemented |
| SCRUM03-F005-UI-001 | Exam schedule view | Frontend | ExaminationsPage component | Manual | Implemented |
| SCRUM03-F005-BE-001 | Exam processing | Backend | ExaminationService | test_services.py | Implemented |
| SCRUM03-F005-INT-001 | Portal sync | Backend | MockExaminationPortalAdapter, SyncService | test_e2e_workflows.py | Implemented |
| SCRUM03-F006 | Announcements | Backend | AnnouncementService, Source/Announcement models | test_api.py | Implemented |
| SCRUM03-F006-UI-001 | Announcements feed | Frontend | AnnouncementsPage component | Manual | Implemented |
| SCRUM03-F006-BE-001 | Aggregation/normalization | Backend | AnnouncementService | test_services.py | Implemented |
| SCRUM03-F006-INT-001 | Portal sync | Backend | MockAnnouncementPortalAdapter, SyncService | - | Implemented |
| SCRUM03-F006-DATA-001 | Traceability data | Backend | Announcement model (source, timestamp) | test_e2e_workflows.py | Implemented |
| SCRUM03-F007 | Placements | Backend | PlacementService, Company/Opportunity/Contribution | test_api.py | Implemented |
| SCRUM03-F007-UI-001 | Placement view | Frontend | PlacementsPage component | Manual | Implemented |
| SCRUM03-F007-BE-001 | Placement processing | Backend | PlacementService | test_services.py | Implemented |
| SCRUM03-F007-INT-001 | Placement sync | Backend | MockPlacementPortalAdapter, SyncService | - | Implemented |
| SCRUM03-F007-CON-001 | Senior contributions | Backend + Frontend | PlacementContribution model, PlacementsPage | test_e2e_workflows.py | Implemented |
| SCRUM03-F008 | Study Materials | Backend | StudyMaterialService, StudyMaterialRepository | test_api.py | Implemented |
| SCRUM03-F008-UI-001 | Browse/access | Frontend | StudyMaterialsPage component | Manual | Implemented |
| SCRUM03-F008-UI-002 | Search/filter | Frontend | StudyMaterialsPage component | Manual | Implemented |
| SCRUM03-F008-BE-001 | Catalog service | Backend | StudyMaterialService | test_services.py | Implemented |
| SCRUM03-F008-CON-001 | Permitted contributions | Backend + Frontend | StudyMaterial model, StudyMaterialsPage | - | Implemented |
| SCRUM03-F008-REL-001 | Assignment context | Backend | StudyMaterialService.get_by_subject | test_e2e_workflows.py | Implemented |
| SCRUM03-F009 | Assignments | Backend | AssignmentService, AssignmentRepository | test_api.py, test_services.py | Implemented |
| SCRUM03-F009-UI-001 | Assignment CRUD | Frontend | AssignmentsPage component | Manual | Implemented |
| SCRUM03-F009-DATA-001 | Assignment details | Backend | Assignment model, status classification | test_services.py | Implemented |
| SCRUM03-F009-UI-002 | Upcoming/overdue views | Frontend | AssignmentsPage tabs | Manual | Implemented |
| SCRUM03-F009-REL-001 | Assignment→Reminder | Backend | AssignmentService.create() creates reminder | test_e2e_workflows.py | Implemented |
| SCRUM03-F009-REL-002 | Completion→Reminder | Backend | AssignmentService.mark_completed() cancels reminders | test_e2e_workflows.py | Implemented |
| SCRUM03-F010 | Reminders | Backend | ReminderService, ReminderRepository, Reminder model with origin field | test_services.py (8 tests) | Implemented |
| SCRUM03-F010-UI-001 | Reminder management | Frontend | RemindersPage.jsx, remindersService.js, tab filters, context badges, create/edit modals | Manual | Implemented |
| SCRUM03-F010-BE-001 | Reminder scheduling | Backend | ReminderService: create_reminder, create_automatic_reminder, get_student_reminders, update_reminder, cancel_linked_reminders, process_due_reminders | test_services.py (8 tests) | Implemented |
| SCRUM03-F010-JOB-001 | Background processing | Backend | JobScheduler.process_reminders_job (60s interval, atomic state transition, exception-safe) | test_services.py | Implemented |
| SCRUM03-F011 | Notifications | Backend | NotificationService, NotificationRepository | test_api.py, test_services.py | Implemented |
| SCRUM03-F011-UI-001 | Notifications center | Frontend | NotificationsPage component | Manual | Implemented |
| SCRUM03-F011-BE-001 | Notification generation | Backend | NotificationService, ReminderService integration | test_services.py | Implemented |
| SCRUM03-F011-JOB-001 | Background processing | Backend | JobScheduler, process_notifications_job | - | Implemented |
| SCRUM03-F011-REL-001 | Reminder→Notification | Backend | ReminderService.process_due_reminders | test_e2e_workflows.py | Implemented |
| SCRUM03-E2E-001 | Assignment→Reminder→Notification | System | test_e2e_workflows.py | test_e2e_workflows.py | Implemented |
| SCRUM03-E2E-002 | Assignment→Materials | System | test_e2e_workflows.py | test_e2e_workflows.py | Implemented |
| SCRUM03-T-001 | Auth test coverage | Test | test_services.py, test_api.py | - | Implemented |
| SCRUM03-T-002 | Assignments/reminders/notifications test | Test | test_services.py, test_e2e_workflows.py | - | Implemented |
| SCRUM03-T-003 | Announcement feed test | Test | test_api.py, test_e2e_workflows.py | - | Implemented |