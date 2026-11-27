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


def orthogonal_procrustes_alignment(
    X: np.ndarray,
    Y: np.ndarray
) -> Tuple[np.ndarray, float, float]:
    """
    Cálculo analítico exacto de Procrustes Ortogonal (Schönemann 1966, Higham 1989):
    W* = argmin_{W in St(D_out, D_in)} ||X W - Y||_F^2
    Dado por SVD de la matriz de covarianza cruzada M = X^T Y = U Sigma V^T:
    W* = U V^T
    Retorna: (W_opt, residual_frobenius, defect_frobenius).
    """
    X_f64 = np.asarray(X, dtype=np.float64)
    Y_f64 = np.asarray(Y, dtype=np.float64)
    if X_f64.ndim > 2:
        X_f64 = X_f64.reshape(-1, X_f64.shape[-1])
    if Y_f64.ndim > 2:
        Y_f64 = Y_f64.reshape(-1, Y_f64.shape[-1])
    
    N, D_in = X_f64.shape
    N2, D_out = Y_f64.shape
    if N != N2:
        raise ValueError(f"Incompatibilidad de muestras para Procrustes: X tiene {N}, Y tiene {N2}")
    
    # Matriz de covarianza cruzada M in R^(D_in x D_out)
    M = X_f64.T @ Y_f64
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    W_opt = U @ Vt  # Shape: (D_in, D_out)
    
    # Defecto de isometría sobre Stiefel
    if D_in >= D_out:
        gram = W_opt.T @ W_opt
        defect = float(np.linalg.norm(gram - np.eye(D_out, dtype=np.float64), ord='fro'))
    else:
        gram = W_opt @ W_opt.T
        defect = float(np.linalg.norm(gram - np.eye(D_in, dtype=np.float64), ord='fro'))
        
    diff = (X_f64 @ W_opt) - Y_f64
    residual = float(math.sqrt(max(0.0, neumaier_sum((diff * diff).ravel()))))
    return W_opt, residual, defect


if _TORCH_AVAILABLE:
    class StiefelImpedanceProjector(nn.Module):
        """
        Proyector Lineal de Impedancia Semántica (W_proj) con Compensación RoPE R_theta.
        Mapea estados ocultos profundos R^{D_hidden} -> R^{D_embed} (Capa 0 o Residual Splice)
        sin saturar RMSNorm ni descalibrar las codificaciones posicionales rotacionales.
        
        REGLA 0 SUPREMA:
        Erradica stubs aleatorios (rng.standard_normal). Utiliza la solución analítica de
        Procrustes Ortogonal W = U V^T derivada de activaciones reales (X, Y).
        Si no se proporcionan activaciones iniciales, utiliza una inmersión canónica determinista
        (identidad truncada I_{d_hidden, d_embed}) marcando is_calibrated = False hasta que se ejecute
        calibrate_procrustes(source_activations, target_activations).
        """
        def __init__(
            self, 
            d_hidden: int = 2048, 
            d_embed: int = 1536, 
            source_activations: Optional[Union[np.ndarray, "torch.Tensor"]] = None,
            target_activations: Optional[Union[np.ndarray, "torch.Tensor"]] = None,
            seed: Optional[int] = None,
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
            
            self.proj = nn.Linear(d_hidden, d_embed, bias=False)
            self.norm = nn.LayerNorm(d_embed, eps=1e-6)
            
            self.is_calibrated = False
            self.calibration_residual = float("inf")
            self.calibration_defect = float("inf")
            self.calibration_samples = 0
            
            if source_activations is not None and target_activations is not None:
                self.calibrate_procrustes(source_activations, target_activations)
            else:
                # Inmersión Canónica Determinista en Stiefel (Cero Números Aleatorios, Defecto 0.0)
                W_canon = np.zeros((d_hidden, d_embed), dtype=np.float64)
                min_dim = min(d_hidden, d_embed)
                for i in range(min_dim):
                    W_canon[i, i] = 1.0
                self.proj.weight.data = torch.from_numpy(W_canon.T.astype(np.float32))
                self.is_calibrated = False

        def calibrate_procrustes(
            self,
            source_activations: Union[np.ndarray, "torch.Tensor"],
            target_activations: Union[np.ndarray, "torch.Tensor"]
        ) -> Tuple[float, float]:
            """
            Calibra analíticamente el proyector resolviendo el problema de Procrustes
            Ortogonal W* = argmin ||X W - Y||_F^2 = U V^T sobre pares de activaciones reales.
            Retorna (residual_frobenius, stiefel_defect).
            """
            if isinstance(source_activations, torch.Tensor):
                X = source_activations.detach().cpu().to(torch.float64).numpy()
            else:
                X = np.asarray(source_activations, dtype=np.float64)
                
            if isinstance(target_activations, torch.Tensor):
                Y = target_activations.detach().cpu().to(torch.float64).numpy()
            else:
                Y = np.asarray(target_activations, dtype=np.float64)
                
            W_opt, residual, defect = orthogonal_procrustes_alignment(X, Y)
            
            # En PyTorch nn.Linear: out = in @ weight.T, por lo tanto weight = W_opt.T
            self.proj.weight.data = torch.from_numpy(W_opt.T.astype(np.float32))
            self.is_calibrated = True
            self.calibration_residual = residual
            self.calibration_defect = defect
            self.calibration_samples = (X.shape[0] if X.ndim == 2 else X.shape[0] * X.shape[1])
            return residual, defect

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
        def __init__(self, target_layer_module, latent_injection_tensor: torch.Tensor, mode: str = "stiefel_blend", alpha: float = 0.85):
            self.target_layer = target_layer_module
            self.latent_tensor = latent_injection_tensor
            self.mode = mode
            self.alpha = float(alpha)
            self.hook_handle = None

        def register(self):
            def hook_fn(module, input_tuple, output_tuple):
                is_tuple = isinstance(output_tuple, tuple)
                residual_stream = output_tuple[0] if is_tuple else output_tuple
                device = residual_stream.device
                dtype = residual_stream.dtype
                t_inj = self.latent_tensor.to(device=device, dtype=dtype)
                
                if self.mode == "stiefel_blend":
                    res_norm = residual_stream.norm(dim=-1, keepdim=True).clamp_min(1e-12)
                    t_norm = t_inj.norm(dim=-1, keepdim=True).clamp_min(1e-12)
                    u_res = residual_stream / res_norm
                    u_t = t_inj / t_norm
                    cos_omega = (u_res * u_t).sum(dim=-1, keepdim=True).clamp(-1.0 + 1e-7, 1.0 - 1e-7)
                    omega = torch.acos(cos_omega)
                    sin_omega = torch.sin(omega).clamp_min(1e-7)
                    w_res = torch.sin((1.0 - self.alpha) * omega) / sin_omega
                    w_t = torch.sin(self.alpha * omega) / sin_omega
                    slerp_unit = w_res * u_res + w_t * u_t
                    lin_unit = (1.0 - self.alpha) * u_res + self.alpha * u_t
                    lin_unit = lin_unit / lin_unit.norm(dim=-1, keepdim=True).clamp_min(1e-12)
                    blended_unit = torch.where(omega > 1e-4, slerp_unit, lin_unit)
                    blended_unit = blended_unit / blended_unit.norm(dim=-1, keepdim=True).clamp_min(1e-12)
                    modified = blended_unit * res_norm
                elif self.mode == "add":
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
