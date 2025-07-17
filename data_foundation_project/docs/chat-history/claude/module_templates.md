# Internal API Templates for Student Rotation

## Module 1: Data Foundation API
**Base URL**: `http://localhost:3001/api/data`

### **Required API Endpoints**

#### **GET /health**
```json
Response (200 OK):
{
    "status": "healthy",
    "service": "data-foundation",
    "database_connection": "active",
    "record_count": 10523,
    "last_updated": "2024-07-14T10:30:00Z"
}
```

#### **GET /geological-sites**
```json
Query Parameters:
- limit: integer (default: 100, max: 1000)
- offset: integer (default: 0)
- mineral_type: string (optional filter)
- location: string (optional filter)

Response (200 OK):
{
    "total_count": 10523,
    "returned_count": 100,
    "sites": [
        {
            "id": 1,
            "coordinates": [115.8605, -31.9505],
            "mineral_type": "Gold",
            "location_name": "Perth Hills",
            "metadata": "Gold exploration site with high-grade ore...",
            "exploration_date": "2023-08-15",
            "company": "Western Mining Corp",
            "confidence_score": 0.94
        }
    ],
    "processing_time_ms": 45
}
```

#### **GET /quality-metrics**
```json
Response (200 OK):
{
    "total_records": 10523,
    "valid_geometries": 10481,
    "quality_score": 0.996,
    "missing_metadata": 12,
    "duplicate_records": 8,
    "last_validation": "2024-07-14T09:15:00Z"
}
```

#### **POST /spatial-query**
```json
Request Body:
{
    "center_coordinates": [115.8605, -31.9505],
    "radius_km": 50,
    "mineral_filters": ["Gold", "Copper"],
    "max_results": 20
}

Response (200 OK):
{
    "query_center": [115.8605, -31.9505],
    "radius_km": 50,
    "results_count": 18,
    "sites": [...],
    "processing_time_ms": 78
}
```

### **Measurable Learning Outcomes**
```python
# Supervisor Assessment - Same Test for Any Student
def assess_module1_api():
    # 1. Performance Benchmark
    start_time = time.time()
    response = requests.get("http://localhost:3001/api/data/geological-sites?limit=1000")
    response_time = time.time() - start_time
    assert response.status_code == 200
    assert response_time < 0.1, "Must respond <100ms for 1000 records"
    
    # 2. Data Quality Validation
    quality = requests.get("http://localhost:3001/api/data/quality-metrics").json()
    assert quality["quality_score"] >= 0.99, "Data quality must be 99%+"
    assert quality["total_records"] >= 10000, "Must have 10,000+ records"
    
    # 3. Spatial Query Capability
    spatial_query = {
        "center_coordinates": [115.8605, -31.9505],
        "radius_km": 10,
        "max_results": 5
    }
    spatial_response = requests.post("http://localhost:3001/api/data/spatial-query", 
                                   json=spatial_query)
    assert spatial_response.status_code == 200
    assert len(spatial_response.json()["sites"]) <= 5
    
    return "✅ Module 1 API competency validated"
```

---

## Module 2: AI/Cortex Engine API
**Base URL**: `http://localhost:3002/api/ai`

### **Required API Endpoints**

#### **GET /health**
```json
Response (200 OK):
{
    "status": "healthy",
    "service": "ai-cortex-engine",
    "cortex_connection": "active",
    "embeddings_count": 8745,
    "models_available": ["text-embedding-1024", "mixtral-8x7b"],
    "last_updated": "2024-07-14T10:30:00Z"
}
```

#### **POST /embed**
```json
Request Body:
{
    "text": "Gold exploration site with high-grade ore samples",
    "model": "text-embedding-1024"
}

Response (200 OK):
{
    "embedding": [0.123, -0.456, 0.789, ...],  // 1024 dimensions
    "model_used": "text-embedding-1024",
    "text_length": 45,
    "processing_time_ms": 120
}
```

