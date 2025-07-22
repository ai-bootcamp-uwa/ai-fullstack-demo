from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LoginResponse(BaseModel):
    """User login response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfile(BaseModel):
    """User profile response model."""
    username: str
    role: str

class GeologicalSite(BaseModel):
    """Individual geological site model."""
    site_id: str
    name: str
    commodity: List[str]
    operator: str
    report_year: int
    location: Dict[str, float]  # {"lat": -32.1, "lng": 115.8}

class GeologicalQueryResponse(BaseModel):
    """Geological query response model."""
    query: str
    ai_explanation: str
    results: List[Dict[str, Any]]
    total_found: int

class ChatResponse(BaseModel):
    """Chat message response model."""
    response: str
    conversation_id: str
    timestamp: datetime
    sources: List[str] = []

class SpatialQueryResponse(BaseModel):
    """Spatial query response model."""
    results: List[Dict[str, Any]]
    total_found: int
    query_params: Dict[str, Any]

class QualityMetricsResponse(BaseModel):
    """Data quality metrics response model."""
    total_reports: int
    unique_commodities: int
    date_range: Dict[str, str]
    data_quality_score: float
    sample_size: int

class HealthResponse(BaseModel):
    """Service health check response model."""
    status: str
    service: str
    dependencies: Optional[Dict[str, str]] = None

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    timestamp: datetime

# New chat history response models
class ChatSessionResponse(BaseModel):
    """Response for chat session information."""
    chat_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class ChatListResponse(BaseModel):
    """Response for listing user's chat sessions."""
    chats: List[ChatSessionResponse]
    total: int

class ChatDetailResponse(BaseModel):
    """Response for detailed chat history with messages."""
    session: ChatSessionResponse
    messages: List[Dict[str, Any]]  # Will contain ChatMessage data

class EnhancedChatResponse(BaseModel):
    """Response for enhanced chat with history context."""
    message_id: str
    response: str
    chat_id: str
    timestamp: datetime
    context_messages_used: int  # How many previous messages included 