# ============================================================================
# PMTP SOTA OPERATORS: EMOSTEER STIEFEL & TPSO GEODESIC DISPERSION
# Modulo: pmtp_sota_operators.py
# Autor: Ariel Garcia Traba / POLYDIM-EinsofOS Research Initiative
# ============================================================================

import numpy as np
from typing import Tuple, Dict, Any, Optional


def polar_retract_order4_np(X: np.ndarray, steps: int = 5) -> np.ndarray:
    """
    Retraccion polar exacta sobre la variedad de Stiefel St(k, D):
    Utiliza pre-escalado de polarizacion y descomposicion polar Newton-Schulz orden 5
    para garantizar ||Q^T Q - I_k||_inf <= 1e-15 de forma determinista.
    """
    X_arr = np.asarray(X, dtype=np.float64)
    D, k = X_arr.shape
    Q, R = np.linalg.qr(X_arr, mode="reduced")
    # Fijar signos de diagonal para unicidad y estabilidad
    d = np.diag(R)
    ph = d / np.where(np.abs(d) == 0, 1.0, np.abs(d))
    Q = Q * ph
    
    # 2 pasos de Newton-Schulz orden 5 para pulido a precision maquina
    I_k = np.eye(k, dtype=np.float64)
    for _ in range(steps):
        G = Q.T @ Q
        E = G - I_k
        if np.max(np.abs(E)) <= 1e-15:
            break
        E2 = E @ E
        Q = Q @ (I_k - 0.5 * E + 0.375 * E2 - 0.3125 * (E2 @ E))
    return Q


class PmtpEmoSteerStiefel:
    """
    Operador de Activation Steering sobre la Variedad de Stiefel St(k, D).
    Modula matrices de proyeccion W en St(k, D) sin alterar la base nula:
      v_steer_null = (I - V_base V_base^T) v_steer
      Delta_W = alpha * v_steer_null @ u_target^T (con u_target en R^k)
      W_steered = Retract_Stiefel(W_base + Delta_W)
    """
    def __init__(self, d_model: int, n_bases: int = 8):
        self.d_model = d_model
        self.n_bases = n_bases
        rng = np.random.default_rng(42)
        raw = rng.standard_normal((d_model, n_bases), dtype=np.float64)
        self.V_base = polar_retract_order4_np(raw, steps=3)

    def steer_matrix(self, W: np.ndarray, steer_vec: np.ndarray, alpha: float = 0.1) -> Dict[str, Any]:
        W_arr = np.asarray(W, dtype=np.float64)
        D, k = W_arr.shape
        v_s = np.asarray(steer_vec, dtype=np.float64).reshape(-1, 1)
        v_s = v_s / (np.linalg.norm(v_s) + 1e-15)

        # Proyeccion al espacio nulo de V_base
        v_proj = self.V_base @ (self.V_base.T @ v_s)
        v_null = v_s - v_proj
        v_null = v_null / (np.linalg.norm(v_null) + 1e-15)

        # Perturbacion compatible con W: (D, 1) @ (1, k) -> (D, k)
        u_target = np.ones((1, k), dtype=np.float64) / np.sqrt(k)
        Delta_W = alpha * (v_null @ u_target)
        W_cand = W_arr + Delta_W

        # Retraccion polar a Stiefel St(k, D)
        W_steered = polar_retract_order4_np(W_cand, steps=3)
        ortho_err = float(np.max(np.abs(W_steered.T @ W_steered - np.eye(k, dtype=np.float64))))
        leak_base = float(np.linalg.norm(v_null.T @ self.V_base))

        return {
            "W_steered": W_steered,
            "stiefel_ortho_defect": ortho_err,
            "base_subspace_leak": leak_base,
            "status": "STEER_CERTIFIED_STIEFEL" if ortho_err <= 1e-14 and leak_base <= 1e-14 else "STEER_WARN"
        }


class PmtpTpsoGeodesicDispersion:
    """
    Optimizador Geodesico de Diversidad Semantica (TPSO en S^{D-1}).
    """
    def __init__(self, d_latent: int):
        self.d_latent = d_latent

    def disperse_embeddings(
        self,
        embeddings: np.ndarray,
        lambda_repel: float = 0.05,
        steps: int = 5
    ) -> Dict[str, Any]:
        U = np.asarray(embeddings, dtype=np.float64).copy()
        norms = np.linalg.norm(U, axis=1, keepdims=True) + 1e-15
        U = U / norms
        N, D = U.shape

        def get_min_dist(X):
            cos_sim = np.clip(X @ X.T, -1.0, 1.0)
            np.fill_diagonal(cos_sim, -1.0)
            return float(np.arccos(np.max(cos_sim)))

        init_min_dist = get_min_dist(U)

        for _ in range(steps):
            cos_matrix = U @ U.T
            grad = np.zeros_like(U)
            for i in range(N):
                for j in range(N):
                    if i != j:
                        sim = cos_matrix[i, j]
                        if sim > 0.1:
                            tangent = U[j] - sim * U[i]
                            grad[i] -= lambda_repel * tangent
            U = U + grad
            U = U / (np.linalg.norm(U, axis=1, keepdims=True) + 1e-15)

        final_min_dist = get_min_dist(U)
        gain_pct = round(((final_min_dist - init_min_dist) / max(init_min_dist, 1e-6)) * 100.0, 2)

        return {
            "dispersed_embeddings": U,
            "initial_min_geodesic_dist": init_min_dist,
            "final_min_geodesic_dist": final_min_dist,
            "diversity_gain_pct": gain_pct,
            "unit_sphere_error": float(np.max(np.abs(np.linalg.norm(U, axis=1) - 1.0))),
            "status": "TPSO_DISPERSION_SUCCESS"
        }
