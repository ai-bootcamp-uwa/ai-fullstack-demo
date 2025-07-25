"""
Snowflake integration module for hybrid Azure OpenAI + Snowflake system.
Handles vector schema setup, connection management, and database operations.
"""
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
import snowflake.connector
from snowflake.connector import DictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import time
from contextlib import contextmanager

# Handle imports for both standalone and package usage
try:
    from .config import unified_config
except ImportError:
    from config import unified_config

logger = logging.getLogger(__name__)

class SnowflakeVectorStore:
    """Manages Snowflake vector storage operations for the hybrid system."""

    def __init__(self):
        self.config = unified_config.snowflake
        self._engine = None
        self._connection_tested = False

    def _get_engine(self):
        """Get or create SQLAlchemy engine for Snowflake connection."""
        if self._engine is None:
            try:
                params = self.config.get_connection_params()
                connection_string = (
                    f"snowflake://{params['user']}:{params['password']}@"
                    f"{params['account']}/{params['database']}/{params['schema']}"
                    f"?warehouse={params['warehouse']}&role={params['role']}"
                )
                self._engine = create_engine(connection_string, pool_size=self.config.pool_size)
                logger.info("Snowflake SQLAlchemy engine created successfully")
            except Exception as e:
                logger.error(f"Failed to create Snowflake engine: {e}")
                raise
        return self._engine

    @contextmanager
    def get_connection(self):
        """Get a database connection with proper cleanup."""
        engine = self._get_engine()
        connection = None
        try:
            connection = engine.connect()
            yield connection
        finally:
            if connection:
                connection.close()

    def test_connection(self) -> bool:
        """Test the Snowflake connection and return True if successful."""
        if not self.config.is_configured():
            logger.warning("Snowflake configuration is incomplete")
            return False

        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                if test_value == 1:
                    self._connection_tested = True
                    logger.info("Snowflake connection test successful")
                    return True
                else:
                    logger.error("Snowflake connection test failed: unexpected result")
                    return False
        except Exception as e:
            logger.error(f"Snowflake connection test failed: {e}")
            return False

    def create_vector_schema(self) -> bool:
        """Create the vector schema tables alongside existing geological data tables."""
        if not self.test_connection():
            logger.error("Cannot create vector schema: Snowflake connection failed")
            return False

        try:
            schema_sql = self._get_vector_schema_sql()

            with self.get_connection() as conn:
                # Execute each statement separately
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

                for statement in statements:
                    logger.debug(f"Executing: {statement[:100]}...")
                    conn.execute(text(statement))
                    conn.commit()

                logger.info("Vector schema created/verified successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to create vector schema: {e}")
            return False

    def add_embedding_columns_to_geological_reports(self) -> bool:
        """Add embedding columns to existing Module 1 GEOLOGICAL_REPORTS table"""
        if not self.test_connection():
            logger.error("Cannot alter table: Snowflake connection failed")
            return False
        try:
            alter_statements = [
                "ALTER TABLE GEOLOGICAL_REPORTS ADD COLUMN IF NOT EXISTS TITLE_EMBEDDING VARIANT",
                "ALTER TABLE GEOLOGICAL_REPORTS ADD COLUMN IF NOT EXISTS EMBEDDING_MODEL VARCHAR(100)",
                "ALTER TABLE GEOLOGICAL_REPORTS ADD COLUMN IF NOT EXISTS EMBEDDING_CREATED_AT TIMESTAMP"
            ]
            conn_params = self.config.get_connection_params()
            raw_conn = snowflake.connector.connect(**conn_params)
            try:
                cursor = raw_conn.cursor()
                for statement in alter_statements:
                    logger.info(f"Executing: {statement}")
                    cursor.execute(statement)
                    raw_conn.commit()
                logger.info("Successfully added embedding columns to GEOLOGICAL_REPORTS")
                return True
            finally:
                cursor.close()
                raw_conn.close()
        except Exception as e:
            logger.error(f"Failed to add embedding columns: {e}")
            return False

    def _get_vector_schema_sql(self) -> str:
        """(Deprecated) Get the SQL statements for creating vector schema."""
        return """(Deprecated)"""

    def get_vector_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored vectors and system health."""
        if not self.test_connection():
            return {"error": "Snowflake connection failed"}

        try:
            with self.get_connection() as conn:
                # Get title embeddings statistics
                title_stats_sql = """
                SELECT
                    COUNT(*) as total_title_embeddings,
                    COUNT(DISTINCT report_id) as unique_reports_with_embeddings,
                    COUNT(DISTINCT model_used) as different_models_used,
                    MIN(created_at) as earliest_embedding,
                    MAX(created_at) as latest_embedding
                FROM TITLE_EMBEDDINGS
                """

                # Get job statistics
                job_stats_sql = """
                SELECT
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_jobs,
                    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending_jobs
                FROM EMBEDDING_JOBS
                """

                # Get recent health checks
                health_stats_sql = """
                SELECT
                    component,
                    status,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(*) as check_count
                FROM HYBRID_SYSTEM_HEALTH
                WHERE checked_at >= DATEADD(HOUR, -24, CURRENT_TIMESTAMP)
                GROUP BY component, status
                ORDER BY component, status
                """

                title_result = conn.execute(text(title_stats_sql)).fetchone()
                job_result = conn.execute(text(job_stats_sql)).fetchone()
                health_results = conn.execute(text(health_stats_sql)).fetchall()

                return {
                    "title_embeddings": {
                        "total_embeddings": title_result[0] if title_result else 0,
                        "unique_reports": title_result[1] if title_result else 0,
                        "models_used": title_result[2] if title_result else 0,
                        "earliest_embedding": str(title_result[3]) if title_result and title_result[3] else None,
                        "latest_embedding": str(title_result[4]) if title_result and title_result[4] else None
                    },
                    "embedding_jobs": {
                        "total_jobs": job_result[0] if job_result else 0,
                        "completed_jobs": job_result[1] if job_result else 0,
                        "failed_jobs": job_result[2] if job_result else 0,
                        "pending_jobs": job_result[3] if job_result else 0
                    },
                    "health_checks_24h": [
                        {
                            "component": row[0],
                            "status": row[1],
                            "avg_response_time_ms": float(row[2]) if row[2] else None,
                            "check_count": row[3]
                        }
                        for row in health_results
                    ]
                }

        except Exception as e:
            logger.error(f"Failed to get vector statistics: {e}")
            return {"error": str(e)}

    def _supports_vector_type(self) -> bool:
        """Check if Snowflake instance supports VECTOR data types."""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT SYSTEM$GET_SUPPORTED_FEATURES('VECTOR_DATA_TYPE')")).fetchone()
                return bool(result and result[0])
        except Exception:
            return False

    def store_embedding(self, report_id: int, title_text: str, embedding_vector: List[float],
                       model_used: str = "text-embedding-ada-002") -> bool:
        """Update existing GEOLOGICAL_REPORTS record with embedding"""
        if not self.test_connection():
            logger.error("Cannot store embedding: Snowflake connection failed")
            return False
        try:
            conn_params = self.config.get_connection_params()
            raw_conn = snowflake.connector.connect(**conn_params)
            try:
                cursor = raw_conn.cursor()
                embedding_json = json.dumps(embedding_vector)
                update_sql = """
                UPDATE GEOLOGICAL_REPORTS
                SET TITLE_EMBEDDING = PARSE_JSON(%s),
                    EMBEDDING_MODEL = %s,
                    EMBEDDING_CREATED_AT = CURRENT_TIMESTAMP
                WHERE ANUMBER = %s
                """
                cursor.execute(update_sql, (embedding_json, model_used, report_id))
                if cursor.rowcount == 0:
                    logger.warning(f"No record found with ANUMBER = {report_id}")
                    return False
                raw_conn.commit()
                logger.debug(f"Updated embedding for report {report_id}")
                return True
            finally:
                cursor.close()
                raw_conn.close()
        except Exception as e:
            logger.error(f"Failed to store embedding for report {report_id}: {e}")
            return False

    def store_embeddings_bulk(self, embedding_data: List[Dict]) -> bool:
        """Store multiple embeddings in a single transaction"""
        try:
            conn_params = self.config.get_connection_params()
            raw_conn = snowflake.connector.connect(**conn_params)
            try:
                cursor = raw_conn.cursor()
                # Prepare bulk update using CASE WHEN for each report
                if not embedding_data:
                    return True
                case_title_embedding = "\n".join([
                    f"WHEN {data['report_id']} THEN PARSE_JSON(%s)" for data in embedding_data
                ])
                case_model = "\n".join([
                    f"WHEN {data['report_id']} THEN %s" for data in embedding_data
                ])
                report_ids = [str(data['report_id']) for data in embedding_data]
                update_sql = f"""
                UPDATE GEOLOGICAL_REPORTS
                SET TITLE_EMBEDDING = CASE ANUMBER
                {case_title_embedding}
                END,
                EMBEDDING_MODEL = CASE ANUMBER
                {case_model}
                END,
                EMBEDDING_CREATED_AT = CURRENT_TIMESTAMP
                WHERE ANUMBER IN ({','.join(report_ids)})
                """
                params = []
                for data in embedding_data:
                    params.append(json.dumps(data['embedding_vector']))
                for data in embedding_data:
                    params.append(data['model_used'])
                cursor.execute(update_sql, params)
                raw_conn.commit()
                return True
            finally:
                cursor.close()
                raw_conn.close()
        except Exception as e:
            logger.error(f"Failed to store embeddings in bulk: {e}")
            return False

    def record_health_check(self, component: str, status: str, response_time_ms: int = None,
                           error_message: str = None, metadata: Dict = None) -> bool:
        """Record a health check result."""
        logger.debug(f"Attempting to record health check for component: {component}")

        if not self.test_connection():
            logger.warning("Cannot record health check: Snowflake connection failed")
            return False

        try:
            with self.get_connection() as conn:
                # Convert metadata to JSON string for VARIANT type
                # Snowflake will automatically convert JSON strings to VARIANT
                metadata_json = None
                if metadata:
                    try:
                        metadata_json = json.dumps(metadata)
                        logger.debug(f"Metadata converted to JSON: {metadata_json}")
                    except Exception as e:
                        logger.error(f"Failed to convert metadata to JSON: {e}")
                        return False

                insert_sql = """
                INSERT INTO HYBRID_SYSTEM_HEALTH
                (component, status, response_time_ms, error_message, metadata, checked_at)
                SELECT :component, :status, :response_time_ms, :error_message,
                       CASE WHEN :metadata IS NOT NULL THEN PARSE_JSON(:metadata) ELSE NULL END,
                       CURRENT_TIMESTAMP
                """

                params = {
                    "component": component,
                    "status": status,
                    "response_time_ms": response_time_ms,
                    "error_message": error_message,
                    "metadata": metadata_json  # JSON string or None - Snowflake handles conversion
                }

                logger.debug(f"Executing SQL with params: {params}")

                conn.execute(text(insert_sql), params)
                conn.commit()

                logger.info(f"Successfully recorded health check for component {component}")
                return True

        except Exception as e:
            logger.error(f"Failed to record health check for {component}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            # Log the full exception details for debugging
            logger.exception("Health check recording exception details:")
            return False

    def search_similar_titles(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar titles using robust CTE-based cosine similarity in Snowflake."""
        if not self.test_connection():
            logger.error("Cannot search: Snowflake connection failed")
            return []
        try:
            conn_params = self.config.get_connection_params()
            raw_conn = snowflake.connector.connect(**conn_params)
            try:
                cursor = raw_conn.cursor(snowflake.connector.DictCursor)
                query_json = json.dumps(query_embedding)
                search_sql = """
                WITH
                  query_vector AS (
                    SELECT PARSE_JSON(%s) AS qv
                  ),
                  flattened AS (
                    SELECT
                      r.ANUMBER,
                      r.TITLE,
                      r.OPERATOR,
                      r.TARGET_COMMODITIES,
                      r.REPORT_YEAR,
                      s.index AS idx,
                      s.value::FLOAT AS stored_value,
                      q.qv[s.index]::FLOAT AS query_value
                    FROM GEOLOGICAL_REPORTS r
                    CROSS JOIN query_vector q
                    , TABLE(FLATTEN(input => r.TITLE_EMBEDDING)) s
                    WHERE r.TITLE_EMBEDDING IS NOT NULL
                  ),
                  aggregates AS (
                    SELECT
                      ANUMBER,
                      TITLE,
                      OPERATOR,
                      TARGET_COMMODITIES,
                      REPORT_YEAR,
                      SUM(stored_value * query_value) AS dot_product,
                      SQRT(SUM(POW(stored_value, 2))) AS stored_magnitude,
                      SQRT(SUM(POW(query_value, 2))) AS query_magnitude
                    FROM flattened
                    GROUP BY ANUMBER, TITLE, OPERATOR, TARGET_COMMODITIES, REPORT_YEAR
                  )
                SELECT
                  ANUMBER,
                  TITLE,
                  OPERATOR,
                  TARGET_COMMODITIES,
                  REPORT_YEAR,
                  CASE
                    WHEN stored_magnitude > 0 AND query_magnitude > 0
                    THEN dot_product / (stored_magnitude * query_magnitude)
                    ELSE 0.0
                  END AS similarity_score
                FROM aggregates
                WHERE similarity_score >= 0
                ORDER BY similarity_score DESC
                LIMIT %s
                """
                cursor.execute(search_sql, (query_json, limit))
                results = cursor.fetchall()
                return [
                    {
                        "report_id": row['ANUMBER'],
                        "title_text": row['TITLE'],
                        "similarity_score": float(row['SIMILARITY_SCORE']) if row['SIMILARITY_SCORE'] else 0.0,
                        "operator": row['OPERATOR'],
                        "commodities": row['TARGET_COMMODITIES'],
                        "year": row['REPORT_YEAR']
                    }
                    for row in results
                ]
            finally:
                raw_conn.close()
        except Exception as e:
            logger.error(f"Failed to search similar titles: {e}")
            return []

    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search using embeddings stored in GEOLOGICAL_REPORTS table with robust CTE-based cosine similarity in Snowflake."""
        try:
            conn_params = self.config.get_connection_params()
            raw_conn = snowflake.connector.connect(**conn_params)
            try:
                cursor = raw_conn.cursor(snowflake.connector.DictCursor)
                query_json = json.dumps(query_embedding)
                search_sql = """
                WITH
                  query_vector AS (
                    SELECT PARSE_JSON(%s) AS qv
                  ),
                  flattened AS (
                    SELECT
                      r.ANUMBER,
                      r.TITLE,
                      r.OPERATOR,
                      r.TARGET_COMMODITIES,
                      r.REPORT_YEAR,
                      s.index AS idx,
                      s.value::FLOAT AS stored_value,
                      q.qv[s.index]::FLOAT AS query_value
                    FROM GEOLOGICAL_REPORTS r
                    CROSS JOIN query_vector q
                    , TABLE(FLATTEN(input => r.TITLE_EMBEDDING)) s
                    WHERE r.TITLE_EMBEDDING IS NOT NULL
                  ),
                  aggregates AS (
                    SELECT
                      ANUMBER,
                      TITLE,
                      OPERATOR,
                      TARGET_COMMODITIES,
                      REPORT_YEAR,
                      SUM(stored_value * query_value) AS dot_product,
                      SQRT(SUM(POW(stored_value, 2))) AS stored_magnitude,
                      SQRT(SUM(POW(query_value, 2))) AS query_magnitude
                    FROM flattened
                    GROUP BY ANUMBER, TITLE, OPERATOR, TARGET_COMMODITIES, REPORT_YEAR
                  )
                SELECT
                  ANUMBER,
                  TITLE,
                  OPERATOR,
                  TARGET_COMMODITIES,
                  REPORT_YEAR,
                  CASE
                    WHEN stored_magnitude > 0 AND query_magnitude > 0
                    THEN dot_product / (stored_magnitude * query_magnitude)
                    ELSE 0.0
                  END AS similarity_score
                FROM aggregates
                WHERE similarity_score >= 0
                ORDER BY similarity_score DESC
                LIMIT %s
                """
                cursor.execute(search_sql, (query_json, top_k))
                results = cursor.fetchall()
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'id': row['ANUMBER'],
                        'similarity_score': float(row['SIMILARITY_SCORE']) if row['SIMILARITY_SCORE'] else 0.0,
                        'metadata': {
                            'original_metadata': {
                                'report_id': row['ANUMBER'],
                                'operator': row['OPERATOR'],
                                'commodities': row['TARGET_COMMODITIES'],
                                'year': row['REPORT_YEAR']
                            },
                            'text_content': row['TITLE']
                        }
                    })
                return formatted_results
            finally:
                cursor.close()
                raw_conn.close()
        except Exception as e:
            logger.error(f"Failed to search similar titles: {e}")
            return []

    def get_reports_needing_embeddings(self, limit: int = 1000) -> List[int]:
        """Get ANUMBER of reports that don't have embeddings yet"""
        try:
            conn_params = self.config.get_connection_params()
            raw_conn = snowflake.connector.connect(**conn_params)
            try:
                cursor = raw_conn.cursor()
                query = """
                SELECT ANUMBER
                FROM GEOLOGICAL_REPORTS
                WHERE TITLE IS NOT NULL
                AND (TITLE_EMBEDDING IS NULL OR TITLE_EMBEDDING = 'null')
                ORDER BY ANUMBER
                LIMIT %s
                """
                cursor.execute(query, (limit,))
                results = cursor.fetchall()
                return [row[0] for row in results]
            finally:
                cursor.close()
                raw_conn.close()
        except Exception as e:
            logger.error(f"Failed to get reports needing embeddings: {e}")
            return []


# Global instance for the hybrid system
snowflake_vector_store = SnowflakeVectorStore()
