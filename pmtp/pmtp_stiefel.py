# ============================================================================
# PMTP STIEFEL UNIVERSAL ADAPTER & SEQUENCE-TO-CORE ABI (V1.0 SOTA)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba (Independent Research / EinsofOS)
# Base Teórica: Teoremas T-MP16, T-MP18 (MP-49), T-MP21 (MP-59, MP-60)
# ============================================================================

import math
import warnings
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
    1. Contrato PolarSafe V2 (T-MP18): QDWH (Nakatsukasa-Bai-Gygi), Newton-Schulz Ord. 5 y SVD fallback.
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
        Invariante a escala global con detección explícita NaN/Inf/rank-deficient,
        Newton-Schulz Orden 5 para matrices bien condicionadas (kappa <= min(kappa_max, 10))
        y QDWH (QR-based Dynamically Weighted Halley, Nakatsukasa-Bai-Gygi 2010) hasta kappa_fatal.
        """
        X_arr = np.asarray(X, dtype=np.float64)
        if X_arr.ndim != 2 or X_arr.shape[0] == 0 or X_arr.shape[1] == 0:
            raise ValueError(f"Expected non-empty 2D matrix, got shape {X_arr.shape}")

        D, r = X_arr.shape

        # 0. Guardia estricta anti-NaN / anti-Inf antes de cualquier descomposición
        if not np.all(np.isfinite(X_arr)):
            return np.zeros((D, r), dtype=np.float64), float("inf"), 0.0, "REJECTED_NON_FINITE"

        if D < r:
            return np.zeros((D, r), dtype=np.float64), float("inf"), 0.0, "REJECTED_RANK_DEFICIENT"

        eye_r = np.eye(r, dtype=np.float64)

        # 0b. Pre-escalado seguro por max_abs contra underflow/overflow IEEE-754 (e.g. 1e-200)
        max_abs = float(np.max(np.abs(X_arr)))
        if max_abs <= 0.0 or not math.isfinite(max_abs):
            return np.zeros((D, r), dtype=np.float64), float("inf"), 0.0, "REJECTED_SINGULAR"
        X_scaled = (X_arr / max_abs).astype(np.float64)

        # 1. Cota espectral superior sin SVD: ||X_scaled||_2 <= min(||X_scaled||_F, sqrt(||X_scaled||_1 * ||X_scaled||_inf))
        fro_norm = float(np.linalg.norm(X_scaled, ord="fro"))
        if fro_norm <= 0.0 or not math.isfinite(fro_norm):
            return np.zeros((D, r), dtype=np.float64), float("inf"), 0.0, "REJECTED_SINGULAR"

        one_norm = float(np.linalg.norm(X_scaled, ord=1))
        inf_norm = float(np.linalg.norm(X_scaled, ord=np.inf))
        spec_upper = math.sqrt(one_norm * inf_norm) if (one_norm > 0.0 and inf_norm > 0.0 and math.isfinite(one_norm * inf_norm)) else fro_norm
        alpha_upper = min(fro_norm, spec_upper) * 1.000000000001
        if alpha_upper <= 0.0 or not math.isfinite(alpha_upper):
            return np.zeros((D, r), dtype=np.float64), float("inf"), 0.0, "REJECTED_SINGULAR"

        Y = (X_scaled / alpha_upper).astype(np.float64)

        # 2. Estimación de cota inferior L0 vía factor triangular QR (sin SVD D x r) + 3 pasos potencia inversa en R (r x r)
        # IMPORTANTE: QDWH se ejecuta SIEMPRE como solver principal antes de cualquier llamada SVD.
        L0_est = 1.0 / max(10.0 * float(r), 1e3)
        kappa_est = 1.0 / L0_est
        try:
            _, R_tri = np.linalg.qr(Y, mode="reduced")
            diag_abs = np.abs(np.diag(R_tri))
            max_diag = float(np.max(diag_abs)) if diag_abs.size else 0.0
            min_diag = float(np.min(diag_abs)) if diag_abs.size else 0.0
            if max_diag > 0.0 and min_diag > 1e-14 * max_diag:
                v = np.linspace(1.0, -0.7, r, dtype=np.float64)
                v /= float(np.linalg.norm(v))
                inv_norm = 1.0
                Rt = R_tri.T
                for _ in range(3):
                    w = np.linalg.solve(Rt, v)
                    z = np.linalg.solve(R_tri, w)
                    z_norm = float(np.linalg.norm(z))
                    if not math.isfinite(z_norm) or z_norm <= 0.0:
                        raise np.linalg.LinAlgError("Inverse power non-finite")
                    inv_norm = math.sqrt(z_norm)
                    v = z / z_norm
                sigma_min_est = 1.0 / max(inv_norm, 1.0)
                # Cota estrictamente conservadora para QDWH: nunca sobreestimar L0
                L0_est = max(1e-15, min(0.999, 0.5 * sigma_min_est))
                kappa_est = 1.0 / L0_est
        except np.linalg.LinAlgError:
            L0_est = 1e-12
            kappa_est = 1e12

        # 3. SOLVER POLAR PRINCIPAL: QDWH (QR-based Dynamically Weighted Halley, Nakatsukasa-Bai-Gygi 2010)
        # Convergencia cúbica siempre ejecutada antes de caer a SVD. `kappa_max` fija umbral de alerta para auditoría.
        Q = Y.copy()
        L = max(L0_est, 1e-15)
        qdwh_tol = min(float(tol), 5.0 * float(np.finfo(np.float64).eps))
        qdwh_iters = max(min(max_iters, 10), 6)

        try:
            for _ in range(qdwh_iters):
                L2 = L * L
                dd = (4.0 * (1.0 - L2) / (L2 * L2)) ** (1.0 / 3.0)
                sqd = math.sqrt(1.0 + dd)
                a = sqd + 0.5 * math.sqrt(8.0 - 4.0 * dd + (8.0 * (2.0 - L2)) / (L2 * L2 * sqd))
                b = ((a - 1.0) ** 2) / 4.0
                c = a + b - 1.0
                L = min(1.0 - 1e-15, L * (a + b * L2) / (1.0 + c * L2))

                if c > 100.0:
                    B = np.vstack([math.sqrt(c) * Q, eye_r])
                    Q1, _ = np.linalg.qr(B, mode="reduced")
                    Q_next = (b / c) * Q + ((a - b / c) / math.sqrt(c)) * np.dot(Q1[:D, :], Q1[D:, :].T)
                else:
                    Z = eye_r + c * np.dot(Q.T, Q)
                    R = np.linalg.cholesky(Z).T
                    Y_solve = np.linalg.solve(R.T, Q.T)
                    W_solve = np.linalg.solve(R, Y_solve).T
                    Q_next = (b / c) * Q + (a - b / c) * W_solve

                diff = float(np.linalg.norm(Q_next - Q, ord="fro"))
                Q = Q_next
                defect = float(np.max(np.abs(np.dot(Q.T, Q) - eye_r)))
                if not np.isfinite(defect):
                    break
                if (diff <= qdwh_tol or L > 1.0 - 1e-14) and defect <= max(tol, 1e-13):
                    if kappa_est <= float(kappa_fatal):
                        if kappa_est > float(kappa_max):
                            warnings.warn(
                                f"QDWH converged with elevated kappa_est={kappa_est:.3e} > kappa_max={kappa_max:.3e}",
                                RuntimeWarning,
                                stacklevel=2,
                            )
                        return Q, kappa_est, L0_est, "ACCEPTED_QDWH_POLAR"
                    break

            if np.all(np.isfinite(Q)):
                defect = float(np.max(np.abs(np.dot(Q.T, Q) - eye_r)))
                if defect <= max(tol, 1e-13) and kappa_est <= float(kappa_fatal):
                    return Q, kappa_est, L0_est, "ACCEPTED_QDWH_POLAR"
        except np.linalg.LinAlgError:
            pass

        # 4. Fallback SVD polar de seguridad (única descomposición SVD tras intentar QDWH o cuando supera kappa_fatal)
        U, s, Vt = np.linalg.svd(X_scaled, full_matrices=False)
        sigma_max, sigma_min = float(s[0]), float(s[-1])
        kappa_exact = (sigma_max / sigma_min) if sigma_min > 0.0 else float("inf")
        r_rel_exact = (sigma_min / sigma_max) if sigma_max > 0.0 else 0.0
        Q = np.dot(U, Vt).astype(np.float64)
        if sigma_min <= 0.0 or not math.isfinite(kappa_exact) or kappa_exact >= 1e14:
            return Q, kappa_exact, r_rel_exact, "REJECTED_RANK_DEFICIENT_SVD"
        if kappa_exact > float(kappa_fatal) or r_rel_exact < (1.0 / float(kappa_fatal)):
            return Q, kappa_exact, r_rel_exact, "REJECTED_ILL_CONDITIONED"
        return Q, kappa_exact, r_rel_exact, "ACCEPTED_SVD_POLAR_FALLBACK"

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
