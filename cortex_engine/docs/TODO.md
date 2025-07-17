# cortex_engine Module TODO List (Class/Function Level)

## src/main.py
- [ ] Create FastAPI app
- [ ] Implement /embed endpoint
- [ ] Implement /similarity-search endpoint
- [ ] Implement /rag-query endpoint

## src/embedding.py
- [ ] Class: EmbeddingGenerator
    - [ ] Method: generate_embeddings(data)
    - [ ] Method: load_model()

## src/vector_store.py
- [ ] Class: VectorStore
    - [ ] Method: add_vectors(vectors, metadata)
    - [ ] Method: search(query_vector, top_k)
    - [ ] Method: save()
    - [ ] Method: load()

## src/similarity.py
- [ ] Function: compute_similarity(vec1, vec2)
- [ ] Class: SimilaritySearch
    - [ ] Method: search(query, top_k)
    - [ ] Method: rag_query(query)

## src/data_client.py
- [ ] Class: DataFoundationClient
    - [ ] Method: fetch_reports()
    - [ ] Method: fetch_report_by_id(report_id)

## src/tests/test_embedding.py
- [ ] Test: test_generate_embeddings

## src/tests/test_similarity.py
- [ ] Test: test_similarity_search

## src/tests/test_api.py
- [ ] Test: test_embed_endpoint
- [ ] Test: test_similarity_search_endpoint
- [ ] Test: test_rag_query_endpoint 