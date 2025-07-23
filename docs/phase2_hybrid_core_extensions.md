# Phase 2: Hybrid Core Extensions Implementation

## 📋 Overview

Phase 2 extends the core cortex engine modules to support the hybrid Azure OpenAI + Snowflake architecture while maintaining full backward compatibility. This phase focuses on enhancing the foundational components: embedding generation, vector storage, similarity search, and introducing specialized title processing.

**Implementation Date:** January 2025  
**Status:** ✅ Complete  
**Dependencies:** Phase 1 (Configuration & Schema Setup)

---

## 🎯 Objectives Achieved

### ✅ Primary Goals
- **Extended embedding generation** with hybrid configuration support
- **Dual backend vector storage** (memory + Snowflake) with automatic fallback
- **Enhanced similarity search** with multiple search types and RAG improvements
- **Specialized title processing** for geological document titles
- **Comprehensive testing suite** with real credential validation
- **Full backward compatibility** with existing code

### ✅ Technical Achievements
- **Zero breaking changes** - All existing code continues to work
- **Gradual migration path** - Components can be upgraded individually
- **Production-ready features** - Error handling, monitoring, and health checks
- **Performance optimization** - Efficient batch processing and caching

---

## 🏗️ Architecture Extensions

### Before Phase 2
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   embedding.py  │    │ vector_store.py │    │  similarity.py  │
│                 │    │                 │    │                 │
│ • Azure OpenAI  │    │ • In-memory     │    │ • Basic search  │
│ • Basic config  │    │ • Simple store  │    │ • Legacy RAG    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### After Phase 2
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🔄 HYBRID CORE EXTENSIONS                         │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│  embedding.py   │ vector_store.py │  similarity.py  │   title_processor.py    │
│                 │                 │                 │        (NEW)            │
│ ✅ Hybrid config│ ✅ Dual backend │ ✅ Multi-search │ ✅ Quality assessment   │
│ ✅ Title preproc│ ✅ Auto fallback│ ✅ Enhanced RAG │ ✅ Batch processing     │
│ ✅ Quality ctrl │ ✅ Stats/monitor│ ✅ Hybrid RAG   │ ✅ Geological domain    │
│ ✅ Dimensions   │ ✅ Performance  │ ✅ Search stats │ ✅ Workflow integration │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                     │
                            ┌────────▼────────┐
                            │  Unified Config │
                            │ ✅ Azure OpenAI │
                            │ ✅ Snowflake    │
                            │ ✅ Feature flags│
                            └─────────────────┘
```

---

## 🔧 Extended Components

### 1. Enhanced Embedding Generation (`embedding.py`)

#### **New Features:**
- **Hybrid Configuration Support**
  ```python
  # Legacy mode (backward compatible)
  generator = EmbeddingGenerator(use_hybrid=False)
  
  # New hybrid mode
  generator = EmbeddingGenerator(use_hybrid=True)
  ```

- **Title-Specific Processing**
  ```python
  # Enhanced title embedding with preprocessing
  embeddings = generator.generate_title_embeddings(
      titles=["DDH-001 Au Assay Results", "RC Drilling Program"],
      preprocess=True  # Applies geological domain preprocessing
  )
  ```

- **Quality Improvements**
  - Geological abbreviation expansion (DDH → Diamond Drill Hole)
  - Context prefixes for better embeddings
  - Automatic dimension detection
  - Enhanced error handling

#### **Configuration Options:**
```python
# Hybrid configuration
generator = EmbeddingGenerator(use_hybrid=True)

# Check configuration status
if generator.is_configured():
    dimension = generator.get_embedding_dimension()  # e.g., 1536
