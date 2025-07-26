#!/usr/bin/env python3
"""
Validate and clean geometry data in CSV before uploading to Snowflake
"""

import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPolygon
import os

def validate_geometry(geometry_str):
    """Validate and clean geometry string"""
    if pd.isna(geometry_str) or geometry_str == '':
        return None
    
    try:
        # Try to parse the geometry
        geom = wkt.loads(geometry_str)
        
        # Check if it's a valid geometry
        if geom.is_valid:
            return geometry_str
        else:
            print(f"Invalid geometry found: {geometry_str[:100]}...")
            return None
            
    except Exception as e:
        print(f"Error parsing geometry: {e}")
        print(f"Problematic geometry: {geometry_str[:100]}...")
        return None

def clean_csv_geometry(input_csv, output_csv):
    """Clean geometry data in CSV file"""
    print(f"Reading CSV file: {input_csv}")
    df = pd.read_csv(input_csv)
    
    print(f"Original records: {len(df)}")
    
    # Validate geometry column
    print("Validating geometry data...")
    df['geometry_clean'] = df['geometry'].apply(validate_geometry)
    
    # Count invalid geometries
    invalid_count = df['geometry_clean'].isna().sum()
    valid_count = len(df) - invalid_count
    
    print(f"Valid geometries: {valid_count}")
    print(f"Invalid geometries: {invalid_count}")
    
    # Replace original geometry with cleaned version
    df['geometry'] = df['geometry_clean']
    df = df.drop('geometry_clean', axis=1)
    
    # Save cleaned CSV
    df.to_csv(output_csv, index=False)
    print(f"Cleaned CSV saved to: {output_csv}")
    
    return df

def main():
    # File paths
    input_csv = os.path.join(os.path.dirname(__file__), '../processed/Exploration_Reports_1000.csv')
    output_csv = os.path.join(os.path.dirname(__file__), '../processed/Exploration_Reports_1000_clean.csv')
    
    # Clean the geometry data
    df = clean_csv_geometry(input_csv, output_csv)
    
    # Show sample of cleaned data
    print("\nSample of cleaned data:")
    print(df[['ANUMBER', 'TITLE', 'geometry']].head())

if __name__ == "__main__":
    main() 