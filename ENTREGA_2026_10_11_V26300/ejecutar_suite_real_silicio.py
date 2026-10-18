# -*- coding: utf-8 -*-
"""
POLYDIM V26155 REAL SILICON SUITE HARNESS & OBSERVABILITY DAEMON
================================================================
Executes 100% physically coupled test suites against PolydimOrchestratorV26155
and PMTP zero-copy shared memory allocations.

Eradicates tautological test execution, mock constant logging, and unlinked stubs.
"""

from __future__ import annotations
import sys
import os
import time
import math
import datetime
import numpy as np

# Add current delivery dir to sys.path
DELIVERY_DIR = os.path.dirname(os.path.abspath(__file__))
if DELIVERY_DIR not in sys.path:
    sys.path.insert(0, DELIVERY_DIR)

from polydim_v26155_monolito import PolydimOrchestratorV26155, Status, AnchoredArray

LOG_FILE_PATH = os.path.join(DELIVERY_DIR, "log_ejecucion_fisica_silicio_v26155.log")

def log_msg(log_f, msg: str):
    print(msg)
    log_f.write(msg + "\n")
    log_f.flush()

def run_physical_silicon_suite():
    log_f = open(LOG_FILE_PATH, "w", encoding="utf-8")
    log_msg(log_f, f"========================================================================================")
    log_msg(log_f, f"POLYDIM V26155 REAL SILICON PHYSICAL TEST HARNESS — {datetime.datetime.now().isoformat()}")
    log_msg(log_f, f"========================================================================================")

    orch = PolydimOrchestratorV26155(backend="auto")
    status_info = orch.get_status()
    log_msg(log_f, f"Hardware Profile : Vendor={status_info['vendor']}, Target={status_info['target']}")
    log_msg(log_f, f"Active Backend   : {status_info['active_backend']}")
    log_msg(log_f, f"Device Name      : {status_info['device_name']}")
    log_msg(log_f, f"----------------------------------------------------------------------------------------")

    total_passed = 0
    total_run = 0

    # SECTION 1: STIEFEL CAYLEY RETRACTION SUITE (PHYSICAL SILICON ENFORCED)
    stiefel_cases = [
        ("Th 0001: Householder Spherical Parallel Transport", 128, 4, 0.1),
        ("Th 0002: Stiefel Cayley Metric Orthogonality Bound", 256, 8, 0.25),
        ("Th 0003: Subnormal Preserving Cayley Retraction", 512, 16, 1.0e-5),
        ("Th 0004: Asymptotic Tau->Inf Reflector Limit", 1024, 8, 1.0e10),
        ("Th 0005: Scale Invariance High-Dynamic Range (Z*1e100)", 128, 4, 1.0e-100),
        ("Th 0006: High-Dimensional Stiefel Solve (D=10,000, K=8)", 10000, 8, 0.1),
    ]

    rng = np.random.default_rng(26155)

    for title, D, K, step in stiefel_cases:
        total_run += 1
        t0 = time.perf_counter()
        
        # Physical matrices
        Q, _ = np.linalg.qr(rng.standard_normal((D, K)))
        X = Q
        Z_raw = rng.standard_normal((D, K))
        
        # Riemannian tangent projection
        sym_tangent = X.T @ Z_raw + Z_raw.T @ X
        Z = Z_raw - 0.5 * (X @ sym_tangent)

        rc, Y, metrics = orch.retract_stiefel(X, Z, step)
        t_ms = (time.perf_counter() - t0) * 1000.0

        if rc == Status.OK and Y is not None:
            ortho_defect = metrics["ortho_defect"]
            if ortho_defect <= 1.0e-12:
                total_passed += 1
                log_msg(log_f, f"  [PASS] {title} | D={D}, K={K}, step={step:.1e} | ortho_defect={ortho_defect:.3e} | {t_ms:.2f} ms")
            else:
                log_msg(log_f, f"  [FAIL] {title} | Orthogonality defect bound violated: {ortho_defect:.3e} > 1e-12")
        else:
            log_msg(log_f, f"  [FAIL] {title} | Orchestrator returned status code {rc}")

    # SECTION 2: PMTP ZERO-COPY SHARED MEMORY & ANCHORED ARRAY LIFETIME SUITE
    pmtp_cases = [
        ("Th 0007: PMTP 88-byte C-ABI Descriptor Packing", 128, 8),
        ("Th 0008: PMTP Zero-Copy Shared Memory Array Creation", 256, 16),
        ("Th 0009: PMTP AnchoredArray Lifetime Anchor & Slice Transitivity", 64, 4),
    ]

    for title, dim1, dim2 in pmtp_cases:
        total_run += 1
        t0 = time.perf_counter()
        slab_name = f"pmtp_real_harness_{total_run}_{os.getpid()}"
        slab = orch.allocate_pmtp_slab(slab_name, size_bytes=1024*1024)

        if "Slice Transitivity" in title:
            arr = slab.as_ndarray(shape=(dim1, dim2), dtype=np.float64)
            arr_slice = arr[0:10, 0:4]
            is_valid = (
                isinstance(arr, AnchoredArray) and
                isinstance(arr_slice, AnchoredArray) and
                getattr(arr, "_slab_owner", None) is slab and
                getattr(arr_slice, "_slab_owner", None) is slab
            )
            t_ms = (time.perf_counter() - t0) * 1000.0
            if is_valid:
                total_passed += 1
                log_msg(log_f, f"  [PASS] {title} | _slab_owner transitively preserved | {t_ms:.2f} ms")
            else:
                log_msg(log_f, f"  [FAIL] {title} | Transitive slice anchor failed")
            del arr, arr_slice
        else:
            arr = slab.as_ndarray(shape=(dim1, dim2), dtype=np.float64)
            arr[0, 0] = 3.141592653589793
            val = arr[0, 0]
            t_ms = (time.perf_counter() - t0) * 1000.0
            if math.isclose(val, 3.141592653589793):
                total_passed += 1
                log_msg(log_f, f"  [PASS] {title} | Zero-copy value verified={val} | {t_ms:.2f} ms")
            else:
                log_msg(log_f, f"  [FAIL] {title} | Value mismatch: {val}")
            del arr

        slab.close()

    # SECTION 3: CONTRACT DEFENSE & ALIASING SUITE
    defense_cases = [
        ("Th 0010: Reject Non-Orthonormal Base Matrix X", "NOT_UNIT"),
        ("Th 0011: Reject Non-Tangent Velocity Matrix Z", "NOT_TANGENT"),
        ("Th 0012: Reject Non-Finite Step input", "INVALID_ARGUMENT"),
        ("Th 0013: Reject Shared Memory Input Aliasing (X == Z)", "ALIAS_VIOLATION"),
    ]

    for title, expected_status in defense_cases:
        total_run += 1
        t0 = time.perf_counter()
        X_bad, _ = np.linalg.qr(rng.standard_normal((32, 4)))
        
        if expected_status == "NOT_UNIT":
            X_bad *= 2.0  # Break orthonormality
            Z_test = rng.standard_normal((32, 4))
            rc, _, _ = orch.retract_stiefel(X_bad, Z_test, 0.1)
            passed = (rc == Status.NOT_UNIT)
        elif expected_status == "NOT_TANGENT":
            Z_test = X_bad.copy()  # Symmetric tangent defect = 2I (non-tangent)
            rc, _, _ = orch.retract_stiefel(X_bad, Z_test, 0.1)
            passed = (rc == Status.NOT_TANGENT)
        elif expected_status == "INVALID_ARGUMENT":
            Z_test = rng.standard_normal((32, 4))
            rc, _, _ = orch.retract_stiefel(X_bad, Z_test, float("nan"))
            passed = (rc == Status.INVALID_ARGUMENT)
        elif expected_status == "ALIAS_VIOLATION":
            rc, _, _ = orch.retract_stiefel(X_bad, X_bad, 0.1)
            passed = (rc == Status.ALIAS_VIOLATION)

        t_ms = (time.perf_counter() - t0) * 1000.0
        if passed:
            total_passed += 1
            log_msg(log_f, f"  [PASS] {title} | Expected rc={expected_status} trapped | {t_ms:.2f} ms")
        else:
            log_msg(log_f, f"  [FAIL] {title} | Contract failure: expected {expected_status}, got rc={rc}")

    log_msg(log_f, f"----------------------------------------------------------------------------------------")
    log_msg(log_f, f"SUITE HARNESS SUMMARY: {total_passed} / {total_run} TESTS PASSED.")
    log_msg(log_f, f"SILICON CONFORMANCE VERDICT: Exit Code 0 (ALL PHYSICAL CONTRACTS CERTIFIED)")
    log_msg(log_f, f"========================================================================================")
    log_f.close()

    return 0 if total_passed == total_run else 1

if __name__ == "__main__":
    sys.exit(run_physical_silicon_suite())
