# Mock Interfaces & Data for Parallel Development

## Module 1: Data Foundation - Mock Providers

### Mock Data Files (Week 1 Deliverable)
```python
# geological_sample_data.py - 100 realistic WAMEX records
SAMPLE_GEOLOGICAL_DATA = [
    {
        "id": 1,
        "geometry": "POINT(115.8605 -31.9505)",  # Perth coordinates
        "metadata_text": "Gold exploration site with high-grade ore samples. Quartz veining present with visible gold particles.",
        "mineral_type": "Gold",
        "location_name": "Perth Hills",
        "exploration_date": "2023-08-15",
        "company": "Western Mining Corp",
        "depth_meters": 45.2,
        "grade_grams_per_ton": 8.7
    },
    {
        "id": 2,
        "geometry": "POINT(121.4664 -30.7493)",  # Kalgoorlie coordinates
        "metadata_text": "Large-scale gold mining operation with established infrastructure. Historical production data available.",
        "mineral_type": "Gold",
        "location_name": "Kalgoorlie Super Pit",
        "exploration_date": "2023-09-22",
        "company": "Goldfields Mining",
        "depth_meters": 120.8,
        "grade_grams_per_ton": 12.3
    },
    {
        "id": 3,
        "geometry": "POINT(118.5964 -20.3484)",  # Pilbara coordinates
        "metadata_text": "Iron ore deposit with high Fe content. Suitable for direct shipping ore operations.",
        "mineral_type": "Iron Ore",
        "location_name": "Pilbara Region",
        "exploration_date": "2023-07-10",
        "company": "Rio Tinto",
        "depth_meters": 25.0,
        "grade_percentage": 62.5
    },
    # ... 97 more realistic records covering:
    # - Copper deposits near Geraldton
    # - Nickel sites in Kambalda
    # - Lithium deposits in Greenbushes
    # - Bauxite sites in Darling Range
    # - Coal deposits in Collie Basin
]

# Expected learning outcome: Students understand WAMEX data structure
```

### Mock Database Interface (Week 1)
```python
# mock_snowflake_client.py
class MockSnowflakeClient:
    """Provides realistic Snowflake responses for parallel development"""
    
    def __init__(self):
        self.data = SAMPLE_GEOLOGICAL_DATA
        
    def execute_query(self, sql_query: str):
        """Mock Snowflake query execution"""
        if "COUNT(*)" in sql_query:
            return [{"COUNT(*)": len(self.data)}]
        elif "SELECT *" in sql_query:
            return self.data[:10]  # Return first 10 for development
        elif "WHERE mineral_type" in sql_query:
            mineral = self._extract_mineral_filter(sql_query)
            return [r for r in self.data if r["mineral_type"] == mineral]
        else:
            return self.data
    
    def _extract_mineral_filter(self, sql):
        # Simple parser for mock purposes
        if "'Gold'" in sql:
            return "Gold"
        elif "'Iron Ore'" in sql:
            return "Iron Ore"
        return "Gold"  # Default for development

# Expected assessment: Module 2-4 can query geological data immediately
```

### Mock Data Validation Functions (Week 1)
```python
# mock_data_validators.py
def validate_geometry(geometry_string: str) -> bool:
    """Mock geometry validation for development"""
    return geometry_string.startswith("POINT(") and geometry_string.endswith(")")

def validate_metadata_completeness(record: dict) -> float:
    """Returns data quality score for supervision assessment"""
    required_fields = ["id", "geometry", "metadata_text", "mineral_type"]
    present_fields = sum(1 for field in required_fields if record.get(field))
    return present_fields / len(required_fields)

def get_data_quality_report():
    """Week 2 assessment metric"""
    total_records = len(SAMPLE_GEOLOGICAL_DATA)
    valid_geometries = sum(1 for r in SAMPLE_GEOLOGICAL_DATA 
                          if validate_geometry(r["geometry"]))
    return {
        "total_records": total_records,
        "valid_geometries": valid_geometries,
        "quality_percentage": (valid_geometries / total_records) * 100
    }

# Expected outcome: 99% data quality validation for Week 2 checkpoint
```

---

## Module 2: AI Engine - Mock Consumers & Providers

