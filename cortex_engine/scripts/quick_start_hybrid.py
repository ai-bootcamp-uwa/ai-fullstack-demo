#!/usr/bin/env python3
"""
Quick Start Script for Azure OpenAI + Snowflake Hybrid System
This script demonstrates the basic functionality of the hybrid implementation.
"""

import asyncio
import os
import json
from pathlib import Path
import sys

# Add the cortex_engine src to Python path
current_dir = Path(__file__).parent
cortex_src = current_dir.parent / "src"
sys.path.insert(0, str(cortex_src))

# Add data foundation project to path
data_foundation_path = current_dir.parent.parent / "data_foundation_project"
sys.path.insert(0, str(data_foundation_path))

class QuickStartDemo:
    """Demonstrates the hybrid Azure OpenAI + Snowflake system"""
    
    def __init__(self):
        self.step_counter = 1
    
    def print_step(self, title, description=""):
        """Print a formatted step"""
        print(f"\n{self.step_counter}️⃣ {title}")
        if description:
            print(f"   {description}")
        print("-" * 50)
        self.step_counter += 1
    
    def print_success(self, message):
        """Print success message"""
        print(f"   ✅ {message}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"   ❌ {message}")
    
    def check_environment(self):
        """Check if required environment variables are set"""
        self.print_step("Environment Check", "Verifying Azure OpenAI and Snowflake configuration")
        
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY", 
            "AZURE_OPENAI_API_VERSION",
            "EMBEDDING_MODEL",
            "CHAT_MODEL"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.print_error(f"Missing environment variables: {', '.join(missing_vars)}")
            print("\n   💡 Please set these in your .env file:")
            print("      AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
            print("      AZURE_OPENAI_API_KEY=your_api_key_here")
            print("      AZURE_OPENAI_API_VERSION=2024-02-01")
            print("      EMBEDDING_MODEL=text-embedding-ada-002")
            print("      CHAT_MODEL=gpt-4o-mini")
            return False
        
        self.print_success("All required environment variables are set")
        return True
    
    async def test_azure_openai(self):
        """Test Azure OpenAI connection"""
        self.print_step("Azure OpenAI Test", "Testing embedding generation and chat completion")
        
        try:
            from hybrid.azure_client import SimpleAzureClient
            
            azure_client = SimpleAzureClient()
            
            # Test embedding generation
            test_text = "This is a test geological exploration site"
            embedding = azure_client.generate_embedding(test_text)
            
            self.print_success(f"Embedding generated: {len(embedding)} dimensions")
            
            # Test chat completion
            messages = [
                {"role": "user", "content": "Say hello to test the chat completion"}
            ]
            chat_response = azure_client.chat_completion(messages)
            
            self.print_success(f"Chat completion: {chat_response[:50]}...")
            
            return True
            
        except Exception as e:
            self.print_error(f"Azure OpenAI test failed: {e}")
            return False
    
    async def test_snowflake_connection(self):
        """Test Snowflake connection"""
        self.print_step("Snowflake Connection Test", "Testing database connectivity")
        
        try:
            from src.snowflake_client import snowflake_client
            
            # Test basic connection
            test_query = "SELECT CURRENT_TIMESTAMP() as current_time"
            result = await snowflake_client.execute_query(test_query)
            
            if result:
                self.print_success(f"Connected to Snowflake at {result[0]['current_time']}")
                return True
            else:
                self.print_error("No result from Snowflake test query")
                return False
                
        except Exception as e:
            self.print_error(f"Snowflake connection failed: {e}")
            return False
    
    async def setup_vector_tables(self):
        """Setup vector tables in Snowflake"""
        self.print_step("Vector Tables Setup", "Creating tables for storing embeddings")
        
        try:
            from src.snowflake_client import snowflake_client
            
            # Create simple embeddings table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS azure_embeddings (
                id VARCHAR PRIMARY KEY,
                source_text TEXT NOT NULL,
                embedding_vector VECTOR(FLOAT, 1536),
                metadata VARIANT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
            )
            """
            
            await snowflake_client.execute_query(create_table_sql)
            self.print_success("Vector table created/verified")
            
            # Check if table exists and get count
            count_query = "SELECT COUNT(*) as count FROM azure_embeddings"
            result = await snowflake_client.execute_query(count_query)
            
            if result:
                count = result[0]['count']
                self.print_success(f"Table has {count} existing embeddings")
            
            return True
            
        except Exception as e:
            self.print_error(f"Vector table setup failed: {e}")
            return False
    
    async def test_hybrid_workflow(self):
        """Test the complete hybrid workflow"""
        self.print_step("Hybrid Workflow Test", "Testing Azure OpenAI + Snowflake integration")
        
        try:
            from hybrid.hybrid_service import SimpleHybridService
            
            hybrid_service = SimpleHybridService()
            
            # Test data
            test_texts = [
                "Gold exploration site in Western Australia with high-grade ore deposits",
                "Copper mining operation in the Pilbara region",
                "Iron ore extraction facility near Tom Price"
            ]
            
            # Step 1: Embed and store
            for i, text in enumerate(test_texts):
                result = await hybrid_service.embed_and_store(
                    text=text,
                    id=f"quickstart_test_{i}",
                    metadata={"source": "quick_start_demo", "index": i}
                )
                
                if result['success']:
                    self.print_success(f"Stored: {text[:50]}...")
                else:
                    self.print_error(f"Failed to store: {text[:50]}...")
            
            # Step 2: Search and chat
            search_result = await hybrid_service.search_and_chat(
                query="Tell me about mining operations in Western Australia",
                top_k=3
            )
            
            if search_result.get('chat_response'):
                self.print_success("Search and chat completed")
                print(f"   🤖 AI Response: {search_result['chat_response'][:100]}...")
                print(f"   🔍 Found {search_result['context_sources']} relevant sources")
            else:
                self.print_error("Search and chat failed")
            
            return True
            
        except Exception as e:
            self.print_error(f"Hybrid workflow test failed: {e}")
            return False
    
    async def test_geological_integration(self):
        """Test integration with geological data from Module 1"""
        self.print_step("Geological Data Integration", "Testing Module 1 data processing")
        
        try:
            from src.snowflake_client import snowflake_client
            
            # Check if geological data exists
            check_query = """
            SELECT COUNT(*) as count 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'GEOLOGICAL_REPORTS'
            """
            
            result = await snowflake_client.execute_query(check_query)
            
            if result and result[0]['count'] > 0:
                # Get sample geological data
                sample_query = """
                SELECT anumber, title, target_commodities 
                FROM geological_reports 
                WHERE title IS NOT NULL 
                LIMIT 3
                """
                
                geological_data = await snowflake_client.execute_query(sample_query)
                
                if geological_data:
                    self.print_success(f"Found {len(geological_data)} geological reports")
                    
                    # Show sample data
                    for report in geological_data:
                        print(f"      📋 {report['anumber']}: {report['title']}")
                        print(f"          Commodities: {report['target_commodities']}")
                    
                    return True
                else:
                    self.print_error("No geological data found")
                    return False
            else:
                print("   ⚠️ No geological_reports table found")
                print("   💡 This is normal if Module 1 data hasn't been migrated to Snowflake yet")
                return True
                
        except Exception as e:
            self.print_error(f"Geological integration test failed: {e}")
            return False
    
    def print_summary(self, results):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 QUICK START SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        print("\nTest Results:")
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {status} {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Your hybrid system is ready to use.")
            print("\nNext steps:")
            print("  1. Start the API server: uvicorn src.main:app --reload --port 3002")
            print("  2. Test the endpoints:")
            print("     - POST /simple-embed")
            print("     - POST /simple-search") 
            print("     - POST /process-geological-data")
            print("  3. See the full documentation in docs/azure_snowflake_hybrid_implementation.md")
        else:
            print("\n⚠️ Some tests failed. Please check the error messages above.")
            print("💡 Make sure your .env file has the correct Azure OpenAI and Snowflake credentials.")

async def main():
    """Run the quick start demo"""
    
    print("🚀 Azure OpenAI + Snowflake Hybrid System - Quick Start")
    print("=" * 60)
    print("This script will test the basic functionality of your hybrid system.")
    print("Make sure you have configured your .env file with Azure OpenAI credentials.")
    
    demo = QuickStartDemo()
    results = {}
    
    # Run all tests
    results["Environment Check"] = demo.check_environment()
    
    if results["Environment Check"]:
        results["Azure OpenAI"] = await demo.test_azure_openai()
        results["Snowflake Connection"] = await demo.test_snowflake_connection()
        
        if results["Snowflake Connection"]:
            results["Vector Tables Setup"] = await demo.setup_vector_tables()
            
            if results["Vector Tables Setup"]:
                results["Hybrid Workflow"] = await demo.test_hybrid_workflow()
                results["Geological Integration"] = await demo.test_geological_integration()
    
    # Print summary
    demo.print_summary(results)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the demo
    asyncio.run(main()) 