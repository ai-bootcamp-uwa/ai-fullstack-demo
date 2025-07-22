import os
import numpy as np
from .config import AzureOpenAIConfig

class EmbeddingGenerator:
    def __init__(self):
        self.client = None
        self.model = os.getenv("EMBEDDING_MODEL")  # No default
        self.config = AzureOpenAIConfig()

    def load_model(self):
        """Initialize the Azure OpenAI client. Fail if not configured."""
        azure_endpoint = self.config.endpoint
        api_key = self.config.api_key
        api_version = self.config.api_version

        if not (api_key and azure_endpoint and api_version and self.model):
            raise RuntimeError("Azure OpenAI configuration is incomplete. Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, and EMBEDDING_MODEL in your environment. No fallback or local mode is allowed.")

        try:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            print(f"Azure OpenAI client initialized with model: {self.model}")
        except Exception as e:
            raise RuntimeError(f"Error initializing Azure OpenAI client: {e}")

    def generate_embeddings(self, data):
        """Generate embeddings for the input data using Azure OpenAI text-embedding-ada-002. No fallback allowed."""
        if self.client is None:
            self.load_model()

        try:
            texts = [str(item) for item in data]
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
        except Exception as e:
            raise RuntimeError(f"Error generating embeddings with Azure OpenAI: {e}")
