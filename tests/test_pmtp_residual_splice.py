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
    orthogonal_procrustes_alignment,
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


def test_orthogonal_procrustes_and_control_x():
    """
    Test de Procrustes Ortogonal Analítico y Prueba de Falsación Control X (§0.3 Regla 0).
    Verifica que la solución analítica minimice la distancia euclídea y que
    los datos incorrelados (Control X) produzcan un residuo significativamente mayor.
    """
    rng = np.random.default_rng(20261120)
    N = 256
    D_in = 128
    D_out = 64
    
    # Base latente ortogonal de referencia sobre Stiefel
    X_raw = rng.standard_normal((N, D_in))
    Q, _ = np.linalg.qr(X_raw)
    X = Q[:, :D_in]  # Activaciones normalizadas en la variedad
    
    A_raw = rng.standard_normal((D_in, D_out))
    U_ref, _, Vt_ref = np.linalg.svd(A_raw, full_matrices=False)
    W_true = U_ref @ Vt_ref  # (D_in, D_out) en St(D_out, D_in)
    
    # Y correlacionado con ruido térmico bajo
    Y_correlated = X @ W_true + 0.001 * rng.standard_normal((N, D_out))
    
    W_opt, res_corr, defect_corr = orthogonal_procrustes_alignment(X, Y_correlated)
    assert defect_corr < 1e-13, f"Defecto Stiefel excesivo: {defect_corr}"
    
    # CONTROL X: Entrada incorrelada pura (Ruido independiente)
    Y_control_x = rng.standard_normal((N, D_out))
    W_opt_ctrl, res_ctrl, defect_ctrl = orthogonal_procrustes_alignment(X, Y_control_x)
    assert defect_ctrl < 1e-13, f"Defecto Stiefel en Control X excesivo: {defect_ctrl}"
    
    # Prueba de Falsación (§0.3): El residuo sobre Control X DEBE ser sustancialmente mayor
    ratio_falsacion = res_ctrl / max(1e-12, res_corr)
    assert ratio_falsacion > 50.0, f"Falla en Test de Control X: ratio={ratio_falsacion} no discrimina estructura real"


def test_stiefel_projector_and_hook():
    torch = pytest.importorskip("torch")
    import torch.nn as nn

    d_hidden = 128
    d_embed = 64
    batch_size = 2
    seq_len = 4

    # 1. Proyector de Impedancia (Inmersión Canónica Determinista por defecto)
    projector = StiefelImpedanceProjector(d_hidden=d_hidden, d_embed=d_embed)
    assert not projector.is_calibrated, "El proyector no calibrado debe reportar is_calibrated=False"
    assert projector.stiefel_defect() < 1e-14, f"Defecto canónico debe ser <= 1e-14: {projector.stiefel_defect()}"
    x = torch.randn(batch_size, seq_len, d_hidden)
    y = projector(x)
    assert y.shape == (batch_size, seq_len, d_embed)
    assert torch.isfinite(y).all()

    # Calibración Procrustes con activaciones objetivo reales
    act_source = torch.randn(32, d_hidden)
    act_target = torch.randn(32, d_embed)
    res, defect = projector.calibrate_procrustes(act_source, act_target)
    assert projector.is_calibrated, "Debe marcarse como calibrado tras Procrustes"
    assert defect < 1e-13, f"Defecto Stiefel post-calibración (FP64) excesivo: {defect}"
    assert projector.stiefel_defect() < 1e-5, f"Defecto Stiefel en pesos PyTorch (FP32) excesivo: {projector.stiefel_defect()}"

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
    test_orthogonal_procrustes_and_control_x()
    test_stiefel_projector_and_hook()
    print("ALL TESTS PASSED — EXIT CODE 0")
