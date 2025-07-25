# Complete Setup Guide: Module 1 & Module 2

**AI Full-Stack Geological Data Pipeline - From Zero to Running System**

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Clean Existing Data (Optional)](#clean-existing-data-optional)
3. [Fresh Installation Setup](#fresh-installation-setup)
4. [Module 1: Data Foundation Setup](#module-1-data-foundation-setup)
5. [Module 2: Cortex Engine Setup](#module-2-cortex-engine-setup)
6. [Running Both Modules](#running-both-modules)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Required:**

- Python 3.8+
- Virtual environment support (venv module)
- Azure OpenAI account with API keys
- Snowflake account with appropriate permissions
- Git and terminal/command line

**Get Azure OpenAI Access:**

- Visit: https://azure.microsoft.com/en-us/products/ai-services/openai-service
- Note your endpoint format: `https://YOUR-RESOURCE-NAME.openai.azure.com/`

---

## Clean Existing Data (Optional)

### If You Have Existing Installation

**Step 1: Stop All Running Services**

```bash
# Kill any running processes on our ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3002 | xargs kill -9 2>/dev/null || true
lsof -ti:3003 | xargs kill -9 2>/dev/null || true

# If using Makefile
make stop
```

**Step 2: Clean Virtual Environment**

```bash
# Remove existing virtual environment
rm -rf .venv

# If using Makefile
make clean
```

**Step 3: Clean Snowflake Data (Optional)**

**Option A: Clean All Tables**

```sql
-- Connect to Snowflake SQL worksheet and run:
USE WAREHOUSE COMPUTE_WH;
USE DATABASE WAMEX_EXPLORATION;
USE SCHEMA GEOSPATIAL_DATA;

-- Drop all tables (complete reset)
DROP TABLE IF EXISTS GEOLOGICAL_REPORTS;
DROP TABLE IF EXISTS TITLE_EMBEDDINGS;
DROP TABLE IF EXISTS REPORT_METADATA;
DROP TABLE IF EXISTS EMBEDDING_JOBS;
DROP TABLE IF EXISTS HYBRID_SYSTEM_HEALTH;
```

**Option B: Clean Data Only (Keep Structure)**

```sql
-- Keep tables but remove all data
TRUNCATE TABLE GEOLOGICAL_REPORTS;
TRUNCATE TABLE TITLE_EMBEDDINGS;
TRUNCATE TABLE REPORT_METADATA;
TRUNCATE TABLE EMBEDDING_JOBS;
TRUNCATE TABLE HYBRID_SYSTEM_HEALTH;
```

**Step 4: Remove Log Files**

```bash
# Remove all log files
rm -rf data_foundation_project/logs
rm -rf cortex_engine/logs
rm -rf backend_gateway/logs

# Remove PID files
rm -f data_foundation_project/data_foundation.pid
rm -f cortex_engine/cortex_engine.pid
rm -f backend_gateway/backend_gateway.pid
```

---

## Fresh Installation Setup

### Step 1: Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd ai-fullstack-demo-clean
```

### Step 2: Setup Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Base Dependencies

```bash
# Install root dependencies
pip install -r requirements.txt
```

---

## Module 1: Data Foundation Setup

### Step 1: Install Module 1 Dependencies

```bash
# Install Module 1 specific dependencies
pip install -r data_foundation_project/requirements.txt

# Install in development mode
pip install -e ./data_foundation_project
```

### Step 2: Configure Snowflake for Module 1

```bash
cd data_foundation_project

# Copy environment template
cp env_template.txt .env

# Edit .env with your Snowflake credentials
nano .env  # or use your preferred editor
```

**Required Snowflake Configuration:**

```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=WAMEX_EXPLORATION
SNOWFLAKE_SCHEMA=GEOSPATIAL_DATA
SNOWFLAKE_ROLE=SYSADMIN

# Optional: Set authenticator if using SSO
SNOWFLAKE_AUTHENTICATOR=externalbrowser
```

### Step 3: Test Snowflake Connection

```bash
# Test connection and create tables
python scripts/migrate_to_snowflake.py --setup-only

# Expected output:
# ✅ Snowflake connection test successful
# ✅ Tables created/verified successfully
```

### Step 4: Load Data to Snowflake

```bash
# Option A: Load limited dataset (recommended for testing, skips existing records by default)
python scripts/migrate_to_snowflake.py --max-records 1000
python scripts/migrate_to_snowflake.py

# Option B: Load full dataset (if you have large shapefile, skips existing records by default)
python scripts/migrate_to_snowflake.py --max-records 100000

# Option C: Custom shapefile path
python scripts/migrate_to_snowflake.py --shapefile /path/to/your/data.shp --max-records 500

# Option D: Check for existing conflicts only (no migration)
python scripts/migrate_to_snowflake.py --check-existing

# Option E: Force replace existing records
python scripts/migrate_to_snowflake.py --force-replace

# Option F: Fail if any conflicts exist
python scripts/migrate_to_snowflake.py --fail-on-conflicts
```

> **Note:**
> By default, the migration script will **skip records that already exist in Snowflake** (based on ANUMBER).
> Use `--force-replace` to overwrite, or `--fail-on-conflicts` to abort if any conflicts are found.

**Expected Output:**

```
🚀 Starting Snowflake migration...
✅ Snowflake connection successful
📁 Loading shapefile...
📊 Dataset loaded: X,XXX records
📤 Loading 1000 records in 40 chunks of 25...
✅ Migration completed successfully
📊 Final record count: 1,000
```

### Step 5: Verify Data Load

```bash
# Quick verification
python -c "
from src.snowflake_client import snowflake_client
result = snowflake_client.execute_query('SELECT COUNT(*) FROM GEOLOGICAL_REPORTS')
print(f'✅ Records loaded: {result[0][\"COUNT(*)\"]:,}')
"
```

---

## Module 2: Cortex Engine Setup

### Step 1: Install Module 2 Dependencies

```bash
cd ../cortex_engine

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Step 2: Configure Azure OpenAI

```bash
# Copy configuration template
cp env.example .env

# Edit .env with your Azure OpenAI credentials
nano .env  # or use your preferred editor
```

**Required Azure OpenAI Configuration:**

```env
# Azure OpenAI Configuration (REQUIRED)
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-01

# Model Configuration (REQUIRED)
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-4o-mini

# Snowflake Configuration (Copy from Module 1)
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=WAMEX_EXPLORATION
SNOWFLAKE_SCHEMA=GEOSPATIAL_DATA
SNOWFLAKE_ROLE=SYSADMIN

# Optional: Rate Limiting
MAX_EMBEDDING_REQUESTS_PER_MINUTE=120
MAX_EMBEDDING_TOKENS_PER_MINUTE=20000
```

### Step 3: Test Azure OpenAI Configuration

```bash
# Test your configuration
python tests/test_deployments.py

# Expected output:
# ✅ Azure OpenAI connection successful
# ✅ Embedding model test PASSED
# ✅ Chat model test PASSED
```

### Step 4: Setup Embedding Tables

```bash
# Add embedding columns to existing GEOLOGICAL_REPORTS table
export PYTHONPATH=.
python scripts/setup_geological_embeddings.py

# Expected output:
# 🔧 Setting up geological reports for embeddings...
# ✅ Embedding columns added to GEOLOGICAL_REPORTS table
# 📊 Found X reports needing embeddings
# 🎯 Processing X reports
# 🎉 Completed! Processed X embeddings
```

---

## Running Both Modules

### Option A: Using Makefile (Recommended)

```bash
# Return to root directory
cd ..

# Setup everything (if not done already)
make setup

# Start all modules
make run-all

# Expected output:
# 🚀 Starting all 3 modules...
# 📊 Module 1: Data Foundation (port 8000)...
# 🤖 Module 2: Cortex Engine (port 3002)...
# 🔗 Module 3: Backend Gateway (port 3003)...
# 🎉 All modules started!
```

### Option B: Manual Terminal Sessions

**Terminal 1: Module 1 (Data Foundation)**

```bash
cd data_foundation_project
source ../.venv/bin/activate
uvicorn src.api.main:app --port 8000 --reload
```

**Terminal 2: Module 2 (Cortex Engine)**

```bash
cd cortex_engine
source ../.venv/bin/activate
uvicorn src.main:app --port 3002
```

**Terminal 3: Module 3 (Backend Gateway) - Optional**

```bash
cd backend_gateway
source ../.venv/bin/activate
uvicorn src.api.main:app --port 3003 --reload
```

---

## Verification & Testing

### Step 1: Check All Services Are Running

```bash
# Using Makefile
make test

# Manual check
curl http://localhost:8000/reports?limit=1  # Module 1
curl http://localhost:3002/health           # Module 2
curl http://localhost:3003/api/backend/health  # Module 3 (if running)
```

**Expected Output:**

```
📊 Module 1 (Data Foundation): ✅ ONLINE
🤖 Module 2 (Cortex Engine): ✅ ONLINE
🔗 Module 3 (Backend Gateway): ✅ ONLINE
```

### Step 2: Test Module 1 Data Access

```bash
# Test basic data retrieval
curl "http://localhost:8000/reports?limit=3"

# Test filtering
curl "http://localhost:8000/filter-reports?commodity=GOLD&limit=2"

# Test health check
curl "http://localhost:8000/health"
```

### Step 3: Test Module 2 AI Capabilities

```bash
# Test health and configuration
curl http://localhost:3002/health
curl http://localhost:3002/config

# Test embedding generation
curl -X POST http://localhost:3002/embed \
  -H "Content-Type: application/json" \
  -d '{"data": ["Geological exploration site with iron ore deposits"]}'

# Test embedding status
curl http://localhost:3002/embedding-status
```

### Step 4: Test Full Pipeline

```bash
cd cortex_engine
export PYTHONPATH=.
python scripts/execute_full_pipeline.py

# Expected output:
# 🚀 CORTEX ENGINE FULL PIPELINE EXECUTION
# ✅ Module 1 (Data Foundation): ONLINE
# ✅ Module 2 (Cortex Engine): CONFIGURED
# ✅ Data acquisition completed: 10 reports
# ✅ Embeddings generated: 5 vectors
# ✅ Similarity analysis completed
# ✅ RAG testing completed
# 🎉 EXECUTION STATUS: SUCCESS
```

### Step 5: Verify Embedding Data in Snowflake

```sql
-- Connect to Snowflake SQL worksheet and verify:
SELECT
    COUNT(*) as total_reports,
    COUNT(TITLE_EMBEDDING) as reports_with_embeddings,
    COUNT(DISTINCT EMBEDDING_MODEL) as models_used
FROM GEOLOGICAL_REPORTS;

-- Expected result:
-- total_reports: 1000 (or your loaded amount)
-- reports_with_embeddings: should be > 0
-- models_used: 1 (text-embedding-ada-002)
```

---

## Troubleshooting

### Common Issues

**1. Port Already in Use**

```bash
# Kill processes on our ports
make kill-ports

# Or manually:
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3002 | xargs kill -9 2>/dev/null || true
```

**2. Snowflake Connection Failed**

```bash
# Check credentials in .env files
# Verify network connectivity
ping your_account.snowflakecomputing.com

# Test connection
cd data_foundation_project
python scripts/migrate_to_snowflake.py --validate-only
```

**3. Azure OpenAI Configuration Issues**

```bash
# Check your .env file in cortex_engine/
# Verify endpoint format: https://YOUR-RESOURCE-NAME.openai.azure.com/
# Test configuration
cd cortex_engine
python tests/test_deployments.py
```

**4. Missing Dependencies**

```bash
# Reinstall all dependencies
make clean
make setup

# Or manually:
pip install -r requirements.txt
pip install -r data_foundation_project/requirements.txt
pip install -r cortex_engine/requirements.txt
```

**5. Embedding Generation Fails**

```bash
# Check Azure OpenAI quotas and limits
# Verify model deployment names in Azure portal
# Check rate limiting settings in .env
```

### Log File Locations

When using `make run-all`, logs are saved to:

- **Module 1**: `data_foundation_project/logs/data_foundation.log`
- **Module 2**: `cortex_engine/logs/cortex_engine.log`
- **Module 3**: `backend_gateway/logs/backend_gateway.log`

```bash
# View recent logs
tail -f data_foundation_project/logs/data_foundation.log
tail -f cortex_engine/logs/cortex_engine.log

# Or using Makefile
make logs
```

### Performance Notes

- **Module 1**: Can handle 1000+ records/second for data loading
- **Module 2**: Target 200+ embeddings/minute with bulk processing
- **Total Setup Time**: ~10 minutes for complete fresh installation
- **Embedding 1000 Reports**: ~5-10 minutes depending on Azure OpenAI limits

---

## 🎉 Success!

You now have a fully operational AI Full-Stack Geological Data Pipeline with:

✅ **Module 1**: Geological data API with 1000+ reports
✅ **Module 2**: AI-powered embedding generation and similarity search
✅ **Snowflake Integration**: Cloud data warehouse with vector capabilities
✅ **Azure OpenAI**: Production-ready AI embedding and chat models

**Next Steps:**

- Explore the API documentation at http://localhost:3002/docs
- Run similarity searches and RAG queries
- Scale up to process more geological reports
- Integrate with Module 3 (Backend Gateway) for authentication
