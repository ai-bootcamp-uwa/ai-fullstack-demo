"""
Configuration module for cortex_engine Azure OpenAI integration.
Centralizes all model and API settings.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AzureOpenAIConfig:
    """Configuration class for Azure OpenAI settings."""
    
    def __init__(self):
        # Azure OpenAI Connection Settings
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://22965-md5ohpse-eastus2.services.ai.azure.com/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        # Model Configuration
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        
        # Rate Limiting (from your Azure deployment)
        self.max_embedding_requests_per_minute = int(os.getenv("MAX_EMBEDDING_REQUESTS_PER_MINUTE", "120"))
        self.max_embedding_tokens_per_minute = int(os.getenv("MAX_EMBEDDING_TOKENS_PER_MINUTE", "20000"))
        
        # Retry Configuration
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay_seconds = int(os.getenv("RETRY_DELAY_SECONDS", "1"))
    
    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured."""
        return bool(self.api_key and self.endpoint)
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """Validate the configuration and return (is_valid, error_message)."""
        if not self.api_key:
            return False, "AZURE_OPENAI_API_KEY is not set"
        
        if not self.endpoint:
            return False, "AZURE_OPENAI_ENDPOINT is not set"
        
        # Accept all Azure endpoint formats
        valid_endings = ['.cognitiveservices.azure.com/', '.openai.azure.com/', '.services.ai.azure.com/']
        if not any(self.endpoint.endswith(ending) for ending in valid_endings):
            return False, "AZURE_OPENAI_ENDPOINT should end with '.cognitiveservices.azure.com/', '.openai.azure.com/', or '.services.ai.azure.com/'"
        
        if not self.embedding_model:
            return False, "EMBEDDING_MODEL is not set"
        
        if not self.chat_model:
            return False, "CHAT_MODEL is not set"
        
        return True, None
    
    def get_client_kwargs(self) -> dict:
        """Get keyword arguments for AzureOpenAI client initialization."""
        return {
            "azure_endpoint": self.endpoint,
            "api_key": self.api_key,
            "api_version": self.api_version
        }
    
    def __str__(self) -> str:
        """String representation (safe - no API key)."""
        return f"""AzureOpenAIConfig:
  Endpoint: {self.endpoint}
  API Version: {self.api_version}
  Embedding Model: {self.embedding_model}
  Chat Model: {self.chat_model}
  Configured: {self.is_configured()}"""

# Global configuration instance
config = AzureOpenAIConfig() 