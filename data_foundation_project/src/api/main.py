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

# Initialize enhanced DataLoader with Snowflake support
loader = DataLoader(use_snowflake=True)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint with detailed status"""
    return loader.health_check()

# TODO: Endpoint to get a list of reports
@app.get("/reports")
def list_reports(
    limit: int = Query(10, ge=1, le=100, description="Number of reports to return"),
    offset: int = Query(0, ge=0, description="Number of reports to skip")
):
    """Get a paginated list of geological reports"""
    try:
        reports = loader.get_reports(limit=limit, offset=offset)
        return {
            "reports": reports,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_returned": len(reports)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reports")

# TODO: Endpoint to get a report by ID
@app.get("/reports/{report_id}")
def get_report(report_id: int):
    """Get a specific geological report by ID"""
    try:
        report = loader.get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch report")

# TODO: Endpoint to filter reports by commodity, year, or company
@app.get("/reports/filter")
def filter_reports(
    commodity: Optional[str] = Query(None, description="Filter by commodity (e.g., COPPER)"),
    year: Optional[int] = Query(None, description="Filter by report year"),
    company: Optional[str] = Query(None, description="Filter by operator/company")
):
    """Filter geological reports by various criteria"""
    try:
        reports = loader.filter_reports(commodity=commodity, year=year, company=company)
        return {
            "reports": reports,
            "filters": {
                "commodity": commodity,
                "year": year,
                "company": company
            },
            "total_returned": len(reports)
        }
    except Exception as e:
        logger.error(f"Error filtering reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to filter reports")

# TODO: Endpoint to return report geometry (as WKT)
@app.get("/reports/{report_id}/geometry")
def get_report_geometry(report_id: int):
    """Get the geometry of a specific report"""
    try:
        report = loader.get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if 'GEOMETRY' not in report or not report['GEOMETRY']:
            raise HTTPException(status_code=404, detail="No geometry data available for this report")
            
        return {
            "report_id": report_id,
            "geometry": report['GEOMETRY']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching geometry for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch report geometry")

# New spatial query endpoint
@app.post("/spatial-query")
def spatial_query(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    radius_km: float = Query(10.0, ge=0.1, le=100.0, description="Search radius in kilometers")
):
    """Find geological reports near a specific location"""
    try:
        reports = loader.spatial_query(
            latitude=latitude, 
            longitude=longitude, 
            radius_km=radius_km
        )
        return {
            "reports": reports,
            "query": {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km
            },
            "total_found": len(reports)
        }
    except Exception as e:
        logger.error(f"Error in spatial query: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute spatial query")

# Data quality metrics endpoint
@app.get("/quality-metrics")
def get_quality_metrics():
    """Get data quality metrics for the geological reports database"""
    try:
        metrics = loader.get_data_quality_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching quality metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch quality metrics")

# Administrative endpoints
@app.post("/admin/setup-tables")
def setup_tables():
    """Create Snowflake tables (admin only)"""
    try:
        if not loader.snowflake_available:
            raise HTTPException(status_code=503, detail="Snowflake not available")
        
        loader.setup_snowflake_tables()
        return {"message": "Tables created/verified successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up tables: {e}")
        raise HTTPException(status_code=500, detail="Failed to setup tables")

@app.post("/admin/migrate-data")
def migrate_data(shapefile_path: Optional[str] = None):
    """Migrate data from shapefile to Snowflake (admin only)"""
    try:
        if not loader.snowflake_available:
            raise HTTPException(status_code=503, detail="Snowflake not available")
        
        # Use default shapefile path if not provided
        if not shapefile_path:
            data_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
            shapefiles = list(data_dir.rglob('*.shp'))
            if not shapefiles:
                raise HTTPException(status_code=404, detail="No shapefile found in data directory")
            shapefile_path = str(shapefiles[0])
        
        records_loaded = loader.migrate_shapefile_to_snowflake(shapefile_path)
        return {
            "message": "Data migration completed successfully",
            "records_loaded": records_loaded,
            "source_file": shapefile_path
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error migrating data: {e}")
        raise HTTPException(status_code=500, detail="Failed to migrate data")

# Legacy compatibility - keeping the old endpoints for backward compatibility
@app.get("/geological-sites")
def get_geological_sites(limit: int = 10, offset: int = 0):
    """Legacy endpoint - redirects to /reports"""
    return list_reports(limit=limit, offset=offset)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=app_config.api_host, 
        port=app_config.api_port,
        log_level=app_config.log_level.lower()
    )
