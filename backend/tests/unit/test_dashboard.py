import pytest
from unittest.mock import AsyncMock, MagicMock

from app.modules.dashboard.service import DashboardService


def create_dashboard_service():
    assignment_service = MagicMock()
    examination_service = MagicMock()
    announcement_service = MagicMock()
    attendance_service = MagicMock()
    academic_service = MagicMock()
    reminder_service = MagicMock()
    notification_service = MagicMock()
    placement_service = MagicMock()
    widget_repo = MagicMock()

    service = DashboardService(
        assignment_service=assignment_service,
        examination_service=examination_service,
        announcement_service=announcement_service,
        attendance_service=attendance_service,
        academic_service=academic_service,
        reminder_service=reminder_service,
        notification_service=notification_service,
        placement_service=placement_service,
        widget_repo=widget_repo,
    )

    return service


@pytest.mark.asyncio
async def test_dashboard_aggregates_all_sections():
    service = create_dashboard_service()

    student = MagicMock()
    student.id = 1

    service.assignment_service.get_by_student = AsyncMock(return_value=[])
    service.assignment_service.get_upcoming = AsyncMock(return_value=[])
    service.assignment_service.get_overdue = AsyncMock(return_value=[])

    service.examination_service.get_upcoming_exams = AsyncMock(
        return_value=[]
    )

    service.announcement_service.get_recent_announcements = AsyncMock(
        return_value=[]
    )

    service.attendance_service.get_attendance_summary = AsyncMock(
        return_value={
            "total_classes_attended": 10,
            "total_classes": 12,
            "overall_percentage": 83.33,
            "subjects_count": 2,
            "records": [],
            "is_unavailable": False,
        }
    )

    service.academic_service.get_student_academics = AsyncMock(
        return_value=[]
    )

    service.reminder_service.get_by_student = AsyncMock(
        return_value=[]
    )

    service.notification_service.get_unread_count = AsyncMock(
        return_value=3
    )

    service.placement_service.get_open_opportunities = AsyncMock(
        return_value=[]
    )

    result = await service.get_dashboard_data(student)

    assert "upcoming_assignments" in result
    assert "overdue_assignments" in result
    assert "upcoming_examinations" in result
    assert "recent_announcements" in result
    assert "attendance_summary" in result
    assert "academic_summary" in result
    assert "pending_reminders" in result
    assert "unread_notifications_count" in result
    assert "placement_opportunities" in result

    assert result["unread_notifications_count"] == 3
    assert result["unavailable_sections"] == []


@pytest.mark.asyncio
async def test_dashboard_continues_when_attendance_fails():
    service = create_dashboard_service()

    student = MagicMock()
    student.id = 1

    service.assignment_service.get_by_student = AsyncMock(
        return_value=[]
    )
    service.assignment_service.get_upcoming = AsyncMock(
        return_value=[]
    )
    service.assignment_service.get_overdue = AsyncMock(
        return_value=[]
    )

    service.examination_service.get_upcoming_exams = AsyncMock(
        return_value=[]
    )

    service.announcement_service.get_recent_announcements = AsyncMock(
        return_value=[]
    )

    service.attendance_service.get_attendance_summary = AsyncMock(
        side_effect=RuntimeError("Attendance service failed")
    )

    service.academic_service.get_student_academics = AsyncMock(
        return_value=[]
    )

    service.reminder_service.get_by_student = AsyncMock(
        return_value=[]
    )

    service.notification_service.get_unread_count = AsyncMock(
        return_value=2
    )

    service.placement_service.get_open_opportunities = AsyncMock(
        return_value=[]
    )

    result = await service.get_dashboard_data(student)

    assert result["upcoming_assignments"] == []
    assert result["upcoming_examinations"] == []
    assert result["academic_summary"] == []
    assert result["unread_notifications_count"] == 2

    assert "attendance" in result["unavailable_sections"]

    assert result["attendance_summary"]["is_unavailable"] is True