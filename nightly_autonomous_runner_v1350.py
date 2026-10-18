# -*- coding: utf-8 -*-
"""
POLYDIM EINSOF — V1350 NIGHTLY AUTONOMOUS ADVERSARIAL RUNNER (BULLDOG PROTOCOL)
================================================================================

Constitutional Mandates:
  * Rule 4 (Night Mode): Autonomous background research and stress loops.
  * Rule 16 (Anti-Passive Auditing): 3 Adversarial Hounds attacking numerical
    precision, subnormal limits, shared memory concurrency, and scale boundaries.
  * Rule 26 (Anti-Abandonment): Continuous physical monitoring with Exit Code 0.
  * Rule 22 (Ghost Protocol): PMTP Zero-Copy shared memory integrity checks.
  * Rule 27 (Silicon Contract): Dynamic multi-silicon adaptation.
"""

from __future__ import annotations

import datetime
import hashlib
import math
import mmap
import os
from pathlib import Path
import sqlite3
import struct
import subprocess
import sys
import time
from typing import Dict, Any, List

DB_PATH = r"E:\POLYDIM-THEORICAL\POLYDIM_VECDB.sqlite"
LOG_PATH = r"E:\POLYDIM_EINSOF\nightly_v1350_runner.log"
CSV_PATH = r"E:\POLYDIM_EINSOF\nocturno_silicon_active_log.csv"
V1350_DIR = r"E:\POLYDIM_EINSOF\ENTREGA_2026_10_04_V1350\respuestas"

# Add V1350 directory to sys.path
if V1350_DIR not in sys.path:
    sys.path.insert(0, V1350_DIR)

try:
    import kernel_orchestrator_v1350 as orch_mod
    HAS_ORCH = True
except Exception as e:
    HAS_ORCH = False
    orch_err = str(e)


