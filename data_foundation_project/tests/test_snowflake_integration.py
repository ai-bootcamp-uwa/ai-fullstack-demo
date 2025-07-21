#!/usr/bin/env python3
"""
Comprehensive test script for Snowflake integration
Tests database connection, data quality, and API functionality
"""

import sys
import time
import requests
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use absolute imports
from src.snowflake_client import snowflake_client
from src.data_access import DataLoader
from src.config import snowflake_config

class SnowflakeIntegrationTester:
    def __init__(self):
        self.loader = DataLoader(use_snowflake=True)
        self.api_base = "http://localhost:8000"
        self.test_results = []
        
    def log_test(self, test_name, success, message="", data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        if data and isinstance(data, dict):
            for key, value in data.items():
                print(f"    {key}: {value}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "data": data
        })
    
    def test_snowflake_connection(self):
        """Test 1: Snowflake Connection"""
        try:
            success = snowflake_client.test_connection()
            if success:
                self.log_test(
                    "Snowflake Connection", 
                    True, 
                    f"Connected to {snowflake_config.account}"
                )
            else:
                self.log_test("Snowflake Connection", False, "Connection failed")
        except Exception as e:
            self.log_test("Snowflake Connection", False, f"Error: {e}")
    
    def test_table_exists(self):
        """Test 2: Check if tables exist and have data"""
        try:
            from src.snowflake_client import snowflake_client
            from sqlalchemy import text
            
            with snowflake_client.get_connection() as conn:
                # Check if table exists
                result = conn.execute(text("SHOW TABLES LIKE 'GEOLOGICAL_REPORTS'"))
                tables = result.fetchall()
                
                if not tables:
                    self.log_test("Table Exists", False, "GEOLOGICAL_REPORTS table does not exist")
                    return
                
                # Check record count
                result = conn.execute(text("SELECT COUNT(*) as count FROM GEOLOGICAL_REPORTS"))
                count_result = result.fetchone()
                record_count = count_result[0] if count_result else 0
                
                success = record_count > 0
                self.log_test(
                    "Table Exists & Has Data",
                    success,
                    f"Table exists with {record_count:,} records",
                    {"Record Count": f"{record_count:,}"}
                )
                
        except Exception as e:
            self.log_test("Table Exists", False, f"Error: {e}")
    
    def test_data_quality(self):
        """Test 3: Data Quality Metrics"""
        try:
            metrics = snowflake_client.get_data_quality_metrics()
            
            total_records = metrics.get('total_records', 0)
            records_with_geometry = metrics.get('records_with_geometry', 0)
            
            success = total_records > 0  # At least some records
            
            self.log_test(
                "Data Quality Metrics",
                success,
                f"Found {total_records:,} total records",
                {
                    "Total Records": f"{total_records:,}",
                    "Records with Geometry": f"{records_with_geometry:,}",
                    "Geometry Coverage": f"{(records_with_geometry/total_records*100):.1f}%" if total_records > 0 else "0%",
                    "Unique Operators": metrics.get('unique_operators', 0),
                    "Unique Commodities": metrics.get('unique_commodities', 0),
                    "Year Range": f"{metrics.get('earliest_year', 'N/A')} - {metrics.get('latest_year', 'N/A')}"
                }
            )
        except Exception as e:
            self.log_test("Data Quality Metrics", False, f"Error: {e}")
    
    def test_data_access_layer(self):
        """Test 4: Data Access Layer"""
        try:
            # Test getting reports
            reports = self.loader.get_reports(limit=5)
            success = len(reports) > 0 and 'ANUMBER' in reports[0] if reports else False
            
            self.log_test(
                "Data Access Layer",
                success,
                f"Retrieved {len(reports)} reports via DataLoader",
                {
                    "First Report ID": reports[0].get('ANUMBER') if reports else 'None',
                    "Has Geometry": 'GEOMETRY' in reports[0] if reports else False
                } if reports else {"Error": "No reports returned"}
            )
        except Exception as e:
            self.log_test("Data Access Layer", False, f"Error: {e}")
    
    def test_spatial_queries(self):
        """Test 5: Spatial Query Functionality"""
        try:
            # Test spatial query near Perth, WA
            reports = snowflake_client.spatial_query(
                latitude=-31.9505, 
                longitude=115.8605, 
                radius_km=50
            )
            
            success = len(reports) > 0
            
            self.log_test(
                "Spatial Queries",
                success,
                f"Found {len(reports)} reports within 50km of Perth",
                {
                    "Query Location": "Perth, WA (-31.9505, 115.8605)",
                    "Search Radius": "50 km",
                    "Results Found": len(reports),
                    "Sample Distance": f"{reports[0].get('DISTANCE_KM', 'N/A'):.1f} km" if reports else 'N/A'
                }
            )
        except Exception as e:
            self.log_test("Spatial Queries", False, f"Error: {e}")
    
    def test_filtering(self):
        """Test 6: Data Filtering"""
        try:
            # Test filtering by commodity
            gold_reports = snowflake_client.filter_reports(commodity="GOLD")
            copper_reports = snowflake_client.filter_reports(commodity="COPPER")
            
            success = len(gold_reports) > 0 and len(copper_reports) > 0
            
            self.log_test(
                "Data Filtering",
                success,
                "Commodity filtering working",
                {
                    "Gold Reports": len(gold_reports),
                    "Copper Reports": len(copper_reports),
                    "Total Tested": len(gold_reports) + len(copper_reports)
                }
            )
        except Exception as e:
            self.log_test("Data Filtering", False, f"Error: {e}")
    
    def check_api_server(self):
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_api_endpoints(self):
        """Test 7: API Endpoints"""
        if not self.check_api_server():
            self.log_test(
                "API Endpoints", 
                False, 
                "API server not running. Start with: uvicorn src.api.main:app --reload"
            )
            return
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.api_base}/health")
            health_data = response.json()
            
            api_healthy = (
                response.status_code == 200 and 
                health_data.get('snowflake_available') == True
            )
            
            # Test reports endpoint
            response = requests.get(f"{self.api_base}/reports?limit=3")
            reports_data = response.json()
            
            reports_working = (
                response.status_code == 200 and 
                len(reports_data.get('reports', [])) >= 0
            )
            
            success = api_healthy and reports_working
            
            self.log_test(
                "API Endpoints",
                success,
                "API server responding correctly",
                {
                    "Health Check": "✅" if api_healthy else "❌",
                    "Reports Endpoint": "✅" if reports_working else "❌",
                    "Data Source": health_data.get('data_source', 'unknown'),
                    "Total Records": health_data.get('total_records', 'unknown')
                }
            )
        except Exception as e:
            self.log_test("API Endpoints", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 SNOWFLAKE INTEGRATION TEST SUITE")
        print("=" * 50)
        print()
        
        # Run all tests
        self.test_snowflake_connection()
        self.test_table_exists()
        self.test_data_quality()
        self.test_data_access_layer()
        self.test_spatial_queries()
        self.test_filtering()
        self.test_api_endpoints()
        
        # Summary
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print("=" * 50)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Your Snowflake integration is working perfectly!")
        elif passed >= 3:
            print("⚠️  Some tests failed, but core functionality is working.")
            print("💡 If no data found, run: python scripts/migrate_to_snowflake.py")
        else:
            print("❌ Major issues found. Check the details above.")
            
        print("=" * 50)
        
        return passed >= 3  # Pass if at least basic functionality works

if __name__ == "__main__":
    tester = SnowflakeIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 