#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_integration import SnowflakeVectorStore
from src.data_client import DataFoundationClient
from src.embedding import EmbeddingGenerator

async def main():
    print("🔧 Setting up geological reports for embeddings...")
    # Step 1: Add embedding columns to existing table
    store = SnowflakeVectorStore()
    if not store.add_embedding_columns_to_geological_reports():
        print("❌ Failed to add embedding columns")
        return
    print("✅ Embedding columns added to GEOLOGICAL_REPORTS table")
    # Step 2: Get reports that need embeddings
    report_ids_needing_embeddings = store.get_reports_needing_embeddings(limit=1000)
    print(f"📊 Found {len(report_ids_needing_embeddings)} reports needing embeddings")
    if not report_ids_needing_embeddings:
        print("✅ All reports already have embeddings!")
        return
    # Step 3: Fetch those specific reports from Module 1
    data_client = DataFoundationClient()
    all_reports = await data_client.fetch_reports(limit=5000)
    # Filter to only the ones needing embeddings
    reports_to_process = [
        r for r in all_reports
        if r.get("ANUMBER") in report_ids_needing_embeddings and r.get("TITLE")
    ]
    print(f"🎯 Processing {len(reports_to_process)} reports")
    # Step 4: Process in batches
    BATCH_SIZE = 25
    total_processed = 0
    embedder = EmbeddingGenerator(use_hybrid=True)
    for i in range(0, len(reports_to_process), BATCH_SIZE):
        batch = reports_to_process[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(reports_to_process) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"📦 Processing batch {batch_num}/{total_batches}: {len(batch)} reports")
        for report in batch:
            title = report.get("TITLE")
            anumber = report.get("ANUMBER")
            # Generate embedding
            embeddings = embedder.generate_embeddings([title])
            embedding_vector = embeddings[0].tolist()
            # Store in existing GEOLOGICAL_REPORTS table
            success = store.store_embedding(anumber, title, embedding_vector)
            if success:
                total_processed += 1
                if total_processed % 10 == 0:
                    print(f"   ✅ Processed {total_processed}/{len(reports_to_process)} reports")
    print(f"🎉 Completed! Processed {total_processed} embeddings")

if __name__ == "__main__":
    asyncio.run(main())
