#!/usr/bin/env python3
"""
Setup script for Snowflake vector schema in the hybrid Azure OpenAI + Snowflake system.
This script creates the necessary tables for storing embeddings and monitoring system health.
"""

import sys
import os
import logging
from pathlib import Path

# Add the cortex_engine src to Python path
current_dir = Path(__file__).parent
cortex_src = current_dir.parent / "src"
sys.path.insert(0, str(cortex_src))

# Also add the cortex_engine root to handle imports
cortex_root = current_dir.parent
sys.path.insert(0, str(cortex_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main setup function."""
    print("🏔️  SNOWFLAKE HYBRID SCHEMA SETUP")
    print("=" * 50)
    
    try:
        # Import after adding to path - use absolute imports
        import src.config as config_module
        import src.snowflake_integration as snowflake_module
        
        unified_config = config_module.unified_config
        snowflake_vector_store = snowflake_module.snowflake_vector_store
        
        # Check configuration
        print("\n📋 CONFIGURATION CHECK")
        print("-" * 30)
        
        validation_results = unified_config.validate_all()
        
        # Azure OpenAI check
        azure_status = validation_results["azure_openai"]
        print(f"Azure OpenAI Configured: {'✅' if azure_status['configured'] else '❌'}")
        if azure_status['error']:
            print(f"  Error: {azure_status['error']}")
        
        # Snowflake check
        snowflake_status = validation_results["snowflake"]
        print(f"Snowflake Configured: {'✅' if snowflake_status['configured'] else '❌'}")
        if snowflake_status['error']:
            print(f"  Error: {snowflake_status['error']}")
        
        # Hybrid system check
        hybrid_status = validation_results["hybrid"]
        print(f"Hybrid Features Enabled: {'✅' if hybrid_status['enabled'] else '⚠️  Disabled'}")
        
        if not snowflake_status['configured']:
            print("\n❌ Cannot proceed: Snowflake is not properly configured")
            print("Please check your .env file and ensure all Snowflake settings are provided:")
            print("  - SNOWFLAKE_ACCOUNT")
            print("  - SNOWFLAKE_USER")
            print("  - SNOWFLAKE_PASSWORD")
            print("  - SNOWFLAKE_WAREHOUSE")
            print("  - SNOWFLAKE_DATABASE")
            print("  - SNOWFLAKE_SCHEMA")
            return False
        
        # Test Snowflake connection
        print("\n🔗 SNOWFLAKE CONNECTION TEST")
        print("-" * 30)
        
        print("Testing Snowflake connection...")
        if snowflake_vector_store.test_connection():
            print("✅ Snowflake connection successful")
        else:
            print("❌ Snowflake connection failed")
            print("Please verify your credentials and network connectivity")
            return False
        
        # Create vector schema
        print("\n🏗️  CREATING VECTOR SCHEMA")
        print("-" * 30)
        
        print("Creating vector tables and indexes...")
        if snowflake_vector_store.create_vector_schema():
            print("✅ Vector schema created successfully")
        else:
            print("❌ Failed to create vector schema")
            return False
        
        # Verify schema creation
        print("\n📊 SCHEMA VERIFICATION")
        print("-" * 30)
        
        print("Getting vector statistics...")
        stats = snowflake_vector_store.get_vector_statistics()
        
        if "error" in stats:
            print(f"❌ Error getting statistics: {stats['error']}")
            return False
        
        print("✅ Schema verification successful")
        print(f"  Title Embeddings Table: Ready")
        print(f"  Embedding Jobs Table: Ready")
        print(f"  Health Monitoring Table: Ready")
        
        # Test health monitoring
        print("\n🏥 HEALTH MONITORING TEST")
        print("-" * 30)
        
        print("Recording test health check...")
        if snowflake_vector_store.record_health_check(
            component="setup_script",
            status="SUCCESS",
            response_time_ms=100,
            metadata={"test": "schema_setup"}
        ):
            print("✅ Health monitoring working")
        else:
            print("⚠️  Health monitoring test failed (schema still functional)")
        
        # Display configuration summary
        print("\n📋 SETUP SUMMARY")
        print("-" * 30)
        
        print(f"✅ Snowflake Account: {unified_config.snowflake.account}")
        print(f"✅ Database: {unified_config.snowflake.database}")
        print(f"✅ Schema: {unified_config.snowflake.schema}")
        print(f"✅ Vector Dimension: {unified_config.snowflake.vector_dimension}")
        print(f"✅ Batch Size: {unified_config.snowflake.batch_size}")
        
        print("\n🎯 NEXT STEPS")
        print("-" * 30)
        print("1. Enable hybrid features in your .env file:")
        print("   ENABLE_HYBRID_FEATURES=true")
        print("   ENABLE_SNOWFLAKE_VECTORS=true")
        print("   ENABLE_TITLE_EMBEDDINGS=true")
        print("")
        print("2. Start the cortex engine API:")
        print("   uvicorn src.main:app --reload")
        print("")
        print("3. Check hybrid health status:")
        print("   curl http://localhost:8000/health/hybrid")
        print("")
        print("4. Begin title embedding migration:")
        print("   python scripts/migrate_title_embeddings.py")
        
        print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you're in the cortex_engine directory:")
        print("   cd cortex_engine")
        print("2. Install required dependencies:")
        print("   pip install -r requirements.txt")
        print("3. Check that your .env file exists:")
        print("   cp env.example .env")
        print("4. Run the script from cortex_engine root:")
        print("   python scripts/setup_hybrid_schema.py")
        return False
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        logger.exception("Setup failed with exception:")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 