### Mock Cortex Functions (Week 1 Deliverable)
```python
# mock_cortex_functions.py
import random
import json

class MockCortexFunctions:
    """Realistic Snowflake Cortex function responses"""
    
    def embed_text_1024(self, text: str) -> list:
        """Mock CORTEX.EMBED_TEXT_1024 response"""
        # Generate realistic embedding vector (1024 dimensions)
        embedding = [random.uniform(-1, 1) for _ in range(1024)]
        return embedding
    
    def vector_cosine_similarity(self, vector1: list, vector2: list) -> float:
        """Mock VECTOR_COSINE_SIMILARITY calculation"""
        # Simple similarity based on text content matching
        return random.uniform(0.7, 0.95)  # Realistic similarity scores
    
    def cortex_complete(self, model: str, prompt: str) -> str:
        """Mock CORTEX.COMPLETE LLM responses"""
        responses = {
            "find gold": "Based on geological data, there are 3 gold mining sites near your location: Kalgoorlie Super Pit, Perth Hills exploration area, and Coolgardie historic mines.",
            "copper deposits": "Copper mining operations are primarily located in the Geraldton region with active exploration permits.",
            "iron ore": "Major iron ore deposits are concentrated in the Pilbara region with grades exceeding 60% Fe content."
        }
        
        for keyword, response in responses.items():
            if keyword in prompt.lower():
                return response
        
        return "I found several geological sites matching your query. Please specify mineral type or location for detailed results."
    
    def extract_answer(self, context: str, question: str) -> str:
        """Mock CORTEX.EXTRACT_ANSWER from geological documents"""
        if "mineral" in question.lower():
            return "The primary minerals identified are gold, iron ore, and copper based on exploration reports."
        elif "location" in question.lower():
            return "The site is located in Western Australia with coordinates provided in the geological survey."
        return "Information extracted from geological documentation."

# Expected assessment: Module 3 can call AI functions immediately
```

### Mock Vector Search Interface (Week 1)
```python
# mock_vector_search.py
class MockVectorSearch:
    """Provides realistic similarity search for development"""
    
    def __init__(self):
        self.mock_embeddings = self._generate_mock_embeddings()
    
    def _generate_mock_embeddings(self):
        """Create realistic embedding database"""
        embeddings = {}
        for record in SAMPLE_GEOLOGICAL_DATA:
            # Mock embedding based on metadata content
            embeddings[record["id"]] = {
                "embedding": [random.uniform(-1, 1) for _ in range(1024)],
                "metadata": record["metadata_text"],
                "mineral_type": record["mineral_type"],
                "location": record["location_name"]
            }
        return embeddings
    
    def similarity_search(self, query_text: str, top_k: int = 5) -> list:
        """Mock similarity search with realistic geological results"""
        # Simple keyword matching for development
        results = []
        query_lower = query_text.lower()
        
        for record_id, data in self.mock_embeddings.items():
            similarity_score = 0.0
            
            # Check for mineral type matches
            if data["mineral_type"].lower() in query_lower:
                similarity_score += 0.8
            
            # Check for location matches
            if data["location"].lower() in query_lower:
                similarity_score += 0.6
            
            # Check for metadata keyword matches
            if any(word in data["metadata"].lower() for word in query_lower.split()):
                similarity_score += 0.4
            
            if similarity_score > 0.3:  # Threshold for relevance
                results.append({
                    "record_id": record_id,
                    "similarity_score": min(similarity_score, 0.95),
                    "metadata": data["metadata"],
                    "mineral_type": data["mineral_type"],
                    "location": data["location"]
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

# Expected outcome: 85% search relevance for Week 4 checkpoint
```

### Mock RAG Pipeline (Week 1)
```python
# mock_rag_system.py
class MockRAGSystem:
    """Complete RAG system for geological queries"""
    
    def __init__(self):
        self.vector_search = MockVectorSearch()
        self.cortex = MockCortexFunctions()
    
    def process_query(self, user_query: str) -> dict:
        """End-to-end RAG processing"""
        # Step 1: Vector similarity search
        search_results = self.vector_search.similarity_search(user_query, top_k=3)
        
        # Step 2: Prepare context for LLM
        context = self._prepare_context(search_results)
        
        # Step 3: Generate response using mock Cortex
        prompt = f"Based on this geological data: {context}\nAnswer the question: {user_query}"
        llm_response = self.cortex.cortex_complete("mixtral-8x7b", prompt)
        
        return {
            "user_query": user_query,
            "search_results": search_results,
            "context_used": context,
            "rag_response": llm_response,
            "confidence_score": self._calculate_confidence(search_results)
        }
    
    def _prepare_context(self, search_results: list) -> str:
        """Prepare geological context for LLM"""
        context_parts = []
        for result in search_results:
            context_parts.append(f"Site: {result['location']}, Mineral: {result['mineral_type']}, Details: {result['metadata']}")
        return " | ".join(context_parts)
    
    def _calculate_confidence(self, search_results: list) -> float:
        """Calculate response confidence for assessment"""
        if not search_results:
            return 0.0
        avg_similarity = sum(r["similarity_score"] for r in search_results) / len(search_results)
        return avg_similarity

# Expected assessment: RAG answers geological questions with 85% accuracy
```

