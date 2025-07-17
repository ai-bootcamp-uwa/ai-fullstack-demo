"""Service clients for external API integration."""

from .data_client import DataFoundationClient
from .cortex_client import CortexEngineClient

# Global service instances
data_client = DataFoundationClient()
cortex_client = CortexEngineClient()

__all__ = [
    "DataFoundationClient",
    "CortexEngineClient", 
    "data_client",
    "cortex_client"
] 