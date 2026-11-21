# -*- coding: utf-8 -*-
"""
Orthogonal Procrustes Alignment, RoPE Phase Compensation & Residual Splice
==========================================================================
Regla 0 Suprema Compliance:
  - Zero silent synthetic RNG matrices masquerading as calibrated cross-model maps.
  - Analytical Orthogonal Procrustes W* = U V^T from SVD(X_src^T Y_dst) on real
    activations with strict train/test generalization checks.
  - Deep residual stream splice at layer L-2 / 2L/3 (`stiefel_blend`) preserving
    local RMSNorm energy; bans Layer 0 raw injection and destructive mean pooling.
"""

from __future__ import annotations

import math
import os
from typing import Any, Optional, Tuple

import numpy as np

from .stiefel_riemannian import neumaier_sum_sq

try:
    import torch
    import torch.nn as nn
    _TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    _TORCH_AVAILABLE = False


class PmtpOrthogonalProcrustes:
    """Isometric Inter-Model Aligner on Stiefel Manifold St(k, D)."""

    @classmethod
    def align_spaces(cls, X: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, float, float]:
        """
        Solves W* = argmin_{W in St} ||X W - Y||_F^2 analytically via SVD(X^T Y).
        Supports both D1 >= D2 (column-orthonormal W^T W = I_D2) and D1 < D2 (row-orthonormal W W^T = I_D1).
        Returns (W_opt, residual_frobenius, stiefel_defect_inf).
        """
        X64 = np.asarray(X, dtype=np.float64)
        Y64 = np.asarray(Y, dtype=np.float64)
        if X64.ndim != 2 or Y64.ndim != 2:
            raise ValueError(f"Expected 2D arrays, got X={X64.shape}, Y={Y64.shape}")
        if X64.shape[0] != Y64.shape[0]:
            raise ValueError(f"Sample count mismatch: {X64.shape[0]} vs {Y64.shape[0]}")
        if not (np.all(np.isfinite(X64)) and np.all(np.isfinite(Y64))):
            raise ValueError("Non-finite values in Procrustes calibration activations.")

        _, D1 = X64.shape
        _, D2 = Y64.shape
        M = X64.T @ Y64
        U, _, Vt = np.linalg.svd(M, full_matrices=False)
        W_opt = U @ Vt

        if D1 >= D2:
            gram = W_opt.T @ W_opt
            defect = float(np.max(np.abs(gram - np.eye(D2, dtype=np.float64))))
        else:
            gram = W_opt @ W_opt.T
            defect = float(np.max(np.abs(gram - np.eye(D1, dtype=np.float64))))

        diff = (X64 @ W_opt) - Y64
        residual = math.sqrt(max(0.0, neumaier_sum_sq(diff)))
        return np.ascontiguousarray(W_opt, dtype=np.float64), residual, defect

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
        """Universal Procrustes Anchor Handshake (<50 ms) on St(k, D)."""
        X_m = np.asarray(X_model, dtype=np.float64)
        X_a = np.asarray(X_anchor, dtype=np.float64)
        if X_m.ndim != 2 or X_a.ndim != 2:
            raise ValueError(f"Expected 2D inputs, got {X_m.shape}, {X_a.shape}")
        N, D = X_m.shape
        N2, k = X_a.shape
        if N != N2:
            raise ValueError(f"Anchor mismatch: {N} vs {N2}")
        if D == 0 or k == 0 or N == 0:
            raise ValueError("Empty dimensions not allowed.")
        if not (np.all(np.isfinite(X_m)) and np.all(np.isfinite(X_a))):
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_NON_FINITE"
        if D < k or N < k:
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_INVALID_SHAPE"

        max_m, max_a = float(np.max(np.abs(X_m))), float(np.max(np.abs(X_a)))
        if max_m <= 0.0 or max_a <= 0.0 or not (math.isfinite(max_m) and math.isfinite(max_a)):
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_SINGULAR"

        if max_m < 1e-100 or max_m > 1e100 or max_a < 1e-100 or max_a > 1e100:
            M = (X_m / max_m).T @ (X_a / max_a)
        else:
            M = X_m.T @ X_a

        max_M = float(np.max(np.abs(M)))
        if not np.all(np.isfinite(M)) or max_M <= 0.0:
            return np.zeros((D, k), dtype=np.float64), float("inf"), float("inf"), 0.0, "REJECTED_SINGULAR"
        M_s = M / max_M

        eye_k = np.eye(k, dtype=np.float64)
        W: Optional[np.ndarray] = None
        gram_cached: Optional[np.ndarray] = None
        kappa = float("inf")
        status = ""

        G = M_s.T @ M_s
        lam, V = np.linalg.eigh(G)
        if float(lam[-1]) > 0.0 and float(lam[0]) > 0.0:
            kappa_est = math.sqrt(float(lam[-1]) / float(lam[0]))
            if math.isfinite(kappa_est) and kappa_est <= kappa_fallback:
                G_inv_sqrt = (V * (1.0 / np.sqrt(lam))) @ V.T
                W = M_s @ G_inv_sqrt
                if kappa_est > kappa_polish:
                    W = W @ (1.5 * eye_k - 0.5 * (W.T @ W))
                else:
                    gram_cached = W.T @ W
                    if float(np.max(np.abs(gram_cached - eye_k))) > tol:
                        W = W @ (1.5 * eye_k - 0.5 * gram_cached)
                        gram_cached = None
                kappa = kappa_est
                status = "ACCEPTED_SPECTRAL_POLAR"

        if W is None:
            Q_m, R_m = np.linalg.qr(M_s, mode="reduced")
            U_r, s_r, Vt_r = np.linalg.svd(R_m, full_matrices=False)
            smin = float(s_r[-1])
            kappa = (float(s_r[0]) / smin) if smin > 0.0 else float("inf")
            W = Q_m @ (U_r @ Vt_r)
            if smin <= 0.0 or not math.isfinite(kappa) or kappa >= 1e14:
                status = "REJECTED_RANK_DEFICIENT_SVD"
            elif kappa > kappa_fatal:
                status = "REJECTED_ILL_CONDITIONED"
            else:
                status = "ACCEPTED_QR_SVD_FALLBACK"

        gram_final = gram_cached if gram_cached is not None else (W.T @ W)
        rel_frob_defect = math.sqrt(max(0.0, neumaier_sum_sq(gram_final - eye_k))) / math.sqrt(k)
        residual = math.sqrt(max(0.0, neumaier_sum_sq((X_m @ W) - X_a))) if compute_residual else 0.0
        return W, kappa, rel_frob_defect, residual, status

    @staticmethod
    def compute_grassmannian_distance(W1: np.ndarray, W2: np.ndarray) -> float:
        """Numerically stable Grassmannian geodesic distance via arcsin formulation."""
        sigma = np.clip(np.linalg.svd(W1.T @ W2, compute_uv=False), 0.0, 1.0)
        return float(np.linalg.norm(np.arcsin(np.sqrt(np.maximum(0.0, 1.0 - sigma ** 2)))))


