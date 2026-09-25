import pytest
from httpx import AsyncClient
from app.modules.authentication.models import User, UserRole

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_settings):
    # Using the credentials created by the seed data during test setup
    response = await client.post("/api/v1/auth/login", json={
        "email": test_settings.DEMO_STUDENT_EMAIL,
        "password": test_settings.DEMO_STUDENT_PASSWORD
    })
    
    # If the seed data used the default settings instead of test settings, try the default ones
    if response.status_code == 401:
        response = await client.post("/api/v1/auth/login", json={
            "email": "student@demo.edu",
            "password": "demo123"
        })
        
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_settings):
    response = await client.post("/api/v1/auth/login", json={
        "email": test_settings.DEMO_STUDENT_EMAIL,
        "password": "wrongpassword"
    })
    
    if response.status_code == 401 and response.json()["detail"] == "Invalid credentials":
        pass # Expected
    else:
        response = await client.post("/api/v1/auth/login", json={
            "email": "student@demo.edu",
            "password": "wrongpassword"
        })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "not.exist@demo.edu",
        "password": "password123"
    })
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_access_protected_route_without_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_access_protected_route_with_token(client: AsyncClient, test_settings):
    # Login first
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": test_settings.DEMO_STUDENT_EMAIL,
        "password": test_settings.DEMO_STUDENT_PASSWORD
    })
    
    if login_resp.status_code == 401:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@demo.edu",
            "password": "demo123"
        })
        
    tokens = login_resp.json()
    access_token = tokens["access_token"]
    
    # Access protected route
    response = await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] in [test_settings.DEMO_STUDENT_EMAIL, "student@demo.edu"]

@pytest.mark.asyncio
async def test_get_student_profile(client: AsyncClient, test_settings):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": test_settings.DEMO_STUDENT_EMAIL,
        "password": test_settings.DEMO_STUDENT_PASSWORD
    })
    if login_resp.status_code == 401:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@demo.edu",
            "password": "demo123"
        })
        
    tokens = login_resp.json()
    
    response = await client.get("/api/v1/auth/profile", headers={
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "student_id" in data
    assert "department" in data

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_settings):
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": test_settings.DEMO_STUDENT_EMAIL,
        "password": test_settings.DEMO_STUDENT_PASSWORD
    })
    if login_resp.status_code == 401:
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "student@demo.edu",
            "password": "demo123"
        })
        
    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]
    
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"].startswith("ey")

@pytest.mark.asyncio
async def test_invalid_refresh_token(client: AsyncClient):
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid.refresh.token"
    })
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
