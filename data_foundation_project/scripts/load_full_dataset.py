#!/usr/bin/env python3
"""
Partial dataset migration - load first 7000 records in chunks
Based on the successful simple migration test
"""

import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_client import snowflake_client
from sqlalchemy import text

def load_full_dataset():
    start_time = datetime.now()
    total_loaded = 0
    
    try:
        print("🚀 Loading full WAMEX dataset to Snowflake...")
        print(f"⏰ Started at: {start_time}")
        print()
        
        # 1. Find shapefile
        data_dir = Path('data/raw')
        shapefiles = list(data_dir.rglob('*.shp'))
        if not shapefiles:
            print("❌ No shapefiles found")
            return
        
        shapefile = shapefiles[0]
        print(f"📁 Loading: {shapefile}")
        
        # 2. Load dataset, but only keep first 7000
        print("📊 Reading shapefile...")
        gdf = gpd.read_file(shapefile)
        total_records = len(gdf)
        print(f"✅ Dataset loaded: {total_records:,} records")
        
        gdf = gdf.iloc[:7000].copy()
        print(f"📉 Truncated to 7000 records for upload")
        
        # 3. Process geometry safely (same as working simple version)
        print("🔄 Processing geometries...")
        def safe_wkt(geom):
            if geom is None or pd.isna(geom):
                return None
            try:
                return geom.wkt
            except:
                return None
        
        gdf['geometry_wkt'] = gdf['geometry'].apply(safe_wkt)
        
        # 4. Prepare for Snowflake (same column mapping as working version)
        print("📋 Preparing data for Snowflake...")
        df = pd.DataFrame(gdf.drop('geometry', axis=1))
        
        # Use the working column mapping
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
            'geometry_wkt': 'GEOMETRY'
        }
        
        # Only map columns that exist
        existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_mapping)
        
        print(f"📊 Columns mapped: {len(existing_mapping)}")
        
        # 5. Clear existing data
        print("🧹 Clearing existing data...")
        with snowflake_client.get_connection() as conn:
            conn.execute(text("TRUNCATE TABLE GEOLOGICAL_REPORTS"))
        
        # 6. Load data in chunks
        chunk_size = 1000  # Load 1000 records at a time
        total_chunks = (len(df) + chunk_size - 1) // chunk_size
        
        print(f"📤 Loading {len(df):,} records in {total_chunks} chunks of {chunk_size}...")
        
        engine = snowflake_client._get_engine()
        
        for i in range(0, len(df), chunk_size):
            chunk_start = i
            chunk_end = min(i + chunk_size, len(df))
            chunk_df = df.iloc[chunk_start:chunk_end]
            chunk_num = (i // chunk_size) + 1
            
            print(f"  📦 Chunk {chunk_num:3d}/{total_chunks}: Loading records {chunk_start+1:6,} - {chunk_end:6,}")
            
            try:
                chunk_df.to_sql(
                    'GEOLOGICAL_REPORTS',
                    engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                total_loaded += len(chunk_df)
                
                # Progress update every 10 chunks
                if chunk_num % 10 == 0:
                    elapsed = datetime.now() - start_time
                    progress = (chunk_num / total_chunks) * 100
                    print(f"      📈 Progress: {progress:.1f}% ({total_loaded:,}/{total_records:,}) - {elapsed}")
                
            except Exception as e:
                print(f"      ❌ Chunk {chunk_num} failed: {e}")
                print(f"      📊 Chunk data sample:")
                print(f"         Records: {len(chunk_df)}")
                if len(chunk_df) > 0:
                    sample = chunk_df.iloc[0]
                    print(f"         ANUMBER: {sample.get('ANUMBER', 'N/A')}")
                    print(f"         TITLE: {str(sample.get('TITLE', 'N/A'))[:50]}...")
                
                # Continue with next chunk instead of stopping
                continue
        
        # 7. Final verification
        print("\n🔍 Verifying loaded data...")
        with snowflake_client.get_connection() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM GEOLOGICAL_REPORTS"))
            final_count = result.fetchone()[0]
            
            print(f"📈 Final record count: {final_count:,}")
            print(f"📊 Success rate: {(final_count/total_records)*100:.1f}%")
            
            if final_count > 0:
                # Get data quality metrics
                result = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(GEOMETRY) as with_geometry,
                        COUNT(DISTINCT OPERATOR) as unique_operators,
                        MIN(REPORT_YEAR) as earliest_year,
                        MAX(REPORT_YEAR) as latest_year
                    FROM GEOLOGICAL_REPORTS
                """))
                stats = result.fetchone()
                
                print(f"📊 Data Quality Summary:")
                print(f"   Total Records: {stats[0]:,}")
                print(f"   With Geometry: {stats[1]:,} ({(stats[1]/stats[0]*100):.1f}%)")
                print(f"   Unique Operators: {stats[2]:,}")
                print(f"   Year Range: {stats[3]} - {stats[4]}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 Migration completed!")
        print(f"⏰ Duration: {duration}")
        print(f"📊 Records loaded: {total_loaded:,}")
        print(f"⚡ Speed: {total_loaded/duration.total_seconds():.1f} records/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in full migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = load_full_dataset()
    sys.exit(0 if success else 1) 