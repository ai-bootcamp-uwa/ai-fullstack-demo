#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_integration import SnowflakeVectorStore
from src.embedding import EmbeddingGenerator
import requests

def fetch_reports_by_ids(report_ids, batch_size=1000):
    """Fetch reports efficiently by ID list"""
    url = "http://localhost:8000/reports/by_ids"
    for i in range(0, len(report_ids), batch_size):
        batch_ids = report_ids[i:i+batch_size]
        try:
            response = requests.post(url, json={"ids": batch_ids}, timeout=60)
            if response.status_code == 200:
                yield response.json()
            else:
                print(f"❌ Failed to fetch batch {i//batch_size + 1}: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to fetch batch {i//batch_size + 1}: {e}")

def main():
    print("🔧 Setting up geological reports for embeddings...")
    # Step 1: Add embedding columns to existing table
    store = SnowflakeVectorStore()
    if not store.add_embedding_columns_to_geological_reports():
        print("❌ Failed to add embedding columns")
        return
    print("✅ Embedding columns added to GEOLOGICAL_REPORTS table")
    # Step 2: Get reports that need embeddings
    report_ids_needing_embeddings = store.get_reports_needing_embeddings(limit=None)
    print(f"📊 Found {len(report_ids_needing_embeddings)} reports needing embeddings")
    if not report_ids_needing_embeddings:
        print("✅ All reports already have embeddings!")
        return
    # Step 3: Stream fetch and process in batches
    BATCH_SIZE = 300  # Larger batches for speed
    total_processed = 0
    embedder = EmbeddingGenerator(use_hybrid=True)
    print(f"🎯 Processing {len(report_ids_needing_embeddings)} reports in streaming mode")
    for batch_reports in fetch_reports_by_ids(report_ids_needing_embeddings, batch_size=1000):
        if not batch_reports:
            continue
        valid_reports = [r for r in batch_reports if r.get("TITLE") and r.get("ANUMBER")]
        for i in range(0, len(valid_reports), BATCH_SIZE):
            batch = valid_reports[i:i+BATCH_SIZE]
            batch_num = total_processed // BATCH_SIZE + 1
            print(f"📦 Processing batch {batch_num}: {len(batch)} reports")
            batch_titles = [report["TITLE"] for report in batch]
            batch_anumbers = [report["ANUMBER"] for report in batch]
            embeddings = embedder.generate_embeddings(batch_titles)
            embedding_data = [
                {
                    'report_id': anumber,
                    'embedding_vector': embeddings[j].tolist(),
                    'model_used': 'text-embedding-ada-002'
                }
                for j, anumber in enumerate(batch_anumbers)
            ]
            success = store.store_embeddings_bulk(embedding_data)
            if success:
                total_processed += len(batch)
                print(f"   ✅ Processed {total_processed} total reports")
            else:
                print(f"   ❌ Failed to process batch {batch_num}")
    print(f"🎉 Completed! Processed {total_processed} embeddings")

if __name__ == "__main__":
    main()
