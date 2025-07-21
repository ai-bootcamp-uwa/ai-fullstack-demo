#!/usr/bin/env python3
"""
Schema validation - compare Snowflake table with actual shapefile data
"""

import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_client import snowflake_client
from sqlalchemy import text

def check_schema_alignment():
    print("🔍 SCHEMA VALIDATION")
    print("=" * 50)
    
    try:
        # 1. Check Snowflake table schema
        print("\n📋 SNOWFLAKE TABLE SCHEMA:")
        print("-" * 30)
        
        with snowflake_client.get_connection() as conn:
            # Get table schema
            result = conn.execute(text("""
                SHOW COLUMNS IN TABLE GEOLOGICAL_REPORTS
            """))
            
            snowflake_columns = []
            for row in result:
                col_name = row[2]  # Column name
                col_type = row[3]  # Data type
                snowflake_columns.append((col_name, col_type))
                print(f"  {col_name:20} | {col_type}")
            
            print(f"\nSnowflake columns: {len(snowflake_columns)}")
            
            # Get sample data from Snowflake
            print("\n📊 SAMPLE DATA FROM SNOWFLAKE:")
            print("-" * 35)
            
            result = conn.execute(text("""
                SELECT * FROM GEOLOGICAL_REPORTS LIMIT 2
            """))
            
            columns = result.keys()
            rows = result.fetchall()
            
            print("Columns:", [str(col) for col in columns])
            print()
            
            for i, row in enumerate(rows):
                print(f"Row {i+1}:")
                for col, val in zip(columns, row):
                    if val is not None:
                        val_str = str(val)[:100] + ("..." if len(str(val)) > 100 else "")
                    else:
                        val_str = "NULL"
                    print(f"  {col:20} | {val_str}")
                print()
    
    except Exception as e:
        print(f"❌ Error checking Snowflake schema: {e}")
        return False
    
    try:
        # 2. Check original shapefile schema
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
        gdf = gpd.read_file(shapefile, rows=2)
        
        print(f"\nShapefile columns: {len(gdf.columns)}")
        for col in gdf.columns:
            dtype = str(gdf[col].dtype)
            sample_val = gdf[col].iloc[0] if len(gdf) > 0 else "N/A"
            if pd.notna(sample_val) and len(str(sample_val)) > 50:
                sample_val = str(sample_val)[:50] + "..."
            print(f"  {col:20} | {dtype:15} | {sample_val}")
        
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
    
    except Exception as e:
        print(f"❌ Error checking shapefile schema: {e}")
        return False
    
    # 3. Check column mapping
    print("\n🔗 COLUMN MAPPING ANALYSIS:")
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
    snowflake_cols = set([col[0] for col in snowflake_columns])
    
    print("Mapping check:")
    mapped_count = 0
    missing_from_shapefile = []
    missing_from_snowflake = []
    
    for shapefile_col, snowflake_col in column_mapping.items():
        if shapefile_col in shapefile_cols:
            if snowflake_col in snowflake_cols:
                print(f"  ✅ {shapefile_col:15} -> {snowflake_col}")
                mapped_count += 1
            else:
                print(f"  ❌ {shapefile_col:15} -> {snowflake_col} (missing in Snowflake)")
                missing_from_snowflake.append(snowflake_col)
        else:
            print(f"  ⚠️  {shapefile_col:15} -> {snowflake_col} (missing in shapefile)")
            missing_from_shapefile.append(shapefile_col)
    
    print(f"\nMapping summary:")
    print(f"  Successfully mapped: {mapped_count}")
    print(f"  Missing from shapefile: {len(missing_from_shapefile)}")
    print(f"  Missing from Snowflake: {len(missing_from_snowflake)}")
    
    # 4. Check for data access issues
    print("\n🔍 DATA ACCESS COMPATIBILITY:")
    print("-" * 30)
    
    # Check if the DataLoader expects certain column names
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        from src.data_access import DataLoader
        
        loader = DataLoader()
        reports = loader.get_reports(limit=1)
        
        print(f"DataLoader test: Retrieved {len(reports)} reports")
        if len(reports) > 0:
            report = reports[0]
            print("First report structure:")
            print(f"  Type: {type(report)}")
            print(f"  Attributes: {dir(report) if hasattr(report, '__dict__') else 'Not a custom object'}")
            if hasattr(report, '__dict__'):
                for key, val in report.__dict__.items():
                    val_str = str(val)[:50] + ("..." if len(str(val)) > 50 else "")
                    print(f"    {key}: {val_str}")
        
    except Exception as e:
        print(f"❌ DataLoader test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == "__main__":
    check_schema_alignment() 