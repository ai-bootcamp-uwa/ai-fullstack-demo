#!/usr/bin/env python3
"""
Simple migration test - load just a few records to identify issues
"""

import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_client import snowflake_client
from sqlalchemy import text

def test_simple_migration():
    try:
        print("🔍 Testing simple migration with 5 records...")
        
        # 1. Find shapefile
        data_dir = Path('data/raw')
        shapefiles = list(data_dir.rglob('*.shp'))
        if not shapefiles:
            print("❌ No shapefiles found")
            return
        
        shapefile = shapefiles[0]
        print(f"📁 Loading: {shapefile}")
        
        # 2. Load just 5 records
        gdf = gpd.read_file(shapefile)
        print(f"✅ Full dataset: {len(gdf)} records")
        
        # Take first 5 records
        sample_gdf = gdf.head(5).copy()
        print(f"📊 Testing with {len(sample_gdf)} records")
        
        # 3. Process geometry safely
        def safe_wkt(geom):
            if geom is None or pd.isna(geom):
                return None
            try:
                return geom.wkt
            except:
                return None
        
        sample_gdf['geometry_wkt'] = sample_gdf['geometry'].apply(safe_wkt)
        
        # 4. Prepare for Snowflake
        df = pd.DataFrame(sample_gdf.drop('geometry', axis=1))
        
        # Basic column mapping
        column_mapping = {
            'ANUMBER': 'ANUMBER',
            'TITLE': 'TITLE',
            'REPORT_YEA': 'REPORT_YEAR',
            'OPERATOR': 'OPERATOR',
            'TARGET_COM': 'TARGET_COMMODITIES',
            'geometry_wkt': 'GEOMETRY'
        }
        
        # Only map columns that exist
        existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_mapping)
        
        # Keep only the mapped columns
        df = df[list(existing_mapping.values())]
        
        print(f"📋 Columns to load: {list(df.columns)}")
        print(f"📊 Sample data:")
        for i, row in df.head(2).iterrows():
            print(f"  Row {i}: ANUMBER={row.get('ANUMBER', 'N/A')}, TITLE={str(row.get('TITLE', 'N/A'))[:30]}...")
        
        # 5. Clear existing data
        print("🧹 Clearing existing data...")
        with snowflake_client.get_connection() as conn:
            conn.execute(text("TRUNCATE TABLE GEOLOGICAL_REPORTS"))
        
        # 6. Load sample data
        print("📤 Loading sample data to Snowflake...")
        engine = snowflake_client._get_engine()
        
        df.to_sql(
            'GEOLOGICAL_REPORTS',
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=10  # Very small chunks
        )
        
        print("✅ Sample data loaded successfully!")
        
        # 7. Verify
        with snowflake_client.get_connection() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM GEOLOGICAL_REPORTS"))
            count = result.fetchone()[0]
            print(f"📈 Records in table: {count}")
            
            if count > 0:
                result = conn.execute(text("SELECT ANUMBER, TITLE FROM GEOLOGICAL_REPORTS LIMIT 3"))
                records = result.fetchall()
                print("📋 Sample records in Snowflake:")
                for record in records:
                    print(f"  {record[0]}: {record[1]}")
        
        print("🎉 Simple migration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in simple migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_migration() 