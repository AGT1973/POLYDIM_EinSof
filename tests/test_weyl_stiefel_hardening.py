#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
TEST WEYL STIEFEL HARDENING (SABIOS AUDIT REMEDIATION - CIRCUITO 1)
Ecosistema Soberano POLYDIM-EINSOF | Ariel García Traba

================================================================================
OBJECIÓN DEL TRIBUNAL DE SABIOS (OBJ-01) & RESOLUCIÓN MATEMÁTICA:
================================================================================
Miedo / Ataque de los Revisores (Sabios 1 y 3 - IEEE/ACM & NISQ):
  "Reportar precisión Stiefel <= 1e-15 sin demostrar formalmente el número de
   condición kappa_2(X) en aritmética FP64 genera sospecha de inestabilidad o
   divergencia bajo perturbaciones numéricas."

Demostración y Cota Analítica Cerrada (Teorema de Perturbación de Weyl):
  Sea X en R^{D x K} la matriz sobre la variedad de Stiefel con defecto de
  isometría ||X^T X - I_K||_F <= eps < 1.
  Los autovalores de Gram satisfacen |lambda_i - 1| <= ||X^T X - I_K||_2 <= eps.
  Extrayendo raíces cuadradas, los valores singulares están acotados por:
    sqrt(1 - eps) <= sigma_i(X) <= sqrt(1 + eps)
  Por ende, la cota superior analítica para el número de condición espectral es:
    kappa_2(X) = sigma_max / sigma_min <= sqrt((1 + eps) / (1 - eps)) <= 1 + eps + eps^2
  válida para todo 0 <= eps <= 0.5 sin aproximaciones lineales de primer orden.

Piso de Ruido Instrumental FP64:
  En aritmética binary64 (IEEE 754, eps_mach ~= 2.22e-16), el piso instrumental
  acumulado es eps_floor ~= sqrt(K) * eps_mach:
    - K = 32: eps_floor ~= 1.256e-15
    - K = 64: eps_floor ~= 1.776e-15
  La medición empírica en silicio satisface holgadamente kappa_2 <= cota_weyl.
================================================================================
"""

import sys
import numpy as np

def run_weyl_test():
    for K in [32, 64]:
        D = 4096
        np.random.seed(42 + K)
        A = np.random.randn(D, K)
        
        # Householder QR projection to Stiefel manifold V_K(R^D)
        Q, _ = np.linalg.qr(A)
        
        # Measure Frobenius isometry defect: epsilon = ||Q^T Q - I_K||_F
        G = Q.T @ Q
        I_K = np.eye(K, dtype=np.float64)
        eps = np.linalg.norm(G - I_K, 'fro')
        
        # Singular values of Q
        s = np.linalg.svd(Q, compute_uv=False)
        s_max = np.max(s)
        s_min = np.min(s)
        kappa_measured = s_max / s_min
        
        # Strict Weyl condition number closed-form bound and polynomial upper bound
        weyl_bound_closed = np.sqrt((1.0 + eps) / (1.0 - eps))
        weyl_bound_poly = 1.0 + eps + (eps ** 2)
        
        # IEEE 754 FP64 machine epsilon and noise floor
        eps_mach = np.finfo(np.float64).eps
        eps_floor = np.sqrt(K) * eps_mach
        
        print(f"[WEYL_HARDENING] Stiefel Dimension: D={D}, K={K}")
        print(f"[WEYL_HARDENING] Measured Isometry Defect eps: {eps:.6e}")
        print(f"[WEYL_HARDENING] Strict Weyl Closed Bound:     {weyl_bound_closed:.16f}")
        print(f"[WEYL_HARDENING] Strict Polynomial Bound:      {weyl_bound_poly:.16f}")
        print(f"[WEYL_HARDENING] Measured Empirical kappa_2:   {kappa_measured:.16f}")
        print(f"[WEYL_HARDENING] Measured Delta (kappa - 1.0): {kappa_measured - 1.0:.6e}")
        print(f"[WEYL_HARDENING] FP64 Noise Floor (sqrt(K)*u): {eps_floor:.6e}")
        
        # Formal assertions
        assert eps < 1e-14, f"Isometry defect too large: {eps}"
        assert kappa_measured <= weyl_bound_closed + 1e-16, f"Measured kappa ({kappa_measured}) exceeds Weyl bound ({weyl_bound_closed})"
        assert weyl_bound_closed <= weyl_bound_poly, "Polynomial bound violated"
        assert kappa_measured - 1.0 < 2e-15, f"Condition number delta too large: {kappa_measured - 1.0}"
    
    print("[PASS] Test Weyl Stiefel Hardening: Both K=32 and K=64 verified with strict closed bounds, Exit Code 0.")
    return 0

if __name__ == "__main__":
    sys.exit(run_weyl_test())
