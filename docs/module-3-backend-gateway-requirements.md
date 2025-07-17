# Module 3: Backend Gateway API Requirements Document

## Overview

Module 3 is the **Backend Gateway API** that serves as the central orchestration layer for the Full Stack AI Engineer Bootcamp project. It acts as the primary integration point between the frontend application and the backend services (Data Foundation API and AI/Cortex Engine API), providing business logic, authentication, and unified data access.

## Project Information

-   **Module Name**: Backend Gateway API
-   **Base URL**: `http://localhost:3003`
-   **API Prefix**: `/api/backend`
-   **Port**: 3003
-   **Role**: Business logic & integration orchestration
-   **Technology Stack**: FastAPI, Python, JWT Authentication

## System Architecture Position

```
Frontend UI (3004) → Backend Gateway (3003) → Data Foundation API (3001)
                                     ↓
                              AI/Cortex Engine API (3002)
```

The Backend Gateway API is the **central hub** that:

-   Authenticates and authorizes users
-   Orchestrates calls to multiple backend services
-   Implements business logic and data transformation
-   Provides a unified API interface for the frontend

## API Dependencies

### Consumes (Calls)

-   **Data Foundation API** (`http://localhost:3001`) - Geological data retrieval
-   **AI/Cortex Engine API** (`http://localhost:3002`) - AI processing and embeddings
-   **Authentication Service** - User authentication and JWT management

### Consumed By (Serves)

-   **Frontend UI Application** (`http://localhost:3004`) - Primary consumer
-   **External clients** - API consumers
-   **Monitoring services** - Health checks and metrics

## Core Requirements

### 1. Authentication & Security

-   **JWT-based authentication** with secure token management
-   **Role-based access control** for different user types
-   **API key management** for external service access
-   **Rate limiting** to prevent abuse
-   **CORS configuration** for frontend integration

### 2. Business Logic Layer

-   **Data aggregation** from multiple sources
-   **Business rule enforcement** for geological data access
-   **Data validation and transformation** before serving to frontend
-   **Error handling and user-friendly error messages**

### 3. Integration Orchestration

-   **Service discovery** and health checking of dependent APIs
-   **Circuit breaker pattern** for resilient service calls
-   **Request/response transformation** between services
-   **Caching layer** for frequently accessed data

### 4. Performance Requirements

-   **<200ms API response time** (as specified in requirements)
-   **Support for 50+ concurrent users**
-   **Efficient connection pooling** to backend services
-   **Asynchronous processing** for heavy operations

## API Endpoints Specification

### Health & Configuration

```
GET /health
- Returns: Service health status and dependency health
- Response: {"status": "ok", "dependencies": {...}, "version": "1.0.0"}

GET /config
- Returns: Non-sensitive configuration information
- Response: {"services": {...}, "features": {...}}
```

### Authentication Endpoints

```
POST /auth/login
- Request: {"username": "string", "password": "string"}
- Response: {"access_token": "jwt_token", "token_type": "bearer", "expires_in": 3600}

POST /auth/logout
- Request: Authorization header with JWT
- Response: {"message": "Successfully logged out"}

GET /auth/profile
- Request: Authorization header with JWT
- Response: {"user_id": "string", "username": "string", "roles": [...]}

POST /auth/refresh
- Request: {"refresh_token": "string"}
- Response: {"access_token": "jwt_token", "expires_in": 3600}
```

### Geological Data Endpoints

```
GET /geological-sites
- Query params: limit, offset, commodity, year, company
- Response: Aggregated data from Data Foundation API with enrichment
- Example: {"sites": [...], "total_count": 12500, "metadata": {...}}

GET /geological-sites/{site_id}
- Response: Detailed site information with AI-generated insights
- Example: {"site": {...}, "ai_summary": "string", "similar_sites": [...]}

POST /geological-query
- Request: {"query": "natural language query", "filters": {...}}
- Response: Intelligent search results using AI/Cortex Engine
- Example: {"results": [...], "ai_explanation": "string", "confidence": 0.85}
```

### AI-Powered Features

```
POST /chat
- Request: {"message": "string", "conversation_id": "uuid"}
- Response: {"response": "string", "sources": [...], "conversation_id": "uuid"}

POST /similarity-search
- Request: {"query": "string", "type": "geological|company|commodity"}
- Response: {"matches": [...], "scores": [...], "metadata": {...}}

POST /generate-report
- Request: {"site_ids": [...], "report_type": "summary|detailed"}
- Response: {"report_id": "uuid", "status": "processing|completed", "download_url": "string"}
```

### Data Aggregation Endpoints

