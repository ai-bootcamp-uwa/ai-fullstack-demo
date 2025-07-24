import asyncio
from cortex_engine.src.data_client import DataFoundationClient
from cortex_engine.src.embedding import EmbeddingGenerator
from cortex_engine.src.vector_store import VectorStore

async def main():
    # 1. Fetch all reports from Module 1 (remove limit or set high limit)
    data_client = DataFoundationClient()
    reports = await data_client.fetch_reports(limit=1000)  # Adjust or remove limit as needed
    if not reports:
        print("No reports found.")
        return

    # 2. Extract titles and metadata
    titles = []
    metadata = []
    for report in reports:
        title = report.get("TITLE") or report.get("title")
        if not title:
            continue
        titles.append(title)
        metadata.append({"report_id": report.get("ANUMBER") or report.get("id"), "raw": report})

    if not titles:
        print("No titles found in reports.")
        return

    # 3. Process in batches to avoid memory/timeout issues
    BATCH_SIZE = 50  # Process 50 titles at a time
    total_processed = 0
    for i in range(0, len(titles), BATCH_SIZE):
        batch_titles = titles[i:i+BATCH_SIZE]
        batch_metadata = metadata[i:i+BATCH_SIZE]
        print(f"Processing batch {i//BATCH_SIZE + 1}: {len(batch_titles)} titles")
        # Generate embeddings for batch
        embedder = EmbeddingGenerator(use_hybrid=True)
        embeddings = embedder.generate_embeddings(batch_titles)
        # Store batch in Snowflake
        store = VectorStore(use_snowflake=True)
        store.add_vectors(embeddings, batch_metadata, texts=batch_titles)
        total_processed += len(batch_titles)
        print(f"Batch complete. Total processed: {total_processed}/{len(titles)}")
    print(f"Successfully embedded and uploaded {total_processed} titles to Snowflake.")

if __name__ == "__main__":
    asyncio.run(main())
