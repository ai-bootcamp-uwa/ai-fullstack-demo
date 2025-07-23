import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple

# Handle imports for both standalone and package usage
try:
    from .config import unified_config
except ImportError:
    from config import unified_config

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, use_snowflake=False):
        """
        Initialize vector store with optional Snowflake backend.
        
        Args:
            use_snowflake (bool): Whether to use Snowflake for vector storage
        """
        # In-memory storage (legacy mode or backup)
        self.vectors = None  # Shape: (n_samples, n_features)
        self.metadata = []   # List of metadata dicts
        self.texts = []      # Store original text for RAG context
        
        # Snowflake backend
        self.use_snowflake = use_snowflake
        self.snowflake_store = None
        
        if use_snowflake:
            self._init_snowflake_backend()

    def _init_snowflake_backend(self):
        """Initialize Snowflake vector storage backend."""
        try:
            try:
                from .snowflake_integration import SnowflakeVectorStore
            except ImportError:
                from snowflake_integration import SnowflakeVectorStore
            
            # Check if Snowflake is configured
            snowflake_config = unified_config.snowflake
            if not snowflake_config or not snowflake_config.is_configured():
                logger.warning("Snowflake not configured, falling back to in-memory storage")
                self.use_snowflake = False
                return
                
            self.snowflake_store = SnowflakeVectorStore()
            
            # Test connection and create schema if needed
            if not self.snowflake_store.test_connection():
                logger.error("Snowflake connection failed, falling back to in-memory storage")
                self.use_snowflake = False
                self.snowflake_store = None
                return
                
            # Ensure schema exists
            if not self.snowflake_store.create_vector_schema():
                logger.error("Failed to create Snowflake schema, falling back to in-memory storage")
                self.use_snowflake = False
                self.snowflake_store = None
                return
                
            logger.info("Snowflake vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake backend: {e}")
            self.use_snowflake = False
            self.snowflake_store = None

    def add_vectors(self, vectors, metadata, texts=None):
        """Add vectors and their metadata to the store."""
        vectors_array = np.array(vectors)
        
        # Always maintain in-memory storage for backward compatibility
        if self.vectors is None:
            self.vectors = vectors_array
        else:
            self.vectors = np.vstack([self.vectors, vectors_array])
        
        self.metadata.extend(metadata)
        
        # Store original texts for RAG context
        if texts:
            self.texts.extend(texts)
        else:
            # If no texts provided, use metadata as fallback
            self.texts.extend([str(meta) for meta in metadata])
        
        # Also store in Snowflake if enabled
        if self.use_snowflake and self.snowflake_store:
            try:
                self._add_vectors_to_snowflake(vectors_array, metadata, texts)
            except Exception as e:
                logger.error(f"Failed to add vectors to Snowflake: {e}")
                # Don't fail the operation, just log the error

    def _add_vectors_to_snowflake(self, vectors, metadata, texts=None):
        """Add vectors to Snowflake storage."""
        for i, (vector, meta) in enumerate(zip(vectors, metadata)):
            text = texts[i] if texts and i < len(texts) else str(meta)
            
            # Prepare metadata for Snowflake
            snowflake_metadata = {
                'original_metadata': meta,
                'text_content': text,
                'vector_dimension': len(vector),
                'created_by': 'hybrid_vector_store'
            }
            
            # Store the embedding
            success = self.snowflake_store.store_embedding(
                text=text,
                embedding=vector.tolist(),  # Convert numpy array to list
                metadata=snowflake_metadata,
                job_id=f"vector_store_{hash(text) % 1000000}"  # Simple job ID
            )
            
            if not success:
                logger.warning(f"Failed to store vector {i} in Snowflake")

    def search(self, query_vector, top_k=5, use_snowflake=None):
        """
        Return indices and metadata of the top_k most similar vectors.
        
        Args:
            query_vector: Query vector for similarity search
            top_k: Number of results to return
            use_snowflake: Override backend choice for this search
            
        Returns:
            List of tuples: (index, similarity_score, metadata)
        """
        # Determine which backend to use
        backend_choice = use_snowflake if use_snowflake is not None else self.use_snowflake
        
        if backend_choice and self.snowflake_store:
            try:
                return self._search_snowflake(query_vector, top_k)
            except Exception as e:
                logger.error(f"Snowflake search failed: {e}, falling back to in-memory")
                # Fall back to in-memory search
        
        return self._search_memory(query_vector, top_k)

    def _search_memory(self, query_vector, top_k=5):
        """Search using in-memory vectors (legacy implementation)."""
        if self.vectors is None or len(self.vectors) == 0:
            return []
        
        # Handle dimension mismatch gracefully
        query_vector = np.array(query_vector)
        if query_vector.shape[0] != self.vectors.shape[1]:
            logger.warning(f"Query vector dimension {query_vector.shape[0]} doesn't match stored vectors {self.vectors.shape[1]}")
            # For demo purposes, pad or truncate to match
            if query_vector.shape[0] < self.vectors.shape[1]:
                # Pad with zeros
                query_vector = np.pad(query_vector, (0, self.vectors.shape[1] - query_vector.shape[0]))
            else:
                # Truncate
                query_vector = query_vector[:self.vectors.shape[1]]
        
        # Normalize vectors
        norm_vectors = self.vectors / np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norm_query = query_vector / np.linalg.norm(query_vector)
        
        # Compute cosine similarity
        similarities = np.dot(norm_vectors, norm_query)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            result_metadata = self.metadata[idx].copy()
            # Add original text to metadata for RAG
            if idx < len(self.texts):
                result_metadata['original_text'] = self.texts[idx]
            results.append((int(idx), float(similarities[idx]), result_metadata))
        
        return results

    def _search_snowflake(self, query_vector, top_k=5):
        """Search using Snowflake vector similarity."""
        query_vector_list = np.array(query_vector).tolist()
        
        # Perform similarity search
        similar_embeddings = self.snowflake_store.similarity_search(
            query_embedding=query_vector_list,
            top_k=top_k
        )
        
        results = []
        for i, result in enumerate(similar_embeddings):
            # Extract information from Snowflake result
            embedding_id = result.get('id', i)
            similarity_score = result.get('similarity_score', 0.0)
            metadata = result.get('metadata', {})
            
            # Format result to match in-memory format
            formatted_metadata = metadata.get('original_metadata', {}) if isinstance(metadata, dict) else {}
            if 'text_content' in metadata:
                formatted_metadata['original_text'] = metadata['text_content']
                
            results.append((embedding_id, similarity_score, formatted_metadata))
        
        return results

    def get_vector_count(self):
        """Get the total number of vectors stored."""
        if self.use_snowflake and self.snowflake_store:
            try:
                # Get count from Snowflake
                stats = self.snowflake_store.get_vector_stats()
                return stats.get('total_embeddings', 0)
            except Exception as e:
                logger.error(f"Failed to get Snowflake vector count: {e}")
        
        # Fall back to in-memory count
        return len(self.vectors) if self.vectors is not None else 0

    def get_storage_info(self):
        """Get information about the storage backend."""
        info = {
            'backend': 'hybrid' if self.use_snowflake else 'memory',
            'memory_vectors': len(self.vectors) if self.vectors is not None else 0,
            'snowflake_enabled': self.use_snowflake,
            'snowflake_connected': self.snowflake_store is not None
        }
        
        if self.use_snowflake and self.snowflake_store:
            try:
                snowflake_stats = self.snowflake_store.get_vector_stats()
                info['snowflake_vectors'] = snowflake_stats.get('total_embeddings', 0)
                info['snowflake_tables'] = snowflake_stats.get('tables_created', False)
            except Exception as e:
                logger.error(f"Failed to get Snowflake storage info: {e}")
                info['snowflake_error'] = str(e)
        
        return info

    def clear(self):
        """Clear all stored vectors from both backends."""
        # Clear in-memory storage
        self.vectors = None
        self.metadata = []
        self.texts = []
        
        # Clear Snowflake storage if enabled
        if self.use_snowflake and self.snowflake_store:
            try:
                # Note: This would require implementing a clear method in SnowflakeVectorStore
                logger.warning("Snowflake clear not implemented - only in-memory storage cleared")
            except Exception as e:
                logger.error(f"Failed to clear Snowflake storage: {e}")

    def save(self, path):
        """Save vectors and metadata to disk (optional, not implemented)."""
        logger.warning("File-based save/load not implemented - data is in Snowflake/memory")
        pass

    def load(self, path):
        """Load vectors and metadata from disk (optional, not implemented)."""
        logger.warning("File-based save/load not implemented - data is in Snowflake/memory")
        pass