#### **POST /similarity-search**
```json
Request Body:
{
    "query": "gold mines near Perth",
    "top_k": 5,
    "min_similarity": 0.7,
    "filters": {
        "mineral_type": ["Gold"],
        "location_region": "Perth"
    }
}

Response (200 OK):
{
    "query": "gold mines near Perth",
    "results_count": 5,
    "results": [
        {
            "site_id": 1,
            "similarity_score": 0.89,
            "location_name": "Perth Hills",
            "mineral_type": "Gold",
            "metadata_snippet": "Gold exploration site with high-grade ore..."
        }
    ],
    "processing_time_ms": 245
}
```

#### **POST /rag-query**
```json
Request Body:
{
    "question": "What are the most promising gold sites in Western Australia?",
    "context_limit": 5,
    "model": "mixtral-8x7b"
}

Response (200 OK):
{
    "question": "What are the most promising gold sites in Western Australia?",
    "answer": "Based on geological exploration data, the most promising gold sites are...",
    "context_sources": [
        {
            "site_id": 1,
            "location": "Perth Hills",
            "relevance_score": 0.92
        }
    ],
    "confidence_score": 0.87,
    "processing_time_ms": 380
}
```

### **Measurable Learning Outcomes**
```python
# Supervisor Assessment - Snowflake Cortex Competency
def assess_module2_api():
    # 1. Cortex Embedding Mastery
    embed_request = {
        "text": "Copper mining operations in Pilbara region",
        "model": "text-embedding-1024"
    }
    embed_response = requests.post("http://localhost:3002/api/ai/embed", 
                                 json=embed_request)
    assert embed_response.status_code == 200
    embedding = embed_response.json()["embedding"]
    assert len(embedding) == 1024, "Must generate 1024-dimensional embeddings"
    
    # 2. Vector Similarity Search Accuracy
    search_request = {
        "query": "gold exploration sites",
        "top_k": 5,
        "min_similarity": 0.7
    }
    search_response = requests.post("http://localhost:3002/api/ai/similarity-search", 
                                  json=search_request)
    assert search_response.status_code == 200
    results = search_response.json()["results"]
    assert len(results) <= 5
    assert all(r["similarity_score"] >= 0.7 for r in results), "Must meet similarity threshold"
    
    # 3. RAG System Performance
    start_time = time.time()
    rag_request = {
        "question": "Where are copper deposits located in Western Australia?",
        "context_limit": 3
    }
    rag_response = requests.post("http://localhost:3002/api/ai/rag-query", 
                               json=rag_request)
    rag_time = time.time() - start_time
    assert rag_response.status_code == 200
    assert rag_time < 0.5, "RAG responses must be <500ms"
    assert rag_response.json()["confidence_score"] >= 0.8, "RAG accuracy must be 80%+"
    
    return "✅ Module 2 AI/Cortex competency validated"
```

---

## Module 3: Backend API Gateway
**Base URL**: `http://localhost:3003/api/backend`

### **Required API Endpoints**

#### **GET /health**
```json
Response (200 OK):
{
    "status": "healthy",
    "service": "backend-api-gateway",
    "data_service": "connected",
    "ai_service": "connected",
    "auth_service": "active",
    "last_updated": "2024-07-14T10:30:00Z"
}
```

#### **POST /auth/login**
```json
Request Body:
{
    "username": "student1",
    "password": "bootcamp2024"
}

Response (200 OK):
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "username": "student1",
        "role": "researcher"
    }
}
```

#### **POST /geological-query** (Protected)
```json
Headers:
Authorization: Bearer {access_token}

Request Body:
{
    "query": "find gold mines near Perth with high confidence",
    "max_results": 10,
    "include_ai_insights": true
}

Response (200 OK):
{
    "query": "find gold mines near Perth with high confidence",
    "results_count": 8,
    "geological_sites": [
        {
            "id": 1,
            "coordinates": [115.8605, -31.9505],
            "mineral_type": "Gold",
            "location_name": "Perth Hills",
            "confidence_score": 0.94,
            "ai_similarity": 0.89
        }
    ],
    "ai_insights": "Based on geological analysis, these sites show high potential for gold extraction...",
    "processing_time_ms": 180
}
```

