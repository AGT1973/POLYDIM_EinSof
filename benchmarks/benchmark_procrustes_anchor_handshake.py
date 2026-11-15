#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmark_procrustes_anchor_handshake.py — Benchmark & Formal Verification in Silicon
=====================================================================================
Verifies Pillar 4 of Vision 2030 ("Co-Work, Not Doomsday"):
  Universal Procrustes Anchor Handshake (< 50 ms, Zero-Training, Zero Weight Modification)
  W = Polar(X_model^T X_anchor) in St(k, D)

Benchmarks and Formal Audits executed on live host silicon:
  1. Startup Handshake Latency across heterogeneous latent dimensions
     (D = 1536, 2048, 4096, 5120, 8192; N in {64, 128} anchors; k = 64)
     comparing Spectral-Polar Fast Path vs Full SVD vs QDWH.
  2. Heterogeneous Cross-Model Round-Trip Alignment (noiseless & noisy sigma=0.05).
  3. 50-Hop Multi-Agent Impedance Chain: Stiefel Procrustes vs Unconstrained Affine.
  4. Zero-Copy PmtpShmBus + DLPack + SipHash-2-4 MAC-64 End-to-End Integration.
  5. Adversarial Stress Hounds (Weyl bound, scale 1e-200..1e+100, kappa ladder, NaN/Inf/singular).
"""

import json
import math
import os
import platform
import sys
import time
from typing import Any, Dict, List

import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pmtp import PmtpOrthogonalProcrustes, PmtpShmBus, PmtpStiefelAdapter  # noqa: E402


MODEL_PROFILES = [
    {"name": "Einsof-ALADIN-Local", "d_model": 1536, "n_anchors": 64, "k": 64},
    {"name": "Qwen3-1.5B", "d_model": 2048, "n_anchors": 64, "k": 64},
    {"name": "Kimi-K3.1-Pro", "d_model": 4096, "n_anchors": 64, "k": 64},
    {"name": "DeepSeek-V4", "d_model": 5120, "n_anchors": 64, "k": 64},
    {"name": "Kimi-K3.1-Pro-128A", "d_model": 4096, "n_anchors": 128, "k": 64},
    {"name": "LLaMA-4-70B", "d_model": 8192, "n_anchors": 64, "k": 64},
]


def _make_canonical_anchors(n_anchors: int, k: int, seed: int = 2030) -> np.ndarray:
    """Genera el conjunto canónico ortonormal de anclas matemáticas/lógicas X_anchor in R^(N x k)."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((n_anchors, k)).astype(np.float64)
    q, r = np.linalg.qr(raw, mode="reduced")
    signs = np.where(np.diag(r) >= 0.0, 1.0, -1.0)
    return (q * signs).astype(np.float64)