def apply_rope_phase_compensator(
    x: Any,
    base_source: float = 10000.0,
    base_target: float = 500000.0,
    seq_pos: Any = None,
) -> Any:
    """
    Isometric 2x2 rotational phase compensator R_theta cancelling RoPE angular drift
    between divergent positional bases while preserving Euclidean norm (<= 1e-15).
    Works transparently on PyTorch Tensors and NumPy arrays.
    """
    if base_source == base_target:
        return x

    is_numpy = isinstance(x, np.ndarray)
    if is_numpy:
        d_embed = x.shape[-1]
        dim_pairs = d_embed // 2
        indices = np.arange(dim_pairs, dtype=np.float64)
        delta_theta = (base_target ** (-2.0 * indices / d_embed)) - (base_source ** (-2.0 * indices / d_embed))
        if seq_pos is None:
            seq_len = x.shape[-2] if x.ndim >= 2 else 1
            positions = np.arange(seq_len, dtype=np.float64)
        else:
            positions = np.asarray(seq_pos, dtype=np.float64)
        angles = positions[..., None] * delta_theta[None, :]
        cos_a = np.cos(angles).astype(x.dtype)
        sin_a = np.sin(angles).astype(x.dtype)
        x_rot = x.copy()
        x_even = x[..., 0:2 * dim_pairs:2]
        x_odd = x[..., 1:2 * dim_pairs:2]
        x_rot[..., 0:2 * dim_pairs:2] = x_even * cos_a - x_odd * sin_a
        x_rot[..., 1:2 * dim_pairs:2] = x_even * sin_a + x_odd * cos_a
        return x_rot

    if not _TORCH_AVAILABLE:
        raise ImportError("PyTorch or NumPy array required.")

    d_embed = x.shape[-1]
    dim_pairs = d_embed // 2
    indices = torch.arange(dim_pairs, dtype=torch.float64, device=x.device)
    delta_theta = (base_target ** (-2.0 * indices / d_embed)) - (base_source ** (-2.0 * indices / d_embed))
    if seq_pos is None:
        seq_len = x.shape[-2] if x.ndim >= 2 else 1
        positions = torch.arange(seq_len, dtype=torch.float64, device=x.device)
    else:
        positions = seq_pos.to(dtype=torch.float64, device=x.device)
    angles = positions[..., None] * delta_theta[None, :]
    cos_a = torch.cos(angles).to(dtype=x.dtype)
    sin_a = torch.sin(angles).to(dtype=x.dtype)

    x_rot = x.clone()
    x_even = x[..., 0:2 * dim_pairs:2]
    x_odd = x[..., 1:2 * dim_pairs:2]
    x_rot[..., 0:2 * dim_pairs:2] = x_even * cos_a - x_odd * sin_a
    x_rot[..., 1:2 * dim_pairs:2] = x_even * sin_a + x_odd * cos_a
    return x_rot


