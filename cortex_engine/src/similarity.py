import numpy as np
from typing import List, Tuple, Any, Dict
from vector_store import VectorStore
import os
from openai import AzureOpenAI

def compute_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    return dot_product / (norm_a * norm_b)

class SimilaritySearch:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.client = None
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        # Initialize Azure OpenAI client immediately for RAG
        self._load_openai_client()
        
    def _load_openai_client(self):
        """Load Azure OpenAI client for RAG functionality."""
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not api_key or not azure_endpoint:
            raise ValueError("Azure OpenAI credentials (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT) are required for RAG functionality")
            
        try:
            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            print(f"Azure OpenAI client initialized for RAG with model: {self.chat_model}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure OpenAI client for RAG: {e}")
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[int, float, Dict[str, Any]]]:
        """Find the most similar vectors using cosine similarity."""
        if self.vector_store.vectors is None or len(self.vector_store.vectors) == 0:
            return []
        
        similarities = []
        for i, stored_vector in enumerate(self.vector_store.vectors):
            similarity = compute_similarity(query_vector, stored_vector)
            distance = 1 - similarity  # Convert to distance (lower is more similar)
            similarities.append((i, distance, self.vector_store.metadata[i]))
        
        # Sort by distance (ascending - closer is more similar)
        similarities.sort(key=lambda x: x[1])
        
        return similarities[:top_k]
    
    def rag_query(self, query: str) -> Dict[str, Any]:
        """Perform retrieval-augmented generation using Azure OpenAI."""
        # Ensure Azure OpenAI client is available
        assert self.client is not None, "Azure OpenAI client not initialized for RAG"
        
        # Step 1: Generate embedding for the query
        from embedding import EmbeddingGenerator
        embedding_gen = EmbeddingGenerator()
        query_embedding = embedding_gen.generate_embeddings([query])[0]
        
        # Step 2: Retrieve similar documents
        similar_results = self.search(query_embedding, top_k=3)
        
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
        
        # Step 3: Generate response using the configured chat model
        system_prompt = """You are a helpful assistant for geological data analysis. 
        Use the provided context to answer questions about geological samples, mining reports, and exploration data.
        If the context doesn't contain relevant information, say so clearly."""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a helpful answer based on the context above."""
        
        response = self.client.chat.completions.create(
            model=self.chat_model,
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
            "model_used": self.chat_model
        }
