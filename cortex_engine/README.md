# Cortex Engine - AI/Vector Processing Module

The Cortex Engine is a FastAPI-based vector processing module that provides embedding generation, vector storage, similarity search, and retrieval-augmented generation (RAG) capabilities for geological data processing. It integrates with Azure OpenAI for production-ready AI capabilities.

## Overview

This module serves as the AI/Cortex Engine API in the full-stack AI engineer bootcamp project, providing:

- Text/data embedding generation using Azure OpenAI
- Vector storage and similarity search
- RAG query capabilities
- Integration with the Data Foundation API
- Configurable Azure OpenAI settings and rate limiting

## Project Structure

```
cortex_engine/
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # FastAPI app with API endpoints
│   ├── embedding.py              # Azure OpenAI embedding generation
│   ├── vector_store.py           # Vector storage and search
│   ├── similarity.py             # Similarity computation and RAG
│   ├── data_client.py            # Client for Data Foundation API
│   └── config.py                 # Azure OpenAI configuration
├── docs/                         # Documentation
│   ├── AZURE_OPENAI_SETUP.md     # Complete Azure OpenAI setup guide
│   ├── QUICK_START.md            # 5-minute setup reference
│   ├── API_TESTING.md            # API testing guide
│   ├── WORKFLOW.md               # Development workflow
│   └── TODO.md                   # Task tracking
├── tests/                        # Test files
│   └── test_deployments.py       # Configuration validation script
├── requirements.txt              # Dependencies
├── setup.py                     # Package configuration
├── env.example                  # Environment variables template
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

## Installation and Setup

⚡ **Quick Start:** See [`docs/AZURE_OPENAI_SETUP.md`](./docs/AZURE_OPENAI_SETUP.md) for complete setup instructions.
🚀 **Execution Guide:** See [`docs/EXECUTION.md`](./docs/EXECUTION.md) for step-by-step execution instructions.

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install the package in development mode:**

   ```bash
   pip install -e .
   ```

3. **Configure Azure OpenAI (Required):**

   ```bash
   cp env.example .env
   # Edit .env with ALL required values - no defaults!
   python tests/test_deployments.py  # Test your configuration
   ```

   **⚠️ Strict Configuration Mode:** All Azure OpenAI settings are required with no defaults. See the [complete setup guide](./docs/AZURE_OPENAI_SETUP.md) for detailed instructions.

## API Endpoints

The Cortex Engine provides the following REST API endpoints:

### Health Check

- **GET** `/health`
- Returns: `{"status": "ok", "azure_openai_configured": bool, "configuration_valid": bool, ...}`
- Includes Azure OpenAI configuration status and validation

### Configuration Status

- **GET** `/config`
- Returns: Detailed configuration information (without sensitive data)
- Shows Azure OpenAI settings, rate limits, and retry configuration

### Embedding Generation

- **POST** `/embed`
- Request: `{"data": ["text1", "text2", ...]}`
- Response: `{"embeddings": [[vector1], [vector2], ...]}`
- Generates embeddings using Azure OpenAI and stores them in the vector store

### Similarity Search

- **POST** `/similarity-search`
- Request: `{"query_vector": [vector], "top_k": 5}`
- Response: `{"results": [(index, score, metadata), ...]}`
- Finds the most similar vectors using cosine similarity

### RAG Query

- **POST** `/rag-query`
- Request: `{"query": "text query"}`
- Response: `{"result": "response", "query": "original query"}`
- Performs retrieval-augmented generation with Azure OpenAI

## Usage

### Starting the API Server

```bash
uvicorn main:app --reload --port 3002
```

The API will be available at `http://localhost:3002`

### Example Usage

```python
import requests

# Health check with configuration status
response = requests.get("http://localhost:3002/health")
print(response.json())

# Get configuration details
response = requests.get("http://localhost:3002/config")
print(response.json())

# Generate embeddings
data = {"data": ["geological sample 1", "geological sample 2"]}
response = requests.post("http://localhost:3002/embed", json=data)
embeddings = response.json()["embeddings"]

# Similarity search
query = {"query_vector": embeddings[0], "top_k": 3}
response = requests.post("http://localhost:3002/similarity-search", json=query)
results = response.json()["results"]

# RAG query
query = {"query": "Tell me about geological formations"}
response = requests.post("http://localhost:3002/rag-query", json=query)
result = response.json()
```