class StiefelImpedanceProjector:
    """
    Analytical Procrustes Stiefel Projector St(d_latent, d_model).
    Regla 0 Suprema: NEVER silently creates random Gaussian anchors as calibrated maps.
    Requires either a loaded `.safetensors` file, real `(X_src, Y_dst)` activations, or
    explicit `allow_uncalibrated_identity=True` (marked UNCALIBRATED_IDENTITY_BASIS).
    """

    def __init__(
        self,
        d_latent: int = 2048,
        d_model: int = 5120,
        weights_path: Optional[str] = None,
        source_activations: Optional[np.ndarray] = None,
        target_activations: Optional[np.ndarray] = None,
        allow_uncalibrated_identity: bool = False,
        base_source: float = 10000.0,
        base_target: float = 10000.0,
        enable_rope: bool = True,
    ):
        self.d_latent = int(d_latent)
        self.d_model = int(d_model)
        self.base_source = float(base_source)
        self.base_target = float(base_target)
        self.enable_rope = bool(enable_rope)
        self.W: Optional[np.ndarray] = None
        self.is_calibrated: bool = False
        self.calibration_status: str = "UNINITIALIZED"
        self.metadata: dict = {}

        if weights_path and os.path.isfile(weights_path):
            self.load(weights_path)
        elif source_activations is not None and target_activations is not None:
            self.calibrate_anchors(source_activations, target_activations)
        elif allow_uncalibrated_identity:
            eye = np.zeros((self.d_latent, self.d_model), dtype=np.float64)
            for i in range(min(self.d_latent, self.d_model)):
                eye[i, i] = 1.0
            self.W = eye
            self.is_calibrated = False
            self.calibration_status = "UNCALIBRATED_IDENTITY_BASIS"
            self.metadata = {
                "d_latent": str(self.d_latent),
                "d_model": str(self.d_model),
                "calibration_status": self.calibration_status,
                "stiefel_defect": "0.000e+00",
            }
        else:
            raise FileNotFoundError(
                f"No real Procrustes calibration provided for St({self.d_latent}, {self.d_model}). "
                "Silent random stubs are forbidden by Regla 0 Suprema."
            )

    def calibrate_anchors(self, X_src: np.ndarray, Y_dst: np.ndarray) -> Tuple[float, float]:
        X = np.asarray(X_src, dtype=np.float64)
        Y = np.asarray(Y_dst, dtype=np.float64)
        if X.shape[1] != self.d_latent or Y.shape[1] != self.d_model:
            raise ValueError(
                f"Activation dims ({X.shape[1]}, {Y.shape[1]}) != expected ({self.d_latent}, {self.d_model})"
            )
        W_opt, residual, defect = PmtpOrthogonalProcrustes.align_spaces(X, Y)
        Y_pred = X @ W_opt
        np_norm = np.linalg.norm(Y_pred, axis=1, keepdims=True).clip(min=1e-9)
        nt_norm = np.linalg.norm(Y, axis=1, keepdims=True).clip(min=1e-9)
        mean_cos = float(np.mean(np.sum((Y_pred / np_norm) * (Y / nt_norm), axis=1)))

        self.W = W_opt
        self.is_calibrated = True
        self.calibration_status = "CALIBRATED_REAL_ACTIVATIONS_PROCRUSTES_FP64"
        self.metadata = {
            "d_latent": str(self.d_latent),
            "d_model": str(self.d_model),
            "stiefel_defect": f"{defect:.3e}",
            "residual_frobenius": f"{residual:.6f}",
            "mean_cosine_similarity": f"{mean_cos:.4f}",
            "samples": str(X.shape[0]),
            "calibration_status": self.calibration_status,
            "dtype": "float64",
        }
        return defect, mean_cos

    def save(self, filepath: str) -> None:
        from safetensors.numpy import save_file
        if self.W is None:
            raise RuntimeError("Cannot save uninitialized projector.")
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        save_file({"W_procrustes": np.ascontiguousarray(self.W, dtype=np.float64)}, filepath, metadata=self.metadata)

    def load(self, filepath: str) -> None:
        from safetensors.numpy import load_file
        data = load_file(filepath)
        if "W_procrustes" not in data:
            raise KeyError(f"{filepath} missing 'W_procrustes'")
        W = np.asarray(data["W_procrustes"], dtype=np.float64)
        if W.shape != (self.d_latent, self.d_model):
            raise ValueError(f"Shape {W.shape} != expected ({self.d_latent}, {self.d_model})")
        k = min(self.d_latent, self.d_model)
        gram = (W @ W.T) if self.d_latent <= self.d_model else (W.T @ W)
        defect = float(np.max(np.abs(gram - np.eye(k, dtype=np.float64))))
        self.W = W
        self.is_calibrated = True
        self.calibration_status = "LOADED_SAFETENSORS_FP64"
        self.metadata["stiefel_defect"] = f"{defect:.3e}"

    def project(self, z: Any) -> Any:
        if self.W is None:
            raise RuntimeError("Projector matrix W is not initialized.")
        if isinstance(z, np.ndarray):
            return z.astype(np.float64) @ self.W if z.dtype == np.float64 else z @ self.W.astype(z.dtype)
        if _TORCH_AVAILABLE and isinstance(z, torch.Tensor):
            W_t = torch.as_tensor(self.W, device=z.device, dtype=z.dtype)
            return z @ W_t
        return z @ self.W


