import geopandas as gpd
import pandas as pd
from pathlib import Path
import json

class DataLoader:
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
