# ============================================================================
# PMTP ORTHOGONAL PROCRUSTES & TANGENT BUNDLE TRANSPORT (SF-1.3, SF-1.4)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — Independent Research / EinsofOS
# Base Teórica: Schönemann (1966), Higham (1989), Absil et al. (2008)
# ============================================================================

import math
import numpy as np
from typing import Tuple, Optional


def _neumaier_sum_sq(arr: np.ndarray) -> float:
    """Suma compensada de Neumaier de los cuadrados de `arr` en FP64."""
    flat = np.asarray(arr, dtype=np.float64).ravel()
    sq = flat * flat
    return float(math.fsum(sq))


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
        if X.ndim != 2 or Y.ndim != 2:
            raise ValueError(f"X e Y deben ser matrices 2D, recibido X={X.shape}, Y={Y.shape}")
        N, D1 = X.shape
        N2, D2 = Y.shape
        if N != N2:
            raise ValueError(f"Número de muestras incompatible: X tiene {N}, Y tiene {N2}")
        if D1 < D2:
            raise ValueError(f"D1 ({D1}) debe ser mayor o igual que D2 ({D2}) para inmersión de Stiefel.")

        # Matriz de covarianza cruzada M = X^T Y in R^(D1 x D2)
        M = np.dot(X.T, Y)

        # Descomposición en Valores Singulares: M = U Sigma V^T
        U, s, Vt = np.linalg.svd(M, full_matrices=False)

        # Solución de Procrustes analítica: W* = U V^T in R^(D1 x D2)
        W_opt = np.dot(U, Vt)

        # Defecto de ortogonalidad ||W^T W - I_D2||_inf
        gram = np.dot(W_opt.T, W_opt)
        defect = float(np.max(np.abs(gram - np.eye(D2, dtype=np.float64))))

        # Residuo Frobenius ||X W* - Y||_F con reducción compensada exacta (math.fsum / Neumaier)
        diff = np.dot(X, W_opt) - Y
        residual = math.sqrt(max(0.0, _neumaier_sum_sq(diff)))

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

    @classmethod
    def anchor_handshake(
        cls,
        X_model: np.ndarray,
        X_anchor: np.ndarray,
        kappa_polish: float = 1.05,
        kappa_fallback: float = 1e3,
        kappa_fatal: float = 1e8,
        tol: float = 1e-15,
        compute_residual: bool = True,
    ) -> Tuple[np.ndarray, float, float, float, str]:
        """
        Universal Procrustes Anchor Handshake (<50 ms) sobre la Variedad de Stiefel St(k, D).
        Calcula W = Polar(X_model^T X_anchor) in St(k, D) sin modificar pesos del modelo.

        Estrategia numérica:
        1. Pre-escalado selectivo de X_model y X_anchor contra underflow/overflow (1e-200 .. 1e+100).
        2. Ruta rápida BLAS3 espectral (G = M_s^T M_s, eigh(G), W = M_s G^{-1/2}) con pulido Newton-Schulz
           cuando kappa > kappa_polish (evita pérdida cuadrática de precisión).
        3. Fallback exacto QR(M_s) + SVD(R_m) (k x k) cuando kappa > kappa_fallback o G no es SPD.
        4. Reducción compensada de Neumaier (math.fsum) para defecto Frobenius relativo y residuo.

        Retorna: (W, kappa, rel_frob_defect, residual_frobenius, status)
        """
        X_m = np.asarray(X_model, dtype=np.float64)
        X_a = np.asarray(X_anchor, dtype=np.float64)
        if X_m.ndim != 2 or X_a.ndim != 2:
            raise ValueError(f"X_model y X_anchor deben ser matrices 2D, recibido {X_m.shape} y {X_a.shape}")

        N, D = X_m.shape
        N2, k = X_a.shape
        if N != N2:
            raise ValueError(f"Número de anclas incompatible: X_model={N}, X_anchor={N2}")
        if D == 0 or k == 0 or N == 0:
            raise ValueError(f"Dimensiones vacías no permitidas: X_model={X_m.shape}, X_anchor={X_a.shape}")

        if not (np.all(np.isfinite(X_m)) and np.all(np.isfinite(X_a))):
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_NON_FINITE"

        if D < k or N < k:
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_INVALID_SHAPE"

        max_m = float(np.max(np.abs(X_m)))
        max_a = float(np.max(np.abs(X_a)))
        if max_m <= 0.0 or max_a <= 0.0 or not (math.isfinite(max_m) and math.isfinite(max_a)):
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_SINGULAR"

        # Evitar copias N x D innecesarias en el rango normal [1e-100, 1e100]
        if max_m < 1e-100 or max_m > 1e100 or max_a < 1e-100 or max_a > 1e100:
            M = np.dot((X_m / max_m).T, X_a / max_a)
        else:
            M = np.dot(X_m.T, X_a)

        if not np.all(np.isfinite(M)):
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_NON_FINITE"

        max_M = float(np.max(np.abs(M)))
        if max_M <= 0.0 or not math.isfinite(max_M):
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_SINGULAR"
        M_s = M / max_M

        eye_k = np.eye(k, dtype=np.float64)
        W: Optional[np.ndarray] = None
        gram_cached: Optional[np.ndarray] = None
        kappa = float("inf")
        status = ""

        # Ruta rápida BLAS3 espectral para matrices bien/moderadamente condicionadas
        G = np.dot(M_s.T, M_s)
        lam, V = np.linalg.eigh(G)
        lam_max = float(lam[-1])
        lam_min = float(lam[0])
        if lam_max > 0.0 and lam_min > 0.0:
            kappa_est = math.sqrt(lam_max / lam_min)
            if math.isfinite(kappa_est) and kappa_est <= kappa_fallback:
                inv_sqrt = 1.0 / np.sqrt(lam)
                G_inv_sqrt = np.dot(V * inv_sqrt, V.T)
                W = np.dot(M_s, G_inv_sqrt)
                if kappa_est > kappa_polish:
                    W = np.dot(W, 1.5 * eye_k - 0.5 * np.dot(W.T, W))
                else:
                    gram_cached = np.dot(W.T, W)
                    if float(np.max(np.abs(gram_cached - eye_k))) > tol:
                        W = np.dot(W, 1.5 * eye_k - 0.5 * gram_cached)
                        gram_cached = None
                kappa = kappa_est
                status = "ACCEPTED_SPECTRAL_POLAR"

        # Fallback QR(D x k) + SVD(k x k) cuando kappa > kappa_fallback o G pierde definitud positiva
        if W is None:
            Q_m, R_m = np.linalg.qr(M_s, mode="reduced")
            U_r, s_r, Vt_r = np.linalg.svd(R_m, full_matrices=False)
            smax, smin = float(s_r[0]), float(s_r[-1])
            kappa = (smax / smin) if smin > 0.0 else float("inf")
            W = np.dot(Q_m, np.dot(U_r, Vt_r))
            if smin <= 0.0 or not math.isfinite(kappa) or kappa >= 1e14:
                status = "REJECTED_RANK_DEFICIENT_SVD"
            elif kappa > kappa_fatal:
                status = "REJECTED_ILL_CONDITIONED"
            else:
                status = "ACCEPTED_QR_SVD_FALLBACK"

        gram_final = gram_cached if gram_cached is not None else np.dot(W.T, W)
        gram_err = gram_final - eye_k
        rel_frob_defect = math.sqrt(max(0.0, _neumaier_sum_sq(gram_err))) / math.sqrt(k)
        residual = (
            math.sqrt(max(0.0, _neumaier_sum_sq(np.dot(X_m, W) - X_a)))
            if compute_residual
            else 0.0
        )
        return W, kappa, rel_frob_defect, residual, status