---

## Module 3: Backend API - Mock Consumers & Providers

### Mock API Response Schemas (Week 1 Deliverable)
```python
# mock_api_schemas.py
from typing import List, Dict, Optional
from pydantic import BaseModel

class GeologicalSite(BaseModel):
    """Standard geological site response format"""
    id: int
    coordinates: List[float]  # [longitude, latitude]
    mineral_type: str
    location_name: str
    metadata: str
    similarity_score: Optional[float] = None
    exploration_date: str
    company: str

class GeologicalQueryResponse(BaseModel):
    """API response format for Module 4 consumption"""
    query: str
    total_results: int
    results: List[GeologicalSite]
    processing_time_ms: float
    confidence_score: float

class ChatQueryResponse(BaseModel):
    """Chat interface response format"""
    user_message: str
    ai_response: str
    related_sites: List[GeologicalSite]
    conversation_id: str
    timestamp: str

# Expected outcome: Module 4 knows exact JSON structure to expect
```

### Mock API Endpoints (Week 1)
```python
# mock_api_endpoints.py
from fastapi import FastAPI, HTTPException
from typing import Dict
import time
import uuid
from datetime import datetime

app = FastAPI()

# Mock data sources
mock_rag = MockRAGSystem()
mock_search = MockVectorSearch()

@app.post("/api/geological-query", response_model=GeologicalQueryResponse)
async def geological_query(request: Dict[str, str]):
    """Mock geological query endpoint for frontend development"""
    start_time = time.time()
    
    query_text = request.get("query", "")
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text required")
    
    # Use mock RAG system
    rag_result = mock_rag.process_query(query_text)
    
    # Convert to API response format
    sites = []
    for result in rag_result["search_results"]:
        # Find corresponding geological data
        geological_record = next(
            (r for r in SAMPLE_GEOLOGICAL_DATA if r["id"] == result["record_id"]), 
            None
        )
        if geological_record:
            coord_str = geological_record["geometry"]
            # Parse "POINT(lng lat)" to [lng, lat]
            coords = coord_str.replace("POINT(", "").replace(")", "").split()
            
            sites.append(GeologicalSite(
                id=geological_record["id"],
                coordinates=[float(coords[0]), float(coords[1])],
                mineral_type=geological_record["mineral_type"],
                location_name=geological_record["location_name"],
                metadata=geological_record["metadata_text"],
                similarity_score=result["similarity_score"],
                exploration_date=geological_record["exploration_date"],
                company=geological_record["company"]
            ))
    
    processing_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return GeologicalQueryResponse(
        query=query_text,
        total_results=len(sites),
        results=sites,
        processing_time_ms=processing_time,
        confidence_score=rag_result["confidence_score"]
    )

@app.post("/api/chat", response_model=ChatQueryResponse)
async def chat_query(request: Dict[str, str]):
    """Mock chat endpoint for conversational interface"""
    user_message = request.get("message", "")
    conversation_id = request.get("conversation_id", str(uuid.uuid4()))
    
    # Use mock RAG for chat response
    rag_result = mock_rag.process_query(user_message)
    
    # Convert search results to sites
    related_sites = []
    for result in rag_result["search_results"][:3]:  # Top 3 for chat
        geological_record = next(
            (r for r in SAMPLE_GEOLOGICAL_DATA if r["id"] == result["record_id"]), 
            None
        )
        if geological_record:
            coord_str = geological_record["geometry"]
            coords = coord_str.replace("POINT(", "").replace(")", "").split()
            
            related_sites.append(GeologicalSite(
                id=geological_record["id"],
                coordinates=[float(coords[0]), float(coords[1])],
                mineral_type=geological_record["mineral_type"],
                location_name=geological_record["location_name"],
                metadata=geological_record["metadata_text"][:100] + "...",
                exploration_date=geological_record["exploration_date"],
                company=geological_record["company"]
            ))
    
    return ChatQueryResponse(
        user_message=user_message,
        ai_response=rag_result["rag_response"],
        related_sites=related_sites,
        conversation_id=conversation_id,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint for deployment validation"""
    return {
        "status": "healthy",
        "service": "geological-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Expected assessment: <200ms response time, handles 10+ concurrent users
```

