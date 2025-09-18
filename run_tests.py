#!/usr/bin/env python3
"""
Test runner for the VRChat Slideshow Maker
"""

import sys
import os
import subprocess
import argparse

def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified options"""
    
    # Add the src directory to the Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Base pytest command
    cmd = ["python3", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=slideshow_maker", "--cov-report=html", "--cov-report=term"])
    
    # Add test type specific options
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    # Add test directory
    cmd.append("tests/")
    
    print(f"Running tests: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"❌ Tests failed with exit code: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return False

def run_specific_test(test_name, verbose=False):
    """Run a specific test file or test function"""
    
    # Add the src directory to the Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    cmd = ["python3", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.append(f"tests/{test_name}")
    
    print(f"Running specific test: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("=" * 60)
        print("✅ Test passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"❌ Test failed with exit code: {e.returncode}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["pytest"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are installed")
    return True

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run tests for VRChat Slideshow Maker")
    parser.add_argument("--type", choices=["all", "unit", "integration", "fast"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--test", help="Run specific test file or function")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    
    args = parser.parse_args()
    
    if args.check_deps:
        return check_dependencies()
    
    if not check_dependencies():
        return False
    
    if args.test:
        return run_specific_test(args.test, args.verbose)
    else:
        return run_tests(args.type, args.verbose, args.coverage)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
