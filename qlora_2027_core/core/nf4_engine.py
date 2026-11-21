# -*- coding: utf-8 -*-
"""
Authentic 4-bit NormalFloat (NF4) Blockwise Quantization Engine
===============================================================
Implements Dettmers et al. (2023) NF4 codebook quantization in pure PyTorch,
allowing real 4-bit base weights + FP32 trainable LoRA adapters on CPU (ALADIN)
and heterogeneous accelerators without bitsandbytes ABI failures.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

NF4_CODEBOOK_VALUES = [
    -1.0,
    -0.6961928009986877,
    -0.5250730514526367,
    -0.39491748809814453,
    -0.28444138169288635,
    -0.18477343022823334,
    -0.09105003625154495,
    0.0,
    0.07958029955625534,
    0.16093020141124725,
    0.24611230194568634,
    0.33791524171829224,
    0.44070982933044434,
    0.5626170039176941,
    0.7229568362236023,
    1.0,
]

_NF4_CODEBOOK_F32 = torch.tensor(NF4_CODEBOOK_VALUES, dtype=torch.float32)
_NF4_MIDPOINTS_F32 = 0.5 * (_NF4_CODEBOOK_F32[:-1] + _NF4_CODEBOOK_F32[1:])


class NF4Linear(nn.Module):
    """Frozen 4-bit NormalFloat packed linear layer (2 weights/byte, ~3.8x vs FP16)."""

    def __init__(
        self,
        in_features: int,
        out_features: int,
        qweight: torch.Tensor,
        absmax: torch.Tensor,
        orig_numel: int,
        blocksize: int = 64,
        bias: Optional[torch.Tensor] = None,
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.orig_numel = orig_numel
        self.blocksize = blocksize
        self.register_buffer("qweight", qweight)
        self.register_buffer("absmax", absmax)
        if bias is not None:
            self.register_buffer("bias", bias.detach().to(torch.float32))
        else:
            self.bias = None

    @classmethod
    @torch.no_grad()
    def from_linear(cls, linear: nn.Linear, blocksize: int = 64) -> "NF4Linear":
        w = linear.weight.detach().to(torch.float32).contiguous()
        out_f, in_f = w.shape
        flat = w.view(-1)
        orig_numel = flat.numel()

        bs = blocksize if (blocksize % 2 == 0) else blocksize + 1
        pad = (bs - (orig_numel % bs)) % bs
        if pad > 0:
            flat = F.pad(flat, (0, pad))

        blocks = flat.view(-1, bs)
        absmax = blocks.abs().amax(dim=1).clamp(min=1e-8)
        normed = blocks / absmax.unsqueeze(1)
        idx = torch.bucketize(normed.contiguous(), _NF4_MIDPOINTS_F32.to(normed.device)).to(torch.uint8)
        idx_flat = idx.view(-1)
        packed = (idx_flat[0::2] << 4) | idx_flat[1::2]
        bias = linear.bias.detach().clone() if linear.bias is not None else None
        return cls(
            in_features=in_f,
            out_features=out_f,
            qweight=packed.contiguous(),
            absmax=absmax.to(torch.float16).contiguous(),
            orig_numel=orig_numel,
            blocksize=bs,
            bias=bias,
        )

    def dequantize_weight(self, dtype: torch.dtype = torch.float32) -> torch.Tensor:
        packed = self.qweight
        hi = (packed >> 4).to(torch.long)
        lo = (packed & 0x0F).to(torch.long)
        idx = torch.stack((hi, lo), dim=1).view(-1, self.blocksize)
        cb = _NF4_CODEBOOK_F32.to(device=packed.device)
        w = cb[idx] * self.absmax.to(torch.float32).unsqueeze(1)
        return w.view(-1)[: self.orig_numel].view(self.out_features, self.in_features).to(dtype)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.dequantize_weight(dtype=x.dtype)
        b = self.bias.to(x.dtype) if self.bias is not None else None
        return F.linear(x, w, b)


def quantize_peft_base_to_nf4(model: nn.Module, blocksize: int = 64) -> Dict[str, Any]:
    """Replaces frozen base nn.Linear inside PEFT LoraLayers with NF4Linear while keeping LoRA FP32."""
    replaced = 0
    bytes_before = 0
    bytes_after = 0

    for _, module in list(model.named_modules()):
        if hasattr(module, "base_layer") and isinstance(module.base_layer, nn.Linear):
            base = module.base_layer
            bytes_before += base.weight.numel() * base.weight.element_size()
            nf4 = NF4Linear.from_linear(base, blocksize=blocksize)
            bytes_after += nf4.qweight.numel() + nf4.absmax.numel() * 2
            module.base_layer = nf4
            replaced += 1

    return {
        "layers_quantized_nf4": replaced,
        "base_linear_mb_before": round(bytes_before / (1024 * 1024), 4),
        "base_linear_mb_after": round(bytes_after / (1024 * 1024), 4),
        "compression_ratio": round(bytes_before / max(bytes_after, 1), 2),
    }
