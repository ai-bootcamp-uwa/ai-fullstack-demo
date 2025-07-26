#!/usr/bin/env python3
"""
Test Snowflake Connection
Simple script to test if your Snowflake connection works
"""

import yaml
import snowflake.connector
import os
import sys

# Add parent directory to path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_connection():
    """Test the Snowflake connection"""
    # Get the correct path to config file from tests directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "snowflake_config.yaml")
    
    if not os.path.exists(config_path):
        print("❌ Configuration file not found!")
        print(f"Looking for: {config_path}")
        print("Please create config/snowflake_config.yaml with your credentials")
        return False
    
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print("🔗 Testing Snowflake connection...")
        print(f"Account: {config['snowflake']['account']}")
        print(f"User: {config['snowflake']['user']}")
        print(f"Database: {config['snowflake']['database']}")
        print(f"Schema: {config['snowflake']['schema']}")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=config['snowflake']['user'],
            password=config['snowflake']['password'],
            account=config['snowflake']['account'],
            warehouse=config['snowflake']['warehouse'],
            database=config['snowflake']['database'],
            schema=config['snowflake']['schema'],
            role=config['snowflake']['role']
        )
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_USER(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
        result = cursor.fetchone()
        
        print("✅ Connection successful!")
        print(f"Current user: {result[0]}")
        print(f"Current database: {result[1]}")
        print(f"Current schema: {result[2]}")
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'WAMEX_GEO'")
        tables = cursor.fetchall()
        
        if tables:
            print("⚠️  WAMEX_GEO table already exists!")
            print("You may want to drop it first if you want to recreate it.")
        else:
            print("✅ WAMEX_GEO table does not exist - ready to create!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 