#### **POST /chat** (Protected)
```json
Headers:
Authorization: Bearer {access_token}

Request Body:
{
    "message": "What are the best copper mining locations in WA?",
    "conversation_id": "conv-12345",
    "include_map_data": true
}

Response (200 OK):
{
    "message": "What are the best copper mining locations in WA?",
    "ai_response": "The best copper mining locations in Western Australia are primarily in the Geraldton region...",
    "related_sites": [
        {
            "id": 15,
            "location_name": "Geraldton Copper Mine",
            "coordinates": [114.6083, -28.7747],
            "confidence_score": 0.91
        }
    ],
    "conversation_id": "conv-12345",
    "processing_time_ms": 420
}
```

### **Measurable Learning Outcomes**
```python
# Supervisor Assessment - API Integration & Security
def assess_module3_api():
    # 1. Authentication Security
    # Test without authentication
    unauth_response = requests.post("http://localhost:3003/api/backend/geological-query",
                                  json={"query": "test"})
    assert unauth_response.status_code == 401, "Must enforce authentication"
    
    # Test with valid authentication
    login_response = requests.post("http://localhost:3003/api/backend/auth/login",
                                 json={"username": "student1", "password": "bootcamp2024"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 2. API Performance with Authentication
    start_time = time.time()
    auth_headers = {"Authorization": f"Bearer {token}"}
    query_response = requests.post("http://localhost:3003/api/backend/geological-query",
                                 headers=auth_headers,
                                 json={"query": "gold mines Perth", "max_results": 5})
    response_time = time.time() - start_time
    assert query_response.status_code == 200
    assert response_time < 0.2, "Authenticated API calls must be <200ms"
    
    # 3. AI Integration Through API
    chat_response = requests.post("http://localhost:3003/api/backend/chat",
                                headers=auth_headers,
                                json={"message": "Find copper deposits in Pilbara"})
    assert chat_response.status_code == 200
    response_data = chat_response.json()
    assert "ai_response" in response_data
    assert len(response_data["related_sites"]) > 0, "Chat must return relevant geological sites"
    
    return "✅ Module 3 Backend API competency validated"
```

---

## Module 4: Frontend UI API
**Base URL**: `http://localhost:3004` (Web Application)

### **Required Frontend Capabilities**

#### **Health Check Endpoint**
```
GET /health
Response (200 OK):
{
    "status": "healthy",
    "service": "frontend-ui",
    "backend_connectivity": "connected",
    "build_version": "1.0.0",
    "last_deployment": "2024-07-14T10:30:00Z"
}
```

#### **User Interface Requirements**
```yaml
Authentication Pages:
  - /login: User authentication form
  - /register: New user registration (if enabled)
  - /logout: Session termination

Main Application:
  - /: Homepage with geological data overview
  - /map: Interactive map with geological sites
  - /chat: AI-powered chat interface
  - /search: Advanced search and filtering
  - /profile: User account management

Performance Requirements:
  - Initial page load: <3 seconds
  - Map rendering: <2 seconds for 1000+ markers
  - Chat interface: <1 second response display
  - Mobile responsive: Works on 320px+ width screens
```

#### **Frontend API Integration Test Endpoints**
```javascript
// For automated testing of frontend functionality
GET /api/test/authentication-flow
// Tests: Can user log in and access protected features?

GET /api/test/map-performance
// Tests: Does map load 1000+ markers in <2 seconds?

GET /api/test/chat-integration  
// Tests: Does chat interface connect to AI backend?

GET /api/test/mobile-responsive
// Tests: Are all features usable on mobile devices?
```

