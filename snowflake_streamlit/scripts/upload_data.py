#!/usr/bin/env python3
"""
Data Upload Script for Snowflake
Uploads CSV data to Snowflake and creates tables
"""

import yaml
import snowflake.connector
import os
from pathlib import Path

class SnowflakeDataUploader:
    def __init__(self, config_path: str):
        """Initialize with configuration file"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Connect to Snowflake
        self.conn = snowflake.connector.connect(
            user=self.config['snowflake']['user'],
            password=self.config['snowflake']['password'],
            account=self.config['snowflake']['account'],
            warehouse=self.config['snowflake']['warehouse'],
            database=self.config['snowflake']['database'],
            schema=self.config['snowflake']['schema'],
            role=self.config['snowflake']['role']
        )
    
    def execute_sql_file(self, sql_file_path: str):
        """Execute SQL commands from a file"""
        print(f"Executing SQL file: {sql_file_path}")
        
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        cursor = self.conn.cursor()
        try:
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    print(f"Executing: {statement[:50]}...")
                    cursor.execute(statement)
                    print("✓ Statement executed successfully")
                    
        except Exception as e:
            print(f"❌ Error executing SQL: {e}")
            raise
        finally:
            cursor.close()
    
    def upload_csv_to_stage(self, csv_file_path: str, stage_name: str):
        """Upload CSV file to Snowflake stage"""
        print(f"Uploading {csv_file_path} to stage {stage_name}")
        
        cursor = self.conn.cursor()
        try:
            # Create a named stage (not table stage)
            stage_name_clean = stage_name.replace('@%', '').replace('@', '')
            cursor.execute(f"CREATE STAGE IF NOT EXISTS {stage_name_clean}")
            
            # Upload file to stage using PUT command
            put_command = f"PUT file://{csv_file_path} @{stage_name_clean}"
            cursor.execute(put_command)
            
            print("✓ File uploaded to stage successfully")
            
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            raise
        finally:
            cursor.close()
    
    def run_full_pipeline(self):
        """Run the complete data upload pipeline"""
        print("🚀 Starting Snowflake data upload pipeline...")
        
        try:
            # Step 1: Create table
            print("\n📋 Step 1: Creating table...")
            self.execute_sql_file("sql/ddl/01_create_wamex_geo_table.sql")
            
            # Step 2: Upload CSV to stage
            print("\n📤 Step 2: Uploading CSV to stage...")
            csv_file = f"data/processed/{self.config['data_loading']['csv_file']}"
            stage_name = self.config['data_loading']['stage_name']
            self.upload_csv_to_stage(csv_file, stage_name)
            
            # Step 3: Load data into table
            print("\n📊 Step 3: Loading data into table...")
            self.execute_sql_file("sql/ddl/02_load_data.sql")
            
            print("\n✅ Data upload pipeline completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            raise
        finally:
            self.conn.close()

def main():
    """Main function"""
    config_path = "config/snowflake_config.yaml"
    
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        print("Please update the configuration file with your Snowflake credentials")
        return
    
    uploader = SnowflakeDataUploader(config_path)
    uploader.run_full_pipeline()

if __name__ == "__main__":
    main() 