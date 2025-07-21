#!/usr/bin/env python3
"""
Quick test to verify schema fixes and diagnose spatial issues
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_access import DataLoader
from src.snowflake_client import snowflake_client
from sqlalchemy import text

def test_data_fixes():
    print("🧪 TESTING SCHEMA FIXES")
    print("=" * 40)
    
    try:
        # 1. Test DataLoader.get_reports()
        print("\n📊 Testing DataLoader.get_reports()...")
        loader = DataLoader()
        reports = loader.get_reports(limit=2)
        
        print(f"✅ Retrieved {len(reports)} reports")
        
        if len(reports) > 0:
            report = reports[0]
            print("\n🔍 First report structure:")
            
            # Check key fields
            key_fields = ['id', 'anumber', 'ANUMBER', 'title', 'TITLE', 'geometry', 'GEOMETRY']
            for field in key_fields:
                if field in report:
                    val = report[field]
                    if isinstance(val, str) and len(val) > 50:
                        val = val[:50] + "..."
                    print(f"  ✅ {field}: {val}")
                else:
                    print(f"  ❌ {field}: NOT FOUND")
                    
            print(f"\n📋 All available fields: {sorted(report.keys())}")
        
        # 2. Test filtering
        print(f"\n🔍 Testing filtering...")
        copper_reports = loader.filter_reports(commodity="COPPER", limit=2)
        print(f"✅ Copper reports found: {len(copper_reports)}")
        
        if len(copper_reports) > 0:
            report = copper_reports[0]
            print(f"   Sample: ID={report.get('id', 'N/A')}, Commodity={report.get('target_commodities', 'N/A')}")
        
        # 3. Check actual geometry data
        print(f"\n🗺️  Testing geometry data...")
        with snowflake_client.get_connection() as conn:
            result = conn.execute(text("""
                SELECT ANUMBER, 
                       CASE WHEN GEOMETRY IS NOT NULL THEN 'HAS_GEOMETRY' ELSE 'NO_GEOMETRY' END as GEOM_STATUS,
                       ST_X(ST_CENTROID(GEOMETRY)) as CENTER_LONGITUDE,
                       ST_Y(ST_CENTROID(GEOMETRY)) as CENTER_LATITUDE
                FROM GEOLOGICAL_REPORTS 
                WHERE GEOMETRY IS NOT NULL
                LIMIT 3
            """))
            
            rows = result.fetchall()
            print(f"✅ Records with geometry: {len(rows)}")
            
            for row in rows:
                anumber, geom_status, center_lon, center_lat = row
                print(f"   ID {anumber}: {geom_status} at ({center_lat:.4f}, {center_lon:.4f})")
        
        # 4. Test spatial query with a point closer to the data
        if len(rows) > 0:
            # Use the center point of the first geometry as our test location
            test_lat = rows[0][3]  # CENTER_LATITUDE 
            test_lon = rows[0][2]  # CENTER_LONGITUDE
            
            print(f"\n🎯 Testing spatial query near actual data point...")
            print(f"   Test location: ({test_lat:.4f}, {test_lon:.4f})")
            
            spatial_results = loader.spatial_query(
                latitude=test_lat, 
                longitude=test_lon, 
                radius_km=100.0  # Large radius to find something
            )
            print(f"✅ Spatial query results: {len(spatial_results)}")
            
            if len(spatial_results) > 0:
                result = spatial_results[0]
                distance = result.get('distance_km', 'N/A')
                print(f"   Closest: ID={result.get('id', 'N/A')}, Distance={distance}km")
            
            # Also test Perth location for comparison
            print(f"\n🌏 Testing spatial query near Perth...")
            perth_results = loader.spatial_query(
                latitude=-31.9505, 
                longitude=115.8605, 
                radius_km=100.0
            )
            print(f"✅ Perth spatial query results: {len(perth_results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_fixes()
    if success:
        print(f"\n🎉 Schema fixes working! Ready to run full test suite.")
    else:
        print(f"\n❌ Issues remain. Check the errors above.")
    
    sys.exit(0 if success else 1) 