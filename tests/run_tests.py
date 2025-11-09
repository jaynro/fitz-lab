"""
Test runner and configuration
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test suite configuration
def create_test_suite():
    """Create comprehensive test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Unit tests
    from tests.unit import (
        test_models,
        test_pdf_extractor, 
        test_table_extractor,
        test_document_processor
    )
    
    suite.addTests(loader.loadTestsFromModule(test_models))
    suite.addTests(loader.loadTestsFromModule(test_pdf_extractor))
    suite.addTests(loader.loadTestsFromModule(test_table_extractor))
    suite.addTests(loader.loadTestsFromModule(test_document_processor))
    
    # Integration tests (including DeepEval)
    try:
        from tests.integration import test_deepeval_integration
        suite.addTests(loader.loadTestsFromModule(test_deepeval_integration))
        print("✅ DeepEval integration tests included")
    except ImportError:
        print("⚠️  DeepEval not available, skipping integration tests")
    
    return suite


def run_tests():
    """Run all tests with verbose output"""
    print("🧪 Running Fitz Lab Test Suite")
    print("=" * 50)
    
    suite = create_test_suite()
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


def run_unit_tests_only():
    """Run only unit tests"""
    print("🧪 Running Unit Tests Only")
    print("=" * 30)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add unit tests only
    from tests.unit import (
        test_models,
        test_pdf_extractor,
        test_table_extractor, 
        test_document_processor
    )
    
    suite.addTests(loader.loadTestsFromModule(test_models))
    suite.addTests(loader.loadTestsFromModule(test_pdf_extractor))
    suite.addTests(loader.loadTestsFromModule(test_table_extractor))
    suite.addTests(loader.loadTestsFromModule(test_document_processor))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def run_deepeval_tests_only():
    """Run only DeepEval integration tests"""
    try:
        import deepeval
        print("🤖 Running DeepEval Tests Only")
        print("=" * 35)
        
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        from tests.integration import test_deepeval_integration
        suite.addTests(loader.loadTestsFromModule(test_deepeval_integration))
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except ImportError:
        print("❌ DeepEval not available. Install with: pip install deepeval")
        return 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fitz Lab Test Runner')
    parser.add_argument(
        '--type', 
        choices=['all', 'unit', 'deepeval'],
        default='all',
        help='Type of tests to run (default: all)'
    )
    
    args = parser.parse_args()
    
    if args.type == 'unit':
        exit_code = run_unit_tests_only()
    elif args.type == 'deepeval':
        exit_code = run_deepeval_tests_only()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)