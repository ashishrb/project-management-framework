#!/usr/bin/env python3
"""
Test Runner Script
Provides convenient commands for running different types of tests
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def run_unit_tests(verbose=False, coverage=True):
    """Run unit tests."""
    command = ["pytest", "tests/unit/"]
    
    if verbose:
        command.append("-v")
    
    if coverage:
        command.extend(["--cov=app", "--cov-report=term-missing"])
    
    return run_command(command, "Unit Tests")


def run_integration_tests(verbose=False, coverage=True):
    """Run integration tests."""
    command = ["pytest", "tests/integration/"]
    
    if verbose:
        command.append("-v")
    
    if coverage:
        command.extend(["--cov=app", "--cov-append", "--cov-report=term-missing"])
    
    return run_command(command, "Integration Tests")


def run_performance_tests(verbose=False):
    """Run performance tests."""
    command = ["pytest", "tests/performance/", "-m", "performance"]
    
    if verbose:
        command.append("-v")
    
    return run_command(command, "Performance Tests")


def run_all_tests(verbose=False, coverage=True):
    """Run all tests."""
    command = ["pytest", "tests/"]
    
    if verbose:
        command.append("-v")
    
    if coverage:
        command.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
    
    return run_command(command, "All Tests")


def run_code_quality_checks():
    """Run code quality checks."""
    checks = [
        (["black", "--check", "--diff", "app/", "tests/", "scripts/"], "Black Formatting Check"),
        (["isort", "--check-only", "--diff", "app/", "tests/", "scripts/"], "Import Sorting Check"),
        (["flake8", "app/", "tests/", "scripts/"], "Flake8 Linting"),
        (["mypy", "app/", "--ignore-missing-imports"], "MyPy Type Checking"),
        (["bandit", "-r", "app/", "-f", "json", "-o", "bandit-report.json"], "Bandit Security Check"),
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed


def run_security_tests():
    """Run security tests."""
    checks = [
        (["safety", "check", "--json", "--output", "safety-report.json"], "Safety Check"),
        (["bandit", "-r", "app/", "-f", "json", "-o", "bandit-report.json"], "Bandit Security Scan"),
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed


def generate_coverage_report():
    """Generate coverage report."""
    command = ["coverage", "html", "--directory", "htmlcov"]
    return run_command(command, "Coverage Report Generation")


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function."""
    command = ["pytest", test_path]
    
    if verbose:
        command.append("-v")
    
    return run_command(command, f"Specific Test: {test_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Runner for GenAI Metrics Dashboard")
    
    parser.add_argument(
        "test_type",
        choices=[
            "unit", "integration", "performance", "all", 
            "quality", "security", "coverage", "specific"
        ],
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    
    parser.add_argument(
        "--test-path",
        help="Specific test file or function to run (for 'specific' test type)"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🚀 GenAI Metrics Dashboard Test Runner")
    print(f"📁 Working directory: {os.getcwd()}")
    
    success = False
    
    if args.test_type == "unit":
        success = run_unit_tests(args.verbose, not args.no_coverage)
    
    elif args.test_type == "integration":
        success = run_integration_tests(args.verbose, not args.no_coverage)
    
    elif args.test_type == "performance":
        success = run_performance_tests(args.verbose)
    
    elif args.test_type == "all":
        success = run_all_tests(args.verbose, not args.no_coverage)
    
    elif args.test_type == "quality":
        success = run_code_quality_checks()
    
    elif args.test_type == "security":
        success = run_security_tests()
    
    elif args.test_type == "coverage":
        success = generate_coverage_report()
    
    elif args.test_type == "specific":
        if not args.test_path:
            print("❌ --test-path is required for 'specific' test type")
            sys.exit(1)
        success = run_specific_test(args.test_path, args.verbose)
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
