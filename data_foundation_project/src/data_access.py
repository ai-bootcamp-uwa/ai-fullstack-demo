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
    """Enhanced DataLoader with Snowflake integration"""
    
    def __init__(self, use_snowflake: bool = True):
        """
        Initialize DataLoader
        
        Args:
            use_snowflake: If True, use Snowflake for data operations. 
                         If False, fall back to local file operations.
        """
        self.use_snowflake = use_snowflake
        self.snowflake_available = False
        
        if use_snowflake:
            try:
                self.snowflake_available = snowflake_client.test_connection()
                if self.snowflake_available:
                    logger.info("Snowflake connection established successfully")
                else:
                    logger.warning("Snowflake connection failed, falling back to local data")
            except Exception as e:
                logger.warning(f"Snowflake initialization failed: {e}, using local data")
    
    # TODO: Load the raw shapefile data
    def load_raw_shapefile(self, path):
        """Load the raw shapefile data as a GeoDataFrame."""
        return gpd.read_file(path)

    # TODO: Load processed/cleaned data (if available)
    def load_processed_data(self, path):
        """Load processed/cleaned data (GeoJSON, Parquet, or CSV)."""
        ext = Path(path).suffix.lower()
        if ext == '.geojson' or ext == '.json':
            return gpd.read_file(path)
        elif ext == '.parquet':
            return pd.read_parquet(path)
        elif ext == '.csv':
            return pd.read_csv(path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    # TODO: Save a sample of the data as JSON
    def save_sample_json(self, data, path, n=3):
        """Save a sample of the data as JSON (geometry as WKT if present)."""
        sample = data.head(n).copy()
        if 'geometry' in sample:
            sample['geometry'] = sample['geometry'].apply(lambda geom: geom.wkt)
        # Convert non-serializable types to string
        def make_json_serializable(record):
            return {k: (str(v) if isinstance(v, (pd.Timestamp, pd.Timedelta)) or hasattr(v, 'isoformat') else v) for k, v in record.items()}
        records = [make_json_serializable(rec) for rec in sample.to_dict(orient='records')]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(records, f, indent=2)

    # New Snowflake-specific methods
    def setup_snowflake_tables(self):
        """Create Snowflake tables if they don't exist"""
        if not self.snowflake_available:
            raise ValueError("Snowflake is not available. Check connection.")
        
        snowflake_client.create_tables()
        logger.info("Snowflake tables created/verified successfully")
    
    def migrate_shapefile_to_snowflake(self, shapefile_path: str) -> int:
        """
        Migrate data from local shapefile to Snowflake
        
        Returns:
            Number of records loaded
        """
        if not self.snowflake_available:
            raise ValueError("Snowflake is not available. Check connection.")
        
        return snowflake_client.load_shapefile_data(shapefile_path)
    
    def get_reports(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get geological reports - uses Snowflake if available, otherwise local data"""
        if self.use_snowflake and self.snowflake_available:
            return snowflake_client.get_reports(limit=limit, offset=offset)
        else:
            # Fallback to local data (existing implementation)
            return self._get_reports_local(limit=limit, offset=offset)
    
    def get_report_by_id(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific report by ID"""
        if self.use_snowflake and self.snowflake_available:
            return snowflake_client.get_report_by_id(report_id)
        else:
            return self._get_report_by_id_local(report_id)
    
    def filter_reports(self, commodity: Optional[str] = None,
                      year: Optional[int] = None, 
                      company: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Filter reports by criteria"""
        if self.use_snowflake and self.snowflake_available:
            return snowflake_client.filter_reports(
                commodity=commodity, year=year, company=company, limit=limit
            )
        else:
            return self._filter_reports_local(commodity=commodity, year=year, company=company)
    
    def spatial_query(self, latitude: float, longitude: float, 
                     radius_km: float = 10.0) -> List[Dict[str, Any]]:
        """Perform spatial query"""
        if self.use_snowflake and self.snowflake_available:
            return snowflake_client.spatial_query(
                latitude=latitude, longitude=longitude, radius_km=radius_km
            )
        else:
            return self._spatial_query_local(latitude=latitude, longitude=longitude, radius_km=radius_km)
    
    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """Get data quality metrics"""
        if self.use_snowflake and self.snowflake_available:
            return snowflake_client.get_data_quality_metrics()
        else:
            return self._get_quality_metrics_local()
    
    # Local fallback methods (for backward compatibility)
    def _get_reports_local(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Local fallback for getting reports"""
        # This would use the existing local shapefile logic
        # For now, return empty list with a warning
        logger.warning("Using local fallback - limited functionality")
        return []
    
    def _get_report_by_id_local(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Local fallback for getting report by ID"""
        logger.warning("Local fallback not fully implemented")
        return None
    
    def _filter_reports_local(self, commodity: Optional[str] = None,
                             year: Optional[int] = None, 
                             company: Optional[str] = None) -> List[Dict[str, Any]]:
        """Local fallback for filtering reports"""
        logger.warning("Local fallback not fully implemented")
        return []
    
    def _spatial_query_local(self, latitude: float, longitude: float, 
                            radius_km: float = 10.0) -> List[Dict[str, Any]]:
        """Local fallback for spatial queries"""
        logger.warning("Local fallback not fully implemented")
        return []
    
    def _get_quality_metrics_local(self) -> Dict[str, Any]:
        """Local fallback for quality metrics"""
        return {
            "status": "local_fallback",
            "message": "Snowflake not available, using limited local functionality"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the data access layer"""
        health_info = {
            "snowflake_configured": self.use_snowflake,
            "snowflake_available": self.snowflake_available,
            "data_source": "snowflake" if (self.use_snowflake and self.snowflake_available) else "local"
        }
        
        if self.snowflake_available:
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
        else:
            health_info.update({
                "status": "local_only",
                "message": "Operating in local mode"
            })
        
        return health_info
