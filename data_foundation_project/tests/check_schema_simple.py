#!/usr/bin/env python3
"""
Simple schema validation - compare expected vs actual data structure
"""

import sys
import pandas as pd
import geopandas as gpd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_schema_simple():
    print("🔍 SIMPLE SCHEMA VALIDATION")
    print("=" * 50)
    
    try:
        # 1. Check original shapefile schema
        print("\n📁 ORIGINAL SHAPEFILE SCHEMA:")
        print("-" * 32)
        
        data_dir = Path('data/raw')
        shapefiles = list(data_dir.rglob('*.shp'))
        if not shapefiles:
            print("❌ No shapefiles found")
            return False
        
        shapefile = shapefiles[0]
        print(f"File: {shapefile}")
        
        # Load just the first few records to check schema
        gdf = gpd.read_file(shapefile, rows=5)
        
        print(f"\nShapefile columns: {len(gdf.columns)}")
        print("Available columns:")
        for i, col in enumerate(gdf.columns):
            dtype = str(gdf[col].dtype)
            sample_val = gdf[col].iloc[0] if len(gdf) > 0 else "N/A"
            if pd.notna(sample_val) and len(str(sample_val)) > 50:
                sample_val = str(sample_val)[:50] + "..."
            print(f"  {i+1:2d}. {col:20} | {dtype:15} | {sample_val}")
        
        print("\n📊 SAMPLE DATA FROM SHAPEFILE:")
        print("-" * 35)
        
        for i, row in gdf.iterrows():
            print(f"Row {i+1}:")
            for col in gdf.columns:
                val = row[col]
                if col == 'geometry':
                    if val is not None:
                        val_str = f"{val.geom_type} ({val.wkt[:50]}...)"
                    else:
                        val_str = "NULL"
                else:
                    if pd.notna(val):
                        val_str = str(val)[:100] + ("..." if len(str(val)) > 100 else "")
                    else:
                        val_str = "NULL"
                print(f"  {col:20} | {val_str}")
            print()
            if i >= 1:  # Only show first 2 rows
                break
                
    except Exception as e:
        print(f"❌ Error checking shapefile schema: {e}")
        return False
    
    # 2. Check expected column mapping
    print("\n🔗 EXPECTED COLUMN MAPPING:")
    print("-" * 30)
    
    column_mapping = {
        'ANUMBER': 'ANUMBER',
        'TITLE': 'TITLE', 
        'REPORT_YEA': 'REPORT_YEAR',
        'AUTHOR_NAM': 'AUTHOR_NAME',
        'AUTHOR_COM': 'AUTHOR_COMPANY',
        'REPORT_TYP': 'REPORT_TYPE',
        'DATE_FROM': 'DATE_FROM',
        'DATE_TO': 'DATE_TO',
        'PROJECT': 'PROJECT',
        'OPERATOR': 'OPERATOR',
        'ABSTRACT': 'ABSTRACT',
        'KEYWORDS': 'KEYWORDS',
        'TARGET_COM': 'TARGET_COMMODITIES',
        'DATE_RELEA': 'DATE_RELEASED',
        'ITEM_NO': 'ITEM_NO',
        'DPXE_ABS': 'DPXE_ABS',
        'DPXE_REP': 'DPXE_REP',
        'EXTRACT_DA': 'EXTRACT_DATE',
        'DIGITAL_FI': 'DIGITAL_FI',
        'IS_SHAPED': 'IS_SHAPED',
        'geometry': 'GEOMETRY'
    }
    
    shapefile_cols = set(gdf.columns)
    
    print("Mapping check:")
    mapped_count = 0
    missing_from_shapefile = []
    available_mappings = []
    
    for shapefile_col, snowflake_col in column_mapping.items():
        if shapefile_col in shapefile_cols:
            print(f"  ✅ {shapefile_col:15} -> {snowflake_col}")
            mapped_count += 1
            available_mappings.append((shapefile_col, snowflake_col))
        else:
            print(f"  ❌ {shapefile_col:15} -> {snowflake_col} (missing in shapefile)")
            missing_from_shapefile.append(shapefile_col)
    
    print(f"\nMapping summary:")
    print(f"  Successfully mapped: {mapped_count}")
    print(f"  Missing from shapefile: {len(missing_from_shapefile)}")
    
    # 3. Show what columns are actually available but not mapped
    print(f"\n📋 UNMAPPED COLUMNS IN SHAPEFILE:")
    print("-" * 35)
    
    mapped_source_cols = set([mapping[0] for mapping in available_mappings])
    unmapped_cols = shapefile_cols - mapped_source_cols
    
    if unmapped_cols:
        for col in sorted(unmapped_cols):
            if col != 'geometry':  # Skip geometry as it's handled specially
                sample_val = gdf[col].iloc[0] if len(gdf) > 0 else "N/A"
                if pd.notna(sample_val) and len(str(sample_val)) > 30:
                    sample_val = str(sample_val)[:30] + "..."
                print(f"  📌 {col:20} | {sample_val}")
    else:
        print("  ✅ All columns are mapped!")
    
    # 4. Suggest optimal column selection
    print(f"\n🎯 RECOMMENDED COLUMN SELECTION:")
    print("-" * 35)
    
    essential_cols = [
        'ANUMBER', 'TITLE', 'OPERATOR', 'TARGET_COM', 'REPORT_YEA'
    ]
    
    print("Essential columns for basic functionality:")
    for col in essential_cols:
        if col in shapefile_cols:
            target = column_mapping.get(col, col)
            print(f"  ✅ {col:15} -> {target}")
        else:
            print(f"  ❌ {col:15} -> (missing)")
    
    return True

if __name__ == "__main__":
    check_schema_simple() 