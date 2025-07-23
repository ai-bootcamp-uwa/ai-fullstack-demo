"""
Title Processor Module for Hybrid Azure OpenAI + Snowflake System

This module provides specialized processing for document titles, including:
- Text preprocessing and normalization
- Batch embedding generation
- Quality scoring and filtering
- Integration with hybrid storage backends
"""

import logging
import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass

# Handle imports for both standalone and package usage
try:
    from .embedding import EmbeddingGenerator
    from .vector_store import VectorStore
    from .config import unified_config
except ImportError:
    from embedding import EmbeddingGenerator
    from vector_store import VectorStore
    from config import unified_config

logger = logging.getLogger(__name__)

@dataclass
class TitleProcessingResult:
    """Result from title processing operations."""
    original_title: str
    processed_title: str
    embedding: Optional[np.ndarray]
    quality_score: float
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

@dataclass
class BatchProcessingStats:
    """Statistics from batch processing operations."""
    total_titles: int
    successful: int
    failed: int
    average_quality_score: float
    processing_time_seconds: float
    storage_backend: str

class TitleProcessor:
    """
    Advanced title processor for geological and mining document titles.
    Provides preprocessing, quality assessment, and batch processing capabilities.
    """
    
    def __init__(self, use_hybrid=True, use_snowflake=False):
        """
        Initialize title processor with hybrid configuration.
        
        Args:
            use_hybrid (bool): Whether to use hybrid configuration
            use_snowflake (bool): Whether to use Snowflake for vector storage
        """
        self.use_hybrid = use_hybrid
        self.use_snowflake = use_snowflake
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator(use_hybrid=use_hybrid)
        self.vector_store = VectorStore(use_snowflake=use_snowflake)
        
        # Title processing patterns
        self.cleanup_patterns = [
            (r'[_]+', ' '),  # Replace underscores with spaces
            (r'[-]+', ' '),  # Replace hyphens with spaces
            (r'\s+', ' '),   # Normalize whitespace
            (r'\.+$', ''),   # Remove trailing periods
        ]
        
        # Quality assessment patterns
        self.quality_indicators = {
            'has_meaningful_words': r'\b[a-zA-Z]{3,}\b',  # Words with 3+ letters
            'has_numbers': r'\d+',  # Contains numbers
            'has_geological_terms': r'\b(ore|mineral|drill|sample|assay|grade|gold|copper|iron|zinc|lead|exploration|mining|geological|survey)\b',
            'proper_length': lambda title: 5 <= len(title.strip()) <= 200,
            'not_just_numbers': lambda title: not re.match(r'^[\d\s\.\-_]+$', title.strip()),
        }

    def preprocess_title(self, title: str, enhanced: bool = True) -> str:
        """
        Preprocess a single title for better embedding quality.
        
        Args:
            title (str): Raw title text
            enhanced (bool): Whether to apply enhanced preprocessing
            
        Returns:
            str: Processed title
        """
        if not title or not isinstance(title, str):
            return ""
            
        processed = title.strip()
        
        # Basic cleanup
        for pattern, replacement in self.cleanup_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        if enhanced:
            # Enhanced preprocessing for geological titles
            processed = self._apply_geological_preprocessing(processed)
            
        # Final cleanup
        processed = processed.strip()
        
        # Add context prefix if title is meaningful
        if processed and len(processed) > 3:
            if enhanced:
                processed = f"Geological document title: {processed}"
            else:
                processed = f"Document title: {processed}"
        
        return processed

    def _apply_geological_preprocessing(self, title: str) -> str:
        """Apply geological domain-specific preprocessing."""
        
        # Expand common abbreviations
        geological_expansions = {
            r'\bDDH\b': 'Diamond Drill Hole',
            r'\bRC\b': 'Reverse Circulation',
            r'\bAu\b': 'Gold',
            r'\bCu\b': 'Copper',
            r'\bFe\b': 'Iron',
            r'\bZn\b': 'Zinc',
            r'\bPb\b': 'Lead',
            r'\bAg\b': 'Silver',
            r'\bg/t\b': 'grams per tonne',
            r'\bppm\b': 'parts per million',
            r'\bm\b(?=\s|$)': 'metres',
        }
        
        for pattern, replacement in geological_expansions.items():
            title = re.sub(pattern, replacement, title, flags=re.IGNORECASE)
        
        # Normalize coordinate formats
        title = re.sub(r'(\d+)([NSEW])', r'\1 \2', title)
        
        # Standardize depth/length references
        title = re.sub(r'(\d+)[-_](\d+)\s*m', r'\1 to \2 metres', title)
        
        return title

    def assess_title_quality(self, title: str) -> float:
        """
        Assess the quality of a title for embedding purposes.
        
        Args:
            title (str): Title to assess
            
        Returns:
            float: Quality score between 0.0 and 1.0
        """
        if not title or not isinstance(title, str):
            return 0.0
            
        score = 0.0
        max_score = len(self.quality_indicators)
        
        # Check each quality indicator
        for indicator, pattern_or_func in self.quality_indicators.items():
            if callable(pattern_or_func):
                if pattern_or_func(title):
                    score += 1.0
            else:
                if re.search(pattern_or_func, title, re.IGNORECASE):
                    score += 1.0
                    
        # Bonus for optimal length
        length = len(title.strip())
        if 20 <= length <= 100:
            score += 0.5
        elif 10 <= length <= 150:
            score += 0.2
            
        # Penalty for very short or very long titles
        if length < 5 or length > 200:
            score *= 0.5
            
        return min(score / max_score, 1.0)

    def process_single_title(self, title: str, generate_embedding: bool = True, 
                           quality_threshold: float = 0.3) -> TitleProcessingResult:
        """
        Process a single title with full workflow.
        
        Args:
            title (str): Raw title to process
            generate_embedding (bool): Whether to generate embedding
            quality_threshold (float): Minimum quality score to accept
            
        Returns:
            TitleProcessingResult: Processing result
        """
        try:
            # Preprocess title
            processed_title = self.preprocess_title(title, enhanced=True)
            
            # Assess quality
            quality_score = self.assess_title_quality(title)
            
            # Check quality threshold
            if quality_score < quality_threshold:
                return TitleProcessingResult(
                    original_title=title,
                    processed_title=processed_title,
                    embedding=None,
                    quality_score=quality_score,
                    metadata={'rejection_reason': 'quality_threshold'},
                    success=False,
                    error_message=f"Quality score {quality_score:.2f} below threshold {quality_threshold}"
                )
            
            # Generate embedding if requested
            embedding = None
            if generate_embedding:
                if not self.embedding_generator.is_configured():
                    raise RuntimeError("Embedding generator not properly configured")
                    
                embedding = self.embedding_generator.generate_title_embeddings([title], preprocess=False)[0]
            
            # Create metadata
            metadata = {
                'original_length': len(title),
                'processed_length': len(processed_title),
                'quality_score': quality_score,
                'has_embedding': embedding is not None,
                'preprocessing_applied': True,
                'geological_domain': True
            }
            
            return TitleProcessingResult(
                original_title=title,
                processed_title=processed_title,
                embedding=embedding,
                quality_score=quality_score,
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to process title '{title}': {e}")
            return TitleProcessingResult(
                original_title=title,
                processed_title="",
                embedding=None,
                quality_score=0.0,
                metadata={'error_type': type(e).__name__},
                success=False,
                error_message=str(e)
            )

    def process_batch(self, titles: List[str], quality_threshold: float = 0.3,
                     store_results: bool = True, batch_size: int = 100) -> Tuple[List[TitleProcessingResult], BatchProcessingStats]:
        """
        Process a batch of titles with progress tracking.
        
        Args:
            titles (List[str]): List of titles to process
            quality_threshold (float): Minimum quality score
            store_results (bool): Whether to store results in vector store
            batch_size (int): Size of processing batches
            
        Returns:
            Tuple[List[TitleProcessingResult], BatchProcessingStats]: Results and statistics
        """
        import time
        start_time = time.time()
        
        results = []
        successful_count = 0
        failed_count = 0
        quality_scores = []
        
        logger.info(f"Starting batch processing of {len(titles)} titles")
        
        # Process in batches
        for i in range(0, len(titles), batch_size):
            batch_titles = titles[i:i + batch_size]
            batch_results = []
            batch_embeddings = []
            batch_metadata = []
            batch_texts = []
            
            # Process each title in the batch
            for title in batch_titles:
                result = self.process_single_title(title, generate_embedding=True, 
                                                 quality_threshold=quality_threshold)
                results.append(result)
                
                if result.success:
                    successful_count += 1
                    quality_scores.append(result.quality_score)
                    
                    if store_results and result.embedding is not None:
                        batch_results.append(result)
                        batch_embeddings.append(result.embedding)
                        batch_metadata.append(result.metadata)
                        batch_texts.append(result.processed_title)
                else:
                    failed_count += 1
            
            # Store batch results
            if store_results and batch_embeddings:
                try:
                    self.vector_store.add_vectors(
                        vectors=batch_embeddings,
                        metadata=batch_metadata,
                        texts=batch_texts
                    )
                    logger.info(f"Stored batch {i//batch_size + 1}: {len(batch_embeddings)} embeddings")
                except Exception as e:
                    logger.error(f"Failed to store batch {i//batch_size + 1}: {e}")
        
        # Calculate statistics
        processing_time = time.time() - start_time
        avg_quality = np.mean(quality_scores) if quality_scores else 0.0
        storage_backend = self.vector_store.get_storage_info()['backend']
        
        stats = BatchProcessingStats(
            total_titles=len(titles),
            successful=successful_count,
            failed=failed_count,
            average_quality_score=avg_quality,
            processing_time_seconds=processing_time,
            storage_backend=storage_backend
        )
        
        logger.info(f"Batch processing complete: {successful_count}/{len(titles)} successful "
                   f"(avg quality: {avg_quality:.2f}, time: {processing_time:.1f}s)")
        
        return results, stats

    def filter_by_quality(self, titles: List[str], min_quality: float = 0.5) -> List[Tuple[str, float]]:
        """
        Filter titles by quality score without generating embeddings.
        
        Args:
            titles (List[str]): Titles to filter
            min_quality (float): Minimum quality threshold
            
        Returns:
            List[Tuple[str, float]]: Filtered titles with their quality scores
        """
        filtered = []
        
        for title in titles:
            processed = self.preprocess_title(title, enhanced=False)
            quality = self.assess_title_quality(title)
            
            if quality >= min_quality:
                filtered.append((title, quality))
        
        logger.info(f"Filtered {len(filtered)}/{len(titles)} titles above quality threshold {min_quality}")
        return filtered

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processor configuration and statistics."""
        return {
            'processor_config': {
                'use_hybrid': self.use_hybrid,
                'use_snowflake': self.use_snowflake,
                'embedding_configured': self.embedding_generator.is_configured(),
            },
            'vector_store_info': self.vector_store.get_storage_info(),
            'quality_indicators': list(self.quality_indicators.keys()),
            'cleanup_patterns_count': len(self.cleanup_patterns)
        } 