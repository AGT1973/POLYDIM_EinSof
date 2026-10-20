"""MORPHO V0.8 — adversarial tests of claims, not a MORPHO integration test.
Run: python morpho_v08_redteam.py
Dependencies: numpy.
"""
import math
import struct
import numpy as np


def test_double_buffer_aba():
    """Construct an allowed schedule for a two-slot publisher without leases."""
    slots = [[10, 10], [20, 20]]
    active = 0
    # Reader holds slot ID 0 and reads first coordinate.
    read_slot = active
    first = slots[read_slot][0]
    # Writer publishes B (slot 1).
    slots[1][:] = [30, 30]
    active = 1
    # Writer reuses now-inactive A (slot 0) while reader still reads it.
    slots[0][0] = 40
    slots[0][1] = 40
    # Reader finishes reading the stale slot.
    second = slots[read_slot][1]
    observed = (first, second)
    assert observed == (10, 40)
    assert observed not in ((10, 10), (30, 30), (40, 40))
    return observed


def test_polar_scale():
    vals_small = np.linalg.svd(np.eye(2) * 1e-9, compute_uv=False)
    vals_bad = np.linalg.svd(np.diag([1e9, 1e-7]), compute_uv=False)
    assert vals_small[-1] < 1e-8  # Rejects an ideally conditioned matrix
    assert np.isclose(vals_small[0] / vals_small[-1], 1.)
    assert vals_bad[-1] > 1e-8  # Absolute threshold alone accepts this one
    assert vals_bad[0] / vals_bad[-1] > 1e15
    return vals_small[0] / vals_small[-1], vals_bad[0] / vals_bad[-1]


def test_bridge_spherical_noop():
    # A normalized state is not the raw projection; returning normalized
    # input unchanged is not a no-op in the original hidden-state coordinates.
    W = np.eye(3, 2, dtype=np.float64)
    h = np.array([6., 8., 4.])
    z_raw = W.T @ h  # [6, 8]
    z_unit = z_raw / np.linalg.norm(z_raw)
    z_after_unchanged = z_unit.copy()
    h_bad = h + W @ (z_after_unchanged - z_raw)
    # Explicitly preserve the norm/scale for consistent conversion.
    rho = np.linalg.norm(z_raw)
    h_good = h + W @ (rho * (z_after_unchanged - z_unit))
    assert not np.array_equal(h_bad, h)
    assert np.array_equal(h_good, h)
    return float(np.max(np.abs(h_bad - h)))


def test_bridge_sign_and_nonfinite():
    # Arithmetic x + 0 does not preserve the -0.0 bit pattern.
    h = np.array([-0.0], dtype=np.float64)
    computed = h + np.array([+0.0])
    assert h[0] == computed[0]
    assert h.tobytes() != computed.tobytes()
    # Multiplication by beta=0 is not a bypass for invalid delta.
    with np.errstate(invalid='ignore'):
        wrong_bypass = 0.0 * np.array([np.nan])
    assert np.isnan(wrong_bypass[0])
    # With beta=-2 the norm law must use |beta|.
    beta = -2.0
    W = np.array([[1.0], [0.0]])
    dz = np.array([3.0])
    dh = beta * (W @ dz)
    assert np.linalg.norm(dh) == abs(beta) * np.linalg.norm(dz)
    return struct.pack('>d', h[0]).hex(), struct.pack('>d', computed[0]).hex()


def test_cam_statistical_limit():
    # Exact 95% two-sided lower Clopper-Pearson endpoint for n/n successes:
    # alpha^(1/n), for alpha=0.025.
    return 0.025**(1.0 / 8.0)



def test_cam_correlated_keys_no_training():
    """An analytic softmax CAM can achieve 8/8 on correlated noisy keys."""
    rng = np.random.default_rng(123)
    n, d = 8, 64
    common = np.ones(d, dtype=np.float64)
    common /= np.linalg.norm(common)
    variations = rng.normal(size=(n, d))
    variations -= (variations @ common)[:, None] * common
    variations /= np.linalg.norm(variations, axis=1, keepdims=True)
    keys = common[None, :] + 0.3 * variations
    keys /= np.linalg.norm(keys, axis=1, keepdims=True)
    off_diagonal = (keys @ keys.T)[np.triu_indices(n, 1)]
    assert np.min(off_diagonal) > 0.8  # Correlated, nonorthogonal keys
    queries = keys + 0.01 * rng.normal(size=keys.shape)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)
    logits = queries @ keys.T / 0.01
    weights = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    weights /= weights.sum(axis=1, keepdims=True)
    accuracy = np.mean(np.argmax(weights, axis=1) == np.arange(n))
    assert accuracy == 1.0
    return float(np.min(off_diagonal)), float(np.max(off_diagonal)), accuracy

def main():
    mixed = test_double_buffer_aba()
    good_cond, bad_cond = test_polar_scale()
    no_op_error = test_bridge_spherical_noop()
    hex_before, hex_after = test_bridge_sign_and_nonfinite()
    ci = test_cam_statistical_limit()
    corr_min, corr_max, cam_acc = test_cam_correlated_keys_no_training()
    print(f"MP-48 two-slot ABA stale-reader payload: {mixed} [COUNTEREXAMPLE]")
    print(f"MP-49 PolarSafe cond for rejected good matrix: {good_cond:.1f}; accepted bad matrix: {bad_cond:.1e}")
    print(f"MP-50 spherical bridge fake no-op max change: {no_op_error:g}")
    print(f"MP-51 signed-zero bits before: {hex_before}; after: {hex_after}")
    print("MP-51 beta=0 x NaN is NaN; negative beta needs absolute value")
    print(f"MP-52 eight successes, 95% two-sided lower bound: {ci:.4f}")
    print(f"MP-52 softmax CAM without training: {int(cam_acc*8)}/8; key cosine range [{corr_min:.3f}, {corr_max:.3f}]")
    print("MORPHO_V08_ADVERSARIAL_COUNTEREXAMPLES_PASS")


if __name__ == '__main__':
    main()
