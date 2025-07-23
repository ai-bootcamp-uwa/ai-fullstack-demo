import numpy as np
import logging
from typing import List, Tuple, Any, Dict
from openai import AzureOpenAI

# Handle imports for both standalone and package usage
try:
    from .vector_store import VectorStore
    from .config import unified_config
except ImportError:
    from vector_store import VectorStore
    from config import unified_config

logger = logging.getLogger(__name__)

def compute_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    return dot_product / (norm_a * norm_b)

class SimilaritySearch:
    def __init__(self, vector_store: VectorStore, use_hybrid=False):
        """
        Initialize similarity search with vector store and optional hybrid configuration.
        
        Args:
            vector_store (VectorStore): Vector store instance
            use_hybrid (bool): Whether to use hybrid configuration
        """
        self.vector_store = vector_store
        self.client = None
        self.use_hybrid = use_hybrid
        
        # Initialize Azure OpenAI client for RAG functionality
        self._load_openai_client()

    def _load_openai_client(self):
        """Load Azure OpenAI client for RAG functionality using hybrid or legacy config."""
        try:
            if self.use_hybrid:
                # Use hybrid configuration
                azure_config = unified_config.azure_openai
                if not azure_config or not azure_config.is_configured():
                    raise ValueError("Hybrid Azure OpenAI configuration not available or incomplete")
                
                self.client = AzureOpenAI(
                    azure_endpoint=azure_config.endpoint,
                    api_key=azure_config.api_key,
                    api_version=azure_config.api_version
                )
                chat_model = azure_config.chat_model
                logger.info(f"Azure OpenAI client initialized for RAG with hybrid config, model: {chat_model}")
                
            else:
                # Legacy configuration
                try:
                    from .config import config
                except ImportError:
                    from config import config
                
                # Validate configuration first
                is_valid, error_msg = config.validate_config()
                if not is_valid:
                    raise ValueError(f"Azure OpenAI configuration invalid for RAG: {error_msg}")

                # Use legacy centralized config
                client_kwargs = config.get_client_kwargs()
                self.client = AzureOpenAI(**client_kwargs)
                chat_model = config.chat_model
                logger.info(f"Azure OpenAI client initialized for RAG with legacy config, model: {chat_model}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client for RAG: {e}")
            self.client = None
            # Don't raise here - RAG will fail gracefully if client is None

    def search(self, query_vector: np.ndarray, top_k: int = 5, use_snowflake: bool = None) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Find the most similar vectors using cosine similarity.
        
        Args:
            query_vector: Query vector for similarity search
            top_k: Number of results to return
            use_snowflake: Override backend choice for this search
            
        Returns:
            List of tuples: (index, similarity_score, metadata)
        """
        # Delegate to vector store's search method
        return self.vector_store.search(query_vector, top_k, use_snowflake)

    def search_by_text(self, query_text: str, top_k: int = 5, use_snowflake: bool = None) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Search for similar vectors using text query (generates embedding first).
        
        Args:
            query_text: Text query to search for
            top_k: Number of results to return
            use_snowflake: Override backend choice for this search
            
        Returns:
            List of tuples: (index, similarity_score, metadata)
        """
        # Generate embedding for the text query
        try:
            from .embedding import EmbeddingGenerator
        except ImportError:
            from embedding import EmbeddingGenerator
        
        embedding_gen = EmbeddingGenerator(use_hybrid=self.use_hybrid)
        if not embedding_gen.is_configured():
            raise RuntimeError("Embedding generator not properly configured for text search")
            
        query_embedding = embedding_gen.generate_embeddings([query_text])[0]
        
        # Perform the search
        return self.search(query_embedding, top_k, use_snowflake)

    def search_titles(self, query_title: str, top_k: int = 5, use_snowflake: bool = None, preprocess: bool = True) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Search for similar title vectors using title-specific processing.
        
        Args:
            query_title: Title query to search for
            top_k: Number of results to return
            use_snowflake: Override backend choice for this search
            preprocess: Whether to apply title preprocessing
            
        Returns:
            List of tuples: (index, similarity_score, metadata)
        """
        # Generate title embedding with preprocessing
        try:
            from .embedding import EmbeddingGenerator
        except ImportError:
            from embedding import EmbeddingGenerator
        
        embedding_gen = EmbeddingGenerator(use_hybrid=self.use_hybrid)
        if not embedding_gen.is_configured():
            raise RuntimeError("Embedding generator not properly configured for title search")
            
        query_embedding = embedding_gen.generate_title_embeddings([query_title], preprocess=preprocess)[0]
        
        # Perform the search
        return self.search(query_embedding, top_k, use_snowflake)

    def rag_query(self, query: str, use_snowflake: bool = None, search_type: str = "text") -> Dict[str, Any]:
        """
        Perform retrieval-augmented generation using Azure OpenAI.
        
        Args:
            query: User query for RAG
            use_snowflake: Override backend choice for retrieval
            search_type: Type of search ("text" or "title")
            
        Returns:
            Dict containing RAG response and metadata
        """
        # Ensure Azure OpenAI client is available
        if self.client is None:
            raise RuntimeError("Azure OpenAI client not initialized for RAG")

        # Step 1: Retrieve similar documents based on search type
        if search_type == "title":
            similar_results = self.search_titles(query, top_k=3, use_snowflake=use_snowflake)
        else:
            similar_results = self.search_by_text(query, top_k=3, use_snowflake=use_snowflake)

        if not similar_results:
            context = "No relevant documents found."
        else:
            # Extract context from similar results
            contexts = []
            for idx, score, metadata in similar_results:
                # Use original text if available, otherwise use metadata
                if 'original_text' in metadata:
                    contexts.append(f"Document {idx} (similarity: {score:.3f}): {metadata['original_text']}")
                else:
                    contexts.append(f"Document {idx} (similarity: {score:.3f}): {metadata}")
            context = "\n".join(contexts)

        # Step 2: Generate response using the configured chat model
        system_prompt = """You are a helpful assistant for geological data analysis.
        Use the provided context to answer questions about geological samples, mining reports, and exploration data.
        If the context doesn't contain relevant information, say so clearly."""

        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a helpful answer based on the context above."""

        try:
            # Get chat model from configuration
            if self.use_hybrid:
                chat_model = unified_config.azure_openai.chat_model
            else:
                try:
                    from .config import config
                except ImportError:
                    from config import config
                chat_model = config.chat_model
                
            response = self.client.chat.completions.create(
                model=chat_model,  # Use configured chat model (deployment name)
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return {
                "result": response.choices[0].message.content,
                "query": query,
                "context_used": context,
                "similar_documents": len(similar_results),
                "model_used": chat_model,
                "search_type": search_type,
                "backend_used": "snowflake" if (use_snowflake or self.vector_store.use_snowflake) else "memory"
            }
        except Exception as e:
            # Better error handling for Azure OpenAI chat errors
            if "DeploymentNotFound" in str(e):
                if self.use_hybrid:
                    chat_model = unified_config.azure_openai.chat_model
                else:
                    try:
                        from .config import config
                    except ImportError:
                        from config import config
                    chat_model = config.chat_model
                raise RuntimeError(f"Chat deployment '{chat_model}' not found. Check your Azure OpenAI deployment name.")
            elif "InvalidRequestError" in str(e):
                raise RuntimeError(f"Invalid chat request to Azure OpenAI: {e}")
            else:
                raise RuntimeError(f"Azure OpenAI chat API error: {e}")

    def hybrid_rag_query(self, query: str, search_both_backends: bool = True) -> Dict[str, Any]:
        """
        Perform RAG using both in-memory and Snowflake backends for comparison.
        
        Args:
            query: User query for RAG
            search_both_backends: Whether to search both backends
            
        Returns:
            Dict containing results from both backends
        """
        if not search_both_backends or not self.vector_store.use_snowflake:
            # Fall back to regular RAG
            return self.rag_query(query)
            
        try:
            # Search both backends
            memory_results = self.search_by_text(query, top_k=3, use_snowflake=False)
            snowflake_results = self.search_by_text(query, top_k=3, use_snowflake=True)
            
            # Combine and deduplicate results
            all_results = {}
            
            # Add memory results
            for idx, score, metadata in memory_results:
                result_key = str(metadata)  # Simple deduplication key
                if result_key not in all_results or score > all_results[result_key][1]:
                    all_results[result_key] = (idx, score, metadata, "memory")
            
            # Add Snowflake results
            for idx, score, metadata in snowflake_results:
                result_key = str(metadata)
                if result_key not in all_results or score > all_results[result_key][1]:
                    all_results[result_key] = (idx, score, metadata, "snowflake")
            
            # Sort by similarity score
            combined_results = sorted(all_results.values(), key=lambda x: x[1], reverse=True)[:3]
            
            # Generate context
            if not combined_results:
                context = "No relevant documents found."
            else:
                contexts = []
                for idx, score, metadata, backend in combined_results:
                    text = metadata.get('original_text', str(metadata))
                    contexts.append(f"Document {idx} (similarity: {score:.3f}, from {backend}): {text}")
                context = "\n".join(contexts)
            
            # Generate RAG response
            rag_result = self.rag_query(query, use_snowflake=None)  # Use default backend
            
            # Enhance result with hybrid information
            rag_result.update({
                "hybrid_search": True,
                "memory_results": len(memory_results),
                "snowflake_results": len(snowflake_results),
                "combined_results": len(combined_results),
                "context_used": context
            })
            
            return rag_result
            
        except Exception as e:
            logger.error(f"Hybrid RAG query failed: {e}")
            # Fall back to regular RAG
            return self.rag_query(query)

    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about the search capabilities."""
        stats = {
            "vector_store_backend": self.vector_store.get_storage_info(),
            "rag_client_available": self.client is not None,
            "hybrid_mode": self.use_hybrid,
        }
        
        if self.use_hybrid:
            azure_config = unified_config.azure_openai
            stats["azure_config"] = {
                "configured": azure_config.is_configured() if azure_config else False,
                "chat_model": azure_config.chat_model if azure_config else None,
                "embedding_model": azure_config.embedding_model if azure_config else None
            }
        
        return stats
