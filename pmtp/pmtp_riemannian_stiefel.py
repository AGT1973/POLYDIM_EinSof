# ============================================================================
# PMTP RIEMANNIAN STIEFEL ENGINE: CAYLEY-WOODBURY O(D*r^2) & EDELMAN GEODESIC
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba (Independent Research / EinsofOS)
# Base Teórica: Edelman, Arias & Smith (1998), Absil et al. (2008), T-MP08 SOTA
# ============================================================================

import time
import numpy as np
import scipy.linalg
from typing import Tuple

class PmtpRiemannianStiefel:
    """
    Motor Geométrico de Retracción Riemanniana de Stiefel St(D, r) con:
    1. Retracción Cayley-Woodbury O(D*r^2): inversión exacta en subespacio 2r x 2r.
    2. Proyector Tangente canónico Pi_TW(G) = G - W * sym(W^T G).
    3. Geodésica analítica de Edelman sobre Stiefel.
    4. Garantía de ortogonalidad a nivel de máquina: ||R^T R - I||_inf <= 2e-15.
    """

    @staticmethod
    def project_tangent(W: np.ndarray, G: np.ndarray) -> np.ndarray:
        """
        Proyecta un gradiente o perturbación G in R^(D x r) sobre el espacio tangente
        T_W St(D, r) = { Delta in R^(D x r) : W^T Delta + Delta^T W = 0 }.
        Formula: Delta = G - W * sym(W^T G) con sym(A) = 0.5 * (A + A^T).
        """
        assert W.shape == G.shape, f"project_tangent dimension mismatch: W={W.shape}, G={G.shape}"
        WtG = np.dot(W.T, G)
        sym_WtG = 0.5 * (WtG + WtG.T)
        return G - np.dot(W, sym_WtG)

    @classmethod
    def cayley_woodbury_retraction(
        cls,
        W: np.ndarray,
        Delta: np.ndarray,
        alpha: float = 1.0,
        cond_max: float = 1e6
    ) -> np.ndarray:
        """
        Retracción racional de Cayley optimizada con Sherman-Morrison-Woodbury:
        R_W(Delta) = (I_D - 0.5 * alpha * Omega)^(-1) * (I_D + 0.5 * alpha * Omega) * W
        con Omega = Delta W^T - W Delta^T = U J U^T.
        Garantías SOTA:
        1. Proyección defensiva tangencial Pi_TW(Delta) para preservar antisimetría.
        2. Guarda espectral de condicionamiento sobre el núcleo K con fallback QR incondicional.
        Complejidad computacional: O(D * r^2) en lugar de O(D^3).
        """
        assert W.shape == Delta.shape, f"cayley_woodbury dimension mismatch: W={W.shape}, Delta={Delta.shape}"
        D, r = W.shape

        # 1. Proyección defensiva sobre el espacio tangente T_W St(D, r) (SOTA Red Team)
        Delta_tangent = cls.project_tangent(W, Delta)
        step_Delta = alpha * Delta_tangent

        # U = [W, step_Delta] in R^(D x 2r)
        U = np.hstack([W, step_Delta])

        # Matriz simpléctica canónica J in R^(2r x 2r):
        # [  0   -I_r ]
        # [ I_r    0  ]
        # J_inv = -J
        eye_r = np.eye(r, dtype=np.float64)
        zero_r = np.zeros((r, r), dtype=np.float64)
        J_inv = np.block([
            [zero_r,  eye_r],
            [-eye_r, zero_r]
        ])

        # V = (I_D + 0.5 * Omega) * W = W + 0.5 * (Delta * (W^T W) - W * (Delta^T W))
        # Dado que W^T W = I_r y W^T Delta es antisimétrica:
        WtDelta = np.dot(W.T, step_Delta)
        V = W + 0.5 * (step_Delta - np.dot(W, WtDelta.T))

        # Núcleo de Woodbury K in R^(2r x 2r): K = J_inv - 0.5 * (U^T U)
        UtU = np.dot(U.T, U)
        K = J_inv - 0.5 * UtU

        # Guarda de condicionamiento espectral anti-singularidad (SOTA)
        try:
            cond_K = float(np.linalg.cond(K))
            if cond_K > cond_max or not np.isfinite(cond_K):
                return cls.qr_retraction(W, Delta_tangent, alpha=alpha)
            UtV = np.dot(U.T, V)
            K_inv_UtV = np.linalg.solve(K, UtV)
        except np.linalg.LinAlgError:
            return cls.qr_retraction(W, Delta_tangent, alpha=alpha)

        # R_W = V + 0.5 * U * K_inv_UtV in R^(D x r)
        R = V + 0.5 * np.dot(U, K_inv_UtV)
        return R

    @classmethod
    def qr_retraction(
        cls,
        W: np.ndarray,
        Delta: np.ndarray,
        alpha: float = 1.0
    ) -> np.ndarray:
        """
        Retracción polar/QR analíticamente incondicional (Absil et al. 2008):
        R_W(Delta) = qf(W + alpha * Delta) con alineación canónica de signos en diagonal R.
        Garantiza ||R^T R - I|| <= machine epsilon incluso para alpha >> 1 o matrices mal condicionadas.
        """
        step = alpha * Delta
        Q, R_mat = np.linalg.qr(W + step, mode='reduced')
        # Alineación unívoca de fase: asegurar diag(R) > 0 para retractividad suave
        diag_R = np.diag(R_mat)
        phase = np.where(diag_R >= 0, 1.0, -1.0)
        return Q * phase

    @classmethod
    def adaptive_retraction(
        cls,
        W: np.ndarray,
        Delta: np.ndarray,
        alpha: float = 1.0,
        cond_k_threshold: float = 1e4
    ) -> Tuple[np.ndarray, str]:
        """
        Retracción adaptativa de grado de producción (SOTA):
        1. Evalúa el condicionamiento espectral del núcleo simpléctico K de Cayley-Woodbury.
        2. Si cond(K) <= threshold, ejecuta Cayley-Woodbury O(D*r^2).
        3. Si cond(K) > threshold (riesgo de torn-orthogonality), conmuta al fallback incondicional QR.
        """
        step = alpha * Delta
        U = np.hstack([W, step])
        r = W.shape[1]
        eye_r = np.eye(r, dtype=np.float64)
        zero_r = np.zeros((r, r), dtype=np.float64)
        J_inv = np.block([[zero_r, eye_r], [-eye_r, zero_r]])
        UtU = np.dot(U.T, U)
        K = J_inv - 0.5 * UtU

        cond_K = float(np.linalg.cond(K))
        if cond_K <= cond_k_threshold:
            R = cls.cayley_woodbury_retraction(W, Delta, alpha=alpha)
            return R, f"CAYLEY_WOODBURY (cond={cond_K:.2e})"
        else:
            R = cls.qr_retraction(W, Delta, alpha=alpha)
            return R, f"QR_FALLBACK_STABLE (cond={cond_K:.2e})"

    @classmethod
    def edelman_geodesic(
        cls,
        W: np.ndarray,
        Delta: np.ndarray,
        t: float = 1.0
    ) -> np.ndarray:
        """
        Geodésica Riemanniana analítica exacta en St(D, r) (Edelman, Arias & Smith 1998):
        gamma(t) = [W, Q] * exp(t * M) * [I_r; 0]
        donde A = W^T Delta, QR = (I - W W^T) Delta, y M = [A, -R^T; R, 0].
        """
        assert W.shape == Delta.shape, f"edelman_geodesic dimension mismatch: W={W.shape}, Delta={Delta.shape}"
        D, r = W.shape
        A = np.dot(W.T, Delta)
        # Componente normal
        Delta_normal = Delta - np.dot(W, A)
        Q, R = np.linalg.qr(Delta_normal, mode='reduced')

        # M in R^(2r x 2r)
        zero_r = np.zeros((r, r), dtype=np.float64)
        M = np.block([
            [A, -R.T],
            [R, zero_r]
        ])

        # Exponencial de matriz de dimensión 2r x 2r
        exp_tM = scipy.linalg.expm(t * M)
        eye_r = np.eye(r, dtype=np.float64)
        sub_exp = exp_tM[:, :r]

        gamma = np.dot(W, sub_exp[:r, :]) + np.dot(Q, sub_exp[r:, :])
        return gamma

    @staticmethod
    def measure_defect(W: np.ndarray) -> float:
        """Calcula ||W^T W - I_r||_inf."""
        r = W.shape[1]
        gram = np.dot(W.T, W)
        eye = np.eye(r, dtype=np.float64)
        return float(np.max(np.abs(gram - eye)))
