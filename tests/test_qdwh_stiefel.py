import math
import numpy as np
import pytest

from pmtp.pmtp_stiefel import PmtpStiefelAdapter


def _make_conditioned_matrix(rng: np.random.Generator, rows: int, cols: int, kappa: float) -> np.ndarray:
    u, _ = np.linalg.qr(rng.standard_normal((rows, cols)))
    v, _ = np.linalg.qr(rng.standard_normal((cols, cols)))
    sv = np.geomspace(1.0, 1.0 / kappa, cols)
    return u @ np.diag(sv) @ v.T


def test_well_conditioned_qdwh_converges_cleanly():
    rng = np.random.default_rng(7)
    x = _make_conditioned_matrix(rng, 128, 16, kappa=2.5)
    q, kappa_est, r_rel_est, status = PmtpStiefelAdapter.polar_safe_v2(x, tol=1e-14)
    assert status == "ACCEPTED_QDWH_POLAR"
    assert kappa_est >= 2.0
    assert 0.0 < r_rel_est <= 1.0
    defect = float(np.max(np.abs(q.T @ q - np.eye(16))))
    assert defect < 1e-14


@pytest.mark.parametrize("kappa", [100.0, 1e3, 1e5, 1e7])
def test_ill_conditioned_uses_qdwh_and_matches_svd(kappa: float):
    rng = np.random.default_rng(123)
    rows, cols = 256, 32
    u, _ = np.linalg.qr(rng.standard_normal((rows, cols)))
    v, _ = np.linalg.qr(rng.standard_normal((cols, cols)))
    sv = np.geomspace(1.0, 1.0 / kappa, cols)
    x = u @ np.diag(sv) @ v.T

    q, _, _, status = PmtpStiefelAdapter.polar_safe_v2(x, tol=1e-13)
    assert status in ("ACCEPTED_QDWH_POLAR", "ACCEPTED_SVD_POLAR_FALLBACK")
    if kappa <= 1e5:
        assert status == "ACCEPTED_QDWH_POLAR"

    defect = float(np.max(np.abs(q.T @ q - np.eye(cols))))
    err_vs_svd = float(np.max(np.abs(q - (u @ v.T))))
    assert defect < 1e-12
    assert err_vs_svd < 1e-9


def test_fatal_ill_conditioned_rejected_cleanly():
    rng = np.random.default_rng(9)
    x = _make_conditioned_matrix(rng, 64, 8, kappa=1e10)
    q, kappa_2, r_rel, status = PmtpStiefelAdapter.polar_safe_v2(x, kappa_fatal=1e8)
    assert status == "REJECTED_ILL_CONDITIONED"
    assert kappa_2 > 1e8
    assert r_rel < 1e-8
    defect = float(np.max(np.abs(q.T @ q - np.eye(8))))
    assert defect < 1e-13


def test_rank_deficient_matrix_handled_explicitly():
    rng = np.random.default_rng(11)
    x = rng.standard_normal((64, 8))
    x[:, -1] = x[:, 0]  # Exact linear dependency -> sigma_min == 0
    q, kappa_2, r_rel, status = PmtpStiefelAdapter.polar_safe_v2(x)
    assert status == "REJECTED_RANK_DEFICIENT_SVD"
    assert not math.isfinite(kappa_2) or kappa_2 >= 1e14
    assert r_rel <= 1e-14
    defect = float(np.max(np.abs(q.T @ q - np.eye(8))))
    assert defect < 1e-13


def test_underdetermined_shape_rejected():
    x = np.ones((8, 16), dtype=np.float64)
    q, kappa_2, r_rel, status = PmtpStiefelAdapter.polar_safe_v2(x)
    assert status == "REJECTED_RANK_DEFICIENT"
    assert q.shape == (8, 16)
    assert math.isinf(kappa_2)
    assert r_rel == 0.0


def test_zero_and_non_finite_matrices_rejected():
    zero = np.zeros((32, 8), dtype=np.float64)
    q_z, _, _, status_z = PmtpStiefelAdapter.polar_safe_v2(zero)
    assert status_z == "REJECTED_SINGULAR"
    assert np.all(q_z == 0.0)

    for bad_val in (float("nan"), float("inf"), float("-inf")):
        bad = np.ones((32, 8), dtype=np.float64)
        bad[3, 4] = bad_val
        q_b, k_b, r_b, status_b = PmtpStiefelAdapter.polar_safe_v2(bad)
        assert status_b == "REJECTED_NON_FINITE"
        assert np.all(q_b == 0.0)
        assert math.isinf(k_b)
        assert r_b == 0.0


def test_scale_invariance_extreme_magnitudes():
    rng = np.random.default_rng(99)
    base = _make_conditioned_matrix(rng, 64, 8, kappa=500.0)
    q_small, _, _, st_small = PmtpStiefelAdapter.polar_safe_v2(base * 1e-200)
    q_large, _, _, st_large = PmtpStiefelAdapter.polar_safe_v2(base * 1e100)
    assert st_small == "ACCEPTED_QDWH_POLAR"
    assert st_large == "ACCEPTED_QDWH_POLAR"
    assert np.max(np.abs(q_small - q_large)) < 1e-12


def test_adapter_instance_orthogonality_defect():
    adapter = PmtpStiefelAdapter(dim_source=256, dim_latent=32, seed=42)
    defect = adapter.compute_orthogonality_defect()
    assert defect < 1e-14
