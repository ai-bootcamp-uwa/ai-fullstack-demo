from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
import numpy as np

from .embedding import EmbeddingGenerator
from .vector_store import VectorStore
from .similarity import SimilaritySearch
from .config import config

app = FastAPI(title="Cortex Engine API", description="AI/Vector Processing with Azure OpenAI")

# In-memory state for demonstration
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()
similarity_search = SimilaritySearch(vector_store)

class EmbedRequest(BaseModel):
    data: List[Any]

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]

class SimilaritySearchRequest(BaseModel):
    query_vector: List[float]
    top_k: int = 5

class SimilaritySearchResponse(BaseModel):
    results: List[Any]

class RAGQueryRequest(BaseModel):
    query: str

class RAGQueryResponse(BaseModel):
    result: Any
    query: str

@app.get("/health")
def health_check():
    """Basic health check with configuration status."""
    is_configured, error_msg = config.validate_config()

    return {
        "status": "ok",
        "azure_openai_configured": config.is_configured(),
        "embedding_model": config.embedding_model,
        "chat_model": config.chat_model,
        "configuration_valid": is_configured,
        "error": error_msg if not is_configured else None
    }

@app.get("/config")
def get_configuration():
    """Get detailed configuration information (without sensitive data)."""
    is_configured, error_msg = config.validate_config()

    return {
        "endpoint": config.endpoint,
        "api_version": config.api_version,
        "embedding_model": config.embedding_model,
        "chat_model": config.chat_model,
        "rate_limits": {
            "embedding_requests_per_minute": config.max_embedding_requests_per_minute,
            "embedding_tokens_per_minute": config.max_embedding_tokens_per_minute
        },
        "retry_config": {
            "max_retries": config.max_retries,
            "retry_delay_seconds": config.retry_delay_seconds
        },
        "is_configured": config.is_configured(),
        "configuration_valid": is_configured,
        "validation_error": error_msg if not is_configured else None
    }

@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    embeddings = embedding_generator.generate_embeddings(request.data)

    # Convert data to strings for storage
    texts = [str(item) for item in request.data]
    metadata = [{"source": "embed", "text": text, "model": config.embedding_model} for text in texts]

    # Add to vector store with original texts for RAG
    vector_store.add_vectors(embeddings, metadata, texts)

    return {"embeddings": embeddings.tolist()}

@app.post("/similarity-search", response_model=SimilaritySearchResponse)
def similarity_search_endpoint(request: SimilaritySearchRequest):
    query_vector = np.array(request.query_vector)
    results = similarity_search.search(query_vector, top_k=request.top_k)
    return {"results": results}

@app.post("/rag-query", response_model=RAGQueryResponse)
def rag_query_endpoint(request: RAGQueryRequest):
    result = similarity_search.rag_query(request.query)
    return result
