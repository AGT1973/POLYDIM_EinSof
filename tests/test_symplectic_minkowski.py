# Test & Benchmark Suite: Symplectic Dual-Shear & Minkowski Hyperbolic Manifold Kernels
# Verification of Zhongping Ji (2026) integration in POLYDIM / PMTP
# Contrato de Silicio: Exit Code 0 and FP64 precision verification

import os
import sys
import time
import numpy as np

# Add workspace to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pmtp import (
    neumaier_norm,
    neumaier_minkowski_inner_product,
    dual_shear_symplectic_rotation_2d,
    high_dim_torus_symplectic_flow,
    exact_log_symplectic_contraction,
    minkowski_hyperbolic_retraction,
)

def test_dual_shear_vs_trigonometric():
    print("[TEST 1] Dual-Shear vs Trigonometric Exact Rotation...")
    np.random.seed(42)
    p = np.random.randn(1000)
    q = np.random.randn(1000)
    theta = 0.7853981633974483 # pi / 4
    
    # Dual-shear evaluation
    p_shear, q_shear = dual_shear_symplectic_rotation_2d(p, q, theta)
    
    # Exact trigonometric rotation
    c, s = np.cos(theta), np.sin(theta)
    p_trig = c * p - s * q
    q_trig = s * p + c * q
    
    max_err_p = np.max(np.abs(p_shear - p_trig))
    max_err_q = np.max(np.abs(q_shear - q_trig))
    max_err = max(max_err_p, max_err_q)
    print(f"  -> Max error Dual-Shear vs Trig: {max_err:.2e}")
    assert max_err < 1e-14, f"Dual shear rotation error too high: {max_err}"
    print("  [PASS] Test 1 OK.")

def test_symplectic_area_preservation():
    print("[TEST 2] Symplectic Area Preservation (det = 1.0)...")
    theta = 1.23456
    # Basis vectors
    p1, q1 = dual_shear_symplectic_rotation_2d(np.array([1.0]), np.array([0.0]), theta)
    p2, q2 = dual_shear_symplectic_rotation_2d(np.array([0.0]), np.array([1.0]), theta)
    
    # Area = p1*q2 - p2*q1
    det = float(p1[0] * q2[0] - p2[0] * q1[0])
    area_err = abs(det - 1.0)
    print(f"  -> Determinant: {det:.16f}, Error: {area_err:.2e}")
    assert area_err < 1e-14, f"Symplectic volume defect too high: {area_err}"
    print("  [PASS] Test 2 OK.")

def test_elsf_radial_contraction():
    print("[TEST 3] Exact Log-Symplectic Flow (ELSF) Radial Contraction...")
    d = 2048
    latent = np.random.randn(d) * 5.0 # Perturbed away from unit radius
    gamma = 2.0
    dt = 0.5
    
    # Apply single forward pass closed-form contraction
    contracted = exact_log_symplectic_contraction(latent, gamma=gamma, dt=dt, r_target=1.0)
    
    # Calculate radius before and after on first phase plane
    r_old = np.sqrt(latent[0]**2 + latent[1]**2)
    r_new = np.sqrt(contracted[0]**2 + contracted[1]**2)
    
    expected_new = np.exp(np.log(r_old) * np.exp(-gamma * dt))
    err = abs(r_new - expected_new)
    print(f"  -> r_old: {r_old:.4f}, r_new: {r_new:.4f}, expected: {expected_new:.4f}, err: {err:.2e}")
    assert err < 1e-14, f"ELSF contraction mismatch: {err}"
    print("  [PASS] Test 3 OK.")

def test_minkowski_hyperbolic_quadric():
    print("[TEST 4] Minkowski Hyperbolic Level-Set Projection (<z, z>_L = -1.0)...")
    d = 1024 # 1 time-like + 1023 spatial dimensions
    np.random.seed(1337)
    
    max_drift = 0.0
    for trial in range(50):
        # Random vector in R^{1, 1023}
        z_random = np.random.randn(d)
        z_random[0] = abs(z_random[0]) + 1.5 # Ensure z0 > 1
        
        # Project onto H^{1023}
        z_hyp = minkowski_hyperbolic_retraction(z_random, target_curvature=-1.0)
        
        # Check Minkowski inner product with Neumaier compensation
        inner = neumaier_minkowski_inner_product(z_hyp, z_hyp)
        drift = abs(inner - (-1.0))
        if drift > max_drift:
            max_drift = drift
            
    print(f"  -> Maximum Minkowski Quadric Drift over 50 trials (D=1024): {max_drift:.2e}")
    assert max_drift < 1e-14, f"Minkowski hyperbolic quadric condition violated: {max_drift}"
    print("  [PASS] Test 4 OK.")

