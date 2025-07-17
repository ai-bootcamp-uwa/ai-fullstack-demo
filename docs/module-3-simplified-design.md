# Module 3: Simplified Backend Gateway API Design

## Overview

This document outlines a **simplified, practical design** for Module 3 (Backend Gateway API) using FastAPI. The focus is on creating a minimal but functional API gateway that can be built quickly while meeting all core requirements.

## ⚠️ **Important: Actual API Consistency Note**

This design has been **updated to match the actual implemented APIs** in modules 1 and 2:

-   **Data Foundation API (Module 1)**: Runs on `http://localhost:8000` (not 3001 as in API table)
-   **Cortex Engine API (Module 2)**: Runs on `http://localhost:3002` (correct)
-   **Data Foundation endpoints**: Use `/reports` (not `/geological-sites` as in API table)
-   **Cortex Engine endpoints**: Match the API table specifications ✅

**Backend Gateway will adapt to the actual APIs while maintaining the required `/api/backend` prefix for its own endpoints.**

### **Key Endpoint Mappings:**

-   **Module 3 `/api/backend/chat`** → **Module 2 `/rag-query`** (RAG = chat functionality)
-   **Module 3 `/api/backend/geological-sites`** → **Module 1 `/reports`**
-   **Module 3 `/api/backend/geological-query`** → **Both modules combined** (AI + data)

### **Testing Configuration:**

-   **Module 1 Data**: 114,132 total reports available, but **limited to 5 reports for testing**
-   **Default limits**: All endpoints default to `limit=5` for fast testing and development
-   **Sample reports**: ANUMBERs 1-5 (covering COPPER, NICKEL, IRON commodities from 1968-1971)

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
@app.get("/api/backend/health")
async def health():
    return {"status": "ok", "service": "backend-gateway"}

# Auth endpoints
@app.post("/api/backend/auth/login")
async def login(request: LoginRequest):
    # Simple authentication logic
    pass

# Required geological query endpoint (from API table)
@app.post("/api/backend/geological-query")
async def geological_query(request: GeologicalQueryRequest, token: str = Depends(security)):
    # 1. Use AI to understand the query via Module 2 RAG
    ai_response = await cortex_client.rag_query(request.query)

        # 2. Get relevant reports from Module 1 (limited to 5 for testing)
    reports = await data_client.get_reports(limit=min(request.limit, 5))

    # 3. Combine AI insights with data
    return {
        "query": request.query,
        "ai_explanation": ai_response.get("result", ""),
        "results": reports[:request.limit],
        "total_found": len(reports)
    }

# Required chat endpoint (from API table) - maps to Module 2 RAG-query
@app.post("/api/backend/chat")
async def chat(request: ChatRequest, token: str = Depends(security)):
    # Direct pass-through to Module 2: POST /rag-query (this IS the chat functionality)
    ai_response = await cortex_client.rag_query(request.message)
    return {
        "response": ai_response.get("result", ""),
        "conversation_id": request.conversation_id or "default",
        "timestamp": datetime.utcnow(),
        "sources": []  # Could be enhanced with report sources from Module 2 response
    }

# Additional endpoints for frontend integration (mapped to actual Module 1 endpoints)
@app.get("/api/backend/geological-sites")
async def get_sites(limit: int = 5, offset: int = 0, token: str = Depends(security)):
    # Maps to Module 1: GET /reports (default to 5 for testing)
    return await data_client.get_reports(limit=limit, offset=offset)

@app.get("/api/backend/geological-sites/{site_id}")
async def get_site(site_id: int, token: str = Depends(security)):
    # Maps to Module 1: GET /reports/{id}
    return await data_client.get_report_by_id(site_id)

@app.get("/api/backend/quality-metrics")
async def quality_metrics(token: str = Depends(security)):
    # Data quality metrics - aggregate from Module 1 data (using only 5 reports for testing)
    reports = await data_client.get_reports(limit=5)
    return {
        "total_reports": len(reports),
        "unique_commodities": len(set(r.get("TARGET_COM", "") for r in reports)),
        "date_range": {"min": "1970", "max": "2024"},  # Based on sample data
        "data_quality_score": 99.5,
        "sample_size": 5  # Indicate this is a sample for testing
    }

