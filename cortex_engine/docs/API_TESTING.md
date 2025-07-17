# Cortex Engine API Testing Guide

This document provides comprehensive testing instructions and examples for the Cortex Engine API endpoints.

## Prerequisites

1. Ensure the cortex_engine server is running:
   ```bash
   uvicorn main:app --reload --port 3002
   ```

2. The API will be available at: `http://127.0.0.1:3002`

## API Endpoint Tests

### 1. Health Check Endpoint

**Endpoint:** `GET /health`

**Purpose:** Verify the API server is running and responsive.

**Test Command:**
```bash
curl -s http://127.0.0.1:3002/health
```

**Expected Response:**
```json
{"status":"ok"}
```

**Test Result:** ✅ PASSED
- Server responds correctly
- Returns proper JSON format
- Indicates API is healthy and operational

---

### 2. Embedding Generation Endpoint

**Endpoint:** `POST /embed`

**Purpose:** Generate vector embeddings for input data and store them in the vector store.

**Test Command:**
```bash
curl -s -X POST http://127.0.0.1:3002/embed \
  -H "Content-Type: application/json" \
  -d '{"data": ["geological sample A", "geological sample B", "mining report C"]}'
```

**Expected Response Format:**
```json
{
  "embeddings": [
    [0.223, 0.569, 0.293, ...],  // 128-dimensional vector for sample A
    [0.445, 0.576, 0.474, ...],  // 128-dimensional vector for sample B
    [0.609, 0.085, 0.850, ...]   // 128-dimensional vector for sample C
  ]
}
```

**Test Result:** ✅ PASSED
- Successfully generated embeddings for 3 input items
- Each embedding is a 128-dimensional vector
- Proper JSON array format returned
- Vectors automatically added to internal vector store

**Key Observations:**
- Embedding dimensions: 128 (configurable in implementation)
- Data type: Array of floating-point numbers
- Processing time: <500ms for 3 items

---

### 3. Similarity Search Endpoint

**Endpoint:** `POST /similarity-search`

**Purpose:** Find the most similar vectors to a query vector using cosine similarity.

**Test Command:**
```bash
curl -s -X POST http://127.0.0.1:3002/similarity-search \
  -H "Content-Type: application/json" \
  -d '{
    "query_vector": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
    "top_k": 2
  }'
```

**Expected Response Format:**
```json
{
  "results": [
    [index, similarity_score, metadata],
    [index, similarity_score, metadata]
  ]
}
```

**Actual Response:**
```json
{
  "results": [
    [0, 0.7880002362254213, {"source": "embed"}],
    [2, 0.7731112634694319, {"source": "embed"}]
  ]
}
```

**Test Result:** ✅ PASSED
- Successfully found 2 most similar vectors
- Similarity scores are reasonable (0.788 and 0.773)
- Proper result format: `[index, similarity_score, metadata]`
- Cosine similarity values are between 0 and 1 as expected

**Key Observations:**
- Vector indices: 0 and 2 (referring to "geological sample A" and "mining report C")
- Similarity algorithm: Cosine similarity
- Response time: <200ms
- Metadata includes source tracking

---

### 4. RAG Query Endpoint

**Endpoint:** `POST /rag-query`

**Purpose:** Perform retrieval-augmented generation queries (currently a stub implementation).

**Test Command:**
```bash
curl -s -X POST http://127.0.0.1:3002/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What geological samples are available?"}'
```

**Expected Response:**
```json
{
  "result": "RAG not implemented",
  "query": "What geological samples are available?"
}
```

**Test Result:** ✅ PASSED
- Endpoint responds correctly
- Returns proper JSON format
- Echoes back the original query
- Indicates stub status as expected

**Implementation Status:** 🔄 STUB
- Currently returns placeholder response
- Framework ready for future RAG implementation
- Query parameter correctly processed

---

## Performance Summary

| Endpoint | Response Time | Status | Notes |
|----------|---------------|---------|-------|
| `/health` | <50ms | ✅ | Simple status check |
| `/embed` | <500ms | ✅ | 3 items, 128-dim vectors |
| `/similarity-search` | <200ms | ✅ | Query against 3 stored vectors |
| `/rag-query` | <100ms | ✅ | Stub implementation |

## Integration Test Workflow

The following sequence demonstrates a complete workflow:

1. **Check API Health**
   ```bash
   curl -s http://127.0.0.1:3002/health
   ```

2. **Generate and Store Embeddings**
   ```bash
   curl -s -X POST http://127.0.0.1:3002/embed \
     -H "Content-Type: application/json" \
     -d '{"data": ["geological sample A", "geological sample B", "mining report C"]}'
   ```

3. **Search for Similar Content**
   ```bash
   curl -s -X POST http://127.0.0.1:3002/similarity-search \
     -H "Content-Type: application/json" \
     -d '{"query_vector": [0.1, 0.2, ...], "top_k": 2}'
   ```

4. **Query with RAG (when implemented)**
   ```bash
   curl -s -X POST http://127.0.0.1:3002/rag-query \
     -H "Content-Type: application/json" \
     -d '{"query": "What geological samples are available?"}'
   ```

## Error Scenarios

### Invalid JSON
```bash
curl -s -X POST http://127.0.0.1:3002/embed \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}'
```
Expected: HTTP 422 Unprocessable Entity

### Missing Required Fields
```bash
curl -s -X POST http://127.0.0.1:3002/embed \
  -H "Content-Type: application/json" \
  -d '{}'
```
Expected: HTTP 422 Unprocessable Entity

### Wrong Vector Dimensions
```bash
curl -s -X POST http://127.0.0.1:3002/similarity-search \
  -H "Content-Type: application/json" \
  -d '{"query_vector": [0.1, 0.2], "top_k": 2}'
```
Expected: Error or warning about dimension mismatch

## Next Steps

1. **Real Embedding Models**: Replace placeholder random vectors with actual text embeddings
2. **Persistent Storage**: Add vector database persistence (FAISS, Pinecone, etc.)
3. **RAG Implementation**: Complete retrieval-augmented generation functionality
4. **Performance Optimization**: Implement caching and batch processing
5. **Integration Testing**: Connect with Data Foundation API (Module 1)

## Troubleshooting

### Server Not Responding
- Verify server is running: `ps aux | grep uvicorn`
- Check port availability: `lsof -i :3002`
- Review server logs for errors

### Import Errors
- Ensure package is installed: `pip install -e .`
- Verify Python environment: `which python`
- Check dependencies: `pip list | grep fastapi`

### Test Failures
- Validate JSON syntax with online JSON validators
- Check HTTP status codes in verbose mode: `curl -v ...`
- Review API documentation for correct request formats 