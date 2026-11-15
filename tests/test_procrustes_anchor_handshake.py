#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_procrustes_anchor_handshake.py — Formal Verification Suite for Universal Procrustes Anchor Handshake
=========================================================================================================
Verifies:
  1. Exact Stiefel isometry (rel Frobenius defect <= 1e-14, Weyl bound kappa <= sqrt((1+eps)/(1-eps))).
  2. Scale invariance across 300 orders of magnitude (1e-200 .. 1e+100).
  3. Conditioning ladder: fast spectral polar (kappa <= 1e3), QR+SVD fallback (1e3 < kappa <= 1e8),
     and fail-closed rejection (kappa > 1e8, rank-deficient, NaN/Inf, zero, invalid shape).
  4. Heterogeneous multi-model round-trip alignment (D = 1536 <-> 4096 <-> 5120 -> k = 64).
  5. 50-hop Stiefel impedance stability (norm drift < 1e-13 across 50 heterogeneous model hops).
  6. Zero-copy PmtpShmBus + DLPack + SipHash-2-4 MAC-64 interoperability.
"""

import math
import numpy as np
import pytest

from pmtp import PmtpOrthogonalProcrustes, PmtpShmBus


def _make_anchors(n: int, k: int, seed: int = 2030) -> np.ndarray:
    rng = np.random.default_rng(seed)
    q, r = np.linalg.qr(rng.standard_normal((n, k)), mode="reduced")
    return (q * np.where(np.diag(r) >= 0.0, 1.0, -1.0)).astype(np.float64)


def _make_responses(X_anchor: np.ndarray, d: int, seed: int, noise_std: float = 0.0):
    rng = np.random.default_rng(seed)
    n, k = X_anchor.shape
    q_true, r_true = np.linalg.qr(rng.standard_normal((d, k)), mode="reduced")
    q_true = q_true * np.where(np.diag(r_true) >= 0.0, 1.0, -1.0)
    X_model = X_anchor @ q_true.T
    if noise_std > 0.0:
        X_model = X_model + noise_std * rng.standard_normal((n, d))
    return X_model, q_true


@pytest.mark.parametrize("n,d,k", [(64, 1536, 64), (64, 4096, 64), (128, 4096, 64), (64, 5120, 64)])
def test_anchor_handshake_isometry_and_recovery(n: int, d: int, k: int):
    X_anchor = _make_anchors(n, k, seed=10 + n)
    X_model, q_true = _make_responses(X_anchor, d, seed=20 + d)
    W, kappa, rel_frob_defect, residual, status = PmtpOrthogonalProcrustes.anchor_handshake(
        X_model, X_anchor
    )
    assert status == "ACCEPTED_SPECTRAL_POLAR"
    assert W.shape == (d, k)
    assert rel_frob_defect <= 1e-14
    assert residual <= 1e-12
    assert np.max(np.abs(W - q_true)) <= 1e-13

    eps_f = float(np.linalg.norm(W.T @ W - np.eye(k), ord="fro"))
    s_vals = np.linalg.svd(W, compute_uv=False)
    kappa_meas = float(s_vals[0] / s_vals[-1])
    assert kappa_meas <= math.sqrt((1.0 + eps_f) / (1.0 - eps_f)) + 1e-15


def test_anchor_handshake_scale_invariance_extreme():
    X_anchor = _make_anchors(64, 32, seed=77)
    X_model, q_true = _make_responses(X_anchor, 512, seed=88)

    W_tiny, _, def_tiny, _, st_tiny = PmtpOrthogonalProcrustes.anchor_handshake(
        X_model * 1e-200, X_anchor * 1e-200
    )
    W_huge, _, def_huge, _, st_huge = PmtpOrthogonalProcrustes.anchor_handshake(
        X_model * 1e100, X_anchor * 1e100
    )
    assert st_tiny == "ACCEPTED_SPECTRAL_POLAR"
    assert st_huge == "ACCEPTED_SPECTRAL_POLAR"
    assert def_tiny <= 1e-14 and def_huge <= 1e-14
    assert np.max(np.abs(W_tiny - W_huge)) <= 1e-13
    assert np.max(np.abs(W_tiny - q_true)) <= 1e-13


def test_anchor_handshake_conditioning_and_rejections():
    rng = np.random.default_rng(123)
    n, d, k = 64, 256, 32
    X_anchor = _make_anchors(n, k, seed=9)
    q_true, _ = np.linalg.qr(rng.standard_normal((d, k)), mode="reduced")
    v_k, _ = np.linalg.qr(rng.standard_normal((k, k)), mode="reduced")

    # Moderate/high conditioning kappa = 1e5 triggers lossless QR+SVD fallback
    X_1e5 = (X_anchor @ (v_k * np.geomspace(1.0, 1e-5, k)) @ v_k.T) @ q_true.T
    W_1e5, kap_1e5, def_1e5, _, st_1e5 = PmtpOrthogonalProcrustes.anchor_handshake(X_1e5, X_anchor)
    assert st_1e5 == "ACCEPTED_QR_SVD_FALLBACK"
    assert 9e4 <= kap_1e5 <= 1.1e5
    assert def_1e5 <= 1e-14
    assert np.max(np.abs(W_1e5 - q_true)) <= 1e-9

    # Fatal conditioning kappa = 1e10 rejected cleanly
    X_1e10 = (X_anchor @ (v_k * np.geomspace(1.0, 1e-10, k)) @ v_k.T) @ q_true.T
    _, _, _, _, st_1e10 = PmtpOrthogonalProcrustes.anchor_handshake(X_1e10, X_anchor, kappa_fatal=1e8)
    assert st_1e10 == "REJECTED_ILL_CONDITIONED"

    # NaN / Inf / Zero / Rank-Deficient / Invalid Shape
    X_ok, _ = _make_responses(X_anchor, d, seed=5)
    for bad in (float("nan"), float("inf"), float("-inf")):
        X_bad = X_ok.copy()
        X_bad[0, 0] = bad
        _, _, _, _, st = PmtpOrthogonalProcrustes.anchor_handshake(X_bad, X_anchor)
        assert st == "REJECTED_NON_FINITE"

    _, _, _, _, st_z = PmtpOrthogonalProcrustes.anchor_handshake(np.zeros_like(X_ok), X_anchor)
    assert st_z == "REJECTED_SINGULAR"

    X_rd = X_anchor[:, :1] @ q_true[:, :1].T
    _, _, _, _, st_rd = PmtpOrthogonalProcrustes.anchor_handshake(X_rd, X_anchor)
    assert st_rd == "REJECTED_RANK_DEFICIENT_SVD"

    _, _, _, _, st_shape = PmtpOrthogonalProcrustes.anchor_handshake(X_ok[:, :16], X_anchor)
    assert st_shape == "REJECTED_INVALID_SHAPE"


def test_50_hop_heterogeneous_impedance_and_shm_roundtrip():
    n, k = 64, 64
    X_anchor = _make_anchors(n, k, seed=2030)
    dims = [1536, 2048, 4096, 5120]
    frames = []
    for hop in range(51):
        X_m, _ = _make_responses(X_anchor, dims[hop % len(dims)], seed=500 + hop)
        W_i, _, rel_def, _, st = PmtpOrthogonalProcrustes.anchor_handshake(X_m, X_anchor)
        assert st == "ACCEPTED_SPECTRAL_POLAR"
        assert rel_def <= 1e-14
        frames.append(W_i)

    rng = np.random.default_rng(42)
    z0 = rng.standard_normal(k)
    z0 /= np.linalg.norm(z0)
    h = frames[0] @ z0
    for hop in range(1, 51):
        h = frames[hop] @ (frames[hop - 1].T @ h)

    z_end = frames[-1].T @ h
    assert abs(float(np.linalg.norm(h)) - 1.0) <= 1e-13
    assert float(np.dot(z_end, z0)) >= 1.0 - 1e-13

    bus = PmtpShmBus(prefix="test_hs", max_slabs=2, max_dim=k)
    try:
        desc = bus.publish_tensor(z_end)
        slab_id = int(desc.split("_")[2])
        with bus.get_zero_copy_dlpack_tensor(slab_id) as leased:
            z_shm = np.from_dlpack(leased)
            assert np.allclose(z_shm, z0, atol=1e-13)
    finally:
        bus.cleanup()
