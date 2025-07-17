from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Dict, Any

# Local imports - updated for new structure
from ..core.config import settings
from ..core.auth import authenticate_user, create_access_token, get_current_user, get_user_profile
from ..services import data_client, cortex_client
from ..models import (
    LoginRequest, LoginResponse, UserProfile,
    GeologicalQueryRequest, GeologicalQueryResponse,
    ChatRequest, ChatResponse,
    SpatialQueryRequest, SpatialQueryResponse,
    QualityMetricsResponse, HealthResponse,
    RefreshTokenRequest
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

# Chat endpoint (maps to Module 2 RAG-query)
@app.post("/api/backend/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """AI chat functionality using Module 2 RAG system"""
    try:
        # Direct pass-through to Module 2: POST /rag-query (this IS the chat functionality)
        ai_response = await cortex_client.rag_query(request.message)
        
        return ChatResponse(
            response=ai_response.get("result", "No response available"),
            conversation_id=request.conversation_id or "default",
            timestamp=datetime.utcnow(),
            sources=[]  # Could be enhanced with report sources from Module 2 response
        )
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug) 