```
GET /dashboard/stats
- Response: Dashboard metrics aggregated from multiple sources
- Example: {"total_sites": 12500, "active_projects": 45, "recent_activity": [...]}

GET /dashboard/map-data
- Query params: bounds, zoom_level, filters
- Response: Optimized geographic data for map visualization
- Example: {"features": [...], "clusters": [...], "bounds": {...}}
```

## Technical Implementation Details

### Project Structure

```
backend_gateway/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app and route definitions
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py          # User and authentication models
│   │   ├── handlers.py        # Authentication logic
│   │   └── middleware.py      # JWT middleware
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_foundation.py # Data Foundation API client
│   │   ├── cortex_engine.py   # AI/Cortex Engine API client
│   │   └── aggregation.py     # Business logic and data aggregation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py        # Pydantic request models
│   │   ├── responses.py       # Pydantic response models
│   │   └── database.py        # Database models (if needed)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── logging.py         # Logging configuration
│   │   └── cache.py           # Caching utilities
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py            # CORS configuration
│       ├── rate_limit.py      # Rate limiting
│       └── error_handler.py   # Global error handling
├── tests/
│   ├── test_auth.py
│   ├── test_services.py
│   ├── test_endpoints.py
│   └── test_integration.py
├── requirements.txt
├── setup.py
├── .env.example
├── README.md
├── API_DOCUMENTATION.md
└── DEPLOYMENT.md
```

### Dependencies (requirements.txt)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
httpx>=0.25.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
redis>=4.5.0  # For caching
sqlalchemy>=2.0.0  # If database needed
alembic>=1.12.0  # For database migrations
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-httpx>=0.22.0
```

### Environment Configuration

```
# Server Configuration
HOST=localhost
PORT=3003
DEBUG=True
LOG_LEVEL=INFO

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Service URLs
DATA_FOUNDATION_URL=http://localhost:3001
CORTEX_ENGINE_URL=http://localhost:3002

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379/0

# Database (if needed)
DATABASE_URL=sqlite:///./backend_gateway.db

# CORS
ALLOWED_ORIGINS=["http://localhost:3004", "http://localhost:3000"]
```

## Data Models

### Request Models

```python
class LoginRequest(BaseModel):
    username: str
    password: str

class GeologicalQueryRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    include_ai_summary: bool = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    include_sources: bool = True

class SimilaritySearchRequest(BaseModel):
    query: str
    search_type: str = "geological"  # geological, company, commodity
    top_k: int = 5
```

### Response Models

```python
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]

class GeologicalSiteResponse(BaseModel):
    site_id: str
    name: str
    location: Dict[str, float]  # lat, lng
    commodity: List[str]
    operator: str
    report_year: int
    geometry: str  # WKT format
    ai_summary: Optional[str] = None
    metadata: Dict[str, Any]

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[Dict[str, Any]]
    confidence: float
    timestamp: datetime
```

## Integration Patterns

### Data Foundation API Integration

```python
class DataFoundationService:
    async def get_reports(self, limit: int, filters: Dict) -> List[Dict]:
        # Call Data Foundation API and transform response

    async def get_report_by_id(self, report_id: str) -> Dict:
        # Get detailed report with error handling

    async def filter_reports(self, **filters) -> List[Dict]:
        # Advanced filtering with business logic
```

### AI/Cortex Engine Integration

```python
class CortexEngineService:
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Generate embeddings for similarity search

    async def rag_query(self, query: str, context: List[str]) -> str:
        # Intelligent query processing

    async def similarity_search(self, query_vector: List[float]) -> List[Dict]:
        # Find similar geological features
