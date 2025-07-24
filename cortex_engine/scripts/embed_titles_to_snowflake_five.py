import asyncio
from cortex_engine.src.data_client import DataFoundationClient
from cortex_engine.src.embedding import EmbeddingGenerator
from cortex_engine.src.vector_store import VectorStore

async def main():
    # 1. Fetch 5 reports from Module 1
    data_client = DataFoundationClient()
    reports = await data_client.fetch_reports(limit=5)
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

    # 3. Generate embeddings for titles
    embedder = EmbeddingGenerator(use_hybrid=True)
    embeddings = embedder.generate_embeddings(titles)

    # 4. Store embeddings in Snowflake
    store = VectorStore(use_snowflake=True)
    store.add_vectors(embeddings, metadata, texts=titles)
    print(f"Successfully embedded and uploaded {len(titles)} titles to Snowflake.")

if __name__ == "__main__":
    asyncio.run(main())
