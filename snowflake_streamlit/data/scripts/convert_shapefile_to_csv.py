import geopandas as gpd
import os

# Define input and output paths for snowflake_streamlit structure
shapefile_dir = os.path.join(os.path.dirname(__file__), '../raw/Exploration_Reports_shp')
shapefile_path = os.path.join(shapefile_dir, 'Exploration_Reports.shp')
# Output CSV path in data/processed
output_csv = os.path.join(os.path.dirname(__file__), '../processed/Exploration_Reports.csv')

def main():
    # Read the shapefile
    gdf = gpd.read_file(shapefile_path)
    # Convert geometry to WKT
    gdf['geometry'] = gdf['geometry'].apply(lambda x: x.wkt if x is not None else None)
    # Save to CSV
    gdf.to_csv(output_csv, index=False)
    print(f"CSV written to {output_csv}")

if __name__ == "__main__":
    main() 