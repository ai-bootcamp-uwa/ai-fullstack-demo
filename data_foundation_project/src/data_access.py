import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
import logging
from typing import Optional, List, Dict, Any

from .snowflake_client import snowflake_client
from .config import app_config

logger = logging.getLogger(__name__)

class DataLoader:
    """DataLoader with Snowflake-only integration (local fallback removed)"""

    def __init__(self):
        """
        Initialize DataLoader. Fail if Snowflake is not available.
        """
        self.snowflake_available = snowflake_client.test_connection()
        if not self.snowflake_available:
            raise RuntimeError("Snowflake is not available. Module 1 requires a working Snowflake connection.")
        logger.info("Snowflake connection established successfully")

    # Snowflake-specific methods only
    def setup_snowflake_tables(self):
        """Create Snowflake tables if they don't exist"""
        snowflake_client.create_tables()
        logger.info("Snowflake tables created/verified successfully")

    def migrate_shapefile_to_snowflake(self, shapefile_path: str) -> int:
        """
        Migrate data from local shapefile to Snowflake
        Returns:
            Number of records loaded
        """
        return snowflake_client.load_shapefile_data(shapefile_path)

    def get_reports(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get geological reports from Snowflake"""
        return snowflake_client.get_reports(limit=limit, offset=offset)

    def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID from Snowflake"""
        return snowflake_client.get_report_by_id(report_id)

    def filter_reports(self, commodity: Optional[str] = None,
                      year: Optional[int] = None,
                      company: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Filter reports by criteria using Snowflake"""
        return snowflake_client.filter_reports(
            commodity=commodity, year=year, company=company, limit=limit
        )

    def spatial_query(self, latitude: float, longitude: float,
                     radius_km: float = 10.0) -> List[Dict[str, Any]]:
        """Perform spatial query using Snowflake"""
        return snowflake_client.spatial_query(
            latitude=latitude, longitude=longitude, radius_km=radius_km
        )

    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """Get data quality metrics from Snowflake"""
        return snowflake_client.get_data_quality_metrics()

    def health_check(self) -> Dict[str, Any]:
        """Health check for the data access layer (Snowflake only)"""
        health_info = {
            "snowflake_configured": True,
            "snowflake_available": self.snowflake_available,
            "data_source": "snowflake"
        }
        try:
            metrics = self.get_data_quality_metrics()
            health_info.update({
                "status": "healthy",
                "total_records": metrics.get("total_records", 0),
                "last_updated": metrics.get("last_updated")
            })
        except Exception as e:
            health_info.update({
                "status": "degraded",
                "error": str(e)
            })
        return health_info
