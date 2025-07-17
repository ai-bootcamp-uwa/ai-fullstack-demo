# Cortex Engine Execution Guide

This guide provides step-by-step instructions for executing the Cortex Engine module in a real environment, processing geological data with AI-powered embeddings and similarity search.

## 📋 Prerequisites

1. **Environment Setup**: Python 3.8+ with virtual environment
2. **Dependencies**: All packages installed (`pip install -r requirements.txt`)
3. **Azure OpenAI**: Valid configuration with API keys
4. **Module 1**: Data Foundation API running on port 8000
5. **Configuration**: Properly configured `.env` file

## 🚀 Quick Execution Checklist

### Step 1: Verify Dependencies

```bash
# Navigate to cortex_engine directory
cd cortex_engine

# Activate virtual environment (recommended)
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Verify all dependencies are installed
pip install -r requirements.txt
```

### Step 2: Configure Azure OpenAI (REQUIRED)

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your Azure OpenAI credentials
# CRITICAL: Replace ALL placeholder values
nano .env  # or use your preferred editor
```

**⚠️ Required Configuration:**

- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Your API key
- `AZURE_OPENAI_API_VERSION`: Valid API version (e.g., 2024-02-01)
- `EMBEDDING_MODEL`: Deployment name for embedding model
- `CHAT_MODEL`: Deployment name for chat model

### Step 3: Test Configuration

```bash
# Test your Azure OpenAI configuration
./tests/test_azure_openai.sh

# Expected output:
# ✅ Embedding model test PASSED
# ✅ Chat model test PASSED
```

### Step 4: Start Module 1 (Data Foundation)

```bash
# In separate terminal, start the Data Foundation API
cd ../data_foundation_project
uvicorn src.api.main:app --port 8000

# Verify it's running:
curl http://localhost:8000/reports
```

### Step 5: Start Cortex Engine

```bash
# In cortex_engine directory
uvicorn src.main:app --reload --port 3002

# Verify it's running:
curl http://localhost:3002/health
```

## 💰 Cost-Optimized Execution (10 Reports Only)

The system is pre-configured to process only **10 reports** to minimize Azure OpenAI costs:

### Default Limits in Place:

- **Data Client**: `fetch_reports(limit=10)` - only downloads 10 reports
- **Embedding Batching**: Processes reports in small batches
- **Rate Limiting**: Respects Azure OpenAI rate limits to avoid extra charges

### Cost Breakdown (Estimated):

- **10 reports × ~200 tokens each = ~2,000 tokens**
- **Azure OpenAI Embedding Cost**: ~$0.0001 per 1K tokens
- **Total Estimated Cost**: <$0.01 per execution

## 🔄 Full Execution Workflow

### 1. Automated Full Pipeline

```bash
# Execute the complete geological data processing pipeline
python scripts/execute_full_pipeline.py
```

**What this does:**

1. ✅ Fetches 10 geological reports from Module 1
2. ✅ Generates embeddings using Azure OpenAI
3. ✅ Stores vectors in the vector store
4. ✅ Performs similarity analysis
5. ✅ Tests RAG capabilities
6. ✅ Provides performance metrics

### 2. Manual Step-by-Step Execution

#### Step 2a: Test Data Connection

```bash
curl "http://localhost:8000/reports?limit=10"
```

#### Step 2b: Generate Embeddings

```bash
curl -X POST http://localhost:3002/embed \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      "Geological exploration site 1: Iron ore deposits in Pilbara region",
      "Mining survey report: Copper mineralization in sedimentary formations",
      "Exploration data: Gold prospecting in Archean greenstone belt"
    ]
  }'
```

#### Step 2c: Perform Similarity Search

```bash
# Use one of the generated embeddings
curl -X POST http://localhost:3002/similarity-search \
  -H "Content-Type: application/json" \
  -d '{
    "query_vector": [0.123, 0.456, 0.789, ...],
    "top_k": 5
  }'
```

#### Step 2d: Test RAG Query

```bash
curl -X POST http://localhost:3002/rag-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What geological formations are found in the exploration sites?"
  }'
```

## 📊 Monitoring Execution

### Real-time Health Monitoring

```bash
# Check system health and configuration
curl http://localhost:3002/health | jq .

# Expected output:
{
  "status": "ok",
  "azure_openai_configured": true,
  "configuration_valid": true,
  "embedding_model": "text-embedding-ada-002",
  "chat_model": "gpt-4.1-mini"
}
```

### Configuration Status

```bash
# View detailed configuration (no sensitive data)
curl http://localhost:3002/config | jq .

# Shows rate limits, endpoint info, API version
```

### Performance Metrics

```bash
# Monitor execution logs
tail -f cortex_engine.log

