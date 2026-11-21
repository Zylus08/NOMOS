"""
NOMOS CI-Ready Test Runner & Comprehensive Report Generator
Agent H07 & J04
"""

import sys
import time
from pathlib import Path
import pytest

TEST_OUTPUT_PATH = Path("audit/m1/TEST_RESULTS.txt")


def run_tests():
    print("=" * 60)
    print("NOMOS M1 COMPREHENSIVE TEST SUITE EXECUTION")
    print("=" * 60)

    start_time = time.time()

    # Capture output into file and console
    args = [
        "-v",
        "--tb=short",
        "tests",
    ]

    class OutputCapture:
        def __init__(self):
            self.lines = []

        def write(self, s):
            sys.__stdout__.write(s)
            self.lines.append(s)

        def flush(self):
            sys.__stdout__.flush()

    ret_code = pytest.main(args)
    duration = time.time() - start_time

    print(f"\nExecution finished in {duration:.2f} seconds with exit code: {ret_code}")
    return ret_code


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
