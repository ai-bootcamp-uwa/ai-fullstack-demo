import os
import numpy as np
import logging

# Handle imports for both standalone and package usage
try:
    from .config import unified_config
except ImportError:
    from config import unified_config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, use_hybrid=False):
        """
        Initialize embedding generator with optional hybrid configuration.
        
        Args:
            use_hybrid (bool): Whether to use hybrid config or legacy config
        """
        self.client = None
        self.use_hybrid = use_hybrid
        
        if use_hybrid:
            # Use unified hybrid configuration  
            azure_config = unified_config.azure_openai
            self.config = azure_config
            self.model = azure_config.embedding_model if azure_config and azure_config.is_configured() else None
        else:
            # Legacy mode - maintain backward compatibility
            try:
                from .config import AzureOpenAIConfig
            except ImportError:
                from config import AzureOpenAIConfig
            self.config = AzureOpenAIConfig()
            self.model = os.getenv("EMBEDDING_MODEL")  # No default

    def load_model(self):
        """Initialize the Azure OpenAI client. Fail if not configured."""
        if self.use_hybrid and self.config and self.config.is_configured():
            # Use hybrid configuration
            azure_endpoint = self.config.endpoint
            api_key = self.config.api_key
            api_version = self.config.api_version
            model = self.config.embedding_model
        else:
            # Legacy configuration
            azure_endpoint = self.config.endpoint
            api_key = self.config.api_key
            api_version = self.config.api_version
            model = self.model

        if not (api_key and azure_endpoint and api_version and model):
            config_type = "hybrid" if self.use_hybrid else "legacy"
            raise RuntimeError(f"Azure OpenAI configuration ({config_type}) is incomplete. Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, and EMBEDDING_MODEL in your environment. No fallback or local mode is allowed.")

        try:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            logger.info(f"Azure OpenAI client initialized with model: {model} (config: {'hybrid' if self.use_hybrid else 'legacy'})")
        except Exception as e:
            raise RuntimeError(f"Error initializing Azure OpenAI client: {e}")

    def generate_embeddings(self, data):
        """Generate embeddings for the input data using Azure OpenAI. No fallback allowed."""
        if self.client is None:
            self.load_model()

        # Determine model to use
        model = (self.config.embedding_model if self.use_hybrid and self.config 
                else self.model)

        try:
            texts = [str(item) for item in data]
            logger.debug(f"Generating embeddings for {len(texts)} items using model: {model}")
            
            response = self.client.embeddings.create(
                input=texts,
                model=model
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return np.array(embeddings)
        except Exception as e:
            raise RuntimeError(f"Error generating embeddings with Azure OpenAI: {e}")

    def generate_title_embeddings(self, titles, preprocess=True):
        """
        Generate embeddings specifically for title data with optional preprocessing.
        
        Args:
            titles (list): List of title strings
            preprocess (bool): Whether to apply title-specific preprocessing
            
        Returns:
            np.ndarray: Array of embeddings
        """
        if preprocess:
            processed_titles = self._preprocess_titles(titles)
        else:
            processed_titles = titles
            
        logger.info(f"Generating title embeddings for {len(processed_titles)} titles")
        return self.generate_embeddings(processed_titles)

    def _preprocess_titles(self, titles):
        """
        Apply title-specific preprocessing to improve embedding quality.
        
        Args:
            titles (list): Raw title strings
            
        Returns:
            list: Processed title strings
        """
        processed = []
        for title in titles:
            if not title or not isinstance(title, str):
                processed.append("")
                continue
                
            # Basic title preprocessing
            title = title.strip()
            
            # Remove excessive punctuation but keep meaningful structure
            title = title.replace('_', ' ').replace('-', ' ')
            
            # Normalize whitespace
            title = ' '.join(title.split())
            
            # Add context prefix for better embeddings
            if len(title) > 0:
                title = f"Document title: {title}"
            
            processed.append(title)
            
        logger.debug(f"Preprocessed {len(titles)} titles")
        return processed

    def get_embedding_dimension(self):
        """
        Get the dimension of embeddings produced by the current model.
        
        Returns:
            int: Embedding dimension
        """
        # Common embedding dimensions for Azure OpenAI models
        model = (self.config.embedding_model if self.use_hybrid and self.config 
                else self.model)
        
        # Default dimensions for common models
        model_dimensions = {
            'text-embedding-ada-002': 1536,
            'text-embedding-3-small': 1536,
            'text-embedding-3-large': 3072
        }
        
        return model_dimensions.get(model, 1536)  # Default to ada-002 dimension

    def is_configured(self):
        """
        Check if the embedding generator is properly configured.
        
        Returns:
            bool: True if configured, False otherwise
        """
        if self.use_hybrid:
            return (self.config and self.config.is_configured() and 
                   hasattr(self.config, 'embedding_model') and self.config.embedding_model)
        else:
            return (self.config.endpoint and self.config.api_key and 
                   self.config.api_version and self.model)
