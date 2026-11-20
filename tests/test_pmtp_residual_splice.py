# -*- coding: utf-8 -*-
"""
Test Unitario de Silicon Proof: PMTP Residual Splice & Stiefel Projector
=======================================================================
Verifica importación canónica, retracción polar de Stiefel y hooks en silicio.
"""

import numpy as np
import pytest

from pmtp import (
    ResidualStreamSpliceHook,
    StiefelImpedanceProjector,
    AttentionSummaryPooling,
    stiefel_polar_retraction_order4,
)


def test_stiefel_polar_retraction():
    rng = np.random.default_rng(42)
    W = rng.standard_normal((128, 64), dtype=np.float64)
    W_stiefel = stiefel_polar_retraction_order4(W)
    
    # Isometría estricta: W^T W = I_k
    diff = W_stiefel.T @ W_stiefel - np.eye(64)
    max_abs_defect = np.max(np.abs(diff))
    fro_defect = np.linalg.norm(diff, ord='fro')
    assert max_abs_defect < 1e-14, f"Defecto Stiefel max_abs excesivo: {max_abs_defect}"
    assert fro_defect < 1e-13, f"Defecto Stiefel Frobenius excesivo: {fro_defect}"


def test_stiefel_projector_and_hook():
    torch = pytest.importorskip("torch")
    import torch.nn as nn

    d_hidden = 128
    d_embed = 64
    batch_size = 2
    seq_len = 4

    # 1. Proyector de Impedancia
    projector = StiefelImpedanceProjector(d_hidden=d_hidden, d_embed=d_embed)
    x = torch.randn(batch_size, seq_len, d_hidden)
    y = projector(x)
    assert y.shape == (batch_size, seq_len, d_embed)
    assert torch.isfinite(y).all()

    # 2. Attention Summary Pooling
    pooler = AttentionSummaryPooling(mode="last_token")
    pooled = pooler(x)
    assert pooled.shape == (batch_size, 1, d_hidden)

    # 3. Residual Stream Splice Hook
    dummy_layer = nn.Identity()
    latent_to_inject = torch.randn(batch_size, seq_len, d_hidden)
    hook = ResidualStreamSpliceHook(dummy_layer, latent_to_inject, mode="add").register()
    
    out = dummy_layer(x)
    assert torch.allclose(out, x + latent_to_inject, atol=1e-5)
    hook.remove()


if __name__ == "__main__":
    test_stiefel_polar_retraction()
    test_stiefel_projector_and_hook()
    print("ALL TESTS PASSED — EXIT CODE 0")