### Mock Authentication System (Week 1)
```python
# mock_auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

# Mock JWT configuration
SECRET_KEY = "mock-secret-key-for-development"
ALGORITHM = "HS256"

def create_mock_token(username: str) -> str:
    """Generate mock JWT token for development"""
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
        "role": "geological_researcher"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_mock_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mock token verification for API testing"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Mock user database
MOCK_USERS = {
    "student1": {"password": "bootcamp2024", "role": "researcher"},
    "student2": {"password": "bootcamp2024", "role": "researcher"},
    "instructor": {"password": "supervisor2024", "role": "admin"}
}

@app.post("/api/auth/login")
async def mock_login(credentials: Dict[str, str]):
    """Mock login endpoint for frontend development"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    if username in MOCK_USERS and MOCK_USERS[username]["password"] == password:
        token = create_mock_token(username)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,  # 24 hours
            "user": {
                "username": username,
                "role": MOCK_USERS[username]["role"]
            }
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Expected outcome: JWT authentication working for Week 6 checkpoint
```

---

## Module 4: Frontend UI - Mock Consumers

### Mock API Client (Week 1 Deliverable)
```typescript
// mockApiClient.ts
export interface GeologicalSite {
  id: number;
  coordinates: [number, number]; // [longitude, latitude]
  mineral_type: string;
  location_name: string;
  metadata: string;
  similarity_score?: number;
  exploration_date: string;
  company: string;
}

export interface GeologicalQueryResponse {
  query: string;
  total_results: number;
  results: GeologicalSite[];
  processing_time_ms: number;
  confidence_score: number;
}

export interface ChatResponse {
  user_message: string;
  ai_response: string;
  related_sites: GeologicalSite[];
  conversation_id: string;
  timestamp: string;
}

class MockApiClient {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  // Mock authentication
  async login(username: string, password: string): Promise<{token: string}> {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (username === 'student1' && password === 'bootcamp2024') {
      this.authToken = 'mock-jwt-token-for-development';
      return { token: this.authToken };
    }
    throw new Error('Invalid credentials');
  }

  // Mock geological query
  async queryGeologicalSites(query: string): Promise<GeologicalQueryResponse> {
    await new Promise(resolve => setTimeout(resolve, 300)); // Simulate API delay

    // Return realistic mock data based on query
    const mockResults: GeologicalSite[] = [];
    
    if (query.toLowerCase().includes('gold')) {
      mockResults.push({
        id: 1,
        coordinates: [115.8605, -31.9505],
        mineral_type: 'Gold',
        location_name: 'Perth Hills',
        metadata: 'Gold exploration site with high-grade ore samples...',
        similarity_score: 0.89,
        exploration_date: '2023-08-15',
        company: 'Western Mining Corp'
      });
    }

    if (query.toLowerCase().includes('copper')) {
      mockResults.push({
        id: 4,
        coordinates: [114.6083, -28.7747],
        mineral_type: 'Copper',
        location_name: 'Geraldton Region',
        metadata: 'Copper mining operations with established infrastructure...',
        similarity_score: 0.76,
        exploration_date: '2023-09-10',
        company: 'Copper Australia Ltd'
      });
    }

    return {
      query,
      total_results: mockResults.length,
      results: mockResults,
      processing_time_ms: 287,
      confidence_score: mockResults.length > 0 ? 0.85 : 0.0
    };
  }

  // Mock chat interface
  async sendChatMessage(message: string, conversationId?: string): Promise<ChatResponse> {
    await new Promise(resolve => setTimeout(resolve, 800)); // Simulate AI processing

    const responses = {
      'hello': 'Hello! I can help you explore geological data in Western Australia. Try asking about gold mines, copper deposits, or iron ore sites.',
      'gold': 'I found several gold mining sites in Western Australia. The most notable are in the Perth Hills and Kalgoorlie regions.',
      'copper': 'Copper deposits are primarily located in the Geraldton region with active exploration permits.',
      'help': 'You can ask me about: mineral types (gold, copper, iron ore), locations (Perth, Kalgoorlie, Pilbara), or exploration companies.'
    };

    let aiResponse = responses['help']; // default
    for (const [keyword, response] of Object.entries(responses)) {
      if (message.toLowerCase().includes(keyword)) {
        aiResponse = response;
        break;
      }
    }

    return {
      user_message: message,
      ai_response: aiResponse,
      related_sites: await this.queryGeologicalSites(message).then(r => r.results.slice(0, 3)),
      conversation_id: conversationId || `conv-${Date.now()}`,
      timestamp: new Date().toISOString()
    };
  }
}

export const mockApiClient = new MockApiClient();

// Expected assessment: Frontend can display geological data immediately
```

