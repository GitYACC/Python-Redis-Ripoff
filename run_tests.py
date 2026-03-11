#!/usr/bin/env python3
"""
Test runner for Redis implementation
Runs both unit tests and integration tests
"""

import unittest
import sys
import os


def run_all_tests():
    """Run all test suites and return the results"""
    # Discover and run all tests
    loader = unittest.TestLoader()

    # Load unit tests
    try:
        unit_suite = loader.loadTestsFromName('test_database')
        print("✓ Loaded unit tests (Database class)")
    except ImportError as e:
        print(f"✗ Failed to load unit tests: {e}")
        return False

    # Load integration tests
    try:
        integration_suite = loader.loadTestsFromName('test_integration')
        print("✓ Loaded integration tests (Client-Server)")
    except ImportError as e:
        print(f"✗ Failed to load integration tests: {e}")
        return False

    # Combine all test suites
    all_tests = unittest.TestSuite()
    all_tests.addTest(unit_suite)
    all_tests.addTest(integration_suite)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    print("\n" + "="*50)
    print("RUNNING REDIS IMPLEMENTATION TESTS")
    print("="*50)

    result = runner.run(all_tests)

    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0

    print(f"Tests run: {total_tests}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED!")
        return True
    else:
        print("✗ SOME TESTS FAILED")

        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")

        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")

        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)