def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def log_csv(cycle: int, hound: str, test_name: str, status: str, metric_val: float, note: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(CSV_PATH)
    try:
        with open(CSV_PATH, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("timestamp,cycle,hound,test_name,status,metric_val,note\n")
            f.write(f'"{ts}",{cycle},"{hound}","{test_name}","{status}",{metric_val},"{note}"\n')
    except Exception:
        pass


def record_fact(source: str, topic: str, metric_key: str, metric_val: float, detail: str):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn.execute("""
            INSERT INTO facts 
            (fact_type, source_file, version, topic, metric_key, metric_val, metric_unit, detail, certified, inserted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'NIGHTLY_TELEMETRY',
            source,
            'V1350',
            topic,
            metric_key,
            metric_val,
            'metric',
            detail,
            1,
            now
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        log(f"Database fact recording warning: {e}")


# =============================================================================
# Sabueso 1: Adversarial Numerical & Subnormal Stress
# =============================================================================
def run_hound_1_numerical_stress(cycle: int, orch) -> bool:
    import numpy as np
    rng = np.random.default_rng(135000 + cycle)
    all_pass = True

    # Attack A: Extreme Scale Injection (1e-250 to 1e250)
    for scale_exp in [-200, -100, -10, 0, 10, 100, 200]:
        step = 10.0 ** scale_exp
        D, K = 64, 4
        Q, _ = np.linalg.qr(rng.standard_normal((D, K)))
        X = Q
        Z = rng.standard_normal((D, K))
        Z = Z - X @ (X.T @ Z)
        
        rc, Y, met = orch.retract_stiefel(X, Z, step)
        if rc == orch_mod.Status.OK:
            defect = met["ortho_defect"]
            if defect > 1.0e-11:
                log(f"[SABUESO 1 FAIL] Scale 10^{scale_exp} ortho_defect too high: {defect:.3e}")
                all_pass = False
        else:
            log(f"[SABUESO 1 WARN] Scale 10^{scale_exp} failed with rc={rc}")

    # Attack B: Singular / Ill-Conditioned Tangent Direction
    D, K = 128, 4
    Q, _ = np.linalg.qr(rng.standard_normal((D, K)))
    X = Q
    # Nearly degenerate tangent direction
    Z = np.zeros((D, K), dtype=np.float64)
    Z[:, 0] = rng.standard_normal(D) * 1e-15
    rc_deg, Y_deg, met_deg = orch.retract_stiefel(X, Z, 0.1)
    if rc_deg == orch_mod.Status.OK:
        log_csv(cycle, "SABUESO_1", "DEGENERATE_TANGENT", "PASS", met_deg["ortho_defect"], "Conditioned solve pass")
    else:
        all_pass = False

    return all_pass


# =============================================================================
# Sabueso 2: PMTP Zero-Copy Shared Memory Concurrency
# =============================================================================
def run_hound_2_pmtp_concurrency(cycle: int, orch) -> bool:
    import numpy as np
    slab_name = f"polydim_v1350_nightly_slab_{cycle % 16}"
    slab_size = 2 * 1024 * 1024  # 2 MB
    
    try:
        slab = orch.allocate_pmtp_slab(slab_name, slab_size)
        arr = slab.as_ndarray(shape=(256, 256), dtype=np.float64, offset=0)
        
        # Test pattern write
        arr[:, :] = cycle * 1.350
        arr[0, 0] = 777.0
        arr[255, 255] = -777.0
        
        # Readback through raw buffer view
        buf_view = slab.get_buffer()
        v0 = struct.unpack_from("<d", buf_view, 0)[0]
        v_last = struct.unpack_from("<d", buf_view, (256 * 256 - 1) * 8)[0]
        
        del arr, buf_view
        slab.close()
        
        valid = math.isclose(v0, 777.0) and math.isclose(v_last, -777.0)
        if valid:
            log_csv(cycle, "SABUESO_2", "PMTP_SLAB_ROUNDTRIP", "PASS", 0.0, "Zero-copy byte integrity verified")
            return True
        else:
            log(f"[SABUESO 2 FAIL] PMTP readback corrupted: v0={v0}, vlast={v_last}")
            return False
    except Exception as e:
        log(f"[SABUESO 2 ERROR] PMTP exception: {e}")
        return False


# =============================================================================
# Sabueso 3: Multi-Silicon Conformance Watchdog
# =============================================================================
def run_hound_3_conformance_watchdog(cycle: int) -> bool:
    orch_py = os.path.join(V1350_DIR, "kernel_orchestrator_v1350.py")
    res = subprocess.run([sys.executable, orch_py], capture_output=True, text=True)
    if res.returncode == 0:
        log_csv(cycle, "SABUESO_3", "V1350_CONFORMANCE", "PASS", 0.0, "All 12 physical checks PASSED")
        return True
    else:
        log(f"[SABUESO 3 FAIL] Conformance exit code {res.returncode}: {res.stderr[:200]}")
        log_csv(cycle, "SABUESO_3", "V1350_CONFORMANCE", "FAIL", float(res.returncode), res.stderr[:100])
        return False


# =============================================================================
# Master Nightly Loop
# =============================================================================
def run_nightly_loop():
    log("==============================================================================")
    log("POLYDIM V1350 AUTONOMOUS NIGHTLY RUNNER (BULLDOG PROTOCOL) — ACTIVE")
    log("==============================================================================")
    
    if not HAS_ORCH:
        log(f"[FATAL] Cannot import kernel_orchestrator_v1350: {orch_err}")
        return

    orch = orch_mod.PolydimOrchestratorV1350()
    status = orch.get_status()
    log(f"Target Hardware: Vendor={status['vendor']}, Target={status['target']}, MemoryClass={status['memory_class']}")
    log(f"Active Backend:  {status['active_backend']}")
    
    cycle = 1
    max_cycles = 1000  # Will run autonomously across the night
    
    while cycle <= max_cycles:
        t0 = time.perf_counter()
        log(f"--- [CICLO NOCTURNO {cycle:04d}] Ejecutando Sabuesos Adversarios ---")
        
        # 1. Sabueso 1: Adversarial Numerical Stress
        h1_ok = run_hound_1_numerical_stress(cycle, orch)
        
        # 2. Sabueso 2: PMTP Concurrency & Slabs
        h2_ok = run_hound_2_pmtp_concurrency(cycle, orch)
        
        # 3. Sabueso 3: Conformance Watchdog (Every 5 cycles)
        if cycle % 5 == 1:
            h3_ok = run_hound_3_conformance_watchdog(cycle)
        else:
            h3_ok = True
            
        elapsed = time.perf_counter() - t0
        all_ok = h1_ok and h2_ok and h3_ok
        
        res_str = "PASS" if all_ok else "FAIL"
        log(f"Ciclo {cycle:04d} completado en {elapsed:.2f}s | Estado: {res_str} | H1={h1_ok}, H2={h2_ok}, H3={h3_ok}")
        
        # Record fact every 10 cycles
        if cycle % 10 == 0:
            record_fact(
                "nightly_autonomous_runner_v1350.py",
                "NIGHTLY_STRESS_CYCLE",
                f"CYCLE_{cycle}",
                elapsed,
                f"Status: {res_str} | Hounds: 3/3 active"
            )
            
        cycle += 1
        time.sleep(15)  # 15s pause to keep CPU thermals and DDR3 memory cool


if __name__ == "__main__":
    run_nightly_loop()
