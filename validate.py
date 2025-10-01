"""validate.py

Validation script for SOPHON.
Runs all unit tests and checks core invariants.
Motif: Phase (validation)
Ports: [test runner, invariant checker]
Invariants: [test completeness, type safety]
"""

import subprocess
import sys

def run_tests():
    print("Running all unit tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "sophon/tests"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Some tests failed.")
        sys.exit(result.returncode)
    print("All tests passed.")

def check_invariants():
    print("Checking core invariants (stub)...")
    # TODO: Implement invariant checks (type safety, acyclicity, etc.)
    print("All invariants satisfied (stub).")

if __name__ == "__main__":
    run_tests()
    check_invariants()
