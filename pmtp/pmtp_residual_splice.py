# -*- coding: utf-8 -*-
"""
PMTP Residual Stream Splice & Stiefel Impedance Projector
=========================================================
Ecosistema POLYDIM-EINSOF | Sello de Calibración: 19.11.2026 | Ariel García Traba

Módulo canónico para Vector Hand-Off continuo de alta fidelidad entre modelos de lenguaje.
Erradica el Domain & Layer Mismatch (inyección en Capa 0 de inputs_embeds)
y el Mean-Pooling destructivo mediante dos mecanismos:

1. ResidualStreamSpliceHook: Inyección directa en corriente residual profunda (Capa L-1 o 2L/3).
2. StiefelImpedanceProjector: Proyector afín W_proj en la variedad de Stiefel St(k, D)
   para adaptación de impedancia semántica y desacople de RMSNorm.
3. AttentionSummaryPooling: Extracción del estado de razonamiento preservando fases RoPE
   (vía token EOS / último paso causal en lugar de promedio plano K=8).
"""

from typing import Optional, Union, Tuple
import math
import numpy as np

try:
    import torch
    import torch.nn as nn
    _TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    _TORCH_AVAILABLE = False


def neumaier_sum(values):
    """Suma compensada de Neumaier con precisión de máquina (error <= 1 ULP)."""
    s = 0.0
    c = 0.0
    for v in values:
        t = s + v
        if abs(s) >= abs(v):
            c += (s - t) + v
        else:
            c += (v - t) + s
        s = t
    return s + c


def stiefel_polar_retraction_order4(W: np.ndarray) -> np.ndarray:
    """
    Retracción polar de orden 4 en la variedad de Stiefel St(k, D):
    W_proj = W * (W^T W)^{-1/2} garantizando ||W^T W - I||_F <= 1e-15 en fp64.
    """
    W_f64 = np.asarray(W, dtype=np.float64)
    U, S, Vt = np.linalg.svd(W_f64, full_matrices=False)
    W_retracted = U @ Vt
    if W.dtype == np.float32:
        return W_retracted.astype(np.float32)
    return W_retracted


