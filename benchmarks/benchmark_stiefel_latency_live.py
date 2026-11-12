#!/usr/bin/env python3
"""
benchmark_stiefel_latency_live.py — Honest Silicon Benchmark for Stiefel Retraction & Shared Memory
Executes real computations on the current machine and reports measured times and isometry defects.
"""

import time
import platform
import numpy as np
from multiprocessing import shared_memory

def benchmark_stiefel_retraction(dimensions=[512, 1024, 2048], k=64, iterations=5):
    print("=" * 70)
    print("POLYDIM SUITE — LIVE SILICON BENCHMARK (REAL MEASUREMENTS)")
    print(f"Platform: {platform.platform()} | Python: {platform.python_version()}")
    print("=" * 70)
    print(f"{'Dimension D':<15} | {'Rank K':<8} | {'Latency (ms)':<15} | {'Orthogonality Defect':<22}")
    print("-" * 70)

    for D in dimensions:
        times = []
        defects = []
        for seed in range(iterations):
            rng = np.random.default_rng(2026 + seed)
            Z = rng.standard_normal((D, k)).astype(np.float64)
            
            t0 = time.perf_counter_ns()
            # Spectral normalization
            sigma = np.linalg.norm(Z, ord=2)
            if sigma > 1.0:
                Z = Z / sigma
            # 6 iterations of Newton-Schulz order 3
            I_k = np.eye(k, dtype=np.float64)
            for _ in range(6):
                Z = Z @ (1.5 * I_k - 0.5 * (Z.T @ Z))
            t1 = time.perf_counter_ns()
            
            elapsed_ms = (t1 - t0) / 1e6
            defect = float(np.max(np.abs(Z.T @ Z - I_k)))
            times.append(elapsed_ms)
            defects.append(defect)

        avg_time = np.mean(times)
        avg_defect = np.mean(defects)
        print(f"{D:<15} | {k:<8} | {avg_time:<15.3f} | {avg_defect:<22.2e}")

    print("-" * 70)

def benchmark_shared_memory_latency(payload_bytes=64 * 1024, rounds=1000):
    shm_name = f"PMTP_BENCH_{int(time.time())}"
    shm = shared_memory.SharedMemory(create=True, size=payload_bytes, name=shm_name)
    try:
        data = np.ones(payload_bytes // 8, dtype=np.float64) * 42.0
        t0 = time.perf_counter_ns()
        for _ in range(rounds):
            # View-based zero copy write
            view = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
            view[:] = data
        t1 = time.perf_counter_ns()
        avg_us = ((t1 - t0) / rounds) / 1000
        throughput_gb_s = (payload_bytes / (avg_us * 1e-6)) / 1e9
        print(f"Shared Memory Transfer ({payload_bytes // 1024} KB slab): {avg_us:.2f} us/transfer | Throughput: {throughput_gb_s:.2f} GB/s")
    finally:
        shm.close()
        shm.unlink()

if __name__ == "__main__":
    benchmark_stiefel_retraction()
    benchmark_shared_memory_latency()
    print("=" * 70)
    print(">>> BENCHMARK FINISHED SUCCESSFULLY (EXIT CODE 0) <<<")
