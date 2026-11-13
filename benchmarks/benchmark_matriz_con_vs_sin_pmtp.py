#!/usr/bin/env python3
"""
benchmark_matriz_con_vs_sin_pmtp.py
Benchmark Real Multi-Dimensional en Silicio: Transporte JSON 1D vs PmtpShmBus Zero-Copy Autenticado + Stiefel.
Mide latencias reales en microsegundos, bytes serializados y defecto Stiefel real para D in [2048, 4096, 5120, 8192].
"""

import os
import sys
import json
import time
import platform
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pmtp import PmtpShmBus  # noqa: E402
from pmtp.pmtp_stiefel import PmtpStiefelAdapter  # noqa: E402


def run_live_matrix_benchmark() -> dict:
    configs = [
        {"name": "Qwen 3 1.5B Dim", "d_in": 2048, "k": 16},
        {"name": "Qwen 3 8B Dim",   "d_in": 4096, "k": 16},
        {"name": "DeepSeek V4 Dim", "d_in": 5120, "k": 16},
        {"name": "LLaMA 4 70B Dim", "d_in": 8192, "k": 16},
    ]

    rng = np.random.default_rng(2026)
    bus = PmtpShmBus(prefix="mat_live", max_slabs=8, max_dim=8192)
    results = []

    print("=" * 95)
    print("BENCHMARK REAL EN SILICIO: JSON 1D SERIALIZATION VS PMTP SHM (0600 + MAC + STIEFEL)")
    print("=" * 95)

    for cfg in configs:
        d = cfg["d_in"]
        k = cfg["k"]
        vec = rng.standard_normal(d).astype(np.float64)
        vec /= np.linalg.norm(vec)

        # 1. Medir serializacion 1D JSON real (sin PMTP)
        json_times_ms = []
        json_bytes = 0
        for _ in range(10):
            t0 = time.perf_counter_ns()
            s = json.dumps(vec.tolist())
            _ = np.asarray(json.loads(s), dtype=np.float64)
            json_times_ms.append((time.perf_counter_ns() - t0) / 1e6)
            json_bytes = len(s.encode("utf-8"))

        # 2. Medir transporte real PmtpShmBus autenticado (publish + read + MAC verify)
        shm_times_us = []
        # Warmup slab allocation
        desc0 = bus.publish_tensor(vec)
        _ = bus.read_tensor(desc0, verify_stiefel=True, verify_mac=True)

        for _ in range(30):
            t0 = time.perf_counter_ns()
            desc = bus.publish_tensor(vec)
            rec = bus.read_tensor(desc, verify_stiefel=True, verify_mac=True)
            shm_times_us.append((time.perf_counter_ns() - t0) / 1000.0)
            assert np.allclose(rec, vec, atol=1e-15)

        # 3. Medir retraccion PolarSafe V2 en St(k, d)
        raw_w = rng.standard_normal((d, k)).astype(np.float64)
        W_st, kappa, _, status = PmtpStiefelAdapter.polar_safe_v2(raw_w, max_iters=20, tol=1e-15, kappa_max=1e3)
        defect = float(np.max(np.abs(W_st.T @ W_st - np.eye(k, dtype=np.float64))))

        med_json_ms = round(float(np.median(json_times_ms)), 4)
        med_shm_us = round(float(np.median(shm_times_us)), 2)
        speedup = round((med_json_ms * 1000.0) / max(0.01, med_shm_us), 1)
        slab_bytes = 64 + 2 * d * 8

        entry = {
            "name": cfg["name"],
            "manifold": f"St({k}, {d})",
            "d_in": d,
            "k": k,
            "sin_pmtp_json_1d": {
                "serialized_bytes": json_bytes,
                "median_roundtrip_ms": med_json_ms,
                "tokens_equivalent_est": round(json_bytes / 4.0),
            },
            "con_pmtp_shm_mac": {
                "slab_bytes": slab_bytes,
                "median_roundtrip_us": med_shm_us,
                "tokens_transmitted": 0,
                "speedup_vs_json_1d": speedup,
                "stiefel_defect": defect,
                "polarsafe_status": status,
                "kappa": round(float(kappa), 4),
            },
        }
        results.append(entry)
        print(f"{cfg['name']:<20} | JSON 1D: {med_json_ms:7.3f} ms ({json_bytes:6d} B) | PMTP SHM+MAC: {med_shm_us:7.2f} us ({speedup:6.1f}x) | Defect: {defect:.2e}")

    bus.cleanup()
    report = {
        "protocol": "LIVE_SILICON_MATRIX_JSON_VS_PMTP_SHM_MAC",
        "platform": platform.platform(),
        "models": results,
        "exit_code": 0,
    }

    out_path = os.path.join(os.path.dirname(__file__), "benchmark_matriz_con_vs_sin_pmtp.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[+] Reporte JSON crudo guardado en: {out_path}")
    return report


if __name__ == "__main__":
    run_live_matrix_benchmark()
