# Data Upload Guide

This guide explains how to upload geological data to Snowflake for the Streamlit chatbot project.

## Prerequisites

1. **Snowflake Account**: You need access to a Snowflake account
2. **Python Environment**: Install required packages from `requirements.txt`
3. **Data Files**: Ensure your CSV files are in `data/processed/`

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Snowflake Connection

Edit `config/snowflake_config.yaml` with your Snowflake credentials:

```yaml
snowflake:
  account: "your_account.region"
  user: "your_username"
  password: "your_password"
  warehouse: "COMPUTE_WH"
  database: "WAMEX_EXPLORATION"
  schema: "SNOWFLAKE_WAMEX"
  role: "ACCOUNTADMIN"
```

## Upload Process

### Option 1: Automated Python Script (Recommended)

```bash
cd snowflake_streamlit
python scripts/upload_data.py
```

This script will:
1. Create the `WAMEX_GEO` table
2. Upload your CSV to a Snowflake stage
3. Load data into the table with proper type conversions

### Option 2: Manual SQL Execution

1. **Create Table**: Execute `sql/ddl/01_create_wamex_geo_table.sql` in Snowsight
2. **Upload CSV**: Use Snowsight's "Load Data" wizard to upload your CSV
3. **Load Data**: Execute `sql/ddl/02_load_data.sql` in Snowsight

## Data Files

- **Full Dataset**: `data/processed/Exploration_Reports.csv` (353MB)
- **Sample Dataset**: `data/processed/Exploration_Reports_1000.csv` (2.9MB)

## Table Schema

The `WAMEX_GEO` table includes:

| Column | Type | Description |
|--------|------|-------------|
| ANUMBER | NUMBER | Report number |
| TITLE | STRING | Report title |
| REPORT_YEA | NUMBER | Report year |
| ABSTRACT | STRING | Report abstract |
| geometry | GEOGRAPHY | Geospatial data |
| ... | ... | ... |

## Verification

After upload, verify your data:

```sql
-- Check record count
SELECT COUNT(*) FROM WAMEX_GEO;

-- Check geospatial data
SELECT COUNT(*) FROM WAMEX_GEO WHERE geometry IS NOT NULL;

-- Sample data
SELECT ANUMBER, TITLE, REPORT_YEA, OPERATOR 
FROM WAMEX_GEO 
LIMIT 5;
```

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify your Snowflake credentials
2. **Permission Errors**: Ensure your role has CREATE TABLE and INSERT privileges
3. **Data Type Errors**: Check that your CSV format matches the expected schema

### Support

For issues, check:
- Snowflake error logs in Snowsight
- Python script output for detailed error messages
- Table structure in Snowflake for data type mismatches 