import asyncio
from cortex_engine.src.data_client import DataFoundationClient
import snowflake.connector
import os
from dotenv import load_dotenv

async def main():
    # Load environment variables from .env
    load_dotenv()

    # 1. Fetch 5 reports from Module 1
    data_client = DataFoundationClient()
    reports = await data_client.fetch_reports(limit=5)
    if not reports:
        print("No reports found.")
        return

    # 2. Extract titles and metadata
    rows = []
    for report in reports:
        title = report.get("TITLE") or report.get("title")
        report_id = report.get("ANUMBER") or report.get("id")
        if not title or not report_id:
            continue
        rows.append((str(report_id), title))

    if not rows:
        print("No valid titles found in reports.")
        return

    # 3. Connect to Snowflake using environment variables from .env
    conn = snowflake.connector.connect(
        user=os.environ.get('SNOWFLAKE_USER'),
        password=os.environ.get('SNOWFLAKE_PASSWORD'),
        account=os.environ.get('SNOWFLAKE_ACCOUNT'),
        warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE'),
        database=os.environ.get('SNOWFLAKE_DATABASE'),
        schema=os.environ.get('SNOWFLAKE_SCHEMA'),
        role=os.environ.get('SNOWFLAKE_ROLE')
    )
    cur = conn.cursor()

    # 4. Insert each title and its embedding using Cortex EMBED_TEXT_768
    for report_id, title in rows:
        # Use Cortex to generate embedding in SQL
        cur.execute(f'''
            INSERT INTO demo_embeddings (report_id, title, embedding)
            SELECT '{report_id}', '{title.replace("'", "''")}',
                   SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{title.replace("'", "''")}')
        ''')
        print(f"Inserted embedding for report_id={report_id}")

    cur.close()
    conn.close()
    print(f"Successfully embedded and uploaded {len(rows)} titles to Snowflake using Cortex embedding model.")

if __name__ == "__main__":
    asyncio.run(main())
