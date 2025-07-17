# RAG Pipeline Quick Reference

## AI Full-Stack Engineer Bootcamp Project

### 🚀 **10-Step RAG Flow Summary**

| Step | Component      | Process                        | Performance |
| ---- | -------------- | ------------------------------ | ----------- |
| 1️⃣   | **Module 3**   | User Authentication (JWT)      | <50ms       |
| 2️⃣   | **Module 3**   | Chat Request Reception         | <10ms       |
| 3️⃣   | **Module 3→2** | Query Forwarding               | <20ms       |
| 4️⃣   | **Module 2**   | Query Embedding (Azure OpenAI) | 100-200ms   |
| 5️⃣   | **Module 2**   | Vector Similarity Search       | <10ms       |
| 6️⃣   | **Module 2**   | Context Retrieval              | <50ms       |
| 7️⃣   | **Module 2**   | LLM Generation (GPT-4o-mini)   | 1-2 seconds |
| 8️⃣   | **Module 2**   | RAG Response Formation         | <20ms       |
| 9️⃣   | **Module 3**   | Response Formatting            | <20ms       |
| 🔟   | **Module 3**   | Final Delivery                 | <10ms       |

**Total Pipeline Time**: 1.5-2.5 seconds

---

### 🎯 **Key Technologies**

-   **Embedding Model**: Azure OpenAI `text-embedding-ada-002` (1536 dimensions)
-   **Chat Model**: Azure OpenAI `gpt-4o-mini`
-   **Similarity Algorithm**: Cosine similarity
-   **Authentication**: JWT tokens
-   **Vector Store**: In-memory with numpy arrays

---

### 🔄 **Data Transformations**

```
User Query
    ↓ (JWT validation)
Chat Request
    ↓ (format conversion)
RAG Query
    ↓ (Azure OpenAI)
1536-dim Vector
    ↓ (cosine similarity)
Document Rankings
    ↓ (top-k selection)
Context String
    ↓ (prompt engineering)
LLM Prompt
    ↓ (GPT-4o-mini)
AI Response
    ↓ (format conversion)
Chat Response
    ↓ (JSON serialization)
User Answer
```

---

### 📊 **Request/Response Format**

**Input:**

```json
POST /api/backend/chat
{
  "message": "What are copper deposits?",
  "conversation_id": "optional-id"
}
```

**Output:**

```json
{
    "response": "AI-generated contextual answer...",
    "conversation_id": "session-id",
    "timestamp": "2025-01-17T05:16:43.195421",
    "sources": []
}
```

---

### 🛠️ **Quick Testing Commands**

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:3003/api/backend/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | \
  python -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

# 2. Chat Query
curl -X POST "http://localhost:3003/api/backend/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are copper deposits?"}'

# 3. Direct RAG Query (Module 2)
curl -X POST "http://localhost:3002/rag-query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain geological exploration"}'

# 4. Direct Embedding (Module 2)
curl -X POST "http://localhost:3002/embed" \
  -H "Content-Type: application/json" \
  -d '{"data": ["Sample geological text"]}'
```

---

### 💡 **RAG Benefits**

-   ✅ **Grounded responses** (no hallucinations)
-   ✅ **Real-time knowledge** (no retraining needed)
-   ✅ **Domain expertise** (geological focus)
-   ✅ **Cost efficient** (pay-per-use)
-   ✅ **Scalable** (vector search)

---

### 🎯 **Architecture Ports**

-   **Module 1**: `localhost:8000` (Data Foundation)
-   **Module 2**: `localhost:3002` (Cortex Engine/AI)
-   **Module 3**: `localhost:3003` (Backend Gateway)

---

_For detailed documentation, see: [`docs/rag-pipeline-flow.md`](./rag-pipeline-flow.md)_
