from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Any, Dict, Optional, Union
import numpy as np
from dotenv import load_dotenv
import time
import logging

# Load environment variables from .env file
load_dotenv()

# Handle imports for both standalone and package usage
try:
    from .embedding import EmbeddingGenerator
    from .vector_store import VectorStore
    from .similarity import SimilaritySearch
    from .title_processor import TitleProcessor
    from .config import config, unified_config
    from .snowflake_integration import snowflake_vector_store
except ImportError:
    from embedding import EmbeddingGenerator
    from vector_store import VectorStore
    from similarity import SimilaritySearch
    from title_processor import TitleProcessor
    from config import config, unified_config
    from snowflake_integration import snowflake_vector_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cortex Engine Hybrid API", 
    description="AI/Vector Processing with Azure OpenAI + Snowflake Hybrid System",
    version="2.0.0"
)

# Legacy components (for backward compatibility)
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()
similarity_search = SimilaritySearch(vector_store)

# New hybrid components (Phase 2)
hybrid_embedding_generator = EmbeddingGenerator(use_hybrid=True)
hybrid_vector_store = VectorStore(use_snowflake=True)
hybrid_similarity_search = SimilaritySearch(hybrid_vector_store, use_hybrid=True)
title_processor = TitleProcessor(use_hybrid=True, use_snowflake=True)

# ===== EXISTING PYDANTIC MODELS (unchanged) =====
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

# ===== NEW HYBRID PYDANTIC MODELS =====
class HybridEmbedRequest(BaseModel):
    data: List[str] = Field(..., description="List of texts to embed")
    use_title_processing: bool = Field(False, description="Apply title-specific preprocessing")
    quality_threshold: float = Field(0.3, description="Minimum quality threshold for title processing")

class HybridEmbedResponse(BaseModel):
    embeddings: List[List[float]]
    metadata: List[Dict[str, Any]]
    processing_stats: Dict[str, Any]

class VectorSearchRequest(BaseModel):
    query_vector: Optional[List[float]] = None
    query_text: Optional[str] = None
    query_title: Optional[str] = None
    top_k: int = Field(5, ge=1, le=50)
    use_snowflake: Optional[bool] = None
    preprocess_title: bool = True

class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    search_metadata: Dict[str, Any]

class HybridRAGRequest(BaseModel):
    query: str
    search_type: str = Field("text", description="Search type: 'text' or 'title'")
    use_snowflake: Optional[bool] = None
    compare_backends: bool = False

class HybridRAGResponse(BaseModel):
    result: str
    metadata: Dict[str, Any]

class TitleProcessingRequest(BaseModel):
    titles: List[str]
    quality_threshold: float = Field(0.3, ge=0.0, le=1.0)
    generate_embeddings: bool = True
    store_results: bool = True
    batch_size: int = Field(100, ge=1, le=1000)

class TitleProcessingResponse(BaseModel):
    results: List[Dict[str, Any]]
    stats: Dict[str, Any]

class HybridHealthResponse(BaseModel):
    status: str
    components: Dict[str, Any]
    hybrid_enabled: bool
    overall_health: str

class VectorStatsResponse(BaseModel):
    snowflake_stats: Dict[str, Any]
    connection_status: str

class SystemStatusResponse(BaseModel):
    system_info: Dict[str, Any]
    storage_info: Dict[str, Any]
    processing_capabilities: Dict[str, Any]

# Existing endpoints (unchanged)
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

