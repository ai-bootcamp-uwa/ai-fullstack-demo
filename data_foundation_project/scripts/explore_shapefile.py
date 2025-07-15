import geopandas as gpd
from pathlib import Path
import json
import pandas as pd

# Path to the shapefile (search recursively)
data_dir = Path(__file__).parent.parent / 'data' / 'raw'
shapefiles = list(data_dir.rglob('*.shp'))

if not shapefiles:
    raise FileNotFoundError(f"No .shp file found in {data_dir} or its subdirectories.")

shapefile = shapefiles[0]

# Output path for sample records
output_path = Path(__file__).parent.parent / 'data' / 'processed' / 'sample_records.json'
output_path.parent.mkdir(parents=True, exist_ok=True)

def make_json_serializable(record):
    # Convert all non-serializable types to string
    return {k: (str(v) if isinstance(v, (pd.Timestamp, pd.Timedelta)) or hasattr(v, 'isoformat') else v) for k, v in record.items()}

# TODO: Main script for exploring the shapefile data

def main():
    # TODO: Read the shapefile and print basic info
    # TODO: Output a sample as JSON
    pass

if __name__ == "__main__":
    main()
