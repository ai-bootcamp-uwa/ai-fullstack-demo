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

    def _get_vector_schema_sql(self) -> str:
        """Get the SQL statements for creating vector schema using VARIANT for embeddings."""
        return f"""
        -- Create table for storing title embeddings using VARIANT (compatible with Snowflake)
        CREATE TABLE IF NOT EXISTS TITLE_EMBEDDINGS (
            id INTEGER AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            title_text TEXT NOT NULL,
            embedding_vector VARIANT,
            model_used VARCHAR(100) DEFAULT 'text-embedding-ada-002',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        );

        -- Create table for tracking embedding jobs
        CREATE TABLE IF NOT EXISTS EMBEDDING_JOBS (
            job_id VARCHAR(100) PRIMARY KEY,
            job_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING',
            total_records INTEGER,
            processed_records INTEGER DEFAULT 0,
            failed_records INTEGER DEFAULT 0,
            error_message TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            metadata VARIANT
        );

        -- Create table for system health monitoring
        CREATE TABLE IF NOT EXISTS HYBRID_SYSTEM_HEALTH (
            check_id INTEGER AUTOINCREMENT,
            component VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL,
            response_time_ms INTEGER,
            error_message TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata VARIANT,
            PRIMARY KEY (check_id)
        );
        """

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
        """
        Store a single title embedding in Snowflake using raw connector and direct JSON.
        """
        if not self.test_connection():
            logger.error("Cannot store embedding: Snowflake connection failed")
            return False
        try:
            # Use raw Snowflake connector to avoid SQLAlchemy issues
            conn_params = self.config.get_connection_params()
            raw_conn = snowflake.connector.connect(**conn_params)
            cursor = None
            try:
                cursor = raw_conn.cursor()
                # Convert embedding to JSON array string
                embedding_json = json.dumps(embedding_vector)
                # Simple INSERT without PARSE_JSON - let Snowflake handle the conversion
                insert_sql = """
                INSERT INTO TITLE_EMBEDDINGS (report_id, title_text, embedding_vector, model_used, created_at)
                SELECT %s, %s, PARSE_JSON(%s), %s, CURRENT_TIMESTAMP
                """
                cursor.execute(insert_sql, (report_id, title_text, embedding_json, model_used))
                raw_conn.commit()
                logger.debug(f"Stored embedding for report {report_id}")
                return True
            finally:
                if cursor:
                    cursor.close()
                raw_conn.close()
        except Exception as e:
            logger.error(f"Failed to store embedding for report {report_id}: {e}")
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
        """Search for similar titles using array-based similarity calculation."""
        if not self.test_connection():
            logger.error("Cannot search: Snowflake connection failed")
            return []
        try:
            with self.get_connection() as conn:
                search_sql = """
                SELECT
                    te.report_id,
                    te.title_text,
                    ARRAY_INNER_PRODUCT(te.embedding_vector, PARSE_JSON(:query_vector)) /
                    (SQRT(ARRAY_INNER_PRODUCT(te.embedding_vector, te.embedding_vector)) *
                     SQRT(ARRAY_INNER_PRODUCT(PARSE_JSON(:query_vector), PARSE_JSON(:query_vector)))) as similarity_score,
                    te.model_used,
                    te.created_at
                FROM TITLE_EMBEDDINGS te
                WHERE te.embedding_vector IS NOT NULL
                ORDER BY similarity_score DESC
                LIMIT :limit
                """
                query_vector_json = json.dumps(query_embedding)
                results = conn.execute(text(search_sql), {
                    "query_vector": query_vector_json,
                    "limit": limit
                }).fetchall()
                return [
                    {
                        "report_id": row[0],
                        "title_text": row[1],
                        "similarity_score": float(row[2]) if row[2] else 0.0,
                        "model_used": row[3],
                        "created_at": str(row[4])
                    }
                    for row in results
                ]
        except Exception as e:
            logger.error(f"Failed to search similar titles: {e}")
            return []

    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search using VARIANT stored embeddings."""
        if not self.test_connection():
            logger.error("Cannot search: Snowflake connection failed")
            return []
        try:
            with self.get_connection() as conn:
                # Convert query to JSON for comparison
                query_json = json.dumps(query_embedding)
                # Use array functions for cosine similarity calculation
                search_sql = """
                SELECT
                    te.report_id,
                    te.title_text,
                    ARRAY_INNER_PRODUCT(te.embedding_vector, PARSE_JSON(:query_json)) /
                    (SQRT(ARRAY_INNER_PRODUCT(te.embedding_vector, te.embedding_vector)) *
                     SQRT(ARRAY_INNER_PRODUCT(PARSE_JSON(:query_json), PARSE_JSON(:query_json)))) as similarity_score,
                    te.model_used,
                    te.created_at
                FROM TITLE_EMBEDDINGS te
                WHERE te.embedding_vector IS NOT NULL
                ORDER BY similarity_score DESC
                LIMIT :limit
                """
                result = conn.execute(text(search_sql), {
                    "query_json": query_json,
                    "limit": top_k
                })
                results = result.fetchall()
                # Transform results to match expected format
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'id': row[0],  # report_id
                        'similarity_score': float(row[2]) if row[2] else 0.0,  # similarity_score
                        'metadata': {
                            'original_metadata': {
                                'report_id': row[0],
                                'model_used': row[3],
                                'created_at': str(row[4])
                            },
                            'text_content': row[1]  # title_text
                        }
                    })
                return formatted_results
        except Exception as e:
            logger.error(f"Failed to search similar titles: {e}")
            return []


# Global instance for the hybrid system
snowflake_vector_store = SnowflakeVectorStore()
