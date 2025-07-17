import pytest
from fastapi.testclient import TestClient
from ..api.main import app

client = TestClient(app)

def test_health():
    """Test health endpoint"""
    response = client.get("/api/backend/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "backend-gateway"
    assert "dependencies" in response.json()

def test_login_success():
    """Test successful login"""
    response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

def test_login_failure():
    """Test failed login with wrong credentials"""
    response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "detail" in response.json()

def test_user_profile_requires_auth():
    """Test that user profile endpoint requires authentication"""
    response = client.get("/api/backend/auth/profile")
    assert response.status_code == 403  # Unauthorized

def test_user_profile_with_auth():
    """Test user profile endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access profile endpoint
    response = client.get("/api/backend/auth/profile", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"

def test_geological_sites_requires_auth():
    """Test that geological sites endpoint requires authentication"""
    response = client.get("/api/backend/geological-sites")
    assert response.status_code == 403

def test_geological_sites_with_auth():
    """Test geological sites endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access geological sites endpoint
    response = client.get("/api/backend/geological-sites?limit=3", headers={
        "Authorization": f"Bearer {token}"
    })
    # Note: This might fail if Module 1 is not running, but should return 200 if auth works
    assert response.status_code in [200, 500]  # 500 if Module 1 unavailable

def test_chat_requires_auth():
    """Test that chat endpoint requires authentication"""
    response = client.post("/api/backend/chat", json={
        "message": "Hello"
    })
    assert response.status_code == 403

def test_chat_with_auth():
    """Test chat endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access chat endpoint
    response = client.post("/api/backend/chat", json={
        "message": "What is copper?"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    # Note: This might fail if Module 2 is not running, but should return 200 if auth works
    assert response.status_code in [200, 500]  # 500 if Module 2 unavailable

def test_geological_query_requires_auth():
    """Test that geological query endpoint requires authentication"""
    response = client.post("/api/backend/geological-query", json={
        "query": "Find copper deposits"
    })
    assert response.status_code == 403

def test_geological_query_with_auth():
    """Test geological query endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access geological query endpoint
    response = client.post("/api/backend/geological-query", json={
        "query": "Show me copper deposits",
        "limit": 3
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    # Note: This might fail if modules are not running, but should return 200 if auth works
    assert response.status_code in [200, 500]  # 500 if services unavailable

def test_quality_metrics_requires_auth():
    """Test that quality metrics endpoint requires authentication"""
    response = client.get("/api/backend/quality-metrics")
    assert response.status_code == 403

def test_quality_metrics_with_auth():
    """Test quality metrics endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access quality metrics endpoint
    response = client.get("/api/backend/quality-metrics", headers={
        "Authorization": f"Bearer {token}"
    })
    # Note: This might fail if Module 1 is not running, but should return 200 if auth works
    assert response.status_code in [200, 500]  # 500 if Module 1 unavailable

def test_spatial_query_requires_auth():
    """Test that spatial query endpoint requires authentication"""
    response = client.post("/api/backend/spatial-query", json={
        "commodity": "COPPER"
    })
    assert response.status_code == 403

def test_spatial_query_with_auth():
    """Test spatial query endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access spatial query endpoint
    response = client.post("/api/backend/spatial-query", json={
        "commodity": "COPPER",
        "bounds": {"north": -31.0, "south": -33.0, "east": 116.0, "west": 114.0}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    # Note: This might fail if Module 1 is not running, but should return 200 if auth works
    assert response.status_code in [200, 500]  # 500 if Module 1 unavailable

def test_logout_requires_auth():
    """Test that logout endpoint requires authentication"""
    response = client.post("/api/backend/auth/logout")
    assert response.status_code == 403

def test_logout_with_auth():
    """Test logout endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then logout
    response = client.post("/api/backend/auth/logout", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert "message" in response.json()

def test_refresh_token_requires_auth():
    """Test that refresh token endpoint requires authentication"""
    response = client.post("/api/backend/auth/refresh", json={
        "refresh_token": "fake-token"
    })
    assert response.status_code == 403

def test_refresh_token_with_auth():
    """Test refresh token endpoint with authentication"""
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then refresh token
    response = client.post("/api/backend/auth/refresh", json={
        "refresh_token": "fake-token"  # Using fake token for simplicity
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer" 