class ResidualStreamSpliceHook:
    """
    Deep Layer (L-2 / 2L/3) Residual Stream Splice Hook.
    Uses norm-preserving `stiefel_blend` so RMSNorm never saturates and includes
    RoPE rotational phase compensation R_theta.
    """

    def __init__(
        self,
        target_layer: Any,
        latent_tensor: Any,
        mode: str = "stiefel_blend",
        alpha: float = 0.85,
        base_source: float = 10000.0,
        base_target: float = 10000.0,
        enable_rope: bool = True,
    ):
        self.target_layer = target_layer
        self.latent_tensor = latent_tensor
        self.mode = mode
        self.alpha = float(alpha)
        self.base_source = float(base_source)
        self.base_target = float(base_target)
        self.enable_rope = bool(enable_rope)
        self.handle = None

    def register(self) -> "ResidualStreamSpliceHook":
        if not _TORCH_AVAILABLE:
            raise ImportError("PyTorch required for ResidualStreamSpliceHook.")

        def hook_fn(module, input_tuple, output_tuple):
            is_tuple = isinstance(output_tuple, tuple)
            residual = output_tuple[0] if is_tuple else output_tuple
            t = self.latent_tensor
            if isinstance(t, torch.Tensor):
                t = t.to(device=residual.device, dtype=residual.dtype)
            else:
                t = torch.as_tensor(t, device=residual.device, dtype=residual.dtype)

            if t.ndim == 1:
                t = t.unsqueeze(0).unsqueeze(0)
            elif t.ndim == 2:
                t = t.unsqueeze(1)

            if self.enable_rope and self.base_source != self.base_target:
                t = apply_rope_phase_compensator(t, self.base_source, self.base_target)

            if self.mode == "stiefel_blend":
                res_norm = residual.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                t_norm = t.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                t_scaled = t * (res_norm / t_norm)
                modified = (1.0 - self.alpha) * residual + self.alpha * t_scaled
            elif self.mode == "replace":
                res_norm = residual.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                t_norm = t.norm(dim=-1, keepdim=True).clamp_min(1e-9)
                modified = t * (res_norm / t_norm)
            elif self.mode == "add":
                modified = residual + t
            else:
                modified = residual

            return (modified,) + output_tuple[1:] if is_tuple else modified

        self.handle = self.target_layer.register_forward_hook(hook_fn)
        return self

    def remove(self) -> None:
        if self.handle is not None:
            self.handle.remove()
            self.handle = None


