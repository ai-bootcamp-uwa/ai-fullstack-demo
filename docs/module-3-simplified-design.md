# Module 3: Simplified Backend Gateway API Design

## Overview

This document outlines a **simplified, practical design** for Module 3 (Backend Gateway API) using FastAPI. The focus is on creating a minimal but functional API gateway that can be built quickly while meeting all core requirements.

## Design Principles

1. **Keep it Simple** - Minimal directory structure, essential files only
2. **Fast Development** - Quick to implement and understand
3. **Easy Testing** - Simple test structure
4. **Clear Separation** - Clean boundaries between concerns
5. **Practical Over Perfect** - Working solution over theoretical perfection

## Simplified Directory Structure

```
backend_gateway/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration settings
├── auth.py                    # Authentication logic
├── services.py                # External service clients
├── models.py                  # Pydantic models
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── README.md                 # Setup instructions
├── test_api.py               # Simple API tests
└── Dockerfile                # Container deployment
```

**Total: 9 files** (compared to 20+ in complex structure)

## Core Components

### 1. `main.py` - FastAPI Application

**Purpose**: Main application with all route definitions
**Why Simple**: All endpoints in one file for easy navigation

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
import httpx
from auth import verify_token
from services import DataFoundationClient, CortexEngineClient
from models import *

app = FastAPI(title="Backend Gateway API")
security = HTTPBearer()

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "service": "backend-gateway"}

# Auth endpoints
@app.post("/auth/login")
async def login(request: LoginRequest):
    # Simple authentication logic
    pass

# Geological data endpoints
@app.get("/geological-sites")
async def get_sites(token: str = Depends(security)):
    # Aggregate data from multiple sources
    pass

# AI endpoints
@app.post("/chat")
async def chat(request: ChatRequest, token: str = Depends(security)):
    # Chat with AI using Cortex Engine
    pass
```

### 2. `config.py` - Configuration Management

**Purpose**: Centralized configuration with environment variables
**Why Simple**: Single file for all settings

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Server
    host: str = "localhost"
    port: int = 3003
    debug: bool = True

    # Authentication
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 30

    # Service URLs
    data_foundation_url: str = "http://localhost:3001"
    cortex_engine_url: str = "http://localhost:3002"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. `auth.py` - Authentication Logic

**Purpose**: JWT token handling and user authentication
**Why Simple**: Basic JWT implementation without complex role systems

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from config import settings

# Simple user database (in production, use real database)
USERS_DB = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "user": {"username": "user", "password": "user123", "role": "user"}
}

def authenticate_user(username: str, password: str):
    user = USERS_DB.get(username)
    if user and user["password"] == password:
        return user
    return None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 4. `services.py` - External Service Clients

**Purpose**: Simple HTTP clients for Data Foundation and Cortex Engine APIs
**Why Simple**: Basic httpx clients without complex abstractions

```python
import httpx
from typing import List, Dict, Any
from config import settings

