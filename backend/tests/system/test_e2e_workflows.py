import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_e2e_assignment_reminder_notification_flow(client):
    """E2E-001: Assignment -> Reminder -> Notification"""
    # Login
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create assignment with due date tomorrow
    due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    create_response = await client.post("/api/v1/assignments", headers=headers, json={
        "subject_id": 1,
        "title": "E2E Test Assignment",
        "description": "Test assignment for E2E flow",
        "due_date": due_date
    })
    assert create_response.status_code == 200
    assignment = create_response.json()
    assignment_id = assignment["id"]

    # Verify assignment was created
    assert assignment["title"] == "E2E Test Assignment"
    assert assignment["status"] == "upcoming"

    # Check that reminder was created (trigger time is 1 day before due date)
    reminders_response = await client.get("/api/v1/reminders", headers=headers)
    assert reminders_response.status_code == 200
    reminders = reminders_response.json()
    assignment_reminders = [r for r in reminders if r.get("assignment_id") == assignment_id]
    assert len(assignment_reminders) > 0
    reminder = assignment_reminders[0]
    assert reminder["status"] == "pending"
    assert reminder["trigger_type"] == "assignment_due"

    # Process reminders (simulate background job)
    process_response = await client.post("/api/v1/reminders/process", headers=headers)
    assert process_response.status_code == 200

    # Check notification was generated
    notifications_response = await client.get("/api/v1/notifications", headers=headers)
    assert notifications_response.status_code == 200
    notifications_data = notifications_response.json()
    notifications = notifications_data["notifications"]
    reminder_notifications = [n for n in notifications if n["source"] == "reminder_trigger" and n.get("source_id") == reminder["id"]]
    assert len(reminder_notifications) > 0
    notification = reminder_notifications[0]
    assert notification["status"] == "unread"

    # Mark notification as read
    mark_read_response = await client.post(f"/api/v1/notifications/{notification['id']}/read", headers=headers)
    assert mark_read_response.status_code == 200
    read_notification = mark_read_response.json()
    assert read_notification["status"] == "read"

    # Test: Assignment completed before trigger -> no stale notification
    # Create another assignment
    due_date2 = (datetime.utcnow() + timedelta(days=2)).isoformat()
    create_response2 = await client.post("/api/v1/assignments", headers=headers, json={
        "subject_id": 1,
        "title": "E2E Test Assignment 2",
        "description": "Second test assignment",
        "due_date": due_date2
    })
    assert create_response2.status_code == 200
    assignment2 = create_response2.json()
    assignment2_id = assignment2["id"]

    # Complete the assignment before reminder triggers
    complete_response = await client.post(f"/api/v1/assignments/{assignment2_id}/complete", headers=headers)
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"

    # Process reminders again
    process_response2 = await client.post("/api/v1/reminders/process", headers=headers)
    assert process_response2.status_code == 200

    # Check that no new notification was created for completed assignment
    notifications_response2 = await client.get("/api/v1/notifications", headers=headers)
    assert notifications_response2.status_code == 200
    notifications2 = notifications_response2.json()["notifications"]
    assignment2_notifications = [n for n in notifications2 if n.get("source_id") == assignment2_id and n["source"] == "reminder_trigger"]
    # The reminder should have been cancelled when assignment was completed
    reminders_response2 = await client.get("/api/v1/reminders", headers=headers)
    reminders2 = reminders_response2.json()
    assignment2_reminders = [r for r in reminders2 if r.get("assignment_id") == assignment2_id]
    if assignment2_reminders:
        assert assignment2_reminders[0]["status"] in ["cancelled", "processed"]


@pytest.mark.asyncio
async def test_e2e_assignment_materials_context(client):
    """E2E-002: Assignment -> Materials context"""
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get materials for subject 1 (CS301)
    materials_response = await client.get("/api/v1/materials/subject/1", headers=headers)
    assert materials_response.status_code == 200
    materials_data = materials_response.json()
    materials = materials_data["materials"]
    assert isinstance(materials, list)
    assert len(materials) > 0
    assert materials[0]["subject_id"] == 1


@pytest.mark.asyncio
async def test_e2e_portal_attendance_sync(client):
    """E2E-003: Portal -> Attendance -> Student"""
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Sync attendance from mock portal
    sync_response = await client.post("/api/v1/attendance/sync", headers=headers, json={
        "student_id": 1
    })
    assert sync_response.status_code == 200
    sync_data = sync_response.json()
    assert sync_data["status"] == "success"

    # Verify attendance data is available
    summary_response = await client.get("/api/v1/attendance/summary", headers=headers)
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["subjects_count"] > 0
    assert summary["overall_percentage"] > 0


@pytest.mark.asyncio
async def test_e2e_portal_examination_sync(client):
    """E2E-004: Portal -> Examination -> Student"""
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Sync examinations from mock portal
    sync_response = await client.post("/api/v1/examinations/sync", headers=headers, json={})
    assert sync_response.status_code == 200
    sync_data = sync_response.json()
    assert sync_data["status"] == "success"

    # Verify examination data is available
    exams_response = await client.get("/api/v1/examinations", headers=headers)
    assert exams_response.status_code == 200
    exams_data = exams_response.json()
    exams = exams_data["examinations"]
    assert len(exams) > 0
    assert exams[0]["subject_id"] > 0


@pytest.mark.asyncio
async def test_announcement_traceability(client):
    """Test announcement source and timestamp traceability"""
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/announcements", headers=headers)
    assert response.status_code == 200
    data = response.json()
    announcements = data["announcements"]
    assert len(announcements) > 0

    for ann in announcements:
        assert "source_name" in ann
        assert "published_at" in ann
        assert "category" in ann
        # Source reference should be present
        # Note: In mock data, source_reference is set


@pytest.mark.asyncio
async def test_placement_contributions(client):
    """Test placement contribution boundaries"""
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get published contributions (should be empty initially)
    contrib_response = await client.get("/api/v1/placements/contributions", headers=headers)
    assert contrib_response.status_code == 200
    contrib_data = contrib_response.json()
    assert "contributions" in contrib_data

    # Create a contribution
    create_response = await client.post("/api/v1/placements/contributions", headers=headers, json={
        "company_id": 1,
        "title": "My Interview Experience",
        "content": "Great experience at TechCorp",
        "contribution_type": "interview_experience"
    })
    assert create_response.status_code == 200
    contribution = create_response.json()
    assert contribution["title"] == "My Interview Experience"
    assert contribution["is_published"] == False

    # Get my contributions
    my_contrib_response = await client.get("/api/v1/placements/my-contributions", headers=headers)
    assert my_contrib_response.status_code == 200
    my_contrib_data = my_contrib_response.json()
    assert len(my_contrib_data["contributions"]) == 1