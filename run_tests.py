#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API
"""

import subprocess
import sys
import os

def run_tests():
    """Run pytest tests"""
    try:
        # Change to project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)

        # Run pytest
        result = subprocess.run([sys.executable, "-m", "pytest", "-v"],
                              capture_output=True, text=True)

        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)