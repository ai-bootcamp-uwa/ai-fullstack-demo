from pydantic import BaseModel
from typing import Optional, Dict

class LoginRequest(BaseModel):
    """User login request model."""
    username: str
    password: str

class GeologicalQueryRequest(BaseModel):
    """Geological data query request model."""
    query: str
    limit: int = 5  # Default to 5 for testing
    include_ai_insights: bool = True

class ChatRequest(BaseModel):
    """Chat message request model."""
    message: str
    conversation_id: Optional[str] = None

class SpatialQueryRequest(BaseModel):
    """Spatial/geographic query request model."""
    bounds: Optional[Dict[str, float]] = None  # {"north": -31.0, "south": -33.0, "east": 116.0, "west": 114.0}
    geometry: Optional[str] = None  # WKT geometry for spatial intersection
    distance_km: Optional[float] = None  # Distance from a point
    center_point: Optional[Dict[str, float]] = None  # {"lat": -32.0, "lng": 115.0}
    commodity: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    """Token refresh request model."""
    refresh_token: str

class TokenData(BaseModel):
    """JWT token data model."""
    username: Optional[str] = None 