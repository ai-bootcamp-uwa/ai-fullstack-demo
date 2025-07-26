-- ============================================
-- LOAD DATA INTO WAMEX_GEO TABLE
-- ============================================
-- This script loads CSV data into the WAMEX_GEO table
-- with proper data type conversions and error handling

USE DATABASE WAMEX_EXPLORATION;
USE SCHEMA SNOWFLAKE_WAMEX;

-- Load data from CSV with proper type conversions and error handling
COPY INTO WAMEX_GEO (
    ANUMBER, TITLE, REPORT_YEA, AUTHOR_NAM, AUTHOR_COM, REPORT_TYP, 
    DATE_FROM, DATE_TO, PROJECT, OPERATOR, ABSTRACT, KEYWORDS, 
    TARGET_COM, DATE_RELEA, ITEM_NO, DPXE_ABS, DPXE_REP, 
    EXTRACT_DA, DIGITAL_FI, IS_SHAPED, geometry
)
FROM (
    SELECT
        TRY_TO_NUMBER($1),         -- ANUMBER
        $2,                        -- TITLE
        TRY_TO_NUMBER($3),         -- REPORT_YEA
        $4,                        -- AUTHOR_NAM
        $5,                        -- AUTHOR_COM
        $6,                        -- REPORT_TYP
        TRY_TO_DATE($7),           -- DATE_FROM
        TRY_TO_DATE($8),           -- DATE_TO
        $9,                        -- PROJECT
        $10,                       -- OPERATOR
        $11,                       -- ABSTRACT
        $12,                       -- KEYWORDS
        $13,                       -- TARGET_COM
        TRY_TO_DATE($14),          -- DATE_RELEA
        TRY_TO_NUMBER($15),        -- ITEM_NO
        $16,                       -- DPXE_ABS
        $17,                       -- DPXE_REP
        TRY_TO_DATE($18),          -- EXTRACT_DA
        TRY_TO_NUMBER($19),        -- DIGITAL_FI
        TRY_TO_NUMBER($20),        -- IS_SHAPED
        TRY_TO_GEOGRAPHY($21)      -- geometry (convert WKT to GEOGRAPHY with error handling)
    FROM @wamex_geo/Exploration_Reports_1000.csv
)
FILE_FORMAT = (
    TYPE = 'CSV' 
    FIELD_DELIMITER = ',' 
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    EMPTY_FIELD_AS_NULL = TRUE
)
ON_ERROR = 'CONTINUE';  -- Continue loading even if some rows have errors

-- Verify data was loaded correctly
SELECT 
    COUNT(*) as total_records,
    COUNT(geometry) as records_with_geometry,
    COUNT(ABSTRACT) as records_with_abstract
FROM WAMEX_GEO;

-- Show sample of loaded data
SELECT ANUMBER, TITLE, REPORT_YEA, OPERATOR, TARGET_COM 
FROM WAMEX_GEO 
LIMIT 5;

-- Check for records with invalid geometry
SELECT ANUMBER, TITLE, geometry 
FROM WAMEX_GEO 
WHERE geometry IS NULL 
LIMIT 10; 