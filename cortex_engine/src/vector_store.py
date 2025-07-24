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
    def __init__(self, use_snowflake=True):
        """
        Initialize vector store with Snowflake backend only.
        Raises RuntimeError if Snowflake is not configured or available.
        """
        self.use_snowflake = use_snowflake
        self.snowflake_store = None
        self._init_snowflake_backend()

    def _init_snowflake_backend(self):
        """Initialize Snowflake vector storage backend. Raise error if unavailable."""
        try:
            try:
                from .snowflake_integration import SnowflakeVectorStore
            except ImportError:
                from snowflake_integration import SnowflakeVectorStore

            # Check if Snowflake is configured
            snowflake_config = unified_config.snowflake
            if not snowflake_config or not snowflake_config.is_configured():
                logger.error("Snowflake not configured. Aborting startup.")
                raise RuntimeError("Snowflake vector storage is required but not configured!")

            self.snowflake_store = SnowflakeVectorStore()

            # Test connection and create schema if needed
            if not self.snowflake_store.test_connection():
                logger.error("Snowflake connection failed. Aborting startup.")
                raise RuntimeError("Snowflake vector storage is required but connection failed!")

            if not self.snowflake_store.create_vector_schema():
                logger.error("Failed to create Snowflake schema. Aborting startup.")
                raise RuntimeError("Snowflake vector storage is required but schema creation failed!")

            logger.info("Snowflake vector store initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Snowflake backend: {e}")
            raise RuntimeError(f"Snowflake vector storage is required but initialization failed: {e}")

    def add_vectors(self, vectors, metadata, texts=None):
        """Add vectors and their metadata to the Snowflake store only."""
        vectors_array = np.array(vectors)
        if not self.use_snowflake or not self.snowflake_store:
            raise RuntimeError("Snowflake vector storage is required but not available!")
        try:
            self._add_vectors_to_snowflake(vectors_array, metadata, texts)
        except Exception as e:
            logger.error(f"Failed to add vectors to Snowflake: {e}")
            raise

    def _add_vectors_to_snowflake(self, vectors, metadata, texts=None):
        """Add vectors to Snowflake storage."""
        for i, (vector, meta) in enumerate(zip(vectors, metadata)):
            text = texts[i] if texts and i < len(texts) else str(meta)
            snowflake_metadata = {
                'original_metadata': meta,
                'text_content': text,
                'vector_dimension': len(vector),
                'created_by': 'hybrid_vector_store'
            }
            success = self.snowflake_store.store_embedding(
                text=text,
                embedding=vector.tolist(),
                metadata=snowflake_metadata,
                job_id=f"vector_store_{hash(text) % 1000000}"
            )
            if not success:
                logger.error(f"Failed to store vector {i} in Snowflake")
                raise RuntimeError(f"Failed to store vector {i} in Snowflake")

    def search(self, query_vector, top_k=5, use_snowflake=None):
        """
        Return indices and metadata of the top_k most similar vectors using Snowflake only.
        Raises RuntimeError if Snowflake is not available.
        """
        if not self.use_snowflake or not self.snowflake_store:
            raise RuntimeError("Snowflake vector storage is required but not available!")
        try:
            return self._search_snowflake(query_vector, top_k)
        except Exception as e:
            logger.error(f"Snowflake search failed: {e}")
            raise

    def _search_snowflake(self, query_vector, top_k=5):
        """Search using Snowflake vector similarity."""
        query_vector_list = np.array(query_vector).tolist()
        similar_embeddings = self.snowflake_store.similarity_search(
            query_embedding=query_vector_list,
            top_k=top_k
        )
        results = []
        for i, result in enumerate(similar_embeddings):
            embedding_id = result.get('id', i)
            similarity_score = result.get('similarity_score', 0.0)
            metadata = result.get('metadata', {})
            formatted_metadata = metadata.get('original_metadata', {}) if isinstance(metadata, dict) else {}
            if 'text_content' in metadata:
                formatted_metadata['original_text'] = metadata['text_content']
            results.append((embedding_id, similarity_score, formatted_metadata))
        return results

    def get_vector_count(self):
        """Get the total number of vectors stored in Snowflake."""
        if self.use_snowflake and self.snowflake_store:
            try:
                stats = self.snowflake_store.get_vector_stats()
                return stats.get('total_embeddings', 0)
            except Exception as e:
                logger.error(f"Failed to get Snowflake vector count: {e}")
                raise
        raise RuntimeError("Snowflake vector storage is required but not available!")

    def get_storage_info(self):
        """Get information about the storage backend (Snowflake only)."""
        if self.use_snowflake and self.snowflake_store:
            try:
                snowflake_stats = self.snowflake_store.get_vector_stats()
                return {
                    'backend': 'snowflake',
                    'snowflake_enabled': True,
                    'snowflake_connected': True,
                    'snowflake_vectors': snowflake_stats.get('total_embeddings', 0),
                    'snowflake_tables': snowflake_stats.get('tables_created', False)
                }
            except Exception as e:
                logger.error(f"Failed to get Snowflake storage info: {e}")
                raise
        raise RuntimeError("Snowflake vector storage is required but not available!")

    def clear(self):
        """Clear all stored vectors from Snowflake (not implemented)."""
        if self.use_snowflake and self.snowflake_store:
            logger.warning("Snowflake clear not implemented.")
            return
        raise RuntimeError("Snowflake vector storage is required but not available!")

    def save(self, path):
        logger.warning("File-based save/load not implemented - data is in Snowflake only")
        pass

    def load(self, path):
        logger.warning("File-based save/load not implemented - data is in Snowflake only")
        pass