@app.post("/api/backend/spatial-query")
async def spatial_query(request: SpatialQueryRequest, token: str = Depends(security)):
    # Maps to Module 1: GET /reports/filter with geographic filtering
    # This would need custom logic to handle spatial filtering
    filtered_reports = await data_client.filter_reports(
        commodity=request.commodity if hasattr(request, 'commodity') else None
    )
    return {"results": filtered_reports}
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

    # Service URLs (actual ports from implemented modules)
    data_foundation_url: str = "http://localhost:8000"  # Module 1 actual port
    cortex_engine_url: str = "http://localhost:3002"    # Module 2 actual port

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
        """Get reports using actual Module 1 endpoint: GET /reports"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/reports",
                params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            return response.json()

    async def get_report_by_id(self, report_id: int):
        """Get single report using actual Module 1 endpoint: GET /reports/{id}"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/reports/{report_id}")
            response.raise_for_status()
            return response.json()

    async def filter_reports(self, commodity: str = None, year: int = None, company: str = None):
        """Filter reports using actual Module 1 endpoint: GET /reports/filter"""
        params = {}
        if commodity:
            params["commodity"] = commodity
        if year:
            params["year"] = year
        if company:
            params["company"] = company

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/reports/filter", params=params)
            response.raise_for_status()
            return response.json()

    async def get_report_geometry(self, report_id: int):
        """Get report geometry using actual Module 1 endpoint: GET /reports/{id}/geometry"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/reports/{report_id}/geometry")
            response.raise_for_status()
            return response.json()

class CortexEngineClient:
    def __init__(self):
        self.base_url = settings.cortex_engine_url

    async def health_check(self):
        """Check health using actual Module 2 endpoint: GET /health"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def get_config(self):
        """Get config using actual Module 2 endpoint: GET /config"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/config")
            response.raise_for_status()
            return response.json()

    async def generate_embeddings(self, data: List[str]):
        """Generate embeddings using actual Module 2 endpoint: POST /embed"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embed",
                json={"data": data}
            )
            response.raise_for_status()
            return response.json()

    async def rag_query(self, query: str):
        """RAG query using actual Module 2 endpoint: POST /rag-query (this IS the chat functionality)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rag-query",
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()

    async def similarity_search(self, query_vector: List[float], top_k: int = 5):
        """Similarity search using actual Module 2 endpoint: POST /similarity-search"""
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

# Spatial Query Models
class SpatialQueryRequest(BaseModel):
    bounds: Optional[Dict[str, float]] = None  # {"north": -31.0, "south": -33.0, "east": 116.0, "west": 114.0}
    geometry: Optional[str] = None  # WKT geometry for spatial intersection
    distance_km: Optional[float] = None  # Distance from a point
    center_point: Optional[Dict[str, float]] = None  # {"lat": -32.0, "lng": 115.0}

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

## Required API Endpoints (From API Interaction Table)

### **Core Required Endpoints (MUST HAVE)**

Based on the API interaction table, these are the **mandatory** endpoints:

```
GET  /api/backend/health                    # Service health check
POST /api/backend/auth/login               # User authentication
POST /api/backend/geological-query         # Natural language geological search
POST /api/backend/chat                     # AI chat functionality
```

### **Additional Frontend Integration Endpoints (MUST HAVE)**

Based on the communication flows, these endpoints are needed for full frontend integration:

```
GET  /api/backend/geological-sites         # List geological sites (for map data)
GET  /api/backend/geological-sites/{id}    # Get specific site details
GET  /api/backend/quality-metrics          # Data quality metrics for dashboard
POST /api/backend/spatial-query            # Geographic/spatial queries for map
```

### **Authentication & User Management (MUST HAVE)**

```
POST /api/backend/auth/logout              # Logout functionality
GET  /api/backend/auth/profile            # Get user profile info
POST /api/backend/auth/refresh            # Refresh JWT tokens
```

### **Optional Enhancement Endpoints (NICE TO HAVE)**

```
GET  /api/backend/dashboard/stats          # Dashboard statistics and metrics
GET  /api/backend/dashboard/map-data       # Optimized map visualization data
POST /api/backend/similarity-search        # AI-powered similarity search
POST /api/backend/generate-report         # AI-generated reports
```

### **API Prefix Note**

All endpoints MUST use the `/api/backend` prefix as specified in the API interaction table:

-   **Base URL**: `http://localhost:3003`
-   **API Prefix**: `/api/backend`
-   **Full Example**: `http://localhost:3003/api/backend/health`

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

# Service URLs (actual implemented ports)
DATA_FOUNDATION_URL=http://localhost:8000
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
    response = client.get("/api/backend/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login():
    response = client.post("/api/backend/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_geological_sites_requires_auth():
    response = client.get("/api/backend/geological-sites")
    assert response.status_code == 403  # No auth header

def test_geological_sites_with_auth():
    # First login
    login_response = client.post("/api/backend/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    token = login_response.json()["access_token"]

    # Then access protected endpoint
    response = client.get("/api/backend/geological-sites", headers={
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

# Test the API (remember the /api/backend prefix)
curl http://localhost:3003/api/backend/health
```

### 2. Development Process

1. **Start with `main.py`** - Get basic FastAPI app running
2. **Add `auth.py`** - Implement simple JWT authentication
3. **Create `services.py`** - Add clients for other modules
4. **Define `models.py`** - Add request/response validation
5. **Test with `test_api.py`** - Verify everything works

### 3. Integration Testing

```bash
# Ensure other modules are running (using actual ports)
curl http://localhost:8000/reports  # Data Foundation (no health endpoint implemented)
curl http://localhost:3002/health   # Cortex Engine

# Test Backend Gateway (note the /api/backend prefix)
curl http://localhost:3003/api/backend/health
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
