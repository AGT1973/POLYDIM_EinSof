# -*- coding: utf-8 -*-
"""
PMTP Shared KV-Cache Bridge & Dynamics-Aware Manifold Alignment
===============================================================
Transfers KV-cache across agents without 1D re-tokenization while preventing
RMSNorm saturation in 4-bit NF4 quantized models via Dynamics-Aware Scale
Normalization + Order-4 Stiefel Key retraction.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from .stiefel_riemannian import project_stiefel_polar_order4

try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    torch = None
    _TORCH_AVAILABLE = False


class PmtpSharedKVCacheBridge:
    """Shared KV-Cache bridge for cascaded zero-copy multi-agent inference."""

    def __init__(
        self,
        num_layers: int = 28,
        num_heads: int = 16,
        head_dim: int = 128,
        enable_stiefel_keys: bool = True,
        quantization_aware: bool = True,
    ):
        self.num_layers = int(num_layers)
        self.num_heads = int(num_heads)
        self.head_dim = int(head_dim)
        self.enable_stiefel_keys = bool(enable_stiefel_keys)
        self.quantization_aware = bool(quantization_aware)

    @staticmethod
    def align_tensor_dynamics(tensor: np.ndarray, target_scale: float = 1.0) -> Tuple[np.ndarray, float]:
        """
        Normalizes tensor dispersion to target_scale to prevent 4-bit NF4/int4 block
        quantization overflow and RMSNorm saturation.
        Returns (scaled_tensor, applied_scale).
        """
        arr = np.asarray(tensor, dtype=np.float64)
        std = float(np.std(arr))
        if std > 1e-7:
            scale = float(target_scale) / std
            return arr * scale, scale
        return arr, 1.0

    def export_kv_state(self, past_key_values: Any) -> Dict[str, Any]:
        """Exports DynamicCache or tuple (key, value) layers with optional NF4 normalization & Stiefel retraction."""
        exported_layers = []
        if hasattr(past_key_values, "key_cache") and hasattr(past_key_values, "value_cache"):
            for k, v in zip(past_key_values.key_cache, past_key_values.value_cache):
                k_np = k.detach().cpu().numpy() if (_TORCH_AVAILABLE and isinstance(k, torch.Tensor)) else np.asarray(k)
                v_np = v.detach().cpu().numpy() if (_TORCH_AVAILABLE and isinstance(v, torch.Tensor)) else np.asarray(v)
                exported_layers.append((k_np, v_np))
        elif isinstance(past_key_values, (tuple, list)):
            for layer in past_key_values:
                k, v = layer[0], layer[1]
                k_np = k.detach().cpu().numpy() if (_TORCH_AVAILABLE and isinstance(k, torch.Tensor)) else np.asarray(k)
                v_np = v.detach().cpu().numpy() if (_TORCH_AVAILABLE and isinstance(v, torch.Tensor)) else np.asarray(v)
                exported_layers.append((k_np, v_np))
        else:
            raise ValueError("Unrecognized past_key_values format.")

        processed_layers = []
        max_key_defect = 0.0
        for k_mat, v_mat in exported_layers:
            if self.quantization_aware:
                k_mat, _ = self.align_tensor_dynamics(k_mat, target_scale=1.0)
                v_mat, _ = self.align_tensor_dynamics(v_mat, target_scale=1.0)
            else:
                k_mat = np.asarray(k_mat, dtype=np.float64)
                v_mat = np.asarray(v_mat, dtype=np.float64)

            if self.enable_stiefel_keys and k_mat.ndim >= 2:
                orig_shape = k_mat.shape
                flat_k = k_mat.reshape(-1, orig_shape[-1])
                if min(flat_k.shape) >= 2:
                    retracted_k, defect = project_stiefel_polar_order4(flat_k)
                    max_key_defect = max(max_key_defect, defect)
                    k_mat = retracted_k.reshape(orig_shape)

            processed_layers.append((k_mat, v_mat))

        return {
            "format": "PMTP_SHARED_KV_CACHE_V2_2027",
            "num_layers": len(processed_layers),
            "layers": processed_layers,
            "max_stiefel_key_defect": max_key_defect,
            "quantization_aware": self.quantization_aware,
        }

    def import_kv_state(self, payload: Dict[str, Any], device: str = "cpu", dtype: Any = None) -> Any:
        """Reconstructs tuple of (key, value) tensors for model.generate(past_key_values=...)."""
        if not _TORCH_AVAILABLE:
            return payload["layers"]
        if dtype is None:
            dtype = torch.float32
        imported = []
        for k_np, v_np in payload["layers"]:
            imported.append((
                torch.from_numpy(np.asarray(k_np)).to(device=device, dtype=dtype),
                torch.from_numpy(np.asarray(v_np)).to(device=device, dtype=dtype),
            ))
        return tuple(imported)
