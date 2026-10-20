"""
run_all_modules.py - Master Silicon Orchestrator (Canonical Edition)
Executes the cross-language test suite (C++20, Rust 2021, Triton, Python, Dart FFI).
Usage: python tests/run_all_modules.py
"""

import sys
import os
import subprocess
import time

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

TESTS = [
    {
        "id": 1,
        "module": "PMTP Core Silicon (SEQLock, DLPack, ABI 128B)",
        "script": os.path.join(TESTS_DIR, "run_silicon_verification_suite.py"),
        "expected_exit": 0
    },
    {
        "id": 2,
        "module": "MorphoPeleides (ABA, PolarSafe, CAM, NaN-safety)",
        "script": os.path.join(TESTS_DIR, "morpho_redteam.py"),
        "expected_exit": 0
    },
    {
        "id": 3,
        "module": "Polydim-cla (Grassmann, Procrustes, Idempotencia)",
        "script": os.path.join(os.path.dirname(TESTS_DIR), "pmtp", "polydim_cla_grassmann.py"),
        "expected_exit": 0
    },
    {
        "id": 4,
        "module": "Teoria & Axiomas (Isometria, Antipodal, Lipschitz, Neumaier)",
        "script": os.path.join(TESTS_DIR, "teoria_axiomas.py"),
        "expected_exit": 0
    },
    {
        "id": 5,
        "module": "Triton GPU Engine (SRAM Tiling, Pre-escalado Stiefel)",
        "script": os.path.join(os.path.dirname(TESTS_DIR), "pmtp", "polydim_triton_kernel.py"),
        "expected_exit": 0
    },
    {
        "id": 6,
        "module": "Cross-Language Silicon ABI (C++20 DLL, Rust Newton-Schulz Ord-5 DLL, Python)",
        "script": os.path.join(TESTS_DIR, "test_cross_cpp_rust_python.py"),
        "expected_exit": 0
    },
]

def run_test(test):
    t0 = time.perf_counter()
    result = subprocess.run(
        [PYTHON, test["script"]],
        capture_output=True,
        text=True,
        timeout=60
    )
    elapsed = time.perf_counter() - t0
    passed = (result.returncode == test["expected_exit"])
    return passed, result.returncode, elapsed, result.stdout.strip(), result.stderr.strip()

def main():
    print("=" * 70)
    print("=== POLYDIM-EINSOF — CANONICAL SILICON TEST SUITE ===")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} | Directory: {TESTS_DIR}")
    print()

    results = []
    total_start = time.perf_counter()

    for test in TESTS:
        print(f"[{test['id']}/{len(TESTS)}] {test['module']}")
        try:
            passed, code, elapsed, stdout, stderr = run_test(test)
            status = "PASS" if passed else "FAIL"
            print(f"      [{status}] Exit Code={code} | {elapsed:.2f}s")
            if not passed and stderr:
                print(f"      STDERR: {stderr[:200]}")
            results.append((test["module"], passed, code, elapsed))
        except subprocess.TimeoutExpired:
            print(f"      [TIMEOUT] Exceeded 60s limit")
            results.append((test["module"], False, -1, 60.0))
        print()

    total_elapsed = time.perf_counter() - total_start
    n_passed = sum(1 for _, p, _, _ in results if p)
    n_total = len(results)

    print("=" * 70)
    print(f"GLOBAL RESULT: {n_passed}/{n_total} MODULES PASSED | {total_elapsed:.2f}s")
    print("=" * 70)
    for mod, passed, code, elapsed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} | {mod} ({elapsed:.2f}s)")
    print("=" * 70)

    final_code = 0 if n_passed == n_total else 1
    print(f"EXIT CODE: {final_code}")
    sys.exit(final_code)

if __name__ == "__main__":
    main()
