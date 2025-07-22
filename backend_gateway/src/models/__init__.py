"""Data models for API requests and responses."""

from .requests import (
    LoginRequest,
    GeologicalQueryRequest,
    ChatRequest,
    SpatialQueryRequest,
    RefreshTokenRequest,
    # New chat history requests
    CreateChatRequest,
    ChatMessageRequest
)

from .responses import (
    LoginResponse,
    UserProfile,
    GeologicalQueryResponse,
    ChatResponse,
    SpatialQueryResponse,
    QualityMetricsResponse,
    HealthResponse,
    # New chat history responses
    ChatSessionResponse,
    ChatListResponse,
    ChatDetailResponse,
    EnhancedChatResponse
)

from .chat import (
    ChatSession,
    ChatMessage,
    ChatHistory
)

__all__ = [
    # Request models
    "LoginRequest",
    "GeologicalQueryRequest", 
    "ChatRequest",
    "SpatialQueryRequest",
    "RefreshTokenRequest",
    "CreateChatRequest",
    "ChatMessageRequest",
    # Response models
    "LoginResponse",
    "UserProfile",
    "GeologicalQueryResponse",
    "ChatResponse",
    "SpatialQueryResponse",
    "QualityMetricsResponse",
    "HealthResponse",
    "ChatSessionResponse",
    "ChatListResponse", 
    "ChatDetailResponse",
    "EnhancedChatResponse",
    # Chat data models
    "ChatSession",
    "ChatMessage",
    "ChatHistory"
] 