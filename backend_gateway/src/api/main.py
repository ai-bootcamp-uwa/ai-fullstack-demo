from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Dict, Any

# Local imports - updated for new structure
from ..core.config import settings
from ..core.auth import authenticate_user, create_access_token, get_current_user, get_user_profile
from ..services import data_client, cortex_client
from ..services.chat_service import chat_service
from ..models.chat import ChatMessage
from ..models import (
    LoginRequest, LoginResponse, UserProfile,
    GeologicalQueryRequest, GeologicalQueryResponse,
    ChatRequest, ChatResponse,
    SpatialQueryRequest, SpatialQueryResponse,
    QualityMetricsResponse, HealthResponse,
    RefreshTokenRequest,
    # New chat history models
    CreateChatRequest, ChatMessageRequest,
    ChatSessionResponse, ChatListResponse, 
    ChatDetailResponse, EnhancedChatResponse
)

# Create FastAPI app
app = FastAPI(
    title="Backend Gateway API",
    description="Module 3 - Gateway API for Data Foundation and Cortex Engine",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/api/backend/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    dependencies = {}
    
    # Check Data Foundation service
    try:
        await data_client.get_reports(limit=1)
        dependencies["data_foundation"] = "healthy"
    except Exception:
        dependencies["data_foundation"] = "unhealthy"
    
    # Check Cortex Engine service
    try:
        await cortex_client.health_check()
        dependencies["cortex_engine"] = "healthy"
    except Exception:
        dependencies["cortex_engine"] = "unhealthy"
    
    return HealthResponse(
        status="ok",
        service="backend-gateway",
        dependencies=dependencies
    )

# Authentication endpoints
@app.post("/api/backend/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.token_expire_minutes * 60
    )

@app.post("/api/backend/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout endpoint"""
    return {"message": "Successfully logged out"}

@app.get("/api/backend/auth/profile", response_model=UserProfile)
async def profile(current_user: dict = Depends(get_user_profile)):
    """Get user profile"""
    return UserProfile(
        username=current_user["username"],
        role=current_user["role"]
    )

@app.post("/api/backend/auth/refresh")
async def refresh_token(request: RefreshTokenRequest, current_user: dict = Depends(get_current_user)):
    """Refresh JWT token"""
    access_token_expires = timedelta(minutes=settings.token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user["username"]}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.token_expire_minutes * 60
    )

# Core geological query endpoint (required from API table)
@app.post("/api/backend/geological-query", response_model=GeologicalQueryResponse)
async def geological_query(request: GeologicalQueryRequest, current_user: dict = Depends(get_current_user)):
    """Natural language geological query combining AI insights with data"""
    try:
        # 1. Use AI to understand the query via Module 2 RAG
        ai_response = await cortex_client.rag_query(request.query)
        
        # 2. Get relevant reports from Module 1 (limited to 5 for testing)
        reports = await data_client.get_reports(limit=min(request.limit, 5))
        
        # 3. Combine AI insights with data
        return GeologicalQueryResponse(
            query=request.query,
            ai_explanation=ai_response.get("result", "No AI response available"),
            results=reports[:request.limit] if isinstance(reports, list) else [],
            total_found=len(reports) if isinstance(reports, list) else 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

# Enhanced chat endpoint with history support
@app.post("/api/backend/chat", response_model=EnhancedChatResponse)
async def chat(request: ChatMessageRequest, current_user: dict = Depends(get_current_user)):
    """Enhanced chat with history support and context awareness"""
    try:
        user_id = current_user["username"]
        
        # Get chat history for context
        history = await chat_service.get_chat_history(user_id, request.chat_id)
        if not history:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Add user message to history
        user_message = ChatMessage(role="user", content=request.message)
        await chat_service.add_message(user_id, request.chat_id, user_message)
        
        # Build context if requested
        query = request.message
        context_count = 0
        if request.include_context and history.messages:
            context = chat_service.build_context(history.messages)
            if context:
                query = context + f"Current question: {request.message}"
                context_count = min(len(history.messages), settings.max_context_messages)
        
        # Get AI response from Module 2
        ai_response = await cortex_client.rag_query(query)
        response_text = ai_response.get("result", "No response available")
        
        # Add assistant response to history
        assistant_message = ChatMessage(role="assistant", content=response_text)
        await chat_service.add_message(user_id, request.chat_id, assistant_message)
        
        return EnhancedChatResponse(
            message_id=assistant_message.message_id,
            response=response_text,
            chat_id=request.chat_id,
            timestamp=assistant_message.timestamp,
            context_messages_used=context_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

# Data access endpoints (geological sites - maps to Module 1 reports)
@app.get("/api/backend/geological-sites")
async def get_geological_sites(limit: int = 5, offset: int = 0, current_user: dict = Depends(get_current_user)):
    """Get geological sites (maps to Module 1 reports)"""
    try:
        # Maps to Module 1: GET /reports (actual endpoint)
        return await data_client.get_reports(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch geological sites: {str(e)}")

@app.get("/api/backend/geological-sites/{site_id}")
async def get_geological_site(site_id: int, current_user: dict = Depends(get_current_user)):
    """Get specific geological site (maps to Module 1 report by ID)"""
    try:
        # Maps to Module 1: GET /reports/{id} (actual endpoint)
        return await data_client.get_report_by_id(site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch geological site {site_id}: {str(e)}")

@app.get("/api/backend/quality-metrics", response_model=QualityMetricsResponse)
async def get_quality_metrics(current_user: dict = Depends(get_current_user)):
    """Get data quality metrics for dashboard"""
    try:
        # Get sample reports to calculate metrics
        reports = await data_client.get_reports(limit=5)
        
        if isinstance(reports, list) and len(reports) > 0:
            # Calculate basic metrics from available data
            commodities = set()
            years = []
            
            for report in reports:
                if isinstance(report, dict):
                    if 'commodity' in report:
                        commodities.add(report['commodity'])
                    if 'year' in report:
                        years.append(report['year'])
            
            return QualityMetricsResponse(
                total_reports=len(reports),
                unique_commodities=len(commodities),
                date_range={"min": str(min(years)) if years else "N/A", "max": str(max(years)) if years else "N/A"},
                data_quality_score=0.95,  # Placeholder score
                sample_size=len(reports)
            )
        else:
            # Fallback when no data available
            return QualityMetricsResponse(
                total_reports=0,
                unique_commodities=0,
                date_range={"min": "N/A", "max": "N/A"},
                data_quality_score=0.0,
                sample_size=0
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quality metrics: {str(e)}")

# Spatial query endpoint
@app.post("/api/backend/spatial-query", response_model=SpatialQueryResponse)
async def spatial_query(request: SpatialQueryRequest, current_user: dict = Depends(get_current_user)):
    """Geographic/spatial queries for map visualization"""
    try:
        # Maps to Module 1: GET /reports/filter with geographic filtering
        filtered_reports = await data_client.filter_reports(
            commodity=request.commodity,
            limit=5  # Default to 5 for testing
        )
        
        if not isinstance(filtered_reports, list):
            filtered_reports = []
        
        return SpatialQueryResponse(
            results=filtered_reports,
            total_found=len(filtered_reports),
            query_params={
                "bounds": request.bounds,
                "geometry": request.geometry,
                "distance_km": request.distance_km,
                "center_point": request.center_point,
                "commodity": request.commodity
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spatial query failed: {str(e)}")

# ===== NEW CHAT HISTORY ENDPOINTS =====

@app.post("/api/backend/chats", response_model=ChatSessionResponse)
async def create_chat(request: CreateChatRequest, current_user: dict = Depends(get_current_user)):
    """Create a new chat session"""
    try:
        chat = await chat_service.create_chat(
            user_id=current_user["username"],
            title=request.title,
            first_message=request.first_message
        )
        return ChatSessionResponse(
            chat_id=chat.chat_id,
            title=chat.title,
            message_count=chat.message_count,
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backend/chats", response_model=ChatListResponse)
async def list_chats(current_user: dict = Depends(get_current_user)):
    """List user's chat sessions"""
    try:
        chats = await chat_service.list_user_chats(current_user["username"])
        chat_responses = [
            ChatSessionResponse(
                chat_id=chat.chat_id,
                title=chat.title,
                message_count=chat.message_count,
                created_at=chat.created_at,
                updated_at=chat.updated_at
            )
            for chat in chats
        ]
        return ChatListResponse(chats=chat_responses, total=len(chat_responses))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backend/chats/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    """Get chat details with message history"""
    try:
        history = await chat_service.get_chat_history(current_user["username"], chat_id)
        if not history:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return ChatDetailResponse(
            session=ChatSessionResponse(
                chat_id=history.session.chat_id,
                title=history.session.title,
                message_count=history.session.message_count,
                created_at=history.session.created_at,
                updated_at=history.session.updated_at
            ),
            messages=[msg.dict() for msg in history.messages]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/backend/chats/{chat_id}")
async def delete_chat(chat_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a chat session"""
    try:
        await chat_service.delete_chat(current_user["username"], chat_id)
        return {"message": "Chat deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug) 