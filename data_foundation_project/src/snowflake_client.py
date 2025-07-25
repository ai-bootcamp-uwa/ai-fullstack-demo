import snowflake.connector
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any, Optional
import pandas as pd
import geopandas as gpd
from shapely import wkt
import logging
from contextlib import contextmanager
from snowflake.connector import DictCursor

from .config import snowflake_config

logger = logging.getLogger(__name__)

# Suppress SQLAlchemy's verbose parameter logging
def _suppress_sqlalchemy_logging_global():
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
_suppress_sqlalchemy_logging_global()

class SnowflakeClient:
    """Snowflake client for geological data operations"""

    def __init__(self):
        self.config = snowflake_config
        self._engine = None
        self._session_factory = None

    def _get_engine(self):
        """Create or return SQLAlchemy engine for Snowflake"""
        if self._engine is None:
            if not self.config.validate_credentials():
                raise ValueError("Snowflake credentials are not properly configured. Check your .env file.")

            # Get connection parameters
            conn_params = self.config.get_connection_params()

            # Create Snowflake connection URL for SQLAlchemy
            if self.config.authenticator == "externalbrowser":
                # For external browser auth, don't include password in URL
                connection_url = (
                    f"snowflake://{self.config.user}@{self.config.account}/"
                    f"{self.config.database}/{self.config.schema}"
                    f"?warehouse={self.config.warehouse}&authenticator=externalbrowser"
                )
            else:
                # Standard authentication with password
                connection_url = (
                    f"snowflake://{self.config.user}:{self.config.password}"
                    f"@{self.config.account}/{self.config.database}/{self.config.schema}"
                    f"?warehouse={self.config.warehouse}"
                )

            if self.config.role:
                connection_url += f"&role={self.config.role}"

            self._engine = create_engine(connection_url)
            self._session_factory = sessionmaker(bind=self._engine)
            logger.info(f"Created Snowflake engine for {self.config.database}.{self.config.schema}")

        return self._engine

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        engine = self._get_engine()
        connection = engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def test_connection(self) -> bool:
        """Test Snowflake connection"""
        try:
            # Use direct snowflake.connector for testing (more reliable for auth)
            conn_params = self.config.get_connection_params()
            conn = snowflake.connector.connect(**conn_params)

            # Test with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            logger.info("Snowflake connection test successful")
            return result[0] == 1

        except Exception as e:
            logger.error(f"Snowflake connection test failed: {e}")
            return False

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute a query with extended timeout for large requests"""
        try:
            # Determine if this is a large request
            limit_param = params.get('limit', 10) if params else 10
            if limit_param > 1000:
                # Use direct snowflake connector for large queries (better timeout handling)
                conn_params = self.config.get_connection_params()
                raw_conn = snowflake.connector.connect(**conn_params)
                try:
                    cursor = raw_conn.cursor(DictCursor)
                    cursor.execute(query, params or {})
                    results = cursor.fetchall()
                    # Convert to list of dicts and normalize
                    normalized_results = []
                    for row in results:
                        normalized_row = self._normalize_result_row(dict(row))
                        normalized_results.append(normalized_row)
                    return normalized_results
                finally:
                    cursor.close()
                    raw_conn.close()
            else:
                # Use SQLAlchemy for small queries (existing code)
                with self.get_connection() as conn:
                    result = conn.execute(text(query), params or {})
                    columns = result.keys()
                    rows = result.fetchall()
                    results = [dict(zip(columns, row)) for row in rows]
                    normalized_results = []
                    for row in results:
                        normalized_row = self._normalize_result_row(row)
                        normalized_results.append(normalized_row)
                    return normalized_results
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def _normalize_result_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a result row for API compatibility"""
        normalized = {}

        # Copy all fields as-is first
        for key, value in row.items():
            normalized[key] = value

        # Add uppercase versions of key fields for compatibility
        key_mappings = {
            'anumber': 'ANUMBER',
            'title': 'TITLE',
            'report_year': 'REPORT_YEAR',
            'operator': 'OPERATOR',
            'target_commodities': 'TARGET_COMMODITIES',
            'geometry': 'GEOMETRY'
        }

        for lowercase_key, uppercase_key in key_mappings.items():
            if lowercase_key in row:
                normalized[uppercase_key] = row[lowercase_key]

        # Add 'id' field mapping to anumber for API compatibility
        if 'anumber' in row:
            normalized['id'] = row['anumber']
        elif 'ANUMBER' in row:
            normalized['id'] = row['ANUMBER']

        return normalized

    def execute_query_to_dataframe(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Execute a query and return results as pandas DataFrame"""
        try:
            engine = self._get_engine()
            return pd.read_sql(query, engine, params=params)
        except Exception as e:
            logger.error(f"Query to DataFrame failed: {e}")
            raise

    def ensure_warehouse_database_schema(self):
        """Ensure the warehouse, database, and schema exist in Snowflake."""
        try:
            with snowflake.connector.connect(**self.config.get_connection_params()) as conn:
                cursor = conn.cursor()
                # Create warehouse if not exists
                if self.config.warehouse:
                    cursor.execute(f"CREATE WAREHOUSE IF NOT EXISTS {self.config.warehouse}")
                # Create database if not exists
                if self.config.database:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.database}")
                # Create schema if not exists
                if self.config.schema:
                    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self.config.database}.{self.config.schema}")
                cursor.close()
                logger.info("Ensured warehouse, database, and schema exist.")
        except Exception as e:
            logger.error(f"Failed to ensure warehouse/database/schema: {e}")
            raise

    def create_tables(self):
        """Create the required tables for geological data"""
        # Ensure warehouse, database, and schema exist first
        self.ensure_warehouse_database_schema()
        # SQL for creating tables with GEOGRAPHY support (no indexes for now)
        create_tables_sql = """
        -- Create main geological reports table
        CREATE TABLE IF NOT EXISTS GEOLOGICAL_REPORTS (
            ANUMBER INTEGER PRIMARY KEY,
            TITLE STRING,
            REPORT_YEAR FLOAT,
            AUTHOR_NAME STRING,
            AUTHOR_COMPANY STRING,
            REPORT_TYPE STRING,
            DATE_FROM TIMESTAMP,
            DATE_TO TIMESTAMP,
            PROJECT STRING,
            OPERATOR STRING,
            ABSTRACT STRING,
            KEYWORDS STRING,
            TARGET_COMMODITIES STRING,
            DATE_RELEASED TIMESTAMP,
            ITEM_NO FLOAT,
            DPXE_ABS STRING,
            DPXE_REP STRING,
            EXTRACT_DATE TIMESTAMP,
            DIGITAL_FI INTEGER,
            IS_SHAPED INTEGER,
            GEOMETRY GEOGRAPHY,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        -- Create metadata summary table
        CREATE TABLE IF NOT EXISTS REPORT_METADATA (
            REPORT_ID INTEGER,
            METADATA_TEXT STRING,
            EMBEDDING_VECTOR VECTOR(FLOAT, 1536),
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self.get_connection() as conn:
                # Execute each statement separately
                statements = create_tables_sql.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        conn.execute(text(statement))
            logger.info("Successfully created/verified all tables")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def load_shapefile_data(self, shapefile_path: str, max_records: int = None) -> int:
        """Load data from shapefile into Snowflake, optionally limiting to max_records."""
        try:
            # Load shapefile with GeoPandas
            logger.info(f"Loading shapefile: {shapefile_path}")
            gdf = gpd.read_file(shapefile_path)

            # Limit number of records if specified
            if max_records is not None:
                gdf = gdf.head(max_records).copy()
                logger.info(f"Limiting upload to first {max_records} records.")

            # Convert geometry to WKT for Snowflake, handling null geometries
            def safe_geometry_to_wkt(geom):
                """Safely convert geometry to WKT with size limits"""
                if geom is None or pd.isna(geom):
                    return None
                try:
                    wkt = geom.wkt
                    # Check if geometry is too complex
                    if len(wkt) > 1000000:  # 1MB limit for individual geometry
                        # Try to simplify the geometry
                        try:
                            simplified = geom.simplify(0.001)
                            simplified_wkt = simplified.wkt
                            if len(simplified_wkt) < len(wkt) * 0.8:
                                logger.debug(f"Simplified geometry: {len(wkt)} → {len(simplified_wkt)} chars")
                                return simplified_wkt
                            else:
                                logger.warning(f"Geometry too complex ({len(wkt)} chars), setting to NULL")
                                return None
                        except:
                            logger.warning(f"Failed to simplify complex geometry, setting to NULL")
                            return None
                    return wkt
                except Exception:
                    return None

            gdf['geometry_wkt'] = gdf['geometry'].apply(safe_geometry_to_wkt)

            # Prepare DataFrame for Snowflake
            df = pd.DataFrame(gdf.drop('geometry', axis=1))

            # Rename columns to match Snowflake schema
            column_mapping = {
                'ANUMBER': 'ANUMBER',
                'TITLE': 'TITLE',
                'REPORT_YEA': 'REPORT_YEAR',
                'AUTHOR_NAM': 'AUTHOR_NAME',
                'AUTHOR_COM': 'AUTHOR_COMPANY',
                'REPORT_TYP': 'REPORT_TYPE',
                'DATE_FROM': 'DATE_FROM',
                'DATE_TO': 'DATE_TO',
                'PROJECT': 'PROJECT',
                'OPERATOR': 'OPERATOR',
                'ABSTRACT': 'ABSTRACT',
                'KEYWORDS': 'KEYWORDS',
                'TARGET_COM': 'TARGET_COMMODITIES',
                'DATE_RELEA': 'DATE_RELEASED',
                'ITEM_NO': 'ITEM_NO',
                'DPXE_ABS': 'DPXE_ABS',
                'DPXE_REP': 'DPXE_REP',
                'EXTRACT_DA': 'EXTRACT_DATE',
                'DIGITAL_FI': 'DIGITAL_FI',
                'IS_SHAPED': 'IS_SHAPED',
                'geometry_wkt': 'GEOMETRY'
            }
            # Only map columns that exist
            existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=existing_mapping)

            # Clean oversized geometries to prevent upload failures
            if 'GEOMETRY' in df.columns:
                logger.info("Filtering oversized geometries...")
                # Geometry size diagnostics
                geom_sizes = df['GEOMETRY'].apply(lambda x: len(str(x)) if x else 0)
                logger.info(f"Geometry size analysis:")
                logger.info(f"  Max size: {geom_sizes.max():,} characters")
                logger.info(f"  95th percentile: {geom_sizes.quantile(0.95):,.0f} characters")
                logger.info(f"  90th percentile: {geom_sizes.quantile(0.90):,.0f} characters")
                logger.info(f"  Geometries > 100KB: {(geom_sizes > 100000).sum()}")
                logger.info(f"  Geometries > 500KB: {(geom_sizes > 500000).sum()}")
                logger.info(f"  Geometries > 1MB: {(geom_sizes > 1000000).sum()}")

                def filter_large_geometries(geom_wkt):
                    if geom_wkt is None or pd.isna(geom_wkt):
                        return None
                    geom_str = str(geom_wkt)
                    # Use 500KB as a starting threshold, adjust after diagnostics
                    if len(geom_str) > 500000:
                        try:
                            from shapely.wkt import loads
                            geom = loads(geom_wkt)
                            simplified = geom.simplify(0.001)
                            simplified_wkt = simplified.wkt
                            if len(simplified_wkt) < len(geom_str) * 0.7:
                                logger.info(f"Simplified geometry: {len(geom_str):,} → {len(simplified_wkt):,} chars")
                                return simplified_wkt
                            else:
                                logger.warning(f"Could not simplify geometry enough, setting to NULL")
                                return None
                        except Exception:
                            logger.warning(f"Failed to simplify large geometry, setting to NULL")
                            return None
                    return geom_wkt
                # Apply geometry filtering
                original_geom_count = df['GEOMETRY'].notna().sum()
                df['GEOMETRY'] = df['GEOMETRY'].apply(filter_large_geometries)
                filtered_geom_count = df['GEOMETRY'].notna().sum()
                logger.info(f"Geometry filtering: {original_geom_count}  {filtered_geom_count} valid geometries")

            # Log data quality info
            total_records = len(df)
            null_geometry_count = df['GEOMETRY'].isnull().sum()
            valid_geometry_count = total_records - null_geometry_count

            logger.info(f"Data quality summary:")
            logger.info(f"  Total records: {total_records}")
            logger.info(f"  Valid geometries: {valid_geometry_count}")
            logger.info(f"  Null geometries: {null_geometry_count}")

            # Verify table exists before loading
            with self.get_connection() as conn:
                result = conn.execute(text("SHOW TABLES LIKE 'GEOLOGICAL_REPORTS'"))
                tables = result.fetchall()
                if not tables:
                    logger.error("GEOLOGICAL_REPORTS table does not exist. Creating tables first...")
                    self.create_tables()

            # Clear existing data (since we're doing a fresh load)
            logger.info("Clearing existing data from GEOLOGICAL_REPORTS table...")
            with self.get_connection() as conn:
                conn.execute(text("TRUNCATE TABLE GEOLOGICAL_REPORTS"))

            # Load data to Snowflake using pandas (with explicit method)
            logger.info("Loading data to Snowflake...")
            engine = self._get_engine()

            uploaded_records = 0
            chunk_size = 1000  # Larger chunks for better performance
            num_chunks = (total_records + chunk_size - 1) // chunk_size
            logger.info(f"Starting upload: {total_records} records in {num_chunks} chunks of {chunk_size}.")
            failed_records = 0  # Track how many records we're losing
            for i in range(0, total_records, chunk_size):
                chunk_start = i
                chunk_end = min(i + chunk_size, total_records)
                chunk_df = df.iloc[chunk_start:chunk_end]
                chunk_num = (i // chunk_size) + 1
                percent = (chunk_end / total_records) * 100
                try:
                    with self._suppress_sqlalchemy_logging():
                        chunk_df.to_sql(
                            'GEOLOGICAL_REPORTS',
                            engine,
                            if_exists='append',
                            index=False,
                            method='multi'
                        )
                    uploaded_records += len(chunk_df)
                    if chunk_num % 10 == 0:
                        logger.info(f"Progress: {chunk_num}/{num_chunks} chunks ({percent:.1f}% complete)")
                except Exception as e:
                    clean_error = self._handle_upload_error(e, f"chunk {chunk_num}")
                    logger.error(clean_error)
                    if len(chunk_df) > 0:
                        sample = chunk_df.iloc[0]
                        logger.error(f"Sample record: ANUMBER={sample.get('ANUMBER', 'N/A')}, "
                                     f"TITLE='{str(sample.get('TITLE', 'N/A'))[:50]}...', "
                                     f"GEOMETRY_length={len(str(sample.get('GEOMETRY', '')))}")
                    logger.debug(f"Full chunk error details: {str(e)[:500]}...")
                    failed_records += len(chunk_df)
                    continue
            logger.info(f"Successfully loaded {uploaded_records} records to Snowflake")
            if failed_records > 0:
                logger.error(f"❌ DATA LOSS DETECTED: {failed_records} records failed to upload")
                logger.error(f"Success rate: {(uploaded_records/total_records)*100:.1f}%")
                logger.error("Check error logs above for specific chunk failures")
            else:
                logger.info(f"✅ All {uploaded_records} records uploaded successfully")
            return uploaded_records

        except Exception as e:
            logger.error(f"Failed to load shapefile data: {e}")
            raise

    def _handle_upload_error(self, error: Exception, context: str = "upload") -> str:
        """Convert verbose SQLAlchemy errors to clean, actionable messages"""
        error_str = str(error)
        error_patterns = {
            "duplicate key value violates unique constraint": "ANUMBER conflicts - records already exist",
            "invalid input syntax": "Data format error - check geometry or date fields",
            "constraint violation": "Data constraint error - check required fields",
            "connection timeout": "Snowflake connection timeout - retry with smaller chunks",
            "network error": "Network connection issue - check internet connection",
            "authentication": "Snowflake authentication failed - check credentials",
            "permission denied": "Insufficient Snowflake permissions",
            "too many parameters": "Chunk size too large - reduce chunk_size parameter"
        }
        for pattern, simple_msg in error_patterns.items():
            if pattern.lower() in error_str.lower():
                return f"{context.title()} failed: {simple_msg}"
        if len(error_str) > 200:
            return f"{context.title()} failed: {error_str[:200]}... (truncated)"
        return f"{context.title()} failed: {error_str}"

    @contextmanager
    def _suppress_sqlalchemy_logging(self):
        """Temporarily suppress SQLAlchemy's verbose logging during bulk operations"""
        engine_logger = logging.getLogger('sqlalchemy.engine')
        dialect_logger = logging.getLogger('sqlalchemy.dialects')
        original_engine_level = engine_logger.level
        original_dialect_level = dialect_logger.level
        try:
            engine_logger.setLevel(logging.ERROR)
            dialect_logger.setLevel(logging.ERROR)
            yield
        finally:
            engine_logger.setLevel(original_engine_level)
            dialect_logger.setLevel(original_dialect_level)

    def get_reports(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get geological reports with pagination - optimized for large requests"""
        # Add query hints for large requests
        if limit > 1000:
            query = """
            SELECT /*+ USE_CACHED_RESULT(FALSE) */
                   ANUMBER, TITLE, REPORT_YEAR, AUTHOR_COMPANY, OPERATOR,
                   TARGET_COMMODITIES, PROJECT, GEOMETRY
            FROM GEOLOGICAL_REPORTS
            ORDER BY ANUMBER
            LIMIT :limit OFFSET :offset
            """
        else:
            # Standard query for small requests
            query = """
            SELECT ANUMBER, TITLE, REPORT_YEAR, AUTHOR_COMPANY, OPERATOR,
                   TARGET_COMMODITIES, PROJECT, GEOMETRY
            FROM GEOLOGICAL_REPORTS
            ORDER BY ANUMBER
            LIMIT :limit OFFSET :offset
            """
        return self.execute_query(query, {"limit": limit, "offset": offset})

    def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID"""
        query = """
        SELECT * FROM GEOLOGICAL_REPORTS
        WHERE ANUMBER = :report_id
        """
        results = self.execute_query(query, {"report_id": report_id})
        return results[0] if results else None

    def filter_reports(self, commodity: Optional[str] = None,
                      year: Optional[int] = None,
                      company: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Filter reports by various criteria"""
        conditions = []
        params = {}

        if commodity:
            conditions.append("TARGET_COMMODITIES ILIKE :commodity")
            params["commodity"] = f"%{commodity}%"

        if year:
            conditions.append("REPORT_YEAR = :year")
            params["year"] = year

        if company:
            conditions.append("OPERATOR ILIKE :company")
            params["company"] = f"%{company}%"

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
        SELECT ANUMBER, TITLE, REPORT_YEAR, AUTHOR_COMPANY, OPERATOR,
               TARGET_COMMODITIES, PROJECT, GEOMETRY
        FROM GEOLOGICAL_REPORTS
        WHERE {where_clause}
        ORDER BY ANUMBER
        LIMIT :limit
        """
        params["limit"] = limit
        return self.execute_query(query, params)

    def spatial_query(self, latitude: float, longitude: float,
                     radius_km: float = 10.0) -> List[Dict[str, Any]]:
        """Perform spatial query to find reports near a location"""
        query = """
        SELECT ANUMBER, TITLE, REPORT_YEAR, OPERATOR, TARGET_COMMODITIES,
               ST_DISTANCE(
                   GEOMETRY,
                   ST_POINT(:longitude, :latitude)
               ) / 1000 as DISTANCE_KM,
               GEOMETRY
        FROM GEOLOGICAL_REPORTS
        WHERE ST_DWITHIN(
            GEOMETRY,
            ST_POINT(:longitude, :latitude),
            :radius_meters
        )
        ORDER BY DISTANCE_KM
        LIMIT 50
        """

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius_meters": radius_km * 1000  # Convert km to meters
        }

        return self.execute_query(query, params)

    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """Get data quality metrics for the geological reports"""
        query = """
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT OPERATOR) as unique_operators,
            COUNT(DISTINCT TARGET_COMMODITIES) as unique_commodities,
            MIN(REPORT_YEAR) as earliest_year,
            MAX(REPORT_YEAR) as latest_year,
            COUNT(CASE WHEN GEOMETRY IS NOT NULL THEN 1 END) as records_with_geometry,
            CURRENT_TIMESTAMP as last_updated
        FROM GEOLOGICAL_REPORTS
        """

        result = self.execute_query(query)
        return result[0] if result else {}

# Global client instance
snowflake_client = SnowflakeClient()
