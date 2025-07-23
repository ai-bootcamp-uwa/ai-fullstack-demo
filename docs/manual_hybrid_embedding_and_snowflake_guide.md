# Manual Guide: Hybrid Embedding & Snowflake Storage (Cortex Engine)

This guide provides clear, step-by-step instructions for connecting to Snowflake, creating the required tables, and embedding/storing reports in Snowflake using the recommended full pipeline script for Module 2 (Cortex Engine).

---

## 1. Configure Snowflake & Hybrid Features

Edit your `.env` file in `cortex_engine/` with your actual Snowflake and hybrid settings:

```env
# Snowflake
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-user
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=AI_SYSTEM
SNOWFLAKE_SCHEMA=HYBRID_VECTORS
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Enable hybrid features
ENABLE_HYBRID_FEATURES=true
ENABLE_SNOWFLAKE_VECTORS=true
ENABLE_TITLE_EMBEDDINGS=true
```

---

## 2. Install Dependencies

```bash
cd cortex_engine
pip install -r requirements.txt
```

---

## 3. Set Up Snowflake Tables

Run the setup script to verify your connection and create all required tables:

```bash
python scripts/setup_hybrid_schema.py
```
- This will check your configuration, connect to Snowflake, and create the necessary tables for embeddings and health monitoring.

---

## 4. Start Required Services

- **Module 1 (Data Foundation):**
  ```bash
  cd ../data_foundation_project
  uvicorn src.api.main:app --port 8000
  ```
- **Module 2 (Cortex Engine):**
  ```bash
  cd ../cortex_engine
  uvicorn src.main:app --reload --port 3002
  ```

---

## 5. Embed Reports and Store in Snowflake (Recommended)

Run the full pipeline script to fetch reports, generate embeddings, and store vectors in Snowflake:

```bash
python scripts/execute_full_pipeline.py --max-reports 10
```
- This script will:
  1. Fetch reports from Module 1
  2. Generate embeddings using Azure OpenAI
  3. Store vectors in both memory and Snowflake (if enabled)
  4. Perform similarity search and RAG queries

---

## 6. Verify Embeddings in Snowflake

- Log in to your Snowflake console.
- Run a query like:
  ```sql
  SELECT * FROM AI_SYSTEM.HYBRID_VECTORS.TITLE_EMBEDDINGS LIMIT 10;
  ```
- You should see new rows for each embedded report/title.

---

## 7. Troubleshooting

- **No vectors in Snowflake?**
  - Ensure `ENABLE_SNOWFLAKE_VECTORS=true` in your `.env`.
  - Check logs for errors during embedding or storage.
  - Make sure you ran the pipeline script after enabling hybrid mode.
- **Connection errors?**
  - Double-check your Snowflake credentials and network access.
  - Use the setup script to diagnose issues.
- **Embedding errors?**
  - Ensure your Azure OpenAI credentials are valid and not rate-limited.

---

## 8. References

- [docs/EXECUTION.md](../cortex_engine/docs/EXECUTION.md)
- [scripts/setup_hybrid_schema.py](../cortex_engine/scripts/setup_hybrid_schema.py)
- [scripts/execute_full_pipeline.py](../cortex_engine/scripts/execute_full_pipeline.py)
- [docs/phase2_hybrid_core_extensions.md](../docs/phase2_hybrid_core_extensions.md)

---

**You are now ready to connect, embed, and store your reports in Snowflake using the Cortex Engine hybrid system!** 