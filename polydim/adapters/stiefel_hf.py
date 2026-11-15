"""
POLYDIM STIEFEL ADAPTER INTERFACE FOR HUGGING FACE & PYTORCH
Allows 2-line loading of certified Stiefel Manifold continuous adapters.
Author: Ariel García Traba (Independent Research / POLYDIM-EINSOF Initiative)
"""

import os

try:
    import torch
    import torch.nn as nn
    from safetensors.torch import load_file
    from huggingface_hub import hf_hub_download
    _ModuleBase = nn.Module
    HAS_TORCH = True
except ImportError:
    torch = None
    _ModuleBase = object
    HAS_TORCH = False

class StiefelAdapter(_ModuleBase):
    def __init__(self, W, temperature: float = 0.07):
        if not HAS_TORCH:
            raise ImportError("PyTorch is required to instantiate StiefelAdapter.")
        super().__init__()
        self.register_buffer("W", W) # [d_out, d_in]
        self.temperature = temperature
        self.d_out = W.shape[0]
        self.d_in = W.shape[1]

    @classmethod
    def from_pretrained(cls, repo_id: str = "polydim-cla/polydim-stiefel-manifold-adapters", subfolder: str = "2_qwen2_5_PMTP_v1", token: str = None):
        """Descarga e inicializa el adaptador de Stiefel directamente desde Hugging Face."""
        filename = f"{subfolder}/adapter_weights.safetensors" if subfolder else "adapter_weights.safetensors"
        weights_path = hf_hub_download(repo_id=repo_id, filename=filename, token=token)
        tensors = load_file(weights_path)
        W = tensors["W"].float()
        temp = float(tensors.get("temperature", torch.tensor(0.07)).item())
        return cls(W, temperature=temp)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Proyecta el vector latente continuo a la variedad de Stiefel S^(d_out - 1).
        Preserva la isometria de Hilbert y previene el colapso de entropia de Shannon (DPI).
        Blindado contra autograd NaN breakdown en norma cero o subnormal (PY-SEV1-002).
        """
        # x: [..., d_in]
        # Norma L2 numericamente estable sin division por cero ni gradiente NaN en backward
        sq_norm_x = torch.sum(x * x, dim=-1, keepdim=True)
        norm_x = torch.sqrt(torch.clamp(sq_norm_x, min=1e-24))
        x_unit = x / norm_x

        # Asegurar coincidencia de dispositivo y tipo de datos para W
        w_mat = self.W.to(dtype=x.dtype, device=x.device)

        # Proyeccion Stiefel: [..., d_out]
        proj = torch.matmul(x_unit, w_mat.T)
        sq_norm_p = torch.sum(proj * proj, dim=-1, keepdim=True)
        norm_p = torch.sqrt(torch.clamp(sq_norm_p, min=1e-24))
        return proj / norm_p
