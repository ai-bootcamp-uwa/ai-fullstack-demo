# Backend Gateway API - Module 3

## Overview

The Backend Gateway API (Module 3) serves as the central API gateway for the geological data system, integrating with:

-   **Module 1**: Data Foundation API (Port 8000) - Geological reports and data
-   **Module 2**: Cortex Engine API (Port 3002) - AI/ML services and RAG queries

## 📁 Project Structure

```
backend_gateway/
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── api/                      # API endpoints and routes
│   │   ├── __init__.py
│   │   └── main.py              # FastAPI application and endpoints
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration and settings
│   │   └── auth.py              # Authentication and security
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── requests.py          # Request models
│   │   └── responses.py         # Response models
│   ├── services/                 # External service clients
│   │   ├── __init__.py
│   │   ├── data_client.py       # Module 1 integration
│   │   └── cortex_client.py     # Module 2 integration
│   └── tests/                    # Test modules
│       ├── __init__.py
│       ├── test_api.py          # API endpoint tests
│       └── test_startup.py      # Startup integration tests
├── main.py                       # Application entry point
├── requirements.txt              # Dependencies
├── Dockerfile                    # Docker configuration
└── README.md                     # This file
```

## Quick Start

### 1. Installation

```bash
# Navigate to the backend gateway directory
cd backend_gateway

# Install dependencies
pip install -r requirements.txt

# Copy environment template (if needed)
cp .env.example .env

# (Optional) Edit .env with your preferred settings
```

### 2. Start the Server

```bash
# Start the FastAPI server
uvicorn main:app --reload --port 3003

# Or run directly
python main.py
```

The API will be available at: `http://localhost:3003`

### 3. API Documentation

-   **Interactive Docs**: http://localhost:3003/docs
-   **ReDoc**: http://localhost:3003/redoc
-   **Health Check**: http://localhost:3003/api/backend/health

## API Endpoints

### Authentication

| Method | Endpoint                    | Description       | Auth Required |
| ------ | --------------------------- | ----------------- | ------------- |
| POST   | `/api/backend/auth/login`   | User login        | No            |
| POST   | `/api/backend/auth/logout`  | User logout       | Yes           |
| GET    | `/api/backend/auth/profile` | Get user profile  | Yes           |
| POST   | `/api/backend/auth/refresh` | Refresh JWT token | Yes           |

### Core Functionality

| Method | Endpoint                        | Description                  | Auth Required |
| ------ | ------------------------------- | ---------------------------- | ------------- |
| GET    | `/api/backend/health`           | Service health check         | No            |
| POST   | `/api/backend/geological-query` | AI-powered geological search | Yes           |
| POST   | `/api/backend/chat`             | AI chat interface            | Yes           |

### Data Access

| Method | Endpoint                             | Description                | Auth Required |
| ------ | ------------------------------------ | -------------------------- | ------------- |
| GET    | `/api/backend/geological-sites`      | List geological sites      | Yes           |
| GET    | `/api/backend/geological-sites/{id}` | Get specific site          | Yes           |
| GET    | `/api/backend/quality-metrics`       | Data quality metrics       | Yes           |
| POST   | `/api/backend/spatial-query`         | Geographic/spatial queries | Yes           |

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Default users:

| Username | Password | Role  |
| -------- | -------- | ----- |
| admin    | admin123 | admin |
| user     | user123  | user  |
| demo     | demo123  | user  |

### Example Authentication Flow

```bash
# 1. Login to get token
curl -X POST "http://localhost:3003/api/backend/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer", "expires_in": 1800}

# 2. Use token for protected endpoints
curl -X GET "http://localhost:3003/api/backend/geological-sites" \
  -H "Authorization: Bearer eyJ..."
```

## Development

### Project Architecture

The project follows a modular architecture with clear separation of concerns:

-   **`src/core/`**: Core functionality (config, auth)
-   **`src/api/`**: API endpoints and route handlers
-   **`src/models/`**: Pydantic data models
-   **`src/services/`**: External service integration
-   **`src/tests/`**: Test modules

### Running Tests