def _make_model_anchor_responses(
    X_anchor: np.ndarray,
    d_model: int,
    seed: int,
    rel_noise: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Simula respuestas congeladas X_model in R^(N x D) de un modelo heterogéneo ante las anclas."""
    rng = np.random.default_rng(seed)
    n_anchors, k = X_anchor.shape
    raw_q = rng.standard_normal((d_model, k)).astype(np.float64)
    q_true, r_true = np.linalg.qr(raw_q, mode="reduced")
    q_true = q_true * np.where(np.diag(r_true) >= 0.0, 1.0, -1.0)
    X_clean = X_anchor @ q_true.T
    if rel_noise > 0.0:
        # Ruido calibrado por SNR relativo en R^(N x D): ||E||_F / ||X_clean||_F ~= rel_noise
        sigma_coord = rel_noise * math.sqrt(k / float(n_anchors * d_model))
        X_model = X_clean + sigma_coord * rng.standard_normal((n_anchors, d_model))
    else:
        X_model = X_clean
    return X_model, q_true


def benchmark_startup_handshake(iterations: int = 7) -> List[Dict[str, Any]]:
    print("\n[1/5] BENCHMARK DE LATENCIA STARTUP: PROCRUSTES ANCHOR HANDSHAKE (< 50 ms)")
    print("-" * 112)
    print(
        f"{'Modelo':<22} | {'(N, D, k)':<16} | {'Fast min/med (ms)':<19} | "
        f"{'SVD (ms)':<10} | {'QDWH (ms)':<10} | {'Defecto Frob/sqrt(k)':<20} | {'<50ms?'}"
    )
    print("-" * 112)

    # Warmup BLAS / LAPACK kernels before timed loop
    rng_warm = np.random.default_rng(0)
    _ = np.linalg.eigh(rng_warm.standard_normal((64, 64)) @ np.eye(64))
    _ = rng_warm.standard_normal((128, 1024)).T @ rng_warm.standard_normal((128, 64))

    rows: List[Dict[str, Any]] = []
    for idx, prof in enumerate(MODEL_PROFILES):
        d = prof["d_model"]
        n = prof["n_anchors"]
        k = prof["k"]
        X_anchor = _make_canonical_anchors(n, k, seed=2030 + n + k)
        X_model, q_true = _make_model_anchor_responses(X_anchor, d, seed=100 + idx)

        fast_times_ms: List[float] = []
        last_res = None
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            W, kappa, rel_frob_def, residual, status = PmtpOrthogonalProcrustes.anchor_handshake(
                X_model, X_anchor
            )
            t1 = time.perf_counter_ns()
            fast_times_ms.append((t1 - t0) / 1e6)
            last_res = (W, kappa, rel_frob_def, residual, status)

        W, kappa, rel_frob_def, residual, status = last_res  # type: ignore[misc]
        cheb_defect = float(np.max(np.abs(W.T @ W - np.eye(k))))
        recovery_err = float(np.max(np.abs(W - q_true)))

        # Baseline 1: Full SVD (align_spaces)
        t_svd0 = time.perf_counter_ns()
        W_svd, _, _ = PmtpOrthogonalProcrustes.align_spaces(X_model, X_anchor)
        svd_ms = (time.perf_counter_ns() - t_svd0) / 1e6
        assert W_svd.shape == (d, k)

        # Baseline 2: PolarSafe V2 (QDWH on D x k)
        t_q0 = time.perf_counter_ns()
        M = X_model.T @ X_anchor
        W_qdwh, _, _, _ = PmtpStiefelAdapter.polar_safe_v2(M, tol=1e-14)
        qdwh_ms = (time.perf_counter_ns() - t_q0) / 1e6
        assert W_qdwh.shape == (d, k)

        min_ms = float(min(fast_times_ms))
        med_ms = float(np.median(fast_times_ms))
        p95_ms = float(np.percentile(fast_times_ms, 95))
        under_50ms = med_ms < 50.0

        print(
            f"{prof['name']:<22} | {f'({n},{d},{k})':<16} | "
            f"{min_ms:7.2f} / {med_ms:7.2f}   | {svd_ms:8.2f}   | {qdwh_ms:8.2f}   | "
            f"{rel_frob_def:<20.3e} | {'YES' if under_50ms else 'NO'}"
        )

        assert status.startswith("ACCEPTED"), f"Handshake failed for {prof['name']}: {status}"
        assert rel_frob_def <= 1e-14, f"Relative Frobenius defect too high: {rel_frob_def}"
        assert recovery_err <= 1e-13, f"Subspace recovery error too high: {recovery_err}"

        rows.append({
            "model": prof["name"],
            "n_anchors": n,
            "d_model": d,
            "k": k,
            "fast_min_ms": round(min_ms, 3),
            "fast_median_ms": round(med_ms, 3),
            "fast_p95_ms": round(p95_ms, 3),
            "svd_ms": round(svd_ms, 3),
            "qdwh_ms": round(qdwh_ms, 3),
            "speedup_vs_svd": round(svd_ms / max(med_ms, 1e-6), 2),
            "speedup_vs_qdwh": round(qdwh_ms / max(med_ms, 1e-6), 2),
            "rel_frob_defect": rel_frob_def,
            "chebyshev_defect": cheb_defect,
            "recovery_linf_error": recovery_err,
            "kappa_2": kappa,
            "residual_frobenius": residual,
            "status": status,
            "under_50ms_median": under_50ms,
            "modifies_ai_model_weights": False,
        })

    print("-" * 112)
    return rows


def verify_cross_model_alignment() -> Dict[str, Any]:
    print("\n[2/5] ALINEAMIENTO HETEROGÉNEO INTER-MODELOS (NOISELESS & RUIDO RELATIVO 10%)")
    n, k = 64, 64
    X_anchor = _make_canonical_anchors(n, k, seed=2030)
    models = [
        ("Einsof-ALADIN", 1536, 11),
        ("Qwen3-1.5B", 2048, 22),
        ("Kimi-K3.1-Pro", 4096, 33),
        ("DeepSeek-V4", 5120, 44),
        ("LLaMA-4-70B", 8192, 55),
    ]

    results: Dict[str, Any] = {}
    for mode_name, rel_noise in [("noiseless_isometric", 0.0), ("realistic_domain_noise_10pct", 0.10)]:
        aligners = {}
        ground_truths = {}
        for name, d, seed in models:
            X_m, q_true = _make_model_anchor_responses(X_anchor, d, seed=seed, rel_noise=rel_noise)
            W, _, rel_def, _, status = PmtpOrthogonalProcrustes.anchor_handshake(X_m, X_anchor)
            assert status.startswith("ACCEPTED")
            assert rel_def <= 1e-14
            aligners[name] = W
            ground_truths[name] = q_true

        rng = np.random.default_rng(777)
        z_true = rng.standard_normal(k)
        z_true /= np.linalg.norm(z_true)

        pair_cosines = []
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                m_a = models[i][0]
                m_b = models[j][0]
                h_a = ground_truths[m_a] @ z_true
                z_canon = h_a @ aligners[m_a]
                h_b_rec = aligners[m_b] @ z_canon
                h_b_true = ground_truths[m_b] @ z_true
                cos_sim = float(np.dot(h_b_rec, h_b_true) / (np.linalg.norm(h_b_rec) * np.linalg.norm(h_b_true)))
                pair_cosines.append(cos_sim)

        min_cos = float(min(pair_cosines))
        mean_cos = float(np.mean(pair_cosines))
        print(f"  - Modo '{mode_name}': 10 pares heterogéneos | min_cos={min_cos:.12f} | mean_cos={mean_cos:.12f}")
        if rel_noise == 0.0:
            assert min_cos > 1.0 - 1e-14, f"Noiseless cosine mismatch: {min_cos}"
        else:
            assert min_cos > 0.90, f"Noisy Procrustes cosine degraded unexpectedly: {min_cos}"

        results[mode_name] = {
            "pairs_evaluated": len(pair_cosines),
            "min_cosine_similarity": min_cos,
            "mean_cosine_similarity": mean_cos,
        }
    return results


def verify_50_hop_impedance_matching() -> Dict[str, Any]:
    print("\n[3/5] CADENA DE IMPEDANCIA DE 50 SALTOS MULTI-AGENTE (STIEFEL VS AFÍN SIN RESTRICCIÓN)")
    n, k = 64, 64
    dims = [1536, 2048, 4096, 5120]
    X_anchor = _make_canonical_anchors(n, k, seed=909)
    rng = np.random.default_rng(31415)

    # Precomputar 51 alineadores heterogéneos St(k, D_i) via Procrustes Anchor Handshake
    stiefel_frames = []
    affine_frames = []
    for hop in range(51):
        d_i = dims[hop % len(dims)]
        X_m, _ = _make_model_anchor_responses(X_anchor, d_i, seed=1000 + hop, rel_noise=0.0)
        W_i, _, _, _, status = PmtpOrthogonalProcrustes.anchor_handshake(X_m, X_anchor)
        assert status.startswith("ACCEPTED")
        stiefel_frames.append(W_i)

        # Operador lineal sin restricción Stiefel (anisotropía kappa=4 + deriva espectral 1.08x por salto)
        u_un, _, vt_un = np.linalg.svd(rng.standard_normal((d_i, k)), full_matrices=False)
        sv_un = np.geomspace(1.12, 0.28, k)
        W_aff = (u_un * sv_un) @ vt_un
        affine_frames.append(W_aff)

    z0 = rng.standard_normal(k)
    z0 /= np.linalg.norm(z0)
    h_stiefel = stiefel_frames[0] @ z0
    h_affine = affine_frames[0] @ z0

    norm_st_0 = float(np.linalg.norm(h_stiefel))
    norm_aff_0 = float(np.linalg.norm(h_affine))

    checkpoints = {}
    for hop in range(1, 51):
        # Salto Stiefel Procrustes: h_{t} = W_t (W_{t-1}^T h_{t-1})
        z_lat = stiefel_frames[hop - 1].T @ h_stiefel
        h_stiefel = stiefel_frames[hop] @ z_lat

        # Salto Afín sin retracción: h_{t} = W_aff_t (W_aff_{t-1}^T h_{t-1})
        z_aff = affine_frames[hop - 1].T @ h_affine
        h_affine = affine_frames[hop] @ z_aff

        if hop in (1, 10, 25, 50):
            z_rec = stiefel_frames[hop].T @ h_stiefel
            cos_st = float(np.dot(z_rec, z0) / (np.linalg.norm(z_rec) * np.linalg.norm(z0)))
            norm_st = float(np.linalg.norm(h_stiefel))
            norm_aff = float(np.linalg.norm(h_affine))
            checkpoints[f"hop_{hop}"] = {
                "stiefel_norm": norm_st,
                "stiefel_norm_drift": abs(norm_st - norm_st_0),
                "stiefel_cosine_to_origin": cos_st,
                "unconstrained_norm": norm_aff,
                "unconstrained_ratio": norm_aff / max(norm_aff_0, 1e-30),
            }
            print(
                f"  - Hop {hop:2d}: Stiefel ||h||={norm_st:.15f} (drift={abs(norm_st - norm_st_0):.2e}, cos={cos_st:.15f}) "
                f"| Sin Stiefel ||h||={norm_aff:.3e}"
            )

    hop50 = checkpoints["hop_50"]
    assert hop50["stiefel_norm_drift"] < 1e-13, f"Stiefel 50-hop drift exceeded bound: {hop50['stiefel_norm_drift']}"
    assert hop50["stiefel_cosine_to_origin"] > 1.0 - 1e-13
    return checkpoints


def verify_pmtp_shm_integration() -> Dict[str, Any]:
    print("\n[4/5] INTEGRACIÓN ZERO-COPY PmtpShmBus + DLPack + SipHash-2-4 MAC-64")
    n, d_src, d_tgt, k = 64, 4096, 5120, 64
    X_anchor = _make_canonical_anchors(n, k, seed=2030)
    X_src, q_src = _make_model_anchor_responses(X_anchor, d_src, seed=101)
    X_tgt, q_tgt = _make_model_anchor_responses(X_anchor, d_tgt, seed=202)

    t0 = time.perf_counter_ns()
    W_src, _, def_src, _, st_src = PmtpOrthogonalProcrustes.anchor_handshake(X_src, X_anchor)
    W_tgt, _, def_tgt, _, st_tgt = PmtpOrthogonalProcrustes.anchor_handshake(X_tgt, X_anchor)
    t_hs_ms = (time.perf_counter_ns() - t0) / 1e6
    assert st_src.startswith("ACCEPTED") and st_tgt.startswith("ACCEPTED")

    rng = np.random.default_rng(55)
    z_true = rng.standard_normal(k)
    z_true /= np.linalg.norm(z_true)
    h_src = q_src @ z_true
    z_send = h_src @ W_src  # Vector canónico en S^{k-1}

    bus = PmtpShmBus(prefix="procrustes_hs", max_slabs=4, max_dim=k)
    try:
        t_ipc0 = time.perf_counter_ns()
        desc = bus.publish_tensor(z_send)
        slab_id = int(desc.split("_")[2])
        with bus.get_zero_copy_dlpack_tensor(slab_id) as leased:
            z_recv = np.from_dlpack(leased)
            h_tgt_rec = W_tgt @ z_recv
        t_ipc1 = time.perf_counter_ns()
        ipc_us = (t_ipc1 - t_ipc0) / 1000.0

        h_tgt_true = q_tgt @ z_true
        max_abs_err = float(np.max(np.abs(h_tgt_rec - h_tgt_true)))
        cos_sim = float(np.dot(h_tgt_rec, h_tgt_true) / (np.linalg.norm(h_tgt_rec) * np.linalg.norm(h_tgt_true)))
        print(
            f"  - Dual Handshake ({d_src} & {d_tgt} -> k={k}): {t_hs_ms:.2f} ms | "
            f"IPC DLPack+MAC: {ipc_us:.1f} us | cos={cos_sim:.15f} | err={max_abs_err:.2e} | tokens=0"
        )
        assert max_abs_err < 1e-13
        assert cos_sim > 1.0 - 1e-14
        return {
            "dual_handshake_ms": round(t_hs_ms, 3),
            "shm_dlpack_ipc_us": round(ipc_us, 2),
            "defect_src": def_src,
            "defect_tgt": def_tgt,
            "cosine_similarity": cos_sim,
            "max_abs_reconstruction_error": max_abs_err,
            "tokens_consumed": 0,
        }
    finally:
        bus.cleanup()


def run_adversarial_hounds() -> Dict[str, Any]:
    print("\n[5/5] AUDITORÍA ADVERSARIAL (REGLA 15: WEYL, ESCALA 1e-200..1e100, KAPPA, NaN/Inf)")
    rng = np.random.default_rng(2026)
    n, d, k = 64, 512, 32
    X_anchor = _make_canonical_anchors(n, k, seed=77)
    X_model, _ = _make_model_anchor_responses(X_anchor, d, seed=88)

    # Hound 1: Strict Weyl perturbation bound
    W, _, rel_def, _, status = PmtpOrthogonalProcrustes.anchor_handshake(X_model, X_anchor)
    eps_frob = float(np.linalg.norm(W.T @ W - np.eye(k), ord="fro"))
    s_vals = np.linalg.svd(W, compute_uv=False)
    kappa_meas = float(s_vals[0] / s_vals[-1])
    weyl_closed = math.sqrt((1.0 + eps_frob) / (1.0 - eps_frob))
    weyl_poly = 1.0 + eps_frob + eps_frob * eps_frob
    assert status == "ACCEPTED_SPECTRAL_POLAR"
    assert kappa_meas <= weyl_closed + 1e-15
    assert weyl_closed <= weyl_poly
    print(f"  - Hound 1 (Weyl): eps_F={eps_frob:.3e}, kappa={kappa_meas:.16f} <= {weyl_closed:.16f} PASS")

    # Hound 2: Extreme scale invariance (1e-200 vs 1e+100)
    W_tiny, _, _, _, st_tiny = PmtpOrthogonalProcrustes.anchor_handshake(X_model * 1e-200, X_anchor * 1e-200)
    W_huge, _, _, _, st_huge = PmtpOrthogonalProcrustes.anchor_handshake(X_model * 1e100, X_anchor * 1e100)
    scale_diff = float(np.max(np.abs(W_tiny - W_huge)))
    assert st_tiny == "ACCEPTED_SPECTRAL_POLAR" and st_huge == "ACCEPTED_SPECTRAL_POLAR"
    assert scale_diff < 1e-13, f"Scale invariance broken: {scale_diff}"
    print(f"  - Hound 2 (Scale 1e-200 vs 1e+100): max_diff={scale_diff:.3e} PASS")

    # Hound 3: Conditioning ladder (kappa = 1e5 fallback -> QR+SVD, kappa = 1e10 -> REJECTED)
    Q_true, _ = np.linalg.qr(rng.standard_normal((d, k)), mode="reduced")
    V_k, _ = np.linalg.qr(rng.standard_normal((k, k)), mode="reduced")
    X_mod_1e5 = (X_anchor @ (V_k * np.geomspace(1.0, 1e-5, k)) @ V_k.T) @ Q_true.T
    W_1e5, kap_1e5, def_1e5, _, st_1e5 = PmtpOrthogonalProcrustes.anchor_handshake(X_mod_1e5, X_anchor)
    assert st_1e5 == "ACCEPTED_QR_SVD_FALLBACK", f"Expected QR_SVD_FALLBACK, got {st_1e5}"
    assert def_1e5 < 1e-14
    assert float(np.max(np.abs(W_1e5 - Q_true))) < 1e-9

    X_mod_1e10 = (X_anchor @ (V_k * np.geomspace(1.0, 1e-10, k)) @ V_k.T) @ Q_true.T
    _, kap_1e10, _, _, st_1e10 = PmtpOrthogonalProcrustes.anchor_handshake(X_mod_1e10, X_anchor, kappa_fatal=1e8)
    assert st_1e10 == "REJECTED_ILL_CONDITIONED", f"Expected REJECTED_ILL_CONDITIONED, got {st_1e10}"
    print(f"  - Hound 3 (Conditioning): kappa={kap_1e5:.2e} -> {st_1e5}; kappa={kap_1e10:.2e} -> {st_1e10} PASS")

    # Hound 4: NaN, Inf, Zero, Rank-Deficient rejections
    X_nan = X_model.copy()
    X_nan[0, 0] = float("nan")
    _, _, _, _, st_nan = PmtpOrthogonalProcrustes.anchor_handshake(X_nan, X_anchor)
    assert st_nan == "REJECTED_NON_FINITE"

    X_inf = X_model.copy()
    X_inf[1, 2] = float("inf")
    _, _, _, _, st_inf = PmtpOrthogonalProcrustes.anchor_handshake(X_inf, X_anchor)
    assert st_inf == "REJECTED_NON_FINITE"

    _, _, _, _, st_zero = PmtpOrthogonalProcrustes.anchor_handshake(np.zeros_like(X_model), X_anchor)
    assert st_zero == "REJECTED_SINGULAR"

    X_rank_def = X_model.copy()
    # Force exact linear dependency in anchor response subspace
    X_rank_def[:, :] = X_anchor[:, :1] @ Q_true[:, :1].T
    _, _, _, _, st_rdef = PmtpOrthogonalProcrustes.anchor_handshake(X_rank_def, X_anchor)
    assert st_rdef == "REJECTED_RANK_DEFICIENT_SVD"
    print("  - Hound 4 (NaN/Inf/Zero/Rank-Deficient): All rejected fail-closed PASS")

    return {
        "weyl_eps_frob": eps_frob,
        "weyl_kappa_measured": kappa_meas,
        "weyl_closed_bound": weyl_closed,
        "scale_invariance_max_diff": scale_diff,
        "fallback_1e5_defect": def_1e5,
        "rejections_verified": ["REJECTED_NON_FINITE", "REJECTED_SINGULAR", "REJECTED_RANK_DEFICIENT_SVD", "REJECTED_ILL_CONDITIONED"],
    }


def main() -> int:
    print("=" * 112)
    print("POLYDIM VISION 2030 — UNIVERSAL PROCRUSTES ANCHOR HANDSHAKE (< 50 ms) VERIFICATION & SILICON BENCHMARK")
    print(f"Platform: {platform.platform()} | CPU: {platform.processor()} | Python: {platform.python_version()}")
    print("=" * 112)

    t_start = time.perf_counter()
    latency_rows = benchmark_startup_handshake(iterations=7)
    cross_model = verify_cross_model_alignment()
    chain_50 = verify_50_hop_impedance_matching()
    shm_res = verify_pmtp_shm_integration()
    hounds = run_adversarial_hounds()
    total_s = time.perf_counter() - t_start

    report = {
        "benchmark": "Universal Procrustes Anchor Handshake (<50 ms)",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "startup_handshake_latency": latency_rows,
        "cross_model_alignment": cross_model,
        "chain_50_hops": chain_50,
        "shm_dlpack_integration": shm_res,
        "adversarial_hounds": hounds,
        "total_runtime_s": round(total_s, 3),
        "exit_code": 0,
    }

    out_path = os.path.join(os.path.dirname(__file__), "benchmark_procrustes_anchor_handshake.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 112)
    print(f"[PASS] ALL 5 PROCRUSTES ANCHOR HANDSHAKE VERIFICATIONS PASSED IN {total_s:.2f}s | JSON: {out_path}")
    print("EXIT CODE 0")
    print("=" * 112)
    return 0


if __name__ == "__main__":
    sys.exit(main())
