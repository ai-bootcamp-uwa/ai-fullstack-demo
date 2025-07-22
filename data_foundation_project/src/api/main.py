from fastapi import FastAPI, HTTPException, Query, Depends
from pathlib import Path
import sys
import os
import logging
from typing import Optional, Dict, Any

# Add parent directories to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_access import DataLoader
from src.config import app_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Geological Exploration Reports API",
    description="API for querying Western Australian Mineral Exploration Reports (WAMEX) data",
    version="2.0.0"
)

# Initialize DataLoader (Snowflake-only)
loader = DataLoader()

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint with detailed status"""
    return loader.health_check()

# Get reports endpoint
@app.get("/reports")
def get_reports(limit: int = 10, offset: int = 0):
    try:
        return loader.get_reports(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reports from Snowflake.")

# Get report by ID endpoint
@app.get("/reports/{report_id}")
def get_report_by_id(report_id: int):
    try:
        report = loader.get_report_by_id(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        return report
    except Exception as e:
        logger.error(f"Error fetching report by ID: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch report from Snowflake.")

# Filter reports endpoint
@app.get("/filter-reports")
def filter_reports(
    commodity: Optional[str] = None,
    year: Optional[int] = None,
    company: Optional[str] = None,
    limit: int = 100
):
    try:
        return loader.filter_reports(commodity=commodity, year=year, company=company, limit=limit)
    except Exception as e:
        logger.error(f"Error filtering reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to filter reports from Snowflake.")

# Spatial query endpoint
@app.post("/spatial-query")
def spatial_query(
    latitude: float,
    longitude: float,
    radius_km: float = 10.0
):
    try:
        return loader.spatial_query(latitude=latitude, longitude=longitude, radius_km=radius_km)
    except Exception as e:
        logger.error(f"Error performing spatial query: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform spatial query on Snowflake.")

# Data quality metrics endpoint
@app.get("/quality-metrics")
def get_quality_metrics():
    try:
        return loader.get_data_quality_metrics()
    except Exception as e:
        logger.error(f"Error fetching data quality metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data quality metrics from Snowflake.")
