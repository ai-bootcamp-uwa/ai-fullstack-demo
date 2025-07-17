import numpy as np
from openai import AzureOpenAI
from typing import List, Any
from config import config

class EmbeddingGenerator:
    def __init__(self):
        self.client: AzureOpenAI = None
        # Initialize client immediately
        self.load_model()

    def load_model(self):
        """Initialize the Azure OpenAI client using centralized config."""
        # Validate configuration first
        is_valid, error_msg = config.validate_config()

        if not is_valid:
            raise ValueError(f"Azure OpenAI configuration invalid: {error_msg}")

        try:
            # Use centralized config
            client_kwargs = config.get_client_kwargs()
            self.client = AzureOpenAI(**client_kwargs)
            print(f"Azure OpenAI client initialized with model: {config.embedding_model}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure OpenAI client: {e}")

    def generate_embeddings(self, data: List[Any]) -> np.ndarray:
        """Generate embeddings for the input data using Azure OpenAI."""
        # Ensure client is initialized
        if self.client is None:
            raise RuntimeError("Azure OpenAI client not initialized")

        # Convert data to strings if they aren't already
        texts = [str(item) for item in data]

        try:
            # Use the configured embedding model (deployment name)
            response = self.client.embeddings.create(
                input=texts,
                model=config.embedding_model  # This should be the deployment name
            )

            # Extract embeddings from response
            embeddings = [item.embedding for item in response.data]
            print(f"Generated {len(embeddings)} embeddings using {config.embedding_model}")
            return np.array(embeddings)

        except Exception as e:
            # Better error handling with specific Azure OpenAI errors
            if "DeploymentNotFound" in str(e):
                raise RuntimeError(f"Deployment '{config.embedding_model}' not found. Check your Azure OpenAI deployment name.")
            elif "InvalidRequestError" in str(e):
                raise RuntimeError(f"Invalid request to Azure OpenAI: {e}")
            else:
                raise RuntimeError(f"Azure OpenAI API error: {e}")