class DataFoundationClient:
    def __init__(self):
        self.base_url = settings.data_foundation_url

    async def get_reports(self, limit: int = 10, offset: int = 0):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/reports",
                params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            return response.json()

    async def get_report_by_id(self, report_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/reports/{report_id}")
            response.raise_for_status()
            return response.json()

class CortexEngineClient:
    def __init__(self):
        self.base_url = settings.cortex_engine_url

    async def chat_query(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rag-query",
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()

    async def similarity_search(self, query_vector: List[float], top_k: int = 5):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/similarity-search",
                json={"query_vector": query_vector, "top_k": top_k}
            )
            response.raise_for_status()
            return response.json()

# Global instances
data_client = DataFoundationClient()
cortex_client = CortexEngineClient()
```

### 5. `models.py` - Pydantic Models

**Purpose**: Request/response models for API validation
**Why Simple**: Only essential models, no complex inheritance

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# Geological Data Models
class GeologicalSite(BaseModel):
    site_id: str
    name: str
    commodity: List[str]
    operator: str
    report_year: int
    location: Dict[str, float]  # {"lat": -32.1, "lng": 115.8}

class GeologicalQueryRequest(BaseModel):
    query: str
    limit: int = 10
    include_ai_insights: bool = True

# Chat Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime

# Standard Response Models
class HealthResponse(BaseModel):
    status: str
    service: str
    dependencies: Optional[Dict[str, str]] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
```

## Simplified API Endpoints (Essential Only)

### Core Endpoints (Must Have)

```
GET  /health                    # Service health check
POST /auth/login               # User authentication
GET  /geological-sites         # List geological sites (with auth)
GET  /geological-sites/{id}    # Get specific site (with auth)
POST /chat                     # AI chat functionality (with auth)
```

### Optional Endpoints (Nice to Have)

```
POST /auth/logout              # Logout (clear token client-side)
GET  /dashboard/stats          # Dashboard statistics
POST /geological-query         # Natural language search
```

## Dependencies (Minimal)

### `requirements.txt`

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.2
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
pytest==7.4.3
pytest-asyncio==0.21.1
```

**Total: 8 dependencies** (vs 13+ in complex version)

## Environment Configuration

### `.env.example`

```
# Server Configuration
HOST=localhost
PORT=3003
DEBUG=true

# Authentication
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=30

# Service URLs
DATA_FOUNDATION_URL=http://localhost:3001
CORTEX_ENGINE_URL=http://localhost:3002

# CORS (for frontend)
ALLOWED_ORIGINS=["http://localhost:3004"]
```

## Simple Testing Strategy

### `test_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login():
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_geological_sites_requires_auth():
    response = client.get("/geological-sites")
    assert response.status_code == 403  # No auth header

def test_geological_sites_with_auth():
    # First login
    login_response = client.post("/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access protected endpoint
    response = client.get("/geological-sites", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
```

## Development Workflow

### 1. Quick Start (5 minutes)

```bash
# Clone and setup
git checkout liam-module-3
cd backend_gateway

# Install dependencies
pip install -r requirements.txt

# Copy environment
cp .env.example .env

# Run the server
uvicorn main:app --reload --port 3003
```

### 2. Development Process

1. **Start with `main.py`** - Get basic FastAPI app running
2. **Add `auth.py`** - Implement simple JWT authentication
3. **Create `services.py`** - Add clients for other modules
4. **Define `models.py`** - Add request/response validation
5. **Test with `test_api.py`** - Verify everything works

### 3. Integration Testing

```bash
# Ensure other modules are running
curl http://localhost:3001/health  # Data Foundation
curl http://localhost:3002/health  # Cortex Engine

# Test Backend Gateway
curl http://localhost:3003/health
```

## Key Benefits of Simplified Design

### 🚀 **Development Speed**

-   **Single day implementation** for core functionality
-   **Easy to understand** - all code in 5 main files
-   **Quick debugging** - minimal layers and abstractions

### 🧪 **Testing Simplicity**

-   **One test file** covers all functionality
-   **Easy mocking** - simple service clients
-   **Fast test execution** - minimal setup required

### 📦 **Deployment Ease**

-   **Single container** with minimal dependencies
-   **Simple configuration** - just environment variables
-   **Easy scaling** - stateless design

### 🔧 **Maintenance**

-   **Clear file organization** - know where everything is
-   **Minimal dependencies** - fewer security updates
-   **Easy refactoring** - simple structure to modify

## Success Metrics

### Functional Goals

-   ✅ **5 core endpoints working** within 1 day
-   ✅ **Authentication functional** with JWT tokens
-   ✅ **Integration with both modules** successful
-   ✅ **Basic error handling** implemented

### Performance Goals

-   ✅ **<200ms response time** for all endpoints
-   ✅ **Handles 10+ concurrent users** (sufficient for demo)
-   ✅ **Reliable service integration** with proper error handling

### Development Goals

-   ✅ **Complete implementation** in 1-2 days
-   ✅ **Easy to understand** by other team members
-   ✅ **Simple to test and debug**
-   ✅ **Ready for frontend integration**

## Future Expansion Path

If needed later, the simple structure can be expanded:

1. **Add database** - Move from in-memory to SQLite/PostgreSQL
2. **Add middleware** - Rate limiting, CORS, logging
3. **Split files** - Move routes to separate modules
4. **Add caching** - Redis for frequently accessed data
5. **Advanced auth** - Role-based permissions, OAuth

But for the bootcamp project, the simplified version provides everything needed while being **fast to build and easy to understand**.

---

This simplified design focuses on **getting Module 3 working quickly** while maintaining clean code and proper architecture. It's practical, testable, and ready for real-world use! 🚀
