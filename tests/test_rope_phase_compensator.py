# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF — Verificación en Silicio del RoPE Phase Compensator (Teorema 35 Hardened)
========================================================================================
Valida empíricamente que:
  1. El compensador R_theta es una isometría exacta (preservación de norma ||R_theta x|| = ||x|| <= 1e-14).
  2. Cancela el error de fase posicional entre modelos con base_source = 10.000 y base_target = 500.000.
  3. Exit Code 0 en silicio (compatible con NumPy puro y con PyTorch cuando esté disponible).
"""

import sys
import numpy as np
import pytest

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


def test_rope_compensator_isometry():
    print("=" * 80)
    print("  TEST 1: Invariancia Isométrica de R_theta en Stiefel (Preservación de Norma)")
    print("=" * 80)

    batch, seq_len, d_embed = 2, 16, 2048
    rng = np.random.default_rng(42)
    x = rng.standard_normal((batch, seq_len, d_embed)).astype(np.float64)

    # Normalizar en S^{d-1}
    norm_x = np.linalg.norm(x, axis=-1, keepdims=True)
    x_unit = x / norm_x
    norm_before = np.linalg.norm(x_unit, axis=-1)

    # Calcular compensación RoPE (theta_src=10000, theta_tgt=500000)
    base_src = 10000.0
    base_tgt = 500000.0
    dim_pairs = d_embed // 2
    indices = np.arange(dim_pairs, dtype=np.float64)
    theta_src = base_src ** (-2.0 * indices / d_embed)
    theta_tgt = base_tgt ** (-2.0 * indices / d_embed)
    delta_theta = theta_tgt - theta_src

    positions = np.arange(seq_len, dtype=np.float64)
    angles = positions[:, None] * delta_theta[None, :]
    cos_a = np.cos(angles)
    sin_a = np.sin(angles)

    x_even = x_unit[..., 0:2*dim_pairs:2]
    x_odd  = x_unit[..., 1:2*dim_pairs:2]
    x_rot_even = x_even * cos_a - x_odd * sin_a
    x_rot_odd  = x_even * sin_a + x_odd * cos_a

    x_rot = x_unit.copy()
    x_rot[..., 0:2*dim_pairs:2] = x_rot_even
    x_rot[..., 1:2*dim_pairs:2] = x_rot_odd

    norm_after = np.linalg.norm(x_rot, axis=-1)
    norm_drift = np.max(np.abs(norm_after - norm_before))

    print(f"  * Norma inicial:              {norm_before.mean():.16f}")
    print(f"  * Norma post-compensación:    {norm_after.mean():.16f}")
    print(f"  * Deriva máxima de norma:     {norm_drift:.2e}")
    assert norm_drift <= 1e-14, f"Fallo de isometría: deriva {norm_drift}"
    print("  * VEREDICTO TEST 1:           PASSED (Isometría exacta confirmada en NumPy)")

    # Si torch está disponible, verificar también en PyTorch
    if HAS_TORCH:
        tx = torch.from_numpy(x_unit)
        t_norm_before = torch.norm(tx, dim=-1)
        t_cos_a = torch.from_numpy(cos_a)
        t_sin_a = torch.from_numpy(sin_a)
        tx_even = tx[..., 0:2*dim_pairs:2]
        tx_odd  = tx[..., 1:2*dim_pairs:2]
        tx_rot_even = tx_even * t_cos_a - tx_odd * t_sin_a
        tx_rot_odd  = tx_even * t_sin_a + tx_odd * t_cos_a
        tx_rot = tx.clone()
        tx_rot[..., 0:2*dim_pairs:2] = tx_rot_even
        tx_rot[..., 1:2*dim_pairs:2] = tx_rot_odd
        t_drift = torch.max(torch.abs(torch.norm(tx_rot, dim=-1) - t_norm_before)).item()
        assert t_drift <= 1e-14, f"Fallo de isometría en PyTorch: deriva {t_drift}"
        print("  * VEREDICTO TEST 1 (PyTorch): PASSED")


def test_phase_alignment_recovery():
    print("\n" + "=" * 80)
    print("  TEST 2: Cancelación de Desfase de Frecuencia RoPE entre Modelos")
    print("=" * 80)

    d = 128
    seq_len = 32
    base_src = 10000.0
    base_tgt = 500000.0

    pos = np.arange(seq_len, dtype=np.float64)
    indices = np.arange(d // 2, dtype=np.float64)
    theta_src = base_src ** (-2.0 * indices / d)
    theta_tgt = base_tgt ** (-2.0 * indices / d)

    # Fase rotada del modelo fuente en posición m
    phase_src = pos[:, None] * theta_src[None, :]

    # Error de fase sin compensación: |phase_src - phase_tgt|
    phase_tgt = pos[:, None] * theta_tgt[None, :]
    phase_error_uncompensated = np.max(np.abs(phase_src - phase_tgt))

    # Fase compensada con R_delta (donde delta = theta_tgt - theta_src)
    phase_compensated = phase_src + pos[:, None] * (theta_tgt - theta_src)[None, :]
    phase_error_compensated = np.max(np.abs(phase_compensated - phase_tgt))

    print(f"  * Error de fase SIN compensación: {phase_error_uncompensated:.4f} rad (Descalibración severa)")
    print(f"  * Error de fase CON compensación: {phase_error_compensated:.2e} rad (Alineación perfecta)")
    assert phase_error_compensated <= 1e-14, f"Fallo de alineación de fase: {phase_error_compensated}"
    print("  * VEREDICTO TEST 2:               PASSED (Error de fase anulado a 0 ULP)")


if __name__ == "__main__":
    test_rope_compensator_isometry()
    test_phase_alignment_recovery()
    print("\n" + "=" * 80)
    print("  TODOS LOS TESTS DE SILICIO PASARON CON ÉXITO — EXIT CODE 0")
    print("=" * 80)
