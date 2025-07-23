"""
Configuration module for cortex_engine Azure OpenAI + Snowflake hybrid integration.
Centralizes all model, API, and database settings - NO DEFAULTS, ONLY .env VALUES.
"""
import os
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AzureOpenAIConfig:
    """Configuration class for Azure OpenAI settings - strict mode, no defaults."""

    def __init__(self):
        # Azure OpenAI Connection Settings - NO DEFAULTS
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        # Model Configuration - NO DEFAULTS
        self.embedding_model = os.getenv("EMBEDDING_MODEL")
        self.chat_model = os.getenv("CHAT_MODEL")

        # Rate Limiting - with safe defaults only for optional parameters
        self.max_embedding_requests_per_minute = int(os.getenv("MAX_EMBEDDING_REQUESTS_PER_MINUTE", "120"))
        self.max_embedding_tokens_per_minute = int(os.getenv("MAX_EMBEDDING_TOKENS_PER_MINUTE", "20000"))

        # Retry Configuration - with safe defaults only for optional parameters
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay_seconds = int(os.getenv("RETRY_DELAY_SECONDS", "1"))

    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured."""
        return bool(
            self.api_key and
            self.endpoint and
            self.api_version and
            self.embedding_model and
            self.chat_model
        )

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate the configuration and return (is_valid, error_message)."""
        if not self.api_key:
            return False, "AZURE_OPENAI_API_KEY is required but not set in .env"

        if not self.endpoint:
            return False, "AZURE_OPENAI_ENDPOINT is required but not set in .env"

        if not self.api_version:
            return False, "AZURE_OPENAI_API_VERSION is required but not set in .env"

        # Accept all Azure endpoint formats
        valid_endings = ['.cognitiveservices.azure.com/', '.openai.azure.com/', '.services.ai.azure.com/']
        if not any(self.endpoint.endswith(ending) for ending in valid_endings):
            return False, "AZURE_OPENAI_ENDPOINT should end with '.cognitiveservices.azure.com/', '.openai.azure.com/', or '.services.ai.azure.com/'"

        if not self.embedding_model:
            return False, "EMBEDDING_MODEL is required but not set in .env"

        if not self.chat_model:
            return False, "CHAT_MODEL is required but not set in .env"

        return True, None

    def get_client_kwargs(self) -> dict:
        """Get keyword arguments for AzureOpenAI client initialization."""
        # Validate first
        is_valid, error_msg = self.validate_config()
        if not is_valid:
            raise ValueError(f"Cannot create client kwargs: {error_msg}")

        return {
            "azure_endpoint": self.endpoint,
            "api_key": self.api_key,
            "api_version": self.api_version
        }

    def __str__(self) -> str:
        """String representation (safe - no API key)."""
        return f"""AzureOpenAIConfig (Strict Mode - No Defaults):
  Endpoint: {self.endpoint or 'NOT SET'}
  API Version: {self.api_version or 'NOT SET'}
  Embedding Model: {self.embedding_model or 'NOT SET'}
  Chat Model: {self.chat_model or 'NOT SET'}
  Configured: {self.is_configured()}"""


