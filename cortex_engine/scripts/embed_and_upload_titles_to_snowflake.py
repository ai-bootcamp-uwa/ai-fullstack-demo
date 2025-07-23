#!/usr/bin/env python3
"""
Batch Embed and Upload Report Titles to Snowflake

This script fetches report titles from Module 1 (Data Foundation API),
embeds them using the Cortex Engine hybrid API, and stores the vectors in Snowflake.
It uses only the 'title' field for embedding, as per best practice.
"""

import requests
import os
import sys
import time
from typing import List

# Configuration
DATA_FOUNDATION_URL = os.getenv("DATA_FOUNDATION_URL", "http://localhost:8000")
CORTEX_ENGINE_URL = os.getenv("CORTEX_ENGINE_URL", "http://localhost:3002")
BATCH_SIZE = 10  # Adjust as needed


def fetch_report_titles(limit=1000) -> List[str]:
    """Fetch report titles from Module 1."""
    print(f"Fetching up to {limit} report titles from {DATA_FOUNDATION_URL}...")
    try:
        resp = requests.get(f"{DATA_FOUNDATION_URL}/reports?limit={limit}", timeout=30)
        resp.raise_for_status()
        reports = resp.json()
        titles = [r["title"] for r in reports if "title" in r and r["title"]]
        print(f"  ✅ Got {len(titles)} titles.")
        return titles
    except Exception as e:
        print(f"  ❌ Failed to fetch reports: {e}")
        return []


def embed_and_upload_titles(titles: List[str], batch_size: int = BATCH_SIZE):
    """Embed titles and upload vectors to Snowflake via /embed/hybrid endpoint."""
    total = len(titles)
    print(f"Embedding and uploading {total} titles in batches of {batch_size}...")
    success_count = 0
    for i in range(0, total, batch_size):
        batch = titles[i:i+batch_size]
        payload = {"data": batch}
        try:
            resp = requests.post(f"{CORTEX_ENGINE_URL}/embed/hybrid", json=payload, timeout=120)
            if resp.status_code == 200:
                result = resp.json()
                if "embeddings" in result:
                    print(f"  ✅ Batch {i//batch_size+1}: {len(batch)} titles embedded and uploaded.")
                    success_count += len(batch)
                else:
                    print(f"  ⚠️ Batch {i//batch_size+1}: No embeddings returned. Response: {result}")
            else:
                print(f"  ❌ Batch {i//batch_size+1}: HTTP {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size+1}: Exception: {e}")
        time.sleep(1)  # Avoid rate limits
    print(f"Done. {success_count}/{total} titles embedded and uploaded.")


def main():
    print("\n🚀 Batch Embedding and Upload to Snowflake (Titles Only)")
    print("=" * 60)
    titles = fetch_report_titles(limit=1000)
    if not titles:
        print("No titles to process. Exiting.")
        sys.exit(1)
    embed_and_upload_titles(titles, batch_size=BATCH_SIZE)
    print("\n🎉 All done! Check your Snowflake TITLE_EMBEDDINGS table.")

if __name__ == "__main__":
    main() 