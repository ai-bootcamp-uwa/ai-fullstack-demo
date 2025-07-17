"""
Configuration module for cortex_engine Azure OpenAI integration.
Centralizes all model and API settings - NO DEFAULTS, ONLY .env VALUES.
"""
import os
from typing import Optional
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

    def validate_config(self) -> tuple[bool, Optional[str]]:
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

# Global configuration instance
config = AzureOpenAIConfig()
