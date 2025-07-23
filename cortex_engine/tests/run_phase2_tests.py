#!/usr/bin/env python3
"""
Phase 2 Test Runner - Handles imports and runs integration tests properly
"""

import sys
import os
from pathlib import Path

def main():
    """Run Phase 2 integration tests with proper import handling."""
    
    # Get the cortex_engine root directory
    cortex_root = Path(__file__).parent
    
    # Add to Python path
    sys.path.insert(0, str(cortex_root))
    
    # Change to cortex_engine directory for proper relative imports
    original_cwd = os.getcwd()
    os.chdir(cortex_root)
    
    try:
        # Import and run the test suite
        from tests.test_phase2_integration import run_phase2_tests
        
        print("🚀 Starting Phase 2 Integration Tests...")
        print("=" * 60)
        
        success = run_phase2_tests()
        
        if success:
            print("=" * 60)
            print("🎉 ALL PHASE 2 TESTS COMPLETED SUCCESSFULLY!")
            return 0
        else:
            print("=" * 60)
            print("❌ SOME PHASE 2 TESTS FAILED")
            return 1
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 