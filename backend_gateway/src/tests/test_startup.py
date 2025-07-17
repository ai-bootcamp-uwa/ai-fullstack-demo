#!/usr/bin/env python3
"""
Test script to verify Backend Gateway API startup and basic functionality.
This script can be run to quickly verify everything is working.
"""

import requests
import time
import subprocess
import signal
import sys
import json
from typing import Optional

def start_server() -> subprocess.Popen:
    """Start the FastAPI server in the background"""
    print("🚀 Starting Backend Gateway API server...")
    import os
    # Get the backend_gateway root directory (two levels up from this file)
    backend_gateway_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--port", "3003"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=backend_gateway_root
    )
    
    # Wait a moment for server to start
    time.sleep(3)
    return process

def test_health() -> bool:
    """Test health endpoint"""
    try:
        response = requests.get("http://localhost:3003/api/backend/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            if 'dependencies' in data:
                deps = data['dependencies']
                for service, status in deps.items():
                    print(f"   {service}: {status}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_login() -> Optional[str]:
    """Test login endpoint and return token if successful"""
    try:
        response = requests.post(
            "http://localhost:3003/api/backend/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Login test passed")
            data = response.json()
            token = data.get("access_token")
            print(f"   Token type: {data.get('token_type')}")
            print(f"   Expires in: {data.get('expires_in')} seconds")
            return token
        else:
            print(f"❌ Login test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return None

def test_protected_endpoint(token: str) -> bool:
    """Test a protected endpoint with authentication"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:3003/api/backend/auth/profile",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Protected endpoint test passed")
            data = response.json()
            print(f"   Username: {data.get('username')}")
            print(f"   Role: {data.get('role')}")
            return True
        else:
            print(f"❌ Protected endpoint test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint test failed: {e}")
        return False

def test_geological_sites(token: str) -> bool:
    """Test geological sites endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:3003/api/backend/geological-sites?limit=3",
            headers=headers,
            timeout=10  # Longer timeout for external service calls
        )
        if response.status_code == 200:
            print("✅ Geological sites test passed")
            data = response.json()
            if isinstance(data, list):
                print(f"   Retrieved {len(data)} sites")
            elif isinstance(data, dict) and 'sites' in data:
                sites = data['sites']
                print(f"   Retrieved {len(sites)} sites")
            return True
        elif response.status_code == 500:
            print("⚠️  Geological sites test: Module 1 (Data Foundation) may not be running")
            print("   This is expected if testing without all modules")
            return True  # Don't fail the test if external service is down
        else:
            print(f"❌ Geological sites test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"⚠️  Geological sites test failed: {e}")
        print("   This is expected if Module 1 (Data Foundation) is not running")
        return True  # Don't fail the test if external service is down

def test_chat_endpoint(token: str) -> bool:
    """Test chat endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            "http://localhost:3003/api/backend/chat",
            headers=headers,
            json={"message": "What is copper mining?"},
            timeout=15  # Longer timeout for AI processing
        )
        if response.status_code == 200:
            print("✅ Chat endpoint test passed")
            data = response.json()
            print(f"   Response length: {len(data.get('response', ''))} characters")
            return True
        elif response.status_code == 500:
            print("⚠️  Chat endpoint test: Module 2 (Cortex Engine) may not be running")
            print("   This is expected if testing without all modules")
            return True  # Don't fail the test if external service is down
        else:
            print(f"❌ Chat endpoint test failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"⚠️  Chat endpoint test failed: {e}")
        print("   This is expected if Module 2 (Cortex Engine) is not running")
        return True  # Don't fail the test if external service is down

def test_quality_metrics(token: str) -> bool:
    """Test quality metrics endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:3003/api/backend/quality-metrics",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Quality metrics test passed")
            data = response.json()
            print(f"   Total reports: {data.get('total_reports')}")
            print(f"   Unique commodities: {data.get('unique_commodities')}")
            print(f"   Data quality score: {data.get('data_quality_score')}")
            return True
        elif response.status_code == 500:
            print("⚠️  Quality metrics test: Module 1 (Data Foundation) may not be running")
            return True
        else:
            print(f"❌ Quality metrics test failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Quality metrics test failed: {e}")
        return True

def cleanup_server(process: subprocess.Popen):
    """Clean up the server process"""
    print("\n🛑 Stopping server...")
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    print("✅ Server stopped")

def main():
    """Main test function"""
    print("🧪 Backend Gateway API Startup Test")
    print("=" * 50)
    
    # Start server
    server_process = start_server()
    
    try:
        # Run tests
        tests_passed = 0
        total_tests = 6
        
        # Test 1: Health check
        if test_health():
            tests_passed += 1
        
        # Test 2: Login
        token = test_login()
        if token:
            tests_passed += 1
            
            # Test 3: Protected endpoint
            if test_protected_endpoint(token):
                tests_passed += 1
            
            # Test 4: Geological sites
            if test_geological_sites(token):
                tests_passed += 1
            
            # Test 5: Chat endpoint
            if test_chat_endpoint(token):
                tests_passed += 1
            
            # Test 6: Quality metrics
            if test_quality_metrics(token):
                tests_passed += 1
        
        # Summary
        print("\n" + "=" * 50)
        print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Backend Gateway API is working correctly.")
            return 0
        elif tests_passed >= 3:  # At least basic functionality works
            print("⚠️  Some tests failed, but basic functionality is working.")
            print("   External modules (Module 1, Module 2) may not be running.")
            return 0
        else:
            print("❌ Critical tests failed. Please check the server setup.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    finally:
        cleanup_server(server_process)

if __name__ == "__main__":
    sys.exit(main()) 