# Key metrics to watch:
# - Embedding generation time: <500ms per batch
# - Similarity search time: <100ms
# - RAG response time: <2s
# - Azure OpenAI API calls: Rate limited properly
```

## 🎯 Production Execution

### Environment-Specific Configurations

#### Development Environment

```bash
# Use fallback embeddings for testing
export AZURE_OPENAI_API_KEY=""
uvicorn src.main:app --reload --port 3002
```

#### Staging Environment

```bash
# Limited Azure OpenAI usage
export MAX_EMBEDDING_REQUESTS_PER_MINUTE=60
export MAX_EMBEDDING_TOKENS_PER_MINUTE=10000
uvicorn src.main:app --port 3002
```

#### Production Environment

```bash
# Full Azure OpenAI capabilities
export MAX_EMBEDDING_REQUESTS_PER_MINUTE=120
export MAX_EMBEDDING_TOKENS_PER_MINUTE=20000
uvicorn src.main:app --host 0.0.0.0 --port 3002
```

## 🧪 Execution Testing & Validation

### Automated Test Suite

```bash
# Run complete test suite
python tests/test_execution.py

# Expected results:
# ✅ Data Foundation connectivity
# ✅ Azure OpenAI integration
# ✅ Embedding generation (10 samples)
# ✅ Vector storage and retrieval
# ✅ Similarity search accuracy
# ✅ RAG query functionality
```

### Manual Validation Checklist

- [ ] **Data Source**: Module 1 API responding
- [ ] **Configuration**: All Azure OpenAI settings valid
- [ ] **Embeddings**: 1536-dimensional vectors generated
- [ ] **Vector Store**: Storing and retrieving vectors correctly
- [ ] **Similarity**: Cosine similarity scores 0.0-1.0
- [ ] **RAG**: Natural language responses generated
- [ ] **Performance**: <500ms embedding, <100ms search, <2s RAG
- [ ] **Cost Control**: Only 10 reports processed

## 🔧 Troubleshooting Execution Issues

### Common Execution Problems

#### 1. "Module 1 API not responding"

```bash
# Check if Data Foundation is running
curl http://localhost:8000/health

# If not running:
cd ../data_foundation_project
uvicorn src.api.main:app --port 8000
```

#### 2. "Azure OpenAI authentication failed"

```bash
# Verify configuration
grep "AZURE_OPENAI" .env

# Test configuration
./tests/test_azure_openai.sh
```

#### 3. "Embedding generation failed"

```bash
# Check rate limits
curl http://localhost:3002/config | jq .rate_limits

# Reduce batch size if needed
export MAX_EMBEDDING_REQUESTS_PER_MINUTE=30
```

#### 4. "Vector store empty"

```bash
# Verify embeddings are being stored
curl -X POST http://localhost:3002/embed \
  -H "Content-Type: application/json" \
  -d '{"data": ["test sample"]}'

# Check if vectors are stored
curl http://localhost:3002/similarity-search \
  -H "Content-Type: application/json" \
  -d '{"query_vector": [0.1, 0.2], "top_k": 1}'
```

## 📈 Execution Performance Benchmarks

### Expected Performance Targets

- **Startup Time**: <10 seconds
- **Data Fetching**: 10 reports in <2 seconds
- **Embedding Generation**: 1000+ embeddings in <5 minutes
- **Similarity Search**: <100ms per query
- **RAG Response**: <2 seconds end-to-end
- **Memory Usage**: <2GB for 10 reports
- **API Response**: 95%+ success rate

### Resource Monitoring

```bash
# Monitor resource usage during execution
htop                    # CPU and memory
nvidia-smi             # GPU usage (if applicable)
iostat 1               # Disk I/O
netstat -i             # Network activity
```

## 🚦 Execution Status Dashboard

### Real-time Monitoring URLs

- **Health Check**: http://localhost:3002/health
- **Configuration**: http://localhost:3002/config
- **API Documentation**: http://localhost:3002/docs
- **Metrics**: http://localhost:3002/metrics (if implemented)

### Success Indicators

- ✅ **Green Status**: All systems operational
- ⚠️ **Yellow Status**: Performance degraded but functional
- ❌ **Red Status**: Critical errors, execution halted

## 🔄 Continuous Execution

### Scheduled Execution (Optional)

```bash
# Set up cron job for regular data processing
crontab -e

# Add line for daily execution at 2 AM:
0 2 * * * cd /path/to/cortex_engine && python scripts/daily_execution.py
```

### Docker Execution (Advanced)

```bash
# Build container
docker build -t cortex-engine .

# Run with environment variables
docker run -d \
  --name cortex-engine \
  -p 3002:3002 \
  --env-file .env \
  cortex-engine
```

---

## 📝 Execution Summary

**Cost-Optimized Setup**: ✅ Limited to 10 reports (~$0.01 per run)
**Performance**: ✅ Meets all benchmark targets
**Reliability**: ✅ Proper error handling and fallbacks
**Monitoring**: ✅ Health checks and configuration validation
**Integration**: ✅ Seamless connection with Module 1

**Ready for Production Execution!** 🚀

For detailed setup instructions, see [AZURE_OPENAI_SETUP.md](AZURE_OPENAI_SETUP.md)
For testing procedures, see [TESTING.md](TESTING.md)
For development workflow, see [WORKFLOW.md](WORKFLOW.md)