class SnowflakeConfig:
    """Configuration class for Snowflake database settings."""

    def __init__(self):
        # Snowflake Connection Settings
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")
        
        # Optional Role Configuration
        self.role = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
        
        # Vector Processing Settings
        self.vector_dimension = int(os.getenv("VECTOR_DIMENSION", "1536"))  # Default for Azure text-embedding-ada-002
        self.batch_size = int(os.getenv("SNOWFLAKE_BATCH_SIZE", "1000"))
        
        # Connection Pool Settings
        self.pool_size = int(os.getenv("SNOWFLAKE_POOL_SIZE", "5"))
        self.pool_timeout = int(os.getenv("SNOWFLAKE_POOL_TIMEOUT", "30"))

    def is_configured(self) -> bool:
        """Check if Snowflake is properly configured."""
        return bool(
            self.account and
            self.user and
            self.password and
            self.warehouse and
            self.database and
            self.schema
        )

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate the Snowflake configuration and return (is_valid, error_message)."""
        if not self.account:
            return False, "SNOWFLAKE_ACCOUNT is required but not set in .env"

        if not self.user:
            return False, "SNOWFLAKE_USER is required but not set in .env"

        if not self.password:
            return False, "SNOWFLAKE_PASSWORD is required but not set in .env"

        if not self.warehouse:
            return False, "SNOWFLAKE_WAREHOUSE is required but not set in .env"

        if not self.database:
            return False, "SNOWFLAKE_DATABASE is required but not set in .env"

        if not self.schema:
            return False, "SNOWFLAKE_SCHEMA is required but not set in .env"

        return True, None

    def get_connection_params(self) -> dict:
        """Get connection parameters for Snowflake client."""
        is_valid, error_msg = self.validate_config()
        if not is_valid:
            raise ValueError(f"Cannot create connection params: {error_msg}")

        return {
            "account": self.account,
            "user": self.user,
            "password": self.password,
            "warehouse": self.warehouse,
            "database": self.database,
            "schema": self.schema,
            "role": self.role
        }

    def __str__(self) -> str:
        """String representation (safe - no password)."""
        return f"""SnowflakeConfig:
  Account: {self.account or 'NOT SET'}
  User: {self.user or 'NOT SET'}
  Warehouse: {self.warehouse or 'NOT SET'}
  Database: {self.database or 'NOT SET'}
  Schema: {self.schema or 'NOT SET'}
  Role: {self.role or 'NOT SET'}
  Vector Dimension: {self.vector_dimension}
  Configured: {self.is_configured()}"""


class HybridSystemConfig:
    """Configuration for the hybrid Azure OpenAI + Snowflake system."""
    
    def __init__(self):
        # Feature Flags for gradual rollout
        self.enable_hybrid_features = os.getenv("ENABLE_HYBRID_FEATURES", "false").lower() == "true"
        self.enable_snowflake_vectors = os.getenv("ENABLE_SNOWFLAKE_VECTORS", "false").lower() == "true"
        self.enable_title_embeddings = os.getenv("ENABLE_TITLE_EMBEDDINGS", "false").lower() == "true"
        
        # Performance Settings
        self.embedding_batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
        self.search_result_limit = int(os.getenv("SEARCH_RESULT_LIMIT", "10"))
        
        # Health Check Settings
        self.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))
        
    def is_hybrid_enabled(self) -> bool:
        """Check if hybrid features are enabled."""
        return self.enable_hybrid_features
    
    def __str__(self) -> str:
        """String representation."""
        return f"""HybridSystemConfig:
  Hybrid Features Enabled: {self.enable_hybrid_features}
  Snowflake Vectors Enabled: {self.enable_snowflake_vectors}
  Title Embeddings Enabled: {self.enable_title_embeddings}
  Embedding Batch Size: {self.embedding_batch_size}
  Search Result Limit: {self.search_result_limit}"""


class Config:
    """Unified configuration management for the hybrid system."""
    
    def __init__(self):
        self.azure_openai = AzureOpenAIConfig()
        self.snowflake = SnowflakeConfig()
        self.hybrid = HybridSystemConfig()
    
    def validate_all(self) -> dict:
        """Validate all configurations and return status."""
        azure_valid, azure_error = self.azure_openai.validate_config()
        snowflake_valid, snowflake_error = self.snowflake.validate_config()
        
        return {
            "azure_openai": {
                "configured": self.azure_openai.is_configured(),
                "valid": azure_valid,
                "error": azure_error
            },
            "snowflake": {
                "configured": self.snowflake.is_configured(),
                "valid": snowflake_valid,
                "error": snowflake_error
            },
            "hybrid": {
                "enabled": self.hybrid.is_hybrid_enabled()
            }
        }
    
    def is_ready_for_hybrid(self) -> bool:
        """Check if system is ready for hybrid operations."""
        azure_valid, _ = self.azure_openai.validate_config()
        snowflake_valid, _ = self.snowflake.validate_config()
        return azure_valid and snowflake_valid and self.hybrid.is_hybrid_enabled()

# Global configuration instances (backward compatibility)
config = AzureOpenAIConfig()  # Keep existing variable for backward compatibility

# New unified configuration
unified_config = Config()
