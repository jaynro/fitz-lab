#!/usr/bin/env python3
"""
Simple test runner for Fitz Lab
Usage: python run_tests_simple.py
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Run tests with simple output"""
    print("🧪 Fitz Lab - Running Tests")
    print("=" * 40)
    
    # Try to run the comprehensive test suite
    try:
        from tests.run_tests import run_tests
        return run_tests()
    except ImportError as e:
        print(f"❌ Error importing test modules: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure virtual environment is activated")
        print("2. Install test dependencies: pip install -r requirements.txt")
        print("3. Check that all modules are in the correct directories")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)