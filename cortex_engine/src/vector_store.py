import numpy as np

class VectorStore:
    def __init__(self):
        self.vectors = None  # Shape: (n_samples, n_features)
        self.metadata = []   # List of metadata dicts
        self.texts = []      # Store original text for RAG context

    def add_vectors(self, vectors, metadata, texts=None):
        """Add vectors and their metadata to the store."""
        if self.vectors is None:
            self.vectors = np.array(vectors)
        else:
            self.vectors = np.vstack([self.vectors, vectors])
        
        self.metadata.extend(metadata)
        
        # Store original texts for RAG context
        if texts:
            self.texts.extend(texts)
        else:
            # If no texts provided, use metadata as fallback
            self.texts.extend([str(meta) for meta in metadata])

    def search(self, query_vector, top_k=5):
        """Return indices and metadata of the top_k most similar vectors (by cosine similarity)."""
        if self.vectors is None or len(self.vectors) == 0:
            return []
        
        # Handle dimension mismatch gracefully
        query_vector = np.array(query_vector)
        if query_vector.shape[0] != self.vectors.shape[1]:
            print(f"Warning: Query vector dimension {query_vector.shape[0]} doesn't match stored vectors {self.vectors.shape[1]}")
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

    def save(self, path):
        """Save vectors and metadata to disk (optional, not implemented)."""
        pass

    def load(self, path):
        """Load vectors and metadata from disk (optional, not implemented)."""
        pass