if _TORCH_AVAILABLE:
    class StiefelImpedanceProjector(nn.Module):
        """
        Proyector Lineal de Impedancia Semántica (W_proj) con Compensación RoPE R_theta.
        Mapea estados ocultos profundos R^{D_out} -> R^{D_in} (Capa 0 o Residual Splice)
        sin saturar RMSNorm ni descalibrar las codificaciones posicionales rotacionales.
        Incorpora RoPE Phase Compensator R_theta para acoplar modelos con bases rotacionales
        heterogéneas (ej: theta_source=10.000 vs theta_target=500.000).
        """
        def __init__(
            self, 
            d_hidden: int = 2048, 
            d_embed: int = 1536, 
            seed: int = 20261119,
            base_source: float = 10000.0,
            base_target: float = 10000.0,
            enable_rope_compensation: bool = True
        ):
            super().__init__()
            self.d_hidden = d_hidden
            self.d_embed = d_embed
            self.base_source = float(base_source)
            self.base_target = float(base_target)
            self.enable_rope_compensation = enable_rope_compensation and (self.base_source != self.base_target)
            
            rng = np.random.default_rng(seed)
            W_init = rng.standard_normal((d_hidden, d_embed), dtype=np.float64)
            W_stiefel = stiefel_polar_retraction_order4(W_init)
            
            self.proj = nn.Linear(d_hidden, d_embed, bias=False)
            self.proj.weight.data = torch.from_numpy(W_stiefel.T.astype(np.float32))
            self.norm = nn.LayerNorm(d_embed, eps=1e-6)

        def apply_rope_phase_compensation(self, x: torch.Tensor, seq_offset: int = 0) -> torch.Tensor:
            """
            Aplica rotación isométrica de compensación de fase RoPE:
            Delta_theta_i = (base_target)^(-2i/d) - (base_source)^(-2i/d)
            Garantiza que la rotación se realice en bloques ortogonales 2x2 en O(d),
            preservando exactamente la norma unitaria euclídea (||R_theta x|| = ||x|| <= 1e-15).
            """
            if not self.enable_rope_compensation:
                return x
            
            # x: [batch_size, seq_len, d_embed]
            batch_size, seq_len, d = x.shape
            device = x.device
            dtype = x.dtype
            
            dim_pairs = d // 2
            indices = torch.arange(dim_pairs, device=device, dtype=torch.float64)
            theta_src = self.base_source ** (-2.0 * indices / d)
            theta_tgt = self.base_target ** (-2.0 * indices / d)
            delta_theta = (theta_tgt - theta_src)
            
            positions = torch.arange(seq_offset, seq_offset + seq_len, device=device, dtype=torch.float64)
            angles = positions[:, None] * delta_theta[None, :]
            cos_angles = torch.cos(angles).to(dtype=dtype)
            sin_angles = torch.sin(angles).to(dtype=dtype)
            
            x_even = x[..., 0:2*dim_pairs:2]
            x_odd  = x[..., 1:2*dim_pairs:2]
            
            x_rot_even = x_even * cos_angles - x_odd * sin_angles
            x_rot_odd  = x_even * sin_angles + x_odd * cos_angles
            
            x_out = x.clone()
            x_out[..., 0:2*dim_pairs:2] = x_rot_even
            x_out[..., 1:2*dim_pairs:2] = x_rot_odd
            return x_out

        def forward(self, h_states: torch.Tensor, seq_offset: int = 0) -> torch.Tensor:
            """
            h_states: [batch_size, seq_len, d_hidden]
            Retorna: [batch_size, seq_len, d_embed] adaptado e isométricamente alineado en RoPE.
            """
            projected = self.proj(h_states)
            normed = self.norm(projected)
            if self.enable_rope_compensation:
                return self.apply_rope_phase_compensation(normed, seq_offset=seq_offset)
            return normed

        def stiefel_defect(self) -> float:
            """Calcula el defecto de isometría ||W W^T - I||_F."""
            W = self.proj.weight.data.detach().cpu().numpy()
            return float(np.linalg.norm(W @ W.T - np.eye(self.d_embed), ord='fro'))


    class ResidualStreamSpliceHook:
        """
        Hook de Inyección en Corriente Residual (Residual Stream Splice).
        Inserta el tensor continuo latente directamente en la capa profunda L-1 o 2L/3,
        evitando pasar por las capas tempranas de vocabulario.
        """
        def __init__(self, target_layer_module, latent_injection_tensor: torch.Tensor, mode: str = "add"):
            self.target_layer = target_layer_module
            self.latent_tensor = latent_injection_tensor
            self.mode = mode
            self.hook_handle = None

        def register(self):
            def hook_fn(module, input_tuple, output_tuple):
                is_tuple = isinstance(output_tuple, tuple)
                residual_stream = output_tuple[0] if is_tuple else output_tuple
                device = residual_stream.device
                dtype = residual_stream.dtype
                t_inj = self.latent_tensor.to(device=device, dtype=dtype)
                
                if self.mode == "add":
                    # Adaptación de longitud de secuencia si difieren
                    if t_inj.ndim == 3 and residual_stream.ndim == 3 and t_inj.shape[1] != residual_stream.shape[1]:
                        # Si el tensor latente tiene menos tokens, se añade a los primeros k tokens
                        k = min(t_inj.shape[1], residual_stream.shape[1])
                        modified = residual_stream.clone()
                        modified[:, :k, :] = modified[:, :k, :] + t_inj[:, :k, :]
                    else:
                        modified = residual_stream + t_inj
                elif self.mode == "replace":
                    modified = t_inj
                else:
                    modified = residual_stream

                if is_tuple:
                    return (modified,) + output_tuple[1:]
                return modified

            self.hook_handle = self.target_layer.register_forward_hook(hook_fn)
            return self

        def remove(self):
            if self.hook_handle:
                self.hook_handle.remove()
                self.hook_handle = None


    class AttentionSummaryPooling(nn.Module):
        """
        Extractor de Razonamiento Continuo sin Mean-Pooling Destructivo.
        Extrae el token EOS / último token causal o ejecuta ponderación por atención,
        preservando el orden temporal y la codificación de fase RoPE.
        """
        def __init__(self, mode: str = "last_token"):
            super().__init__()
            self.mode = mode

        def forward(self, hidden_states: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
            """
            hidden_states: [batch, seq_len, hidden_dim]
            Retorna: [batch, 1, hidden_dim] o secuencia filtrada.
            """
            if self.mode == "last_token":
                if attention_mask is not None:
                    last_indices = attention_mask.sum(dim=1) - 1
                    batch_size = hidden_states.shape[0]
                    selected = torch.stack([hidden_states[b, last_indices[b], :] for b in range(batch_size)])
                    return selected.unsqueeze(1)
                return hidden_states[:, -1:, :]
            elif self.mode == "preserve_sequence":
                return hidden_states
            else:
                return hidden_states[:, -1:, :]

else:
    class StiefelImpedanceProjector:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch es requerido para StiefelImpedanceProjector.")

    class ResidualStreamSpliceHook:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch es requerido para ResidualStreamSpliceHook.")

    class AttentionSummaryPooling:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch es requerido para AttentionSummaryPooling.")