```

### 2. Dual Backend Vector Storage (`vector_store.py`)

#### **New Architecture:**
- **Memory + Snowflake Storage**
  ```python
  # Memory-only (legacy)
  store = VectorStore(use_snowflake=False)
  
  # Hybrid storage (memory + Snowflake)
  store = VectorStore(use_snowflake=True)
  ```

- **Automatic Fallback**
  - If Snowflake fails, automatically uses memory storage
  - Transparent operation - no code changes needed
  - Graceful degradation with logging

- **Backend Selection**
  ```python
  # Search specific backend
  results = store.search(query_vector, use_snowflake=True)   # Force Snowflake
  results = store.search(query_vector, use_snowflake=False)  # Force memory
  results = store.search(query_vector)                       # Use default
  ```

#### **Storage Statistics:**
```python
info = store.get_storage_info()
# Returns:
{
    'backend': 'hybrid',              # or 'memory'
    'memory_vectors': 150,
    'snowflake_enabled': True,
    'snowflake_connected': True,
    'snowflake_vectors': 150,
    'snowflake_tables': True
}
```

### 3. Enhanced Similarity Search (`similarity.py`)

#### **New Search Types:**
- **Text-Based Search**
  ```python
  search_engine = SimilaritySearch(vector_store, use_hybrid=True)
  results = search_engine.search_by_text("gold mining exploration", top_k=5)
  ```

- **Title-Specific Search**
  ```python
  results = search_engine.search_titles(
      "copper ore analysis",
      top_k=3,
      preprocess=True  # Apply geological preprocessing
  )
  ```

- **Hybrid RAG Query**
  ```python
  # Compare results from both backends
  response = search_engine.hybrid_rag_query(
      "What mining data is available?",
      search_both_backends=True
  )
  ```

#### **Enhanced RAG Features:**
- **Search Type Selection**
  ```python
  # Text-based RAG
  rag_result = search_engine.rag_query(query, search_type="text")
  
  # Title-based RAG  
  rag_result = search_engine.rag_query(query, search_type="title")
  ```

- **Backend Comparison**
  ```python
  response = search_engine.hybrid_rag_query(query)
  # Returns enhanced metadata:
  {
      'result': 'Generated response...',
      'hybrid_search': True,
      'memory_results': 3,
      'snowflake_results': 2,
      'combined_results': 4,
      'backend_used': 'hybrid'
  }
  ```

### 4. Title Processor Module (`title_processor.py`) - NEW

#### **Core Features:**

- **Quality Assessment**
  ```python
  processor = TitleProcessor(use_hybrid=True, use_snowflake=True)
  
  quality_score = processor.assess_title_quality("DDH-001 Gold Assay Results")
  # Returns: 0.85 (scale 0.0-1.0)
  ```

- **Geological Preprocessing**
  ```python
  processed = processor.preprocess_title("DDH_001_Au_50m_to_75m", enhanced=True)
  # Returns: "Geological document title: Diamond Drill Hole 001 Gold 50 to 75 metres"
  ```

- **Batch Processing**
  ```python
  titles = ["Title 1", "Title 2", "Title 3"]
  results, stats = processor.process_batch(
      titles,
      quality_threshold=0.4,
      store_results=True,
      batch_size=100
  )
  
  # stats provides comprehensive metrics
  print(f"Processed: {stats.successful}/{stats.total_titles}")
  print(f"Average quality: {stats.average_quality_score:.2f}")
  print(f"Processing time: {stats.processing_time_seconds:.1f}s")
  ```

#### **Quality Indicators:**
- ✅ **Meaningful words** (3+ characters)
- ✅ **Geological terms** (ore, mineral, drill, etc.)
- ✅ **Appropriate length** (5-200 characters)
- ✅ **Not just numbers**
- ✅ **Contains numbers** (coordinates, depths)

#### **Geological Domain Features:**
- **Abbreviation Expansion:**
  - `DDH` → `Diamond Drill Hole`
  - `RC` → `Reverse Circulation`
  - `Au` → `Gold`, `Cu` → `Copper`
  - `g/t` → `grams per tonne`

- **Format Standardization:**
  - `50-75m` → `50 to 75 metres`
  - `123N` → `123 N`

---

## 📊 Configuration Management

### Hybrid Configuration Usage

```python
from config import unified_config

# Check if hybrid configuration is available
if unified_config.hybrid_config and unified_config.hybrid_config.is_configured():
    # Use hybrid features
    generator = EmbeddingGenerator(use_hybrid=True)
    store = VectorStore(use_snowflake=True)
    search = SimilaritySearch(store, use_hybrid=True)
else:
    # Fall back to legacy mode
    generator = EmbeddingGenerator(use_hybrid=False)
    store = VectorStore(use_snowflake=False)
    search = SimilaritySearch(store, use_hybrid=False)
```

### Environment Variables

Phase 2 uses the same environment variables as Phase 1:

```bash
# Azure OpenAI (for embeddings and chat)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_MODEL=gpt-4
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Snowflake (for vector storage)
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-user
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=AI_SYSTEM
SNOWFLAKE_SCHEMA=HYBRID_VECTORS
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Feature flags
HYBRID_FEATURES_ENABLED=true
USE_SNOWFLAKE_VECTORS=true
```

---

## 🚀 Usage Examples

### Basic Usage (Backward Compatible)

```python
# Existing code continues to work unchanged
from embedding import EmbeddingGenerator
from vector_store import VectorStore
from similarity import SimilaritySearch

