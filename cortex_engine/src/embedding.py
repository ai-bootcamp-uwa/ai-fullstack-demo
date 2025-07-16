import numpy as np
import os
from openai import AzureOpenAI
from typing import List, Any

class EmbeddingGenerator:
    def __init__(self):
        self.client: AzureOpenAI
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        # Initialize client immediately
        self.load_model()

    def load_model(self):
        """Initialize the Azure OpenAI client."""
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://22965-md5ohpse-eastus2.cognitiveservices.azure.com/")
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required but not set")
            
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required but not set")
            
        try:
            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            print(f"Azure OpenAI client initialized with model: {self.model}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure OpenAI client: {e}")

    def generate_embeddings(self, data: List[Any]) -> np.ndarray:
        """Generate embeddings for the input data using Azure OpenAI text-embedding-ada-002."""
        # Ensure client is initialized
        assert self.client is not None, "Azure OpenAI client not initialized"
        
        # Convert data to strings if they aren't already
        texts = [str(item) for item in data]
        
        # Get embeddings from Azure OpenAI - NO FALLBACK
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        
        # Extract embeddings from response
        embeddings = [item.embedding for item in response.data]
        print(f"Generated {len(embeddings)} embeddings using Azure OpenAI {self.model}")
        return np.array(embeddings)