```

## Security Implementation

### JWT Authentication

-   **Access tokens** with 30-minute expiration
-   **Refresh tokens** with 7-day expiration
-   **Role-based permissions** (admin, geologist, viewer)
-   **API key authentication** for service-to-service calls

### Rate Limiting

-   **100 requests/minute per user** for authenticated endpoints
-   **20 requests/minute per IP** for public endpoints
-   **Special limits for AI endpoints** (10 requests/minute for RAG queries)

### Input Validation

-   **Pydantic models** for all request/response validation
-   **SQL injection prevention** through parameterized queries
-   **XSS protection** for text inputs
-   **File upload validation** if needed

## Testing Strategy

### Unit Tests

-   **Service layer testing** with mocked dependencies
-   **Authentication logic testing**
-   **Business logic validation**
-   **Error handling verification**

### Integration Tests

-   **End-to-end API testing** with real dependencies
-   **Service integration testing**
-   **Database transaction testing**
-   **Authentication flow testing**

### Performance Tests

-   **Load testing** for 50+ concurrent users
-   **Response time validation** (<200ms requirement)
-   **Memory usage monitoring**
-   **Database query optimization**

## Error Handling Strategy

### Standard Error Responses

```python
class APIError(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str

# Example error responses:
{
    "error": "AUTHENTICATION_FAILED",
    "message": "Invalid credentials provided",
    "details": null,
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
}
```

### Error Categories

-   **400 Bad Request**: Invalid input data
-   **401 Unauthorized**: Authentication required
-   **403 Forbidden**: Insufficient permissions
-   **404 Not Found**: Resource not found
-   **422 Unprocessable Entity**: Validation errors
-   **500 Internal Server Error**: Service errors
-   **502 Bad Gateway**: Dependency service errors
-   **503 Service Unavailable**: Service overload

## Monitoring & Observability

### Health Checks

-   **Startup health checks** for all dependencies
-   **Periodic health monitoring** of Data Foundation and Cortex Engine APIs
-   **Database connectivity checks**
-   **Cache service availability**

### Metrics Collection

-   **Request/response times** for all endpoints
-   **Error rates** by endpoint and error type
-   **Authentication success/failure rates**
-   **Dependency service response times**

### Logging Strategy

-   **Structured logging** with JSON format
-   **Request correlation IDs** for tracing
-   **User action logging** for audit trails
-   **Performance metrics logging**

## Deployment Requirements

### Development Environment

```bash
# Start all dependencies
docker-compose up data-foundation cortex-engine

# Start Backend Gateway
uvicorn main:app --reload --port 3003 --host localhost
```

### Production Considerations

-   **Container deployment** with Docker
-   **Environment variable management**
-   **SSL/TLS termination**
-   **Load balancing** for multiple instances
-   **Database connection pooling**
-   **Redis cluster** for caching

## Success Criteria

### Functional Requirements

-   ✅ **All API endpoints respond correctly** with proper status codes
-   ✅ **Authentication system works** with JWT tokens
-   ✅ **Data aggregation functions properly** from multiple sources
-   ✅ **AI features are accessible** through the gateway
-   ✅ **Error handling is comprehensive** and user-friendly

### Performance Requirements

-   ✅ **<200ms API response time** for standard endpoints
-   ✅ **Support for 50+ concurrent users** without degradation
-   ✅ **High availability** with proper error recovery
-   ✅ **Efficient resource usage** with connection pooling

### Integration Requirements

-   ✅ **Data Foundation API integration** working seamlessly
-   ✅ **AI/Cortex Engine API integration** providing intelligent features
-   ✅ **Frontend UI compatibility** with all required endpoints
-   ✅ **Cross-API communication** functioning properly

### Security Requirements

-   ✅ **JWT authentication working** with proper token management
-   ✅ **Rate limiting enforced** to prevent abuse
-   ✅ **Input validation comprehensive** against common attacks
-   ✅ **CORS properly configured** for frontend access

## Future Enhancements

### Phase 2 Features

-   **WebSocket support** for real-time updates
-   **Advanced caching strategies** with Redis
-   **Background job processing** for heavy operations
-   **Advanced analytics** and reporting features

### Phase 3 Features

-   **GraphQL API** for flexible data querying
-   **API versioning** for backward compatibility
-   **Advanced monitoring** with APM tools
-   **Machine learning model serving** integration

## Getting Started

### 1. Environment Setup

```bash
# Clone the repository
git checkout liam-module-3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Set JWT_SECRET_KEY, service URLs, etc.
```

### 3. Development Workflow

```bash
# Start development server
uvicorn main:app --reload --port 3003

# Run tests
pytest

# Check API documentation
# Visit http://localhost:3003/docs
```

### 4. Integration Testing

```bash
# Ensure dependencies are running
curl http://localhost:3001/health  # Data Foundation
curl http://localhost:3002/health  # Cortex Engine

# Test Backend Gateway
curl http://localhost:3003/health
```

## Documentation References

-   **API Interaction Matrix**: `docs/api_interaction_table (1).md`
-   **Data Foundation API**: `data_foundation_project/src/api/main.py`
-   **Cortex Engine API**: `cortex_engine/src/main.py`
-   **System Architecture**: `docs/ai-engineer-bootcamp-summary.md`

---

This requirements document provides a comprehensive foundation for implementing Module 3 (Backend Gateway API) that integrates seamlessly with the existing Data Foundation API (Module 1) and AI/Cortex Engine API (Module 2) while providing the business logic and orchestration layer needed for the full-stack AI application.
