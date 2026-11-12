# ============================================================================
# PMTP STIEFEL UNIVERSAL ADAPTER & SEQUENCE-TO-CORE ABI (V1.0 SOTA)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba (Independent Research / EinsofOS)
# Base Teórica: Teoremas T-MP16, T-MP18 (MP-49), T-MP21 (MP-59, MP-60)
# ============================================================================

import math
from typing import Tuple, Optional, Any, Union
import numpy as np

try:
    import torch
    _HAS_TORCH = True
except ImportError:
    torch = None
    _HAS_TORCH = False

class PmtpStiefelAdapter:
    """
    Adaptador Isométrico Universal sobre la Variedad de Stiefel St(D, r) con:
    1. Contrato PolarSafe V2 (T-MP18): Invariante a escala con Newton-Schulz Orden 4 y SVD fallback.
    2. Proyección Esférica Dirección-Amplitud (u, rho) (T-MP16).
    3. ABI Neuronal Sequence-to-Core (T-MP21): Extracción e inyección en token canónico L-1.
    4. Contrato de Inmutabilidad Anti-Aliasing (MP-59).
    """
    def __init__(
        self,
        dim_source: int,
        dim_latent: int,
        seed: int = 42,
        kappa_max: float = 1e4,
        kappa_fatal: float = 1e8
    ):
        self.d_source = dim_source
        self.d_latent = min(dim_source, dim_latent)
        self.seed = seed
        self.kappa_max = kappa_max
        self.kappa_fatal = kappa_fatal

        # Inicialización y certificación de W en St(d_source, d_latent)
        rng = np.random.default_rng(seed)
        raw = rng.standard_normal((self.d_source, self.d_latent), dtype=np.float64)
        self.W, self.kappa, self.r_rel, self.status = self.polar_safe_v2(
            raw, kappa_max=kappa_max, kappa_fatal=kappa_fatal
        )
        self.W_torch = torch.from_numpy(self.W).to(torch.float32) if _HAS_TORCH else None

    @classmethod
    def polar_safe_v2(
        cls,
        X: np.ndarray,
        max_iters: int = 20,
        tol: float = 1e-13,
        kappa_max: float = 1e3,
        kappa_fatal: float = 1e8
    ) -> Tuple[np.ndarray, float, float, str]:
        """
        Contrato PolarSafe V2 (T-MP18, MP-49):
        Invariante a escala global. Evalúa el condicionamiento relativo:
        kappa_2(X) = sigma_max / sigma_min, r_rel = sigma_min / sigma_max.
        """
        D, r = X.shape
        eye_r = np.eye(r, dtype=np.float64)

        # 1. Auditoría espectral relativa
        s = np.linalg.svd(X, compute_uv=False)
        sigma_max = float(s[0])
        sigma_min = float(s[-1])

        if sigma_max <= 0.0 or not math.isfinite(sigma_max):
            return np.zeros((D, r)), float("inf"), 0.0, "REJECTED_SINGULAR"

        kappa_2 = (sigma_max / sigma_min) if sigma_min > 0.0 else float("inf")
        r_rel = (sigma_min / sigma_max) if sigma_max > 0.0 else 0.0

        # Rechazo explícito de matrices degeneradas
        if kappa_2 > kappa_fatal or r_rel < (1.0 / kappa_fatal):
            U, _, Vt = np.linalg.svd(X, full_matrices=False)
            Q = np.dot(U, Vt).astype(np.float64)
            return Q, kappa_2, r_rel, "REJECTED_ILL_CONDITIONED"

        # 2. Pre-escalado espectral exacto: Y0 = X / sigma_max con guarda de cota unitaria estricta
        Y = (X / (sigma_max * 1.000000000001)).astype(np.float64)

        # 3. Iteración acelerada Newton-Schulz Orden 5 con evaluación de Horner si kappa_2 <= kappa_max
        # Expansión binomial exacta de (I - A)^(-1/2) en torno a A = 0:
        # P(A) = I + (1/2)*A + (3/8)*A^2 + (5/16)*A^3 + (35/128)*A^4
        if kappa_2 <= kappa_max:
            for _ in range(max_iters):
                YtY = np.dot(Y.T, Y)
                A = eye_r - YtY
                max_defect = np.max(np.abs(A))
                if max_defect < tol:
                    return Y, kappa_2, r_rel, "ACCEPTED_NEWTON_SCHULZ_ORD5"
                if not np.isfinite(max_defect) or max_defect > 2.0:
                    break  # Falla de convergencia: conmutar inmediatamente a SVD fallback
                A2 = np.dot(A, A)
                A3 = np.dot(A2, A)
                A4 = np.dot(A2, A2)  # O(r^3) optimizado mediante elevación al cuadrado
                poly = eye_r + 0.5 * A + 0.375 * A2 + 0.3125 * A3 + (35.0 / 128.0) * A4
                Y = np.dot(Y, poly)

        # 4. Fallback SVD polar para condicionamiento moderado
        U, _, Vt = np.linalg.svd(X, full_matrices=False)
        Q = np.dot(U, Vt).astype(np.float64)
        return Q, kappa_2, r_rel, "ACCEPTED_SVD_POLAR_FALLBACK"

    def project_to_spherical(self, h: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Proyección con descomposición Dirección-Amplitud (u, rho) (T-MP16).
        Regularización suave C^inf para eliminar barreras de gradiente y discontinuidad en el origen (SOTA Red Team).
        """
        z_raw = np.dot(h, self.W)
        rho = float(np.linalg.norm(z_raw))
        eps_smooth = 1e-12
        rho_smooth = math.sqrt(rho * rho + eps_smooth * eps_smooth)
        u = z_raw / rho_smooth
        return u, rho

    def inject_stiefel_residual(
        self,
        h: np.ndarray,
        u_prime: np.ndarray,
        rho_prime: float,
        u_orig: np.ndarray,
        rho_orig: float,
        beta: float = 1.0,
        enabled: bool = True
    ) -> np.ndarray:
        """
        Puente Stiefel Residual con bypass exacto de identidad (T-MP16, T-MP21).
        Para beta = 0.0 o intervención nula, copia defensiva bit a bit idéntica.
        """
        if not enabled or abs(beta) == 0.0:
            return h.copy()

        z_orig = rho_orig * u_orig
        z_prime = rho_prime * u_prime
        delta_z = z_prime - z_orig

        if np.all(delta_z == 0.0):
            return h.copy()

        if not np.all(np.isfinite(delta_z)):
            raise FloatingPointError("Delta z no finito en Puente Stiefel Residual")

        delta_h = beta * np.dot(delta_z, self.W.T)
        return h + delta_h

    # ------------------------------------------------------------------------
    # ABI NEURONAL SEQUENCE-TO-CORE (T-MP21, MP-60) — DUAL-MODE (TORCH + NUMPY)
    # ------------------------------------------------------------------------
    def extract_sequence_latent(
        self,
        H: Any,
        token_pos: int = -1
    ) -> Tuple[np.ndarray, float]:
        """
        Extrae coordenadas esféricas (u, rho) a partir del tensor de activación
        tridimensional H in R^(B x L x D) del LLM, por defecto en el último token L-1.
        Soporta transparentemente torch.Tensor y np.ndarray.
        """
        if hasattr(H, "dim"):
            assert H.dim() == 3, f"H debe ser de rango 3 (B, L, D), recibido: {H.shape}"
            h_vec = H[0, token_pos, :].detach().to(torch.float64).cpu().numpy()
        else:
            assert getattr(H, "ndim", 0) == 3, f"H debe ser de rango 3 (B, L, D), recibido: {getattr(H, 'shape', None)}"
            h_vec = np.asarray(H[0, token_pos, :], dtype=np.float64)
        return self.project_to_spherical(h_vec)

    def inject_sequence_residual(
        self,
        H: Any,
        u_prime: np.ndarray,
        rho_prime: float,
        u_orig: np.ndarray,
        rho_orig: float,
        beta: float = 1.0,
        token_pos: int = -1,
        enabled: bool = True
    ) -> Any:
        """
        Inyecta la modulación latente residual exclusivamente en token_pos (L-1).
        Preserva intactos todos los tokens previos [0 ... L-2] y clona defensivamente
        para erradicar el aliasing destructivo in-place (MP-59, MP-60).
        Soporta transparentemente torch.Tensor y np.ndarray.
        """
        if not enabled or abs(beta) == 0.0:
            return H.clone() if hasattr(H, "clone") else H.copy()

        z_orig = rho_orig * u_orig
        z_prime = rho_prime * u_prime
        delta_z = z_prime - z_orig

        if np.all(delta_z == 0.0):
            return H.clone() if hasattr(H, "clone") else H.copy()

        delta_h_np = beta * np.dot(delta_z, self.W.T)
        if hasattr(H, "clone"):
            H_out = H.clone()
            delta_h_tensor = torch.from_numpy(delta_h_np).to(dtype=H.dtype, device=H.device)
            H_out[0, token_pos, :] = H_out[0, token_pos, :] + delta_h_tensor
            return H_out
        else:
            H_out = H.copy()
            H_out[0, token_pos, :] = H_out[0, token_pos, :] + delta_h_np.astype(H.dtype)
            return H_out

    def compute_orthogonality_defect(self) -> float:
        """Calcula ||W^T W - I||_inf en precisión float64."""
        gram = np.dot(self.W.T, self.W)
        eye = np.eye(self.d_latent, dtype=np.float64)
        return float(np.max(np.abs(gram - eye)))