# New hybrid endpoints
@app.post("/embed/hybrid", response_model=HybridEmbedResponse)
def hybrid_embed_endpoint(request: HybridEmbedRequest):
    """Generate embeddings using hybrid Azure OpenAI configuration with optional title processing."""
    start_time = time.time()
    
    if not hybrid_embedding_generator.is_configured():
        raise HTTPException(status_code=503, detail="Hybrid embedding generator not configured")
    
    try:
        if request.use_title_processing:
            # Use title processor for quality filtering and preprocessing
            results, batch_stats = title_processor.process_batch(
                request.data,
                quality_threshold=request.quality_threshold,
                store_results=request.store_results,
                batch_size=min(len(request.data), 50)  # Limit batch size for API
            )
            
            successful_results = [r for r in results if r.success]
            embeddings = [r.embedding for r in successful_results if r.embedding is not None]
            metadata = [r.metadata for r in successful_results]
            
            processing_stats = {
                "total_texts": len(request.data),
                "processed_texts": batch_stats.successful,
                "skipped_texts": batch_stats.failed,
                "average_quality": batch_stats.average_quality_score,
                "processing_time_ms": int(batch_stats.processing_time_seconds * 1000)
            }
        else:
            # Direct embedding generation
            embeddings = hybrid_embedding_generator.generate_embeddings(request.data)
            metadata = [{"source": "hybrid_embed", "text": text} for text in request.data]
            
            processing_stats = {
                "total_texts": len(request.data),
                "processed_texts": len(embeddings),
                "skipped_texts": 0,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        
        return {
            "embeddings": [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings],
            "metadata": metadata,
            "processing_stats": processing_stats
        }
        
    except Exception as e:
        logger.error(f"Hybrid embedding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

@app.post("/search/vector", response_model=VectorSearchResponse)
def vector_search_endpoint(request: VectorSearchRequest):
    """Perform vector similarity search with multiple query types and backend options."""
    start_time = time.time()
    
    try:
        # Determine search method based on input
        if request.query_vector is not None:
            # Direct vector search
            query_vector = np.array(request.query_vector)
            results = hybrid_similarity_search.search(
                query_vector, 
                top_k=request.top_k, 
                use_snowflake=request.use_snowflake
            )
            query_type = "vector"
            
        elif request.query_text is not None:
            # Text-based search
            results = hybrid_similarity_search.search_by_text(
                request.query_text, 
                top_k=request.top_k, 
                use_snowflake=request.use_snowflake
            )
            query_type = "text"
            
        elif request.query_title is not None:
            # Title-specific search
            results = hybrid_similarity_search.search_titles(
                request.query_title, 
                top_k=request.top_k, 
                use_snowflake=request.use_snowflake,
                preprocess=request.preprocess_title
            )
            query_type = "title"
            
        else:
            raise HTTPException(status_code=400, detail="Must provide query_vector, query_text, or query_title")
        
        search_time = int((time.time() - start_time) * 1000)
        
        # Format results for API response
        formatted_results = []
        for idx, score, metadata in results:
            formatted_results.append({
                "index": idx,
                "similarity_score": score,
                "metadata": metadata
            })
        
        return {
            "results": formatted_results,
            "search_metadata": {
                "query_type": query_type,
                "top_k": request.top_k,
                "results_count": len(formatted_results),
                "search_time_ms": search_time,
                "backend_used": "snowflake" if request.use_snowflake else "memory"
            }
        }
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/rag/hybrid", response_model=HybridRAGResponse)
def hybrid_rag_endpoint(request: HybridRAGRequest):
    """Perform retrieval-augmented generation with hybrid backends and search types."""
    start_time = time.time()
    
    if not hybrid_similarity_search.client:
        raise HTTPException(status_code=503, detail="RAG client not configured")
    
    try:
        if request.compare_backends:
            # Use hybrid RAG for backend comparison
            result = hybrid_similarity_search.hybrid_rag_query(
                request.query,
                search_both_backends=True
            )
        else:
            # Standard RAG query
            result = hybrid_similarity_search.rag_query(
                request.query,
                use_snowflake=request.use_snowflake,
                search_type=request.search_type
            )
        
        rag_time = int((time.time() - start_time) * 1000)
        
        # Add timing information
        result["rag_time_ms"] = rag_time
        
        return {
            "result": result.get("result", ""),
            "metadata": result
        }
        
    except Exception as e:
        logger.error(f"Hybrid RAG failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@app.post("/titles/process", response_model=TitleProcessingResponse)
def title_processing_endpoint(request: TitleProcessingRequest):
    """Process geological titles with quality assessment, preprocessing, and optional embedding generation."""
    start_time = time.time()
    
    if not title_processor.embedding_generator.is_configured() and request.generate_embeddings:
        raise HTTPException(status_code=503, detail="Embedding generator not configured for title processing")
    
    try:
        # Process titles in batch
        results, stats = title_processor.process_batch(
            request.titles,
            quality_threshold=request.quality_threshold,
            store_results=request.store_results,
            batch_size=request.batch_size
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "original_title": result.original_title,
                "processed_title": result.processed_title,
                "quality_score": result.quality_score,
                "success": result.success,
                "error_message": result.error_message,
                "metadata": result.metadata,
                "has_embedding": result.embedding is not None
            })
        
        return {
            "results": formatted_results,
            "stats": {
                "total_titles": stats.total_titles,
                "successful": stats.successful,
                "failed": stats.failed,
                "average_quality_score": stats.average_quality_score,
                "processing_time_seconds": stats.processing_time_seconds,
                "storage_backend": stats.storage_backend,
                "api_processing_time_ms": processing_time
            }
        }
        
    except Exception as e:
        logger.error(f"Title processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Title processing failed: {str(e)}")

@app.get("/health/hybrid", response_model=HybridHealthResponse)
def hybrid_health_check():
    """Comprehensive health check for the hybrid Azure OpenAI + Snowflake system."""
    start_time = time.time()
    
    # Check all configurations
    validation_results = unified_config.validate_all()
    
    # Test Azure OpenAI connection
    azure_health = {
        "configured": validation_results["azure_openai"]["configured"],
        "valid": validation_results["azure_openai"]["valid"],
        "error": validation_results["azure_openai"]["error"]
    }
    
    # Test Snowflake connection and record health check
    snowflake_start = time.time()
    snowflake_connected = snowflake_vector_store.test_connection()
    snowflake_response_time = int((time.time() - snowflake_start) * 1000)
    
    snowflake_health = {
        "configured": validation_results["snowflake"]["configured"],
        "valid": validation_results["snowflake"]["valid"],
        "connected": snowflake_connected,
        "response_time_ms": snowflake_response_time,
        "error": validation_results["snowflake"]["error"]
    }
    
    # Record health check in Snowflake if possible
    if snowflake_connected:
        snowflake_vector_store.record_health_check(
            component="hybrid_health_endpoint",
            status="SUCCESS" if azure_health["valid"] and snowflake_health["valid"] else "PARTIAL",
            response_time_ms=int((time.time() - start_time) * 1000),
            metadata={
                "azure_configured": azure_health["configured"],
                "snowflake_configured": snowflake_health["configured"],
                "hybrid_enabled": unified_config.hybrid.is_hybrid_enabled()
            }
        )
    
    # Determine overall health
    overall_health = "HEALTHY"
    if not azure_health["valid"] or not snowflake_health["valid"]:
        overall_health = "DEGRADED"
    if not azure_health["configured"] and not snowflake_health["configured"]:
        overall_health = "UNHEALTHY"
    
    response_time_ms = int((time.time() - start_time) * 1000)
    
    return {
        "status": "ok",
        "components": {
            "azure_openai": azure_health,
            "snowflake": snowflake_health,
            "hybrid_features": {
                "enabled": unified_config.hybrid.is_hybrid_enabled(),
                "vector_storage_enabled": unified_config.hybrid.enable_snowflake_vectors,
                "title_embeddings_enabled": unified_config.hybrid.enable_title_embeddings
            },
            "system": {
                "response_time_ms": response_time_ms,
                "ready_for_hybrid": unified_config.is_ready_for_hybrid()
            }
        },
        "hybrid_enabled": unified_config.hybrid.is_hybrid_enabled(),
        "overall_health": overall_health
    }

@app.get("/config/hybrid")
def get_hybrid_configuration():
    """Get detailed hybrid system configuration (without sensitive data)."""
    validation_results = unified_config.validate_all()
    
    return {
        "azure_openai": {
            "endpoint": unified_config.azure_openai.endpoint,
            "api_version": unified_config.azure_openai.api_version,
            "embedding_model": unified_config.azure_openai.embedding_model,
            "chat_model": unified_config.azure_openai.chat_model,
            "configured": validation_results["azure_openai"]["configured"],
            "valid": validation_results["azure_openai"]["valid"]
        },
        "snowflake": {
            "account": unified_config.snowflake.account,
            "database": unified_config.snowflake.database,
            "schema": unified_config.snowflake.schema,
            "warehouse": unified_config.snowflake.warehouse,
            "vector_dimension": unified_config.snowflake.vector_dimension,
            "batch_size": unified_config.snowflake.batch_size,
            "configured": validation_results["snowflake"]["configured"],
            "valid": validation_results["snowflake"]["valid"]
        },
        "hybrid_system": {
            "features_enabled": unified_config.hybrid.enable_hybrid_features,
            "snowflake_vectors_enabled": unified_config.hybrid.enable_snowflake_vectors,
            "title_embeddings_enabled": unified_config.hybrid.enable_title_embeddings,
            "embedding_batch_size": unified_config.hybrid.embedding_batch_size,
            "search_result_limit": unified_config.hybrid.search_result_limit,
            "ready_for_hybrid": unified_config.is_ready_for_hybrid()
        }
    }

@app.get("/vectors/stats", response_model=VectorStatsResponse)
def get_vector_statistics():
    """Get statistics about stored vectors and Snowflake vector operations."""
    if not unified_config.hybrid.is_hybrid_enabled():
        raise HTTPException(status_code=404, detail="Hybrid features are not enabled")
    
    if not snowflake_vector_store.test_connection():
        return {
            "snowflake_stats": {"error": "Snowflake connection failed"},
            "connection_status": "FAILED"
        }
    
    stats = snowflake_vector_store.get_vector_statistics()
    
    return {
        "snowflake_stats": stats,
        "connection_status": "CONNECTED" if "error" not in stats else "ERROR"
    }

@app.get("/admin/hybrid/status")
def get_detailed_hybrid_status():
    """Detailed status information for hybrid system administration."""
    if not unified_config.hybrid.is_hybrid_enabled():
        raise HTTPException(status_code=404, detail="Hybrid features are not enabled")
    
    # Get comprehensive system status
    validation_results = unified_config.validate_all()
    vector_stats = snowflake_vector_store.get_vector_statistics()
    
    # Test connections
    azure_test_start = time.time()
    azure_configured = unified_config.azure_openai.is_configured()
    azure_response_time = int((time.time() - azure_test_start) * 1000)
    
    snowflake_test_start = time.time()
    snowflake_connected = snowflake_vector_store.test_connection()
    snowflake_response_time = int((time.time() - snowflake_test_start) * 1000)
    
    return {
        "system_status": {
            "timestamp": time.time(),
            "hybrid_ready": unified_config.is_ready_for_hybrid(),
            "components_health": {
                "azure_openai": {
                    "configured": azure_configured,
                    "response_time_ms": azure_response_time,
                    "status": "READY" if azure_configured else "NOT_CONFIGURED"
                },
                "snowflake": {
                    "connected": snowflake_connected,
                    "response_time_ms": snowflake_response_time,
                    "status": "CONNECTED" if snowflake_connected else "DISCONNECTED"
                }
            }
        },
        "configuration": validation_results,
        "vector_statistics": vector_stats,
        "feature_flags": {
            "hybrid_features": unified_config.hybrid.enable_hybrid_features,
            "snowflake_vectors": unified_config.hybrid.enable_snowflake_vectors,
            "title_embeddings": unified_config.hybrid.enable_title_embeddings
        }
    }

@app.get("/system/status", response_model=SystemStatusResponse)
def system_status_endpoint():
    """Get comprehensive system status including all hybrid components."""
    try:
        # Get storage information
        memory_storage = vector_store.get_storage_info()
        hybrid_storage = hybrid_vector_store.get_storage_info()
        
        # Get search statistics
        search_stats = hybrid_similarity_search.get_search_stats()
        
        # Get processor statistics
        processor_stats = title_processor.get_processing_stats()
        
        # Get configuration validation
        config_validation = unified_config.validate_all()
        
        return {
            "system_info": {
                "api_version": "2.0.0",
                "hybrid_ready": unified_config.is_ready_for_hybrid(),
                "configuration_status": config_validation
            },
            "storage_info": {
                "legacy_storage": memory_storage,
                "hybrid_storage": hybrid_storage,
                "vector_counts": {
                    "memory": vector_store.get_vector_count(),
                    "hybrid": hybrid_vector_store.get_vector_count()
                }
            },
            "processing_capabilities": {
                "embedding_generation": {
                    "legacy_configured": embedding_generator.is_configured(),
                    "hybrid_configured": hybrid_embedding_generator.is_configured(),
                    "dimension": hybrid_embedding_generator.get_embedding_dimension()
                },
                "similarity_search": search_stats,
                "title_processing": processor_stats,
                "rag_available": search_stats.get("rag_client_available", False)
            }
        }
        
    except Exception as e:
        logger.error(f"System status failed: {e}")
        raise HTTPException(status_code=500, detail=f"System status unavailable: {str(e)}")

@app.get("/admin/reset")
def reset_system():
    """Reset in-memory storage (admin endpoint)."""
    try:
        # Clear memory storage
        vector_store.clear()
        
        # Note: We don't clear Snowflake storage for safety
        logger.info("System reset completed - memory storage cleared")
        
        return {
            "status": "success",
            "message": "Memory storage cleared",
            "note": "Snowflake storage preserved for safety"
        }
        
    except Exception as e:
        logger.error(f"System reset failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

@app.get("/admin/config/validate")
def validate_configuration():
    """Validate all system configurations (admin endpoint)."""
    try:
        validation_results = unified_config.validate_all()
        
        # Test actual connections
        azure_test = hybrid_embedding_generator.is_configured()
        snowflake_test = unified_config.snowflake.is_configured() and snowflake_vector_store.test_connection()
        
        return {
            "configuration_validation": validation_results,
            "connection_tests": {
                "azure_openai": azure_test,
                "snowflake": snowflake_test
            },
            "system_ready": unified_config.is_ready_for_hybrid(),
            "recommendations": {
                "azure_openai": "Configure AZURE_OPENAI_* environment variables" if not azure_test else "✅ Ready",
                "snowflake": "Configure SNOWFLAKE_* environment variables" if not snowflake_test else "✅ Ready"
            }
        }
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