generator = EmbeddingGenerator()
store = VectorStore()
search = SimilaritySearch(store)

# Generate embeddings
embeddings = generator.generate_embeddings(["Sample text"])

# Store vectors
store.add_vectors(embeddings, [{"type": "sample"}])

# Search
results = search.search(embeddings[0])
```

### Enhanced Hybrid Usage

```python
# New hybrid capabilities
generator = EmbeddingGenerator(use_hybrid=True)
store = VectorStore(use_snowflake=True)
search = SimilaritySearch(store, use_hybrid=True)
processor = TitleProcessor(use_hybrid=True, use_snowflake=True)

# Process titles with quality control
titles = ["DDH-001 Gold Assay", "Bad_title_123"]
results, stats = processor.process_batch(titles, store_results=True)

# Enhanced search capabilities
text_results = search.search_by_text("gold mining data")
title_results = search.search_titles("copper exploration")

# Advanced RAG with backend comparison
rag_response = search.hybrid_rag_query("What geological data is available?")
```

### Complete Workflow Example

```python
from title_processor import TitleProcessor
from vector_store import VectorStore
from similarity import SimilaritySearch

# Initialize hybrid system
processor = TitleProcessor(use_hybrid=True, use_snowflake=True)
store = VectorStore(use_snowflake=True)
search = SimilaritySearch(store, use_hybrid=True)

# Step 1: Process and filter titles
raw_titles = [
    "Exploration_Drilling_Gold_Zone_A",
    "Copper_Grade_Analysis_2024",
    "Iron_Resource_Estimation_Study"
]

# Process with quality filtering
results, stats = processor.process_batch(
    raw_titles,
    quality_threshold=0.4,
    store_results=True
)

print(f"Processed {stats.successful} titles successfully")

# Step 2: Search the stored data
search_results = search.search_by_text("gold exploration drilling")
print(f"Found {len(search_results)} relevant documents")

# Step 3: Generate insights with RAG
rag_response = search.rag_query(
    "What gold exploration data is available?",
    search_type="title"
)

print(f"RAG Response: {rag_response['result']}")
print(f"Used {rag_response['similar_documents']} documents")
print(f"Model: {rag_response['model_used']}")
```

---

## 🧪 Testing & Validation

### Phase 2 Test Suite

The comprehensive test suite validates all Phase 2 functionality:

```bash
cd cortex_engine
python tests/test_phase2_integration.py
```

### Test Coverage

- ✅ **Hybrid embedding generation** - Both legacy and hybrid modes
- ✅ **Dual backend storage** - Memory and Snowflake operations
- ✅ **Enhanced similarity search** - All search types and RAG features
- ✅ **Title processor workflows** - Quality assessment and batch processing
- ✅ **End-to-end workflows** - Complete system integration
- ✅ **Configuration validation** - All configuration combinations

### Test Examples

```python
# Test hybrid embedding
def test_hybrid_embedding():
    generator = EmbeddingGenerator(use_hybrid=True)
    if generator.is_configured():
        embeddings = generator.generate_title_embeddings(
            ["DDH-001 Au Results"], 
            preprocess=True
        )
        assert embeddings.shape[0] == 1
        assert embeddings.shape[1] == generator.get_embedding_dimension()

# Test dual backend storage
def test_dual_backend():
    store = VectorStore(use_snowflake=True)
    # Test both backends
    memory_results = store.search(query, use_snowflake=False)
    snowflake_results = store.search(query, use_snowflake=True)
    assert len(memory_results) > 0
    assert len(snowflake_results) > 0
```

---

## 📈 Performance Considerations

### Optimization Features

- **Batch Processing:** Efficient bulk operations for large datasets
- **Automatic Fallback:** No performance penalty when Snowflake unavailable
- **Caching:** In-memory storage provides fast access
- **Lazy Loading:** Components initialized only when needed

### Performance Metrics

```python
# Get performance statistics
store_info = store.get_storage_info()
search_stats = search.get_search_stats()
processor_stats = processor.get_processing_stats()

