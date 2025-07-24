#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_integration import SnowflakeVectorStore
from src.embedding import EmbeddingGenerator
import requests

def main():
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
    print("📥 Fetching reports in batches...")
    all_reports = []
    batch_size = 500  # Fetch 500 at a time
    total_needed = min(5000, len(report_ids_needing_embeddings))
    for offset in range(0, total_needed, batch_size):
        current_limit = min(batch_size, total_needed - offset)
        print(f"   Fetching batch: offset={offset}, limit={current_limit}")
        response = requests.get(
            "http://localhost:8000/reports",
            params={"limit": current_limit, "offset": offset},
            timeout=120
        )
        response.raise_for_status()
        batch_reports = response.json()
        all_reports.extend(batch_reports)
        if len(batch_reports) < current_limit:
            break
    print(f"📊 Fetched {len(all_reports)} reports total")
    # Filter to only the ones needing embeddings
    reports_to_process = [
        r for r in all_reports
        if r.get("ANUMBER") in report_ids_needing_embeddings and r.get("TITLE")
    ]
    print(f"🎯 Processing {len(reports_to_process)} reports")
    # Step 4: Process in batches using bulk operations
    BATCH_SIZE = 100
    total_processed = 0
    embedder = EmbeddingGenerator(use_hybrid=True)
    for i in range(0, len(reports_to_process), BATCH_SIZE):
        batch = reports_to_process[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(reports_to_process) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"📦 Processing batch {batch_num}/{total_batches}: {len(batch)} reports")
        batch_titles = [report.get("TITLE") for report in batch]
        batch_anumbers = [report.get("ANUMBER") for report in batch]
        embeddings = embedder.generate_embeddings(batch_titles)
        embedding_data = []
        for i, (anumber, title) in enumerate(zip(batch_anumbers, batch_titles)):
            embedding_data.append({
                'report_id': anumber,
                'embedding_vector': embeddings[i].tolist(),
                'model_used': 'text-embedding-ada-002'
            })
        success = store.store_embeddings_bulk(embedding_data)
        if success:
            total_processed += len(batch)
            print(f"   ✅ Processed {total_processed}/{len(reports_to_process)} reports")
        else:
            print(f"   ❌ Failed to process batch {batch_num}")
    print(f"🎉 Completed! Processed {total_processed} embeddings")

if __name__ == "__main__":
    main()
