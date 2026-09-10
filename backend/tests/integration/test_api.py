import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_auth(client):
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_with_auth(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "upcoming_assignments" in data
    assert "overdue_assignments" in data
    assert "upcoming_examinations" in data
    assert "recent_announcements" in data
    assert "attendance_summary" in data
    assert "academic_summary" in data
    assert "pending_reminders" in data
    assert "unread_notifications_count" in data
    assert "placement_opportunities" in data


@pytest.mark.asyncio
async def test_attendance_endpoints(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/attendance/subjects", headers=headers)
    assert response.status_code == 200
    subjects = response.json()
    assert isinstance(subjects, list)
    assert len(subjects) > 0

    response = await client.get("/api/v1/attendance/summary", headers=headers)
    assert response.status_code == 200
    summary = response.json()
    assert "overall_percentage" in summary
    assert "records" in summary


@pytest.mark.asyncio
async def test_assignments_crud(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/assignments", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "upcoming" in data
    assert "overdue" in data
    assert "completed" in data

    create_response = await client.post("/api/v1/assignments", headers=headers, json={
        "subject_id": 1,
        "title": "Test Assignment",
        "description": "Test description",
        "due_date": "2025-12-31T23:59:00"
    })
    assert create_response.status_code == 200
    assignment = create_response.json()
    assert assignment["title"] == "Test Assignment"
    assignment_id = assignment["id"]

    update_response = await client.patch(f"/api/v1/assignments/{assignment_id}", headers=headers, json={
        "title": "Updated Assignment"
    })
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Updated Assignment"

    complete_response = await client.post(f"/api/v1/assignments/{assignment_id}/complete", headers=headers)
    assert complete_response.status_code == 200
    completed = complete_response.json()
    assert completed["status"] == "completed"

    delete_response = await client.delete(f"/api/v1/assignments/{assignment_id}", headers=headers)
    assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_reminders(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reminders", headers=headers)
    assert response.status_code == 200
    reminders = response.json()
    assert isinstance(reminders, list)

    create_response = await client.post("/api/v1/reminders", headers=headers, json={
        "title": "Test Reminder",
        "description": "Test description",
        "trigger_type": "custom",
        "trigger_time": "2025-12-31T23:59:00"
    })
    assert create_response.status_code == 200
    reminder = create_response.json()
    assert reminder["title"] == "Test Reminder"


@pytest.mark.asyncio
async def test_notifications(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/notifications", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    assert "unread_count" in data


@pytest.mark.asyncio
async def test_announcements(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/announcements", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "announcements" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_examinations(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/examinations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "examinations" in data
    assert "is_unavailable" in data


@pytest.mark.asyncio
async def test_academics(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/academics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert "is_unavailable" in data


@pytest.mark.asyncio
async def test_placements(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/placements/opportunities", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "opportunities" in data


@pytest.mark.asyncio
async def test_study_materials(client):
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "student@demo.edu",
        "password": "demo123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/materials", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "materials" in data
    assert "total" in data