# Example metrics:
{
    'backend': 'hybrid',
    'memory_vectors': 1500,
    'snowflake_vectors': 1500,
    'processing_time_seconds': 45.2,
    'average_quality_score': 0.76
}
```

### Best Practices

1. **Use batch processing** for large datasets
2. **Set appropriate quality thresholds** to filter low-quality titles
3. **Monitor storage statistics** for capacity planning
4. **Use hybrid RAG** for comprehensive results
5. **Enable Snowflake** for production scale

---

## 🔧 Migration Guide

### From Phase 1 to Phase 2

**No migration required!** Phase 2 is fully backward compatible.

#### Optional Enhancements

1. **Enable hybrid features:**
   ```python
   # Old way (still works)
   generator = EmbeddingGenerator()
   
   # New way (enhanced features)
   generator = EmbeddingGenerator(use_hybrid=True)
   ```

2. **Use dual backend storage:**
   ```python
   # Old way (memory only)
   store = VectorStore()
   
   # New way (memory + Snowflake)
   store = VectorStore(use_snowflake=True)
   ```

3. **Add title processing:**
   ```python
   # New capability
   processor = TitleProcessor(use_hybrid=True, use_snowflake=True)
   results, stats = processor.process_batch(titles)
   ```

### Gradual Migration Strategy

1. **Phase 1:** Keep existing code unchanged
2. **Phase 2:** Start using hybrid features for new functionality
3. **Phase 3:** Gradually migrate existing code to hybrid features
4. **Phase 4:** Full hybrid system deployment

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Snowflake Connection Issues
```python
# Check Snowflake configuration
from config import unified_config
if unified_config.snowflake_config:
    print(f"Configured: {unified_config.snowflake_config.is_configured()}")
    
# Check vector store connection
store = VectorStore(use_snowflake=True)
info = store.get_storage_info()
print(f"Snowflake connected: {info['snowflake_connected']}")
```

#### 2. Embedding Generation Errors
```python
# Verify configuration
generator = EmbeddingGenerator(use_hybrid=True)
print(f"Configured: {generator.is_configured()}")

# Check dimensions
if generator.is_configured():
    dim = generator.get_embedding_dimension()
    print(f"Expected dimension: {dim}")
```

#### 3. Title Processing Quality Issues
```python
# Check quality assessment
processor = TitleProcessor()
quality = processor.assess_title_quality("Your title here")
print(f"Quality score: {quality}")

# Review quality indicators
stats = processor.get_processing_stats()
print(f"Quality indicators: {stats['quality_indicators']}")
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# All Phase 2 components will now provide detailed logs
```

---

## 🔮 Future Enhancements

### Planned Phase 3 Features

- 🌐 **Extended API endpoints** for hybrid system management
- 📊 **Administrative interfaces** for monitoring and control
- 🔄 **Bulk processing APIs** for large-scale operations
- 📈 **Analytics endpoints** for performance insights

### Potential Phase 4 Features

- 🔄 **Advanced caching strategies**
- 📊 **Machine learning model optimization**
- 🌐 **Multi-region deployment support**
- 🔐 **Enhanced security features**

---

## 📚 Reference

### Key Classes and Methods

#### EmbeddingGenerator
- `__init__(use_hybrid=False)` - Initialize with configuration choice
- `generate_title_embeddings(titles, preprocess=True)` - Title-specific processing
- `get_embedding_dimension()` - Get model dimension
- `is_configured()` - Check configuration status

#### VectorStore  
- `__init__(use_snowflake=False)` - Initialize with backend choice
- `search(query_vector, top_k=5, use_snowflake=None)` - Multi-backend search
- `get_storage_info()` - Storage statistics
- `get_vector_count()` - Total vector count

#### SimilaritySearch
- `__init__(vector_store, use_hybrid=False)` - Initialize with configuration
- `search_by_text(query_text, top_k=5)` - Text-based search
- `search_titles(query_title, top_k=5, preprocess=True)` - Title search
- `hybrid_rag_query(query, search_both_backends=True)` - Multi-backend RAG

#### TitleProcessor
- `__init__(use_hybrid=True, use_snowflake=False)` - Initialize processor
- `process_batch(titles, quality_threshold=0.3)` - Batch processing
- `assess_title_quality(title)` - Quality assessment
- `filter_by_quality(titles, min_quality=0.5)` - Quality filtering

### Configuration Classes
- `unified_config.hybrid_config` - Azure OpenAI configuration
- `unified_config.snowflake_config` - Snowflake configuration

---

## ✅ Phase 2 Completion Checklist

- ✅ **Extended embedding generation** with hybrid support
- ✅ **Dual backend vector storage** with automatic fallback
- ✅ **Enhanced similarity search** with multiple search types
- ✅ **Title processor module** with geological domain expertise
- ✅ **Comprehensive testing suite** with real credential validation
- ✅ **Full backward compatibility** maintained
- ✅ **Performance optimization** implemented
- ✅ **Error handling and monitoring** added
- ✅ **Documentation** completed

**Status: ✅ COMPLETE**  
**Next Phase: 🚀 Phase 3 - API Extensions & User Interfaces** 