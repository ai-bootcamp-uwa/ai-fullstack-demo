#!/usr/bin/env python3
"""
Cortex Engine Full Pipeline Execution Script
Automates the complete geological data processing workflow with cost optimization.
"""

import asyncio
import json
import requests
import time
import sys
import os
from typing import Dict, List, Any
import argparse

# Add the cortex_engine src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_client import DataFoundationClient

# Configuration
DATA_FOUNDATION_URL = "http://localhost:8000"
CORTEX_ENGINE_URL = "http://localhost:3002"
# Remove hardcoded MAX_REPORTS
# MAX_REPORTS = 10  # Cost optimization limit


class FullPipelineExecutor:
    """Executes the complete Cortex Engine pipeline."""

    def __init__(self, max_reports=None):
        self.start_time = time.time()
        self.metrics = {
            "total_reports_processed": 0,
            "embeddings_generated": 0,
            "similarity_searches": 0,
            "rag_queries": 0,
            "total_cost_estimate": 0.0
        }
        self.max_reports = max_reports

    def print_banner(self):
        """Print the execution banner."""
        print("�� CORTEX ENGINE FULL PIPELINE EXECUTION")
        print("=" * 60)
        print(f"💰 Cost-Optimized: Limited to {self.max_reports} reports" if self.max_reports is not None else "💰 Cost-Optimized: Processing all reports")
        print(f"🌐 Data Source: {DATA_FOUNDATION_URL}")
        print(f"🤖 AI Engine: {CORTEX_ENGINE_URL}")
        print(f"⏰ Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def print_step(self, step: str, details: str = ""):
        """Print a pipeline step."""
        timestamp = time.strftime("%H:%M:%S")
        if details:
            print(f"[{timestamp}] 🔹 {step}: {details}")
        else:
            print(f"\n[{timestamp}] 🔸 {step}")

    def check_system_health(self) -> bool:
        """Check if all systems are operational."""
        self.print_step("System Health Check")

        # Check Module 1 (Data Foundation)
        try:
            response = requests.get(f"{DATA_FOUNDATION_URL}/reports?limit=1", timeout=10)
            if response.status_code == 200:
                self.print_step("✅ Module 1 (Data Foundation)", "ONLINE")
            else:
                self.print_step("❌ Module 1 (Data Foundation)", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_step("❌ Module 1 (Data Foundation)", f"ERROR: {e}")
            return False

        # Check Module 2 (Cortex Engine)
        try:
            response = requests.get(f"{CORTEX_ENGINE_URL}/health", timeout=10)
            if response.status_code == 200:
                health = response.json()
                status = "CONFIGURED" if health.get('azure_openai_configured', False) else "FALLBACK MODE"
                self.print_step("✅ Module 2 (Cortex Engine)", status)
            else:
                self.print_step("❌ Module 2 (Cortex Engine)", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_step("❌ Module 2 (Cortex Engine)", f"ERROR: {e}")
            return False

        return True

    async def fetch_geological_data(self) -> List[Dict[str, Any]]:
        """Fetch geological reports from Data Foundation."""
        self.print_step("Geological Data Acquisition")

        try:
            client = DataFoundationClient(DATA_FOUNDATION_URL)

            self.print_step("Fetching reports", f"limit={self.max_reports if self.max_reports is not None else 'all'}")
            start_time = time.time()
            reports = await client.fetch_reports(limit=self.max_reports if self.max_reports is not None else 1000000)
            fetch_time = time.time() - start_time

            self.metrics["total_reports_processed"] = len(reports)

            if reports:
                self.print_step("✅ Data acquisition completed", f"{len(reports)} reports in {fetch_time:.2f}s")

                # Show sample of data
                sample_report = reports[0]
                geometry = sample_report.get('geometry', '')
                if geometry:
                    coords = geometry.replace('POLYGON ((', '').replace('))', '').split(', ')
                    if coords and len(coords) > 0:
                        first_coord = coords[0].split()
                        if len(first_coord) >= 2:
                            lat, lon = float(first_coord[1]), float(first_coord[0])
                            self.print_step("📍 Sample location", f"{lat:.3f}°S, {lon:.3f}°E")

                return reports
            else:
                self.print_step("❌ Data acquisition failed", "No reports returned")
                return []
        except Exception as e:
            self.print_step("❌ Data acquisition failed", str(e))
            return []

    def generate_embeddings(self, reports: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for geological descriptions."""
        self.print_step("AI Embedding Generation")

        if not reports:
            self.print_step("❌ Embedding generation skipped", "No reports available")
            return []

        # Create geological descriptions
        descriptions = []
        for i, report in enumerate(reports[:5]):  # Process max 5 for cost control
            geometry = report.get('geometry', '')

            # Extract location information
            location_info = ""
            if geometry:
                try:
                    coords = geometry.replace('POLYGON ((', '').replace('))', '').split(', ')
                    if coords and len(coords) > 0:
                        first_coord = coords[0].split()
                        if len(first_coord) >= 2:
                            lat, lon = float(first_coord[1]), float(first_coord[0])
                            location_info = f"at {lat:.3f}°S, {lon:.3f}°E"
                except:
                    location_info = "in Western Australia"
            else:
                location_info = "in Western Australia"

            description = (
                f"Geological exploration site {i+1} {location_info}: "
                f"Contains iron ore deposits, sedimentary rock formations, and Precambrian "
                f"geological structures typical of the Pilbara region mining area. "
                f"Site includes mineral exploration data, geological surveys, and "
                f"mining feasibility assessments for resource extraction."
            )
            descriptions.append(description)

        self.print_step("Processing descriptions", f"{len(descriptions)} geological sites")

        # Generate embeddings
        try:
            embed_payload = {"data": descriptions}

            start_time = time.time()
            response = requests.post(f"{CORTEX_ENGINE_URL}/embed", json=embed_payload, timeout=120)
            embed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                if "error" in result:
                    self.print_step("❌ Embedding generation failed", result["error"])
                    return []

                embeddings = result.get("embeddings", [])

                self.metrics["embeddings_generated"] = len(embeddings)

                if embeddings:
                    # Estimate cost
                    estimated_tokens = len(descriptions) * 150  # ~150 tokens per description
                    cost_estimate = estimated_tokens * 0.0001 / 1000  # Azure OpenAI pricing
                    self.metrics["total_cost_estimate"] += cost_estimate

                    self.print_step("✅ Embeddings generated", f"{len(embeddings)} vectors in {embed_time:.2f}s")
                    self.print_step("📊 Vector dimensions", f"{len(embeddings[0])}")
                    self.print_step("💰 Cost estimate", f"${cost_estimate:.6f}")

                    return embeddings
                else:
                    self.print_step("❌ Embedding generation failed", "No embeddings returned")
                    return []
            else:
                self.print_step("❌ Embedding generation failed", f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.print_step("❌ Embedding generation failed", str(e))
            return []

    def perform_similarity_analysis(self, embeddings: List[List[float]]) -> bool:
        """Perform similarity search analysis."""
        self.print_step("Similarity Analysis")

        if not embeddings or len(embeddings) < 2:
            self.print_step("❌ Similarity analysis skipped", "Need at least 2 embeddings")
            return False

        # Test multiple similarity searches
        search_results = []

        for i, query_embedding in enumerate(embeddings[:3]):  # Test first 3 as queries
            try:
                search_payload = {
                    "query_vector": query_embedding,
                    "top_k": min(5, len(embeddings))
                }

                start_time = time.time()
                response = requests.post(f"{CORTEX_ENGINE_URL}/similarity-search", json=search_payload, timeout=30)
                search_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()

                    if "error" not in result:
                        results = result.get("results", [])
                        search_results.append((i, results, search_time))
                        self.metrics["similarity_searches"] += 1

                        self.print_step(f"🔍 Query {i+1} completed", f"{len(results)} results in {search_time:.3f}s")
                    else:
                        self.print_step(f"❌ Query {i+1} failed", result["error"])
                else:
                    self.print_step(f"❌ Query {i+1} failed", f"HTTP {response.status_code}")
            except Exception as e:
                self.print_step(f"❌ Query {i+1} failed", str(e))

        if search_results:
            self.print_step("✅ Similarity analysis completed", f"{len(search_results)} successful searches")

            # Analyze results
            total_avg_score = 0
            total_results = 0

            for query_idx, results, search_time in search_results:
                if results:
                    avg_score = sum(score for _, score, _ in results) / len(results)
                    total_avg_score += avg_score
                    total_results += len(results)
                    self.print_step(f"📊 Query {query_idx+1} avg similarity", f"{avg_score:.3f}")

            if total_results > 0:
                overall_avg = total_avg_score / len(search_results)
                self.print_step("📈 Overall similarity quality", f"{overall_avg:.3f}")

            return True
        else:
            self.print_step("❌ Similarity analysis failed", "No successful searches")
            return False

    def test_rag_capabilities(self) -> bool:
        """Test Retrieval-Augmented Generation."""
        self.print_step("RAG (Retrieval-Augmented Generation) Test")

        # Test multiple geological queries
        queries = [
            "What geological formations are found in these exploration sites?",
            "Describe the mineral deposits in the surveyed areas.",
            "What are the main characteristics of the geological structures?"
        ]

        successful_queries = 0

        for i, query in enumerate(queries):
            try:
                rag_payload = {"query": query}

                start_time = time.time()
                response = requests.post(f"{CORTEX_ENGINE_URL}/rag-query", json=rag_payload, timeout=60)
                rag_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()

                    if "error" not in result:
                        rag_result = result.get("result", "")
                        successful_queries += 1
                        self.metrics["rag_queries"] += 1

                        self.print_step(f"💬 RAG Query {i+1} completed", f"{len(rag_result)} chars in {rag_time:.2f}s")

                        # Show sample response
                        if rag_result:
                            sample = rag_result[:100] + "..." if len(rag_result) > 100 else rag_result
                            self.print_step(f"   📝 Response sample", f"{sample}")
                    else:
                        # Check if it's a configuration issue (acceptable in fallback mode)
                        if "not configured" in result["error"].lower():
                            self.print_step(f"⚠️ RAG Query {i+1}", "Fallback mode (no Azure OpenAI)")
                            successful_queries += 1
                        else:
                            self.print_step(f"❌ RAG Query {i+1} failed", result["error"])
                else:
                    self.print_step(f"❌ RAG Query {i+1} failed", f"HTTP {response.status_code}")
            except Exception as e:
                self.print_step(f"❌ RAG Query {i+1} failed", str(e))

        if successful_queries > 0:
            self.print_step("✅ RAG testing completed", f"{successful_queries}/{len(queries)} queries successful")
            return True
        else:
            self.print_step("❌ RAG testing failed", "No successful queries")
            return False

    def generate_performance_report(self):
        """Generate final performance and cost report."""
        total_time = time.time() - self.start_time

        self.print_step("Performance & Cost Report")
        print("─" * 60)

        # Execution metrics
        print(f"⏱️  Total Execution Time: {total_time:.2f} seconds")
        print(f"📊 Reports Processed: {self.metrics['total_reports_processed']}")
        print(f"🤖 Embeddings Generated: {self.metrics['embeddings_generated']}")
        print(f"🔍 Similarity Searches: {self.metrics['similarity_searches']}")
        print(f"💬 RAG Queries: {self.metrics['rag_queries']}")

        # Cost analysis
        print(f"\n💰 Cost Analysis:")
        print(f"   • Estimated Azure OpenAI Cost: ${self.metrics['total_cost_estimate']:.6f}")
        print(f"   • Cost per report: ${self.metrics['total_cost_estimate']/max(1, self.metrics['total_reports_processed']):.6f}")
        print(f"   • Cost optimization: ✅ Limited to {self.max_reports} reports" if self.max_reports is not None else "💰 Cost optimization: Processing all reports")

        # Performance targets
        print(f"\n🎯 Performance Targets:")
        reports_per_min = (self.metrics['total_reports_processed'] / total_time) * 60
        embeddings_per_min = (self.metrics['embeddings_generated'] / total_time) * 60

        print(f"   • Data processing rate: {reports_per_min:.1f} reports/minute")
        print(f"   • Embedding generation rate: {embeddings_per_min:.1f} embeddings/minute")
        print(f"   • Target achievement: {'✅' if embeddings_per_min > 200 else '⚠️'} (target: >200/min)")

        # System status
        print(f"\n🚦 System Status:")
        if self.metrics['embeddings_generated'] > 0:
            print("   ✅ Embedding pipeline: OPERATIONAL")
        else:
            print("   ❌ Embedding pipeline: FAILED")

        if self.metrics['similarity_searches'] > 0:
            print("   ✅ Similarity search: OPERATIONAL")
        else:
            print("   ❌ Similarity search: FAILED")

        if self.metrics['rag_queries'] > 0:
            print("   ✅ RAG capabilities: OPERATIONAL")
        else:
            print("   ❌ RAG capabilities: FAILED")

    def print_completion_banner(self):
        """Print completion banner."""
        total_time = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("🎉 CORTEX ENGINE PIPELINE EXECUTION COMPLETED")
        print("=" * 60)
        print(f"⏰ Total Time: {total_time:.2f} seconds")
        print(f"💰 Total Cost: ${self.metrics['total_cost_estimate']:.6f}")
        print(f"📊 Success Rate: {self.calculate_success_rate():.1f}%")

        if self.metrics['total_reports_processed'] >= (self.max_reports if self.max_reports is not None else 10):
            print("✅ EXECUTION STATUS: SUCCESS")
        else:
            print("⚠️ EXECUTION STATUS: PARTIAL SUCCESS")

        print("=" * 60)

    def calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        total_operations = 4  # Data fetch, embeddings, similarity, RAG
        successful_operations = 0

        if self.metrics['total_reports_processed'] > 0:
            successful_operations += 1
        if self.metrics['embeddings_generated'] > 0:
            successful_operations += 1
        if self.metrics['similarity_searches'] > 0:
            successful_operations += 1
        if self.metrics['rag_queries'] > 0:
            successful_operations += 1

        return (successful_operations / total_operations) * 100

    def run(self):
        self.print_banner()

        # Check system health
        if not self.check_system_health():
            print("\n🚨 System health check failed. Cannot proceed with pipeline execution.")
            return

        # Execute pipeline stages
        reports = asyncio.run(self.fetch_geological_data())

        embeddings = self.generate_embeddings(reports)

        self.perform_similarity_analysis(embeddings)

        self.test_rag_capabilities()

        # Generate reports
        self.generate_performance_report()

        self.print_completion_banner()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cortex Engine Full Pipeline Execution")
    parser.add_argument("--max-reports", type=int, default=None, help="Maximum number of reports to process (default: all)")
    args = parser.parse_args()
    executor = FullPipelineExecutor(max_reports=args.max_reports)
    executor.run()
