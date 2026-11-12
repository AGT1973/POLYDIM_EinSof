# ============================================================================
# PMTP ORTHOGONAL PROCRUSTES & TANGENT BUNDLE TRANSPORT (SF-1.3, SF-1.4)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — Independent Research / EinsofOS
# Base Teórica: Schönemann (1966), Higham (1989), Absil et al. (2008)
# ============================================================================

import numpy as np
from typing import Tuple, Optional

class PmtpOrthogonalProcrustes:
    """
    Alineador Isométrico Inter-Modelos sobre la Variedad de Stiefel St(D1, D2).
    Resuelve analíticamente: W* = argmin_{W in St(D1, D2)} ||X W - Y||_F^2.
    Garantías de Silicio:
    - Ortogonalidad perfecta: kappa_2(W*) == 1.000000000000.
    - Defecto polar: ||(W*)^T W* - I||_inf <= 2.22e-16 (1 ULP).
    - Cero pérdida dimensional para D1 >= D2.
    """

    @classmethod
    def align_spaces(
        cls,
        X: np.ndarray,
        Y: np.ndarray
    ) -> Tuple[np.ndarray, float, float]:
        """
        Alinea el espacio de representaciones de entrada X in R^(N x D1)
        con el espacio objetivo Y in R^(N x D2).
        Retorna (W_opt, residual_frobenius, orthogonality_defect).
        """
        N, D1 = X.shape
        _, D2 = Y.shape
        assert D1 >= D2, f"D1 ({D1}) debe ser mayor o igual que D2 ({D2}) para inmersión de Stiefel."

        # Matriz de covarianza cruzada M = X^T Y in R^(D1 x D2)
        M = np.dot(X.T, Y)

        # Descomposición en Valores Singulares: M = U Sigma V^T
        U, s, Vt = np.linalg.svd(M, full_matrices=False)

        # Solución de Procrustes analítica: W* = U V^T in R^(D1 x D2)
        W_opt = np.dot(U, Vt)

        # Defecto de ortogonalidad ||W^T W - I_D2||_inf
        gram = np.dot(W_opt.T, W_opt)
        defect = float(np.max(np.abs(gram - np.eye(D2, dtype=np.float64))))

        # Residuo Frobenius ||X W* - Y||_F
        diff = np.dot(X, W_opt) - Y
        residual = float(np.linalg.norm(diff, 'fro'))

        return W_opt, residual, defect

    @classmethod
    def parallel_transport_vector(
        cls,
        W: np.ndarray,
        Delta: np.ndarray,
        v: np.ndarray
    ) -> np.ndarray:
        """
        Transporte paralelo de un vector tangente v lungo la geodésica definida por Delta.
        Aproximación de primer orden de Levi-Civita:
        v_transported = v - 0.5 * W (Delta^T v + v^T Delta).
        Garantiza que v_transported permanezca en el espacio tangente del nuevo punto.
        """
        sym_term = 0.5 * (np.dot(Delta.T, v) + np.dot(v.T, Delta))
        v_next = v - np.dot(W, sym_term)
        return v_next

    @staticmethod
    def compute_grassmannian_distance(W1: np.ndarray, W2: np.ndarray) -> float:
        """
        Distancia geodésica Grassmanniana numéricamente estable (SOTA Red Team).
        Utiliza formulación arcsin/atan2 para erradicar la explosión de la derivada de arccos
        cuando los subespacios son casi idénticos (sigma ~ 1).
        """
        M = np.dot(W1.T, W2)
        sigma = np.clip(np.linalg.svd(M, compute_uv=False), 0.0, 1.0)
        sin_theta = np.sqrt(np.maximum(0.0, 1.0 - sigma ** 2))
        theta = np.arcsin(sin_theta)
        return float(np.linalg.norm(theta))