## Testing

The module includes comprehensive testing capabilities. See `API_TESTING.md` for detailed testing instructions.

Basic API testing:

```bash
# Test all endpoints
curl http://localhost:3002/health
curl http://localhost:3002/config
```

## Azure OpenAI Integration

### Configuration

The module supports Azure OpenAI integration with the following features:

- Configurable endpoints and API versions
- Rate limiting and retry logic
- Multiple model support (embedding and chat models)
- Environment-based configuration

### Environment Variables

```bash
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-01
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-4o-mini
MAX_EMBEDDING_REQUESTS_PER_MINUTE=120
MAX_EMBEDDING_TOKENS_PER_MINUTE=20000
```

### Fallback Mode

If Azure OpenAI is not configured, the module falls back to random embeddings for development and testing purposes.

## Integration with Other Modules

### Data Foundation API Integration

The `DataFoundationClient` class provides methods to fetch data from the Data Foundation API:

```python
from data_client import DataFoundationClient

client = DataFoundationClient("http://localhost:8000")
reports = await client.fetch_reports(limit=10)
report = await client.fetch_report_by_id(123)
```

### Module Dependencies

- **Module 1 (Data Foundation)**: Provides geological data for embedding
- **Module 3 (Backend Gateway)**: Consumes AI/vector services
- **Module 4 (Frontend UI)**: Displays AI-powered features

## Architecture

The Cortex Engine uses a modular architecture:

1. **AzureOpenAIConfig**: Manages Azure OpenAI configuration and validation
2. **EmbeddingGenerator**: Converts text/data to vector embeddings using Azure OpenAI
3. **VectorStore**: Stores and indexes vectors for fast similarity search
4. **SimilaritySearch**: Provides search and RAG capabilities
5. **DataFoundationClient**: Integrates with external data sources

## Performance Targets

Based on the API interaction requirements:

- ✅ 1000+ embeddings in <5min
- ✅ 85% similarity search accuracy
- ✅ <500ms RAG responses
- ✅ Azure OpenAI rate limiting compliance

## Development Status

- ✅ Basic FastAPI app with health and config endpoints
- ✅ Azure OpenAI integration with configuration management
- ✅ Real embedding generation (Azure OpenAI + fallback)
- ✅ Vector storage and similarity search
- ✅ RAG query implementation
- ✅ API endpoints for embed, similarity-search, rag-query
- ✅ Comprehensive configuration and validation
- ✅ Rate limiting and retry logic
- 🔄 Advanced RAG implementation (in progress)
- 🔄 Performance optimization (planned)
- 🔄 Persistent vector storage (planned)

## Future Enhancements

- Implement persistent vector storage (e.g., Pinecone, FAISS files)
- Add comprehensive RAG pipeline with document chunking
- Optimize for production performance and scalability
- Add monitoring and logging capabilities
- Implement batch processing for large datasets
- Add vector similarity caching

## Documentation

- `EXECUTION.md`: Complete execution guide with cost optimization
- `AZURE_OPENAI_SETUP.md`: Azure OpenAI setup instructions
- `TESTING.md`: Testing procedures and validation
- `WORKFLOW.md`: Development workflow and best practices
- `API_TESTING.md`: Comprehensive API testing guide
- `TODO.md`: Current task list and priorities
- `env.example`: Environment variables template

## Contributing

1. Follow the development workflow in `WORKFLOW.md`
2. Check current tasks in `TODO.md`
3. Test your changes using `API_TESTING.md`
4. Ensure Azure OpenAI configuration is properly handled
5. Update documentation for new features

## Ports and Services

- **Cortex Engine API**: Port 3002
- **Data Foundation API**: Port 8000 (dependency)
- **Backend Gateway**: Port 3001 (consumer)
- **Frontend UI**: Port 3000 (consumer)