### **Measurable Learning Outcomes**
```python
# Supervisor Assessment - Frontend & Production Deployment
def assess_module4_ui():
    # 1. Production Deployment Validation
    health_response = requests.get("http://localhost:3004/health")
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert health_data["backend_connectivity"] == "connected"
    
    # 2. Performance Testing
    start_time = time.time()
    homepage_response = requests.get("http://localhost:3004/")
    page_load_time = time.time() - start_time
    assert homepage_response.status_code == 200
    assert page_load_time < 3.0, "Homepage must load in <3 seconds"
    
    # 3. Authentication Flow Testing
    auth_test = requests.get("http://localhost:3004/api/test/authentication-flow")
    assert auth_test.json()["login_working"] == True
    assert auth_test.json()["protected_access"] == True
    
    # 4. Map Performance Testing
    map_test = requests.get("http://localhost:3004/api/test/map-performance")
    assert map_test.json()["markers_loaded"] >= 1000
    assert map_test.json()["render_time_seconds"] < 2.0
    
    # 5. Chat Integration Testing
    chat_test = requests.get("http://localhost:3004/api/test/chat-integration")
    assert chat_test.json()["backend_connected"] == True
    assert chat_test.json()["ai_responses_working"] == True
    
    # 6. Mobile Responsiveness
    mobile_test = requests.get("http://localhost:3004/api/test/mobile-responsive")
    assert mobile_test.json()["mobile_navigation"] == True
    assert mobile_test.json()["mobile_map_interactive"] == True
    
    return "✅ Module 4 Frontend UI competency validated"
```

---

## Cross-Module Integration Testing

### **End-to-End Workflow Validation**
```python
# Supervisor Assessment - Complete System Integration
def assess_complete_system_integration():
    # 1. Data Flow Validation
    # Module 1 → Module 2 → Module 3 → Module 4
    
    # Check data foundation
    data_health = requests.get("http://localhost:3001/api/data/health").json()
    assert data_health["record_count"] >= 10000
    
    # Check AI processing
    ai_health = requests.get("http://localhost:3002/api/ai/health").json()
    assert ai_health["embeddings_count"] >= 5000
    
    # Check backend integration
    backend_health = requests.get("http://localhost:3003/api/backend/health").json()
    assert backend_health["data_service"] == "connected"
    assert backend_health["ai_service"] == "connected"
    
    # Check frontend deployment
    frontend_health = requests.get("http://localhost:3004/health").json()
    assert frontend_health["backend_connectivity"] == "connected"
    
    # 2. End-to-End User Journey Test
    # Login through frontend
    login_data = {"username": "student1", "password": "bootcamp2024"}
    login_response = requests.post("http://localhost:3003/api/backend/auth/login", 
                                 json=login_data)
    token = login_response.json()["access_token"]
    
    # Query geological data through backend
    headers = {"Authorization": f"Bearer {token}"}
    query_data = {"query": "gold mines near Perth", "max_results": 5}
    query_response = requests.post("http://localhost:3003/api/backend/geological-query",
                                 headers=headers, json=query_data)
    assert query_response.status_code == 200
    assert len(query_response.json()["geological_sites"]) > 0
    
    # Test AI chat functionality
    chat_data = {"message": "What minerals are found in the Perth Hills?"}
    chat_response = requests.post("http://localhost:3003/api/backend/chat",
                                headers=headers, json=chat_data)
    assert chat_response.status_code == 200
    assert "Perth" in chat_response.json()["ai_response"]
    
    return "✅ Complete system integration validated"
```

---

## Supervisor Benefits of Internal API Architecture

### **Consistent Assessment Framework**
- **Same API tests** work regardless of which student implemented the module
- **Measurable performance benchmarks** for every rotation
- **Standardized error handling** and response formats
- **Clear pass/fail criteria** for each API endpoint

### **Rotation-Friendly Design**
- **Internal implementation flexibility** - students can choose technologies
- **No integration breakage** during student transitions
- **Clear API contracts** define what each module must deliver
- **Version compatibility** maintained across rotations

### **Snowflake Cortex Competency Tracking**
- **Module 2 API endpoints** directly measure Cortex function mastery
- **Performance benchmarks** for embedding generation and RAG responses
- **Cost optimization tracking** through API usage metrics
- **Production deployment validation** with real Cortex integration

### **Visible Learning Outcomes**
- **Daily API health checks** show student progress
- **Friday assessments** use standardized API tests
- **Cross-module integration tests** validate collaboration
- **Production readiness** measured through complete API functionality

This internal API architecture ensures **every student demonstrates measurable Full Stack AI Engineer competencies** while providing **clear supervision visibility** and **comprehensive Snowflake Cortex expertise development**.