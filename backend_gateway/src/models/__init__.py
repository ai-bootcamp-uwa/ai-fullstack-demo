"""Data models for API requests and responses."""

from .requests import (
    LoginRequest,
    GeologicalQueryRequest,
    ChatRequest,
    SpatialQueryRequest,
    RefreshTokenRequest
)

from .responses import (
    LoginResponse,
    UserProfile,
    GeologicalQueryResponse,
    ChatResponse,
    SpatialQueryResponse,
    QualityMetricsResponse,
    HealthResponse
)

__all__ = [
    # Request models
    "LoginRequest",
    "GeologicalQueryRequest", 
    "ChatRequest",
    "SpatialQueryRequest",
    "RefreshTokenRequest",
    # Response models
    "LoginResponse",
    "UserProfile",
    "GeologicalQueryResponse",
    "ChatResponse",
    "SpatialQueryResponse",
    "QualityMetricsResponse",
    "HealthResponse"
] 