def test_high_dim_performance_benchmark():
    print("[TEST 5] High-Dimensional Latent Performance Benchmark (D=2048)...")
    d = 2048
    state = np.random.randn(d)
    angles = np.full(d // 2, 0.05)
    
    # Warmup
    for _ in range(100):
        _ = high_dim_torus_symplectic_flow(state, angles)
        
    iters = 2000
    t0 = time.perf_counter()
    for _ in range(iters):
        _ = high_dim_torus_symplectic_flow(state, angles)
    t1 = time.perf_counter()
    
    avg_us = ((t1 - t0) / iters) * 1e6
    print(f"  -> High-Dim Torus Symplectic Flow (D=2048): {avg_us:.2f} microseconds / eval")
    assert avg_us < 500.0, f"Flow execution too slow: {avg_us} us"
    print("  [PASS] Test 5 OK.")

def test_unitary_symplectic_stiefel_tradeoff():
    print("[TEST 6] Unitary Intersection U(K) = O(2K) cap Sp(2K, R) & Defect Diagnostics...")
    from pmtp import (
        build_canonical_symplectic_matrix,
        compute_orthogonality_defect,
        compute_symplectic_defect,
        unitary_symplectic_stiefel_evaluation
    )
    
    # 1. Test canonical 2D rotation matrix: should be in U(1) (both eps_orth and eps_sp <= 1e-15)
    theta = 0.654321
    c, s = np.cos(theta), np.sin(theta)
    U1 = np.array([[c, -s],
                   [s,  c]], dtype=np.float64)
    eps_orth_u1, eps_sp_u1 = unitary_symplectic_stiefel_evaluation(U1)
    print(f"  -> U(1) Matrix: eps_orth = {eps_orth_u1:.2e}, eps_sp = {eps_sp_u1:.2e}")
    assert eps_orth_u1 < 1e-14, f"Orthogonality defect in U(1): {eps_orth_u1}"
    assert eps_sp_u1 < 1e-14, f"Symplectic defect in U(1): {eps_sp_u1}"
    
    # 2. Test high-dimensional canonical unitary embedding U(K) for K = 64 (dim = 128)
    K = 64
    dim = 2 * K
    J = build_canonical_symplectic_matrix(dim)
    
    # Block unitary rotation: R = [[cos(t)*I, -sin(t)*I], [sin(t)*I, cos(t)*I]]
    I_K = np.eye(K, dtype=np.float64)
    R_UK = np.block([[c * I_K, -s * I_K],
                     [s * I_K,  c * I_K]])
    eps_orth_uk, eps_sp_uk = unitary_symplectic_stiefel_evaluation(R_UK)
    print(f"  -> U({K}) Embedded Matrix (dim={dim}): eps_orth = {eps_orth_uk:.2e}, eps_sp = {eps_sp_uk:.2e}")
    assert eps_orth_uk < 1e-14, f"Orthogonality defect in U(K): {eps_orth_uk}"
    assert eps_sp_uk < 1e-14, f"Symplectic defect in U(K): {eps_sp_uk}"
    
    # 3. Test generic random orthogonal matrix: in O(dim) but NOT in Sp(dim, R)
    # Demonstrates Perplexity Red Team audit: random polar retraction induces symplectic defect
    np.random.seed(42)
    A = np.random.randn(dim, dim)
    Q, _ = np.linalg.qr(A) # Generic orthogonal
    eps_orth_generic, eps_sp_generic = unitary_symplectic_stiefel_evaluation(Q)
    print(f"  -> Generic O({dim}) Matrix: eps_orth = {eps_orth_generic:.2e}, eps_sp = {eps_sp_generic:.2f}")
    assert eps_orth_generic < 1e-14
    assert eps_sp_generic > 0.1, "Generic orthogonal matrix should have non-zero symplectic defect"
    print("  [PASS] Test 6 OK (Both metrics successfully validated in silicon).")

def run_all_tests():
    print("=================================================================")
    print("PMTP SYMPLECTIC & MINKOWSKI VERIFICATION SUITE")
    print("Host Silicon: x86_64 AVX2 | Precision: IEEE-754 FP64")
    print("=================================================================")
    test_dual_shear_vs_trigonometric()
    test_symplectic_area_preservation()
    test_elsf_radial_contraction()
    test_minkowski_hyperbolic_quadric()
    test_high_dim_performance_benchmark()
    test_unitary_symplectic_stiefel_tradeoff()
    print("=================================================================")
    print("ALL TESTS PASSED CONTRATO DE SILICIO (Exit Code 0).")
    print("=================================================================")

if __name__ == "__main__":
    run_all_tests()
