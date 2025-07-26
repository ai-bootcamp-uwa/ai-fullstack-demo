-- ============================================
-- CREATE WAMEX_GEO TABLE
-- ============================================
-- This script creates the main table for geological exploration reports
-- with proper data types for geospatial and temporal data

USE DATABASE WAMEX_EXPLORATION;
USE SCHEMA SNOWFLAKE_WAMEX;

CREATE OR REPLACE TABLE WAMEX_GEO (
    ANUMBER NUMBER,           -- Report number
    TITLE STRING,             -- Report title
    REPORT_YEA NUMBER,        -- Report year
    AUTHOR_NAM STRING,        -- Author name
    AUTHOR_COM STRING,        -- Author company
    REPORT_TYP STRING,        -- Report type
    DATE_FROM DATE,           -- Start date
    DATE_TO DATE,             -- End date
    PROJECT STRING,           -- Project name
    OPERATOR STRING,          -- Operator
    ABSTRACT STRING,          -- Report abstract
    KEYWORDS STRING,          -- Keywords
    TARGET_COM STRING,        -- Target commodity
    DATE_RELEA DATE,          -- Release date
    ITEM_NO NUMBER,           -- Item number
    DPXE_ABS STRING,          -- DPXE abstract URL
    DPXE_REP STRING,          -- DPXE report URL
    EXTRACT_DA DATE,          -- Extraction date
    DIGITAL_FI NUMBER,        -- Digital file flag
    IS_SHAPED NUMBER,         -- Shapefile flag
    geometry GEOGRAPHY,       -- Geospatial geometry
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Add comments to table and columns
COMMENT ON TABLE WAMEX_GEO IS 'Geological exploration reports with geospatial data from Western Australia';
COMMENT ON COLUMN WAMEX_GEO.geometry IS 'Geospatial geometry in WKT format';
COMMENT ON COLUMN WAMEX_GEO.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN WAMEX_GEO.updated_at IS 'Record last update timestamp';