```bash
# Run all tests
pytest src/tests/ -v

# Run specific test module
pytest src/tests/test_api.py -v

# Run startup integration test
python src/tests/test_startup.py
```

### Code Organization Benefits

1. **Clear Separation**: Each module has a specific responsibility
2. **Easy Testing**: Tests are organized by functionality
3. **Maintainable**: Related code is grouped together
4. **Scalable**: Easy to add new features in appropriate modules
5. **Professional**: Follows Python package conventions

## API Usage Examples

### 1. Health Check

```bash
curl "http://localhost:3003/api/backend/health"
```

### 2. Geological Query (AI-powered)

```bash
# Login first
TOKEN=$(curl -X POST "http://localhost:3003/api/backend/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.access_token')

# Geological query
curl -X POST "http://localhost:3003/api/backend/geological-query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find copper deposits in Western Australia",
    "limit": 5,
    "include_ai_insights": true
  }'
```

### 3. Chat Interface

```bash
curl -X POST "http://localhost:3003/api/backend/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main copper mining regions in Australia?",
    "conversation_id": "session-123"
  }'
```

### 4. Get Geological Sites

```bash
curl -X GET "http://localhost:3003/api/backend/geological-sites?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

## Dependencies

This module integrates with:

### Module 1 - Data Foundation API (Port 8000)

-   **Endpoint**: `http://localhost:8000`
-   **Purpose**: Geological reports and data
-   **Required endpoints**:
    -   `GET /reports`
    -   `GET /reports/{id}`
    -   `GET /reports/filter`
    -   `GET /reports/{id}/geometry`

### Module 2 - Cortex Engine API (Port 3002)

-   **Endpoint**: `http://localhost:3002`
-   **Purpose**: AI/ML services and RAG queries
-   **Required endpoints**:
    -   `GET /health`
    -   `GET /config`
    -   `POST /embed`
    -   `POST /rag-query`
    -   `POST /similarity-search`

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Server Configuration
HOST=localhost
PORT=3003
DEBUG=true

# Authentication
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=30

# Service URLs
DATA_FOUNDATION_URL=http://localhost:8000
CORTEX_ENGINE_URL=http://localhost:3002

# CORS
ALLOWED_ORIGINS=["http://localhost:3004"]
```

## Comprehensive Testing

### Automated Tests

```bash
# Run unit tests
pytest src/tests/test_api.py -v

# Test specific functionality
pytest src/tests/test_api.py::test_login_success -v
pytest src/tests/test_api.py::test_geological_query_with_auth -v
```

### Integration Testing

```bash
# Run full integration test
python src/tests/test_startup.py

# Manual endpoint testing
TOKEN=$(curl -s -X POST "http://localhost:3003/api/backend/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.access_token')

# Test protected endpoints
curl -H "Authorization: Bearer $TOKEN" "http://localhost:3003/api/backend/auth/profile"
curl -H "Authorization: Bearer $TOKEN" "http://localhost:3003/api/backend/geological-sites?limit=3"
curl -H "Authorization: Bearer $TOKEN" "http://localhost:3003/api/backend/quality-metrics"

# Test chat
curl -X POST "http://localhost:3003/api/backend/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about copper mining"}'

# Test geological query
curl -X POST "http://localhost:3003/api/backend/geological-query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me nickel deposits", "limit": 3}'
```

## Docker Support

```bash
# Build the Docker image
docker build -t backend-gateway .

# Run the container
docker run -p 3003:3003 backend-gateway
```

## Migration from Old Structure

The module has been reorganized from a flat structure to a proper Python package structure:

**Old Structure:**

```
backend_gateway/
├── main.py
├── auth.py
├── models.py
├── services.py
├── config.py
└── test_api.py
```

**New Structure:**

```
backend_gateway/
├── src/
│   ├── api/main.py
│   ├── core/{auth.py, config.py}
│   ├── models/{requests.py, responses.py}
│   ├── services/{data_client.py, cortex_client.py}
│   └── tests/{test_api.py, test_startup.py}
└── main.py (entry point)
```

All imports have been updated and the API functionality remains the same.

---

**Module 3 Backend Gateway API** - Part of the geological data analysis platform integrating data access and AI services.
