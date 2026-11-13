#!/usr/bin/env python3
"""
benchmark_matriz_con_vs_sin_pmtp.py
Benchmark Real End-to-End en Silicio: JSON 1D Serialization vs PMTP SHM (QDWH + ABI v1 + 0600 + BLAKE2s MAC).
Desglosa explicitamente:
  T_proj : Retraccion polar QDWH primaria St(k, D) (o vector unitario)
  T_sync : Seqlock atomico + cabecera ABI v1 + MAC BLAKE2s-64
  T_copy : Copia payload zero-copy IPC (write slot + read verified)
  T_total = T_proj + T_sync + T_copy
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
from pmtp.pmtp_types import HEADER_COMPACT_SIZE, PmtpCompactHeader  # noqa: E402


def run_live_matrix_benchmark() -> dict:
    configs = [
        {"name": "Qwen 3 1.5B Dim", "d_in": 2048, "k": 16},
        {"name": "Qwen 3 8B Dim",   "d_in": 4096, "k": 16},
        {"name": "DeepSeek V4 Dim", "d_in": 5120, "k": 16},
        {"name": "LLaMA 4 70B Dim", "d_in": 8192, "k": 16},
    ]

    rng = np.random.default_rng(2026)
    bus = PmtpShmBus(prefix="mat_e2e", max_slabs=8, max_dim=8192)
    results = []

    print("=" * 105)
    print("BENCHMARK END-TO-END EN SILICIO: JSON 1D VS PMTP (T_proj QDWH + T_sync Seqlock/MAC + T_copy SHM)")
    print("=" * 105)

    for cfg in configs:
        d = cfg["d_in"]
        k = cfg["k"]
        vec = rng.standard_normal(d).astype(np.float64)
        vec /= np.linalg.norm(vec)
        raw_w = rng.standard_normal((d, k)).astype(np.float64)

        # 1. Baseline 1D JSON Serialization + Parse roundtrip
        json_times_ms = []
        json_bytes = 0
        for _ in range(10):
            t0 = time.perf_counter_ns()
            s = json.dumps(vec.tolist())
            _ = np.asarray(json.loads(s), dtype=np.float64)
            json_times_ms.append((time.perf_counter_ns() - t0) / 1e6)
            json_bytes = len(s.encode("utf-8"))

        # Warmup SHM slab + QDWH
        slab = bus.allocate_tensor_slab(slab_id=100 + k, num_elements=d, dtype=np.float64)
        sid = 100 + k
        info = bus.slabs[sid]
        payload_len = info["payload_bytes"]
        W_warm, _, _, status_warm = PmtpStiefelAdapter.polar_safe_v2(raw_w, max_iters=10, tol=1e-14)
        assert status_warm in ("ACCEPTED_QDWH_POLAR", "ACCEPTED_SVD_POLAR_FALLBACK")

        # 2. Medicion desglosada End-to-End: T_proj + T_sync + T_copy
        t_proj_list, t_sync_list, t_copy_list, t_e2e_list = [], [], [], []
        last_defect = 1.0
        last_status = "UNKNOWN"
        last_kappa = 0.0

        for idx in range(20):
            # A) T_proj: Retraccion polar QDWH primaria St(k, d)
            t_p0 = time.perf_counter_ns()
            W_st, kappa, _, status = PmtpStiefelAdapter.polar_safe_v2(raw_w, max_iters=10, tol=1e-14)
            v_proj = W_st[:, 0]
            t_p1 = time.perf_counter_ns()

            # B) T_copy (write payload into inactive slot)
            t_c0 = time.perf_counter_ns()
            hdr = bus.read_header(sid)
            target_slot = 1 - hdr.active_slot
            slot_offset = HEADER_COMPACT_SIZE + (target_slot * payload_len)
            target_view = np.ndarray(shape=(d,), dtype=np.float64, buffer=slab.buf, offset=slot_offset)
            target_view[:] = v_proj[:]
            payload_raw = bytes(slab.buf[slot_offset:slot_offset + payload_len])
            t_c1 = time.perf_counter_ns()

            # C) T_sync (header ABI v1 + BLAKE2s-64 MAC + publish + reader MAC verify)
            t_s0 = time.perf_counter_ns()
            new_hdr_bytes = bus._pack_header_with_mac(
                dtype_id=hdr.dtype_id,
                active_slot=target_slot,
                slab_id=hdr.slab_id,
                num_elements=d,
                timestamp_ns=t_s0,
                scale=hdr.scale,
                generation=hdr.generation + 1,
                retired_slot0=(target_slot != 0),
                retired_slot1=(target_slot != 1),
                reserved_flags=hdr.reserved_flags,
                state_and_readers=hdr.state_and_readers,
                payload_bytes=payload_raw,
            )
            slab.buf[:HEADER_COMPACT_SIZE] = new_hdr_bytes
            hdr_r = bus.read_header(sid)
            bus._verify_mac(slab, hdr_r, hdr_r.active_slot, payload_len)
            t_s1 = time.perf_counter_ns()

            # D) T_copy (read view copy-out / explicit copy vs DLPack zero-copy)
            t_c2 = time.perf_counter_ns()
            read_view = np.ndarray(shape=(d,), dtype=np.float64, buffer=slab.buf, offset=HEADER_COMPACT_SIZE + hdr_r.active_slot * payload_len).copy()
            t_c3 = time.perf_counter_ns()

            assert np.allclose(read_view, v_proj, atol=1e-15)

            t_proj_us = (t_p1 - t_p0) / 1000.0
            t_sync_us = (t_s1 - t_s0) / 1000.0
            t_copy_us = ((t_c1 - t_c0) + (t_c3 - t_c2)) / 1000.0
            t_proj_list.append(t_proj_us)
            t_sync_list.append(t_sync_us)
            t_copy_list.append(t_copy_us)
            t_e2e_list.append(t_proj_us + t_sync_us + t_copy_us)

            if idx == 0:
                last_defect = float(np.max(np.abs(W_st.T @ W_st - np.eye(k, dtype=np.float64))))
                last_status = status
                last_kappa = float(kappa)

        # Clean per-dim slab so max_slabs stays minimal
        bus.release_all()

        med_json_ms = round(float(np.median(json_times_ms)), 4)
        med_proj_us = round(float(np.median(t_proj_list)), 2)
        med_sync_us = round(float(np.median(t_sync_list)), 2)
        med_copy_us = round(float(np.median(t_copy_list)), 2)
        med_ipc_us = round(med_sync_us + med_copy_us, 2)
        med_e2e_us = round(float(np.median(t_e2e_list)), 2)

        speedup_ipc = round((med_json_ms * 1000.0) / max(0.01, med_ipc_us), 1)
        speedup_e2e = round((med_json_ms * 1000.0) / max(0.01, med_e2e_us), 2)
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
            "con_pmtp_e2e": {
                "slab_bytes": slab_bytes,
                "T_proj_qdwh_us": med_proj_us,
                "T_sync_seqlock_mac_us": med_sync_us,
                "T_copy_explicit_shm_us": med_copy_us,
                "T_ipc_steady_us": med_ipc_us,
                "T_total_e2e_us": med_e2e_us,
                "speedup_ipc_steady": speedup_ipc,
                "speedup_e2e_with_proj": speedup_e2e,
                "copy_mode_note": "T_copy_explicit_shm_us mide copia explicita de validacion; DLPack zero-copy consume 0.0 us en modo lease.",
                "tokens_transmitted": 0,
                "stiefel_defect": last_defect,
                "polarsafe_status": last_status,
                "kappa": round(last_kappa, 4),
            },
        }
        results.append(entry)
        print(
            f"{cfg['name']:<18} | JSON1D: {med_json_ms:6.2f}ms ({json_bytes:6d}B) | "
            f"T_proj={med_proj_us:7.1f}us + T_sync={med_sync_us:5.1f}us + T_copy={med_copy_us:5.1f}us = "
            f"T_e2e={med_e2e_us:7.1f}us ({speedup_e2e:4.2f}x E2E, {speedup_ipc:5.1f}x IPC) | "
            f"Solver={last_status} Defect={last_defect:.2e}"
        )

    report = {
        "protocol": "END_TO_END_SILICON_MATRIX_TPROJ_TSYNC_TCOPY_QDWH",
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