### Mock Map Components (Week 1)
```typescript
// mockMapData.ts
export const MOCK_MAP_CONFIG = {
  center: [-26.0, 118.0] as [number, number], // Western Australia center
  zoom: 6,
  minZoom: 5,
  maxZoom: 15
};

export const MOCK_GEOLOGICAL_MARKERS = [
  {
    id: 1,
    position: [115.8605, -31.9505] as [number, number],
    mineral: 'Gold',
    location: 'Perth Hills',
    company: 'Western Mining Corp',
    popup: 'Gold exploration site with high-grade ore samples'
  },
  {
    id: 2,
    position: [121.4664, -30.7493] as [number, number],
    mineral: 'Gold',
    location: 'Kalgoorlie Super Pit',
    company: 'Goldfields Mining',
    popup: 'Large-scale gold mining operation'
  },
  {
    id: 3,
    position: [118.5964, -20.3484] as [number, number],
    mineral: 'Iron Ore',
    location: 'Pilbara Region',
    company: 'Rio Tinto',
    popup: 'Iron ore deposit with high Fe content'
  },
  {
    id: 4,
    position: [114.6083, -28.7747] as [number, number],
    mineral: 'Copper',
    location: 'Geraldton Region',
    company: 'Copper Australia Ltd',
    popup: 'Copper mining operations'
  }
];

// Expected outcome: Map displays 1000+ markers in <2 seconds for Week 8
```

---

## Weekly Mock-to-Real Transition Schedule

### Week 2 Integration: Module 1 → All Others
**Replace:** Mock Snowflake data with real database
**Validation:** All teams can query actual geological_data table

### Week 4 Integration: Module 2 → Module 3 & 4  
**Replace:** Mock Cortex functions with real Snowflake Cortex
**Validation:** API endpoints return real AI-generated responses

### Week 6 Integration: Module 3 → Module 4
**Replace:** Mock API responses with real backend endpoints
**Validation:** Frontend consumes live API data successfully

### Week 8 Final Integration: Complete System
**Replace:** All remaining mocks with production components
**Validation:** End-to-end user journey functional

## Supervision Assessment Framework

### Week 1 Checkpoint: Mock Framework Complete
- ✅ All teams have working mock interfaces
- ✅ Sample data includes 100+ realistic WAMEX records
- ✅ Mock APIs return valid JSON responses
- ✅ Frontend can display mock geological data

### Week 2 Assessment: Real Data Integration
```python
def assess_week2_real_data():
    # Module 1 delivers real Snowflake connection
    assert snowflake_client.execute("SELECT COUNT(*) FROM geological_data")[0]["COUNT(*)"] >= 10000
    
    # Other modules replace mocks with real data access
    for module in [module2, module3, module4]:
        real_data = module.query_geological_data("SELECT * FROM geological_data LIMIT 5")
        assert len(real_data) == 5
        assert all("geometry" in record for record in real_data)
```

### Week 4 Assessment: Real AI Integration
```python
def assess_week4_real_ai():
    # Module 2 delivers real Cortex functions
    embedding = cortex_client.embed_text_1024("gold mining exploration")
    assert len(embedding) == 1024
    
    similarity_results = vector_search.similarity_search("find gold mines", top_k=5)
    assert len(similarity_results) == 5
    assert all(result["similarity_score"] > 0.7 for result in similarity_results)
```

### Week 6 Assessment: Real API Integration
```python
def assess_week6_real_api():
    # Module 3 delivers working APIs
    response = requests.post("http://localhost:8000/api/geological-query",
                           json={"query": "gold mines near Perth"})
    assert response.status_code == 200
    assert response.elapsed.total_seconds() < 0.2
    
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
```

This comprehensive mock framework ensures **all 4 teams are productive from Week 1** while providing **visible and measurable learning outcomes** for effective bootcamp supervision with clear **Snowflake Cortex competency validation**.