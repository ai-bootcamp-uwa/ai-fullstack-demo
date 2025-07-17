# Internal API Interaction Matrix for Full Stack AI Engineer Bootcamp

## API Service Overview & Dependencies

| API Service | Base URL | Key Endpoints | Role | Calls (Dependencies) | Called By (Consumers) | Key Measurable Outcomes |
|-------------|----------|---------------|------|---------------------|----------------------|------------------------|
| **Data Foundation API** | `http://localhost:3001/api/data` | • `GET /health`<br/>• `GET /geological-sites`<br/>• `GET /quality-metrics`<br/>• `POST /spatial-query` | Geological data storage & retrieval | • Snowflake Database<br/>• External WAMEX data sources | • AI/Cortex Engine API<br/>• Backend Gateway API | ✅ 10,000+ records loaded<br/>✅ <100ms query response<br/>✅ 99% data quality score |
| **AI/Cortex Engine API** | `http://localhost:3002/api/ai` | • `GET /health`<br/>• `POST /embed`<br/>• `POST /similarity-search`<br/>• `POST /rag-query` | Snowflake Cortex AI processing | • Data Foundation API (for text data)<br/>• Snowflake Cortex functions<br/>• Vector database | • Backend Gateway API<br/>• Frontend UI (direct for testing) | ✅ 1000+ embeddings in <5min<br/>✅ 85% similarity search accuracy<br/>✅ <500ms RAG responses |
| **Backend Gateway API** | `http://localhost:3003/api/backend` | • `GET /health`<br/>• `POST /auth/login`<br/>• `POST /geological-query`<br/>• `POST /chat` | Business logic & integration orchestration | • Data Foundation API<br/>• AI/Cortex Engine API<br/>• Authentication service | • Frontend UI Application<br/>• External clients | ✅ <200ms API response time<br/>✅ JWT authentication working<br/>✅ 50+ concurrent users |
| **Frontend UI Application** | `http://localhost:3004` | • `GET /health`<br/>• `GET /` (homepage)<br/>• `GET /map`<br/>• `GET /chat`<br/>• `GET /login` | User interface & experience | • Backend Gateway API<br/>• Static asset services | • End users<br/>• Monitoring services | ✅ <3sec page load time<br/>✅ <2sec map rendering<br/>✅ Mobile responsive design |

---

## API Communication Flow Patterns

### **Data Retrieval Flow**
```
Frontend UI (3004) → Backend Gateway (3003) → Data Foundation (3001) → Snowflake
```
**Supervision Assessment**: Can users access geological data through the UI?

### **AI Query Processing Flow**
```
Frontend UI (3004) → Backend Gateway (3003) → AI/Cortex Engine (3002) → Snowflake Cortex
                                    ↓
                              Data Foundation (3001) ← AI/Cortex Engine (3002)
```
**Supervision Assessment**: Do AI-powered features work end-to-end?

### **User Authentication Flow**
```
Frontend UI (3004) → Backend Gateway (3003) → Authentication Service
```
**Supervision Assessment**: Is the system secure and properly authenticated?

---

## Weekly Rotation API Ownership

### **Week 1 Assignments**
| Student | Primary API | API Dependencies | Measurable Deliverable |
|---------|-------------|------------------|------------------------|
| **Chris** | Data Foundation API (3001) | Snowflake connection | ✅ Other students can query geological data |
| **Daniel** | AI/Cortex Engine API (3002) | Data Foundation API | ✅ AI functions return relevant results |
| **Liam** | Backend Gateway API (3003) | Data + AI APIs | ✅ Secure endpoints serve integrated data |
| **Jinwen** | Frontend UI (3004) | Backend Gateway API | ✅ Users can interact with geological data |

### **Week 2 Assignments** (Rotation)
| Student | Primary API | New Dependencies | Measurable Deliverable |
|---------|-------------|------------------|------------------------|
| **Chris** | AI/Cortex Engine API (3002) | Inherits from Daniel + Snowflake Cortex | ✅ Real embeddings with 85% accuracy |
| **Daniel** | Backend Gateway API (3003) | Inherits from Liam + Chris's AI API | ✅ Intelligent endpoints with <200ms response |
| **Liam** | Frontend UI (3004) | Inherits from Jinwen + Daniel's Backend | ✅ AI-powered UI features working |
| **Jinwen** | Data Foundation API (3001) | Inherits from Chris + production data | ✅ 10,000+ records with quality validation |

### **Week 3-4 Rotation Pattern Continues**
Each student experiences all 4 APIs, learning complete Full Stack + Snowflake Cortex integration.

---

## Cross-API Integration Checkpoints

### **Week 1 Integration Validation**
| API Pair | Integration Test | Pass Criteria | Student Learning Outcome |
|----------|------------------|---------------|-------------------------|
| Data ↔ AI | AI can process geological data | ✅ Embeddings generated from real data | Students understand data-AI pipeline |
| AI ↔ Backend | Backend serves AI responses | ✅ RAG queries return intelligent answers | Students integrate AI into business logic |
| Backend ↔ Frontend | UI displays integrated data | ✅ Map shows geological sites with AI insights | Students build complete user experience |

### **Week 2 Advanced Integration**
| API Chain | End-to-End Test | Pass Criteria | Supervision Validation |
|-----------|-----------------|---------------|----------------------|
| UI → Backend → AI → Data | User query to geological results | ✅ Natural language search works | Complete AI pipeline functional |
| UI → Backend → Data | Direct data visualization | ✅ Map renders 1000+ sites <2sec | Performance optimization successful |
| UI → Backend (Auth) | Secure user access | ✅ JWT tokens protect all endpoints | Security implementation correct |

---

## Supervision Monitoring Points

### **Daily Health Check Matrix**
| Time | API Check | Exact Endpoint | Expected Response | Student Accountability |
|------|-----------|----------------|-------------------|----------------------|
| **9:00 AM** | Data Foundation health | `GET http://localhost:3001/api/data/health` | 200 OK + record count ≥10,000 | Current API owner demonstrates working service |
| **9:05 AM** | AI/Cortex health | `GET http://localhost:3002/api/ai/health` | 200 OK + embeddings count ≥5,000 | Student shows Cortex integration working |
| **9:10 AM** | Backend Gateway health | `GET http://localhost:3003/api/backend/health` | 200 OK + services connected | Student proves API integration |
| **9:15 AM** | Frontend UI health | `GET http://localhost:3004/health` | 200 OK + backend connectivity | Student demonstrates deployment status |
| **2:00 PM** | Cross-API integration test | Chain: 3004 → 3003 → 3002 → 3001 | Successful data flow end-to-end | Team demonstrates API collaboration |
| **5:00 PM** | Performance benchmarks | All endpoints response time test | <200ms for all API calls | Students show optimization progress |

### **Weekly Assessment Framework**
| Assessment Area | API Measurement | Snowflake Cortex Validation | Pass/Fail Criteria |
|-----------------|-----------------|----------------------------|-------------------|
| **Technical Competency** | API endpoints functional | Cortex functions implemented correctly | ✅ All endpoints respond properly<br/>✅ Performance benchmarks met |
| **Integration Skills** | Cross-API communication working | AI features accessible through APIs | ✅ End-to-end user journeys functional<br/>✅ No broken API dependencies |
| **Production Readiness** | APIs deployed and monitored | Cortex costs optimized | ✅ Public deployment accessible<br/>✅ Monitoring and alerting active |

---

## API Dependency Management for Rotation

### **Mock-to-Real Transition Strategy**
| Week | Real API | Mock APIs | Student Focus | Measurable Outcome |
|------|----------|-----------|---------------|-------------------|
| **Week 1** | Data Foundation (Chris) | AI, Backend, Frontend mocked | Data pipeline mastery | ✅ 10,000+ records accessible |
| **Week 2** | AI/Cortex (Chris) | Backend, Frontend use mocks | Snowflake Cortex mastery | ✅ Real AI responses working |
| **Week 3** | Backend Gateway (Chris) | Frontend uses mocks | API integration mastery | ✅ Secure, performant endpoints |
| **Week 4** | Frontend UI (Chris) | All APIs real | Full stack deployment | ✅ Complete user experience |

### **Handoff Documentation Requirements**
| API Owner Change | Required Documentation | Validation Method | Supervisor Sign-off |
|------------------|------------------------|-------------------|-------------------|
| **Any API rotation** | • API documentation updated<br/>• Performance benchmarks met<br/>• Integration tests passing | ✅ New student can run API successfully<br/>✅ Dependent APIs continue working | ✅ 30-minute demonstration<br/>✅ Cross-API integration verified |

---

## Final Certification API Requirements

### **Individual Student Competency** (Each API Mastered)
| API Mastered | Snowflake Cortex Skill | Production Capability | Employment Readiness |
|--------------|------------------------|----------------------|-------------------|
| **Data Foundation** | Database optimization for AI workloads | Scalable data pipelines | ✅ Can design data architecture |
| **AI/Cortex Engine** | Advanced RAG implementation | Cost-optimized AI deployment | ✅ Can implement production AI features |
| **Backend Gateway** | AI service integration | Secure, scalable APIs | ✅ Can build enterprise backend systems |
| **Frontend UI** | AI-powered user experience | Responsive, accessible interfaces | ✅ Can deliver complete user applications |

### **Team Integration Competency** (All APIs Working Together)
| System Capability | API Integration Required | Measurable Outcome | Employer Value |
|-------------------|-------------------------|-------------------|----------------|
| **Natural Language Geological Search** | Frontend → Backend → AI → Data | ✅ Users can ask "find gold near Perth" and get accurate results | Ready for AI product development roles |
| **Real-time Data Visualization** | Frontend → Backend → Data | ✅ Interactive maps with 1000+ geological sites | Ready for data visualization specialist roles |
| **Secure AI Applications** | Frontend → Backend (Auth) → AI | ✅ Protected AI features with user management | Ready for enterprise AI engineer roles |
| **Production AI Deployment** | All APIs deployed with monitoring | ✅ Complete system accessible via public URL | Ready for DevOps/MLOps roles |

This API interaction matrix provides **complete visibility** into student progress while ensuring **measurable Snowflake Cortex competency development** across all Full Stack AI Engineer skills.