import httpx
from typing import List, Dict, Any

from ..core.config import settings

class CortexEngineClient:
    """Client for Cortex Engine API (Module 2) - Port 3002"""
    
    def __init__(self):
        self.base_url = settings.cortex_engine_url

    async def health_check(self):
        """Check health using actual Module 2 endpoint: GET /health"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Cortex Engine service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Cortex Engine error: {e.response.status_code}")

    async def get_config(self):
        """Get config using actual Module 2 endpoint: GET /config"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/config")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Cortex Engine service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Cortex Engine error: {e.response.status_code}")

    async def generate_embeddings(self, data: List[str]):
        """Generate embeddings using actual Module 2 endpoint: POST /embed"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/embed",
                    json={"data": data}
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Cortex Engine service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Cortex Engine error: {e.response.status_code}")

    async def rag_query(self, query: str):
        """RAG query using actual Module 2 endpoint: POST /rag-query (this IS the chat functionality)"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/rag-query",
                    json={"query": query}
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Cortex Engine service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Cortex Engine error: {e.response.status_code}")

    async def similarity_search(self, query_vector: List[float], top_k: int = 5):
        """Similarity search using actual Module 2 endpoint: POST /similarity-search"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/similarity-search",
                    json={"query_vector": query_vector, "top_k": top_k}
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Cortex Engine service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Cortex Engine error: {e.response.status_code}") 