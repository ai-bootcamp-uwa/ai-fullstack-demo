#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_integration import SnowflakeVectorStore
from src.embedding import EmbeddingGenerator
import requests

def fetch_reports_in_batches(report_ids, batch_size=1000):
    """Fetch reports using existing /reports endpoint with pagination"""
    base_url = "http://localhost:8000/reports"
    needed_ids = set(report_ids)
    collected_reports = []
    offset = 0
    limit = 2000
    while len(collected_reports) < len(report_ids):
        try:
            print(f"   Fetching reports: offset={offset}, limit={limit}")
            response = requests.get(base_url, params={"limit": limit, "offset": offset}, timeout=60)
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                break
            batch_reports = response.json()
            if not batch_reports:
                break
            needed_reports = [r for r in batch_reports if r.get("ANUMBER") in needed_ids]
            collected_reports.extend(needed_reports)
            for report in needed_reports:
                needed_ids.discard(report.get("ANUMBER"))
            if not needed_ids:
                break
            offset += limit
        except Exception as e:
            print(f"❌ Failed to fetch batch: {e}")
            break
    for i in range(0, len(collected_reports), batch_size):
        yield collected_reports[i:i+batch_size]

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
    # Step 3: Fetch reports using simple API call
    print("📥 Fetching reports from Data Foundation API...")
    try:
        # Simple API call to get all reports
        response = requests.get("http://localhost:8000/reports", params={"limit": 1000}, timeout=60)
        response.raise_for_status()
        # Debug: Print response type and structure
        api_data = response.json()
        print(f"🔍 API returned data type: {type(api_data)}")
        # Handle different response formats
        if isinstance(api_data, list):
            # Direct list of reports
            all_reports = api_data
        elif isinstance(api_data, dict) and 'reports' in api_data:
            # Wrapped in 'reports' key
            all_reports = api_data['reports']
        elif isinstance(api_data, dict) and 'data' in api_data:
            # Wrapped in 'data' key
            all_reports = api_data['data']
        else:
            # Try to use the dict directly
            all_reports = [api_data] if isinstance(api_data, dict) else []
        print(f"✅ Processed {len(all_reports)} reports from API")
        if len(all_reports) > 0:
            print(f"📋 Sample report keys: {list(all_reports[0].keys())}")
        # Filter to reports that need embeddings and have titles
        reports_to_process = []
        for report in all_reports:
            if not isinstance(report, dict):
                continue
            # Handle different field name formats (case-insensitive)
            def get_key(d, *keys):
                for k in keys:
                    if k in d:
                        return d[k]
                return None
            anumber = get_key(report, "ANUMBER", "anumber", "id")
            title = get_key(report, "TITLE", "title")
            if anumber in report_ids_needing_embeddings and title:
                reports_to_process.append({
                    "ANUMBER": anumber,
                    "TITLE": title
                })
        print(f"🎯 Processing {len(reports_to_process)} reports that need embeddings")
        if not reports_to_process:
            print("❌ No valid reports found with titles")
            return
        # Step 4: Process in batches
        BATCH_SIZE = 100
        total_processed = 0
        embedder = EmbeddingGenerator(use_hybrid=True)
        for i in range(0, len(reports_to_process), BATCH_SIZE):
            batch = reports_to_process[i:i+BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            print(f"📦 Processing batch {batch_num}: {len(batch)} reports")
            batch_titles = [report["TITLE"] for report in batch]
            batch_anumbers = [report["ANUMBER"] for report in batch]
            # Generate embeddings
            embeddings = embedder.generate_embeddings(batch_titles)
            # Prepare data for storage
            embedding_data = []
            for j, (anumber, title) in enumerate(zip(batch_anumbers, batch_titles)):
                embedding_data.append({
                    'report_id': anumber,
                    'embedding_vector': embeddings[j].tolist(),
                    'model_used': 'text-embedding-ada-002'
                })
            # Store embeddings
            success = store.store_embeddings_bulk(embedding_data)
            if success:
                total_processed += len(batch)
                print(f"   ✅ Processed {total_processed}/{len(reports_to_process)} reports")
            else:
                print(f"   ❌ Failed to process batch {batch_num}")
        print(f"🎉 Completed! Processed {total_processed} embeddings")
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        print("💡 Make sure Data Foundation API is running on port 8000")
    except Exception as e:
        print(f"❌ Error processing reports: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