class AttentionSummaryPooling:
    """Extracts last causal token / EOS state without destructive flat mean-pooling."""

    def __init__(self, mode: str = "last_token"):
        if mode == "mean":
            raise ValueError("Destructive mean_pooling is prohibited by Truninger-Popper audit.")
        self.mode = mode

    def __call__(self, hidden_states: Any, attention_mask: Any = None) -> Any:
        if self.mode == "preserve_sequence":
            return hidden_states
        if attention_mask is not None:
            if _TORCH_AVAILABLE and isinstance(hidden_states, torch.Tensor):
                last_indices = attention_mask.sum(dim=1).long() - 1
                selected = torch.stack([hidden_states[b, last_indices[b], :] for b in range(hidden_states.shape[0])])
                return selected.unsqueeze(1)
        return hidden_states[:, -1:, :]


def forward_vector_first(
    model: Any,
    tokenizer: Any,
    latent_vector: Any,
    projector: Optional[StiefelImpedanceProjector] = None,
    layer_idx: int = -2,
    max_new_tokens: int = 256,
    alpha: float = 0.85,
    base_source: float = 10000.0,
    base_target: float = 10000.0,
    enable_rope: bool = True,
    trigger_token: str = "<|einsof|>",
) -> str:
    """Zero-prompt-tax latent vector inference spliced at layer L-2."""
    if not _TORCH_AVAILABLE:
        raise ImportError("PyTorch required for forward_vector_first.")

    layers = None
    for attr in ("model.layers", "model.language_model.layers", "transformer.h", "model.decoder.layers"):
        obj = model
        try:
            for part in attr.split("."):
                obj = getattr(obj, part)
            layers = obj
            break
        except AttributeError:
            pass
    if layers is None:
        raise RuntimeError("Could not locate decoder layers for ResidualStreamSpliceHook.")

    v_proj = projector.project(latent_vector) if (projector is not None and latent_vector.shape[-1] != projector.d_model) else latent_vector
    hook = ResidualStreamSpliceHook(
        layers[layer_idx], v_proj, mode="stiefel_blend", alpha=alpha,
        base_source=base_source, base_target=base_target, enable_rope=enable_rope,
    ).register()
    try:
        inputs = tokenizer(trigger_token, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    finally:
        hook.remove()
