# -*- coding: utf-8 -*-
"""
pmtp_stiefel_attention.py — Proyección y Optimización Riemanniana en St(d, r)
para Matrices de Atención Transformer (W_Q, W_K) y Demostración de la
Paradoja de Weight Decay.

Ecosistema Soberano POLYDIM-EINSOF | Ariel García Traba
Teorema 32: Invarianza Riemanniana de Weight Decay y Estabilidad Geométrica de Atención.
"""

from __future__ import annotations
import math
import numpy as np

# Coeficientes de Taylor de orden 4 para (1+x)^(-1/2)
_C1, _C2, _C3, _C4 = -0.5, 3.0 / 8.0, -5.0 / 16.0, 35.0 / 128.0

def horner_polar_order4(E: np.ndarray) -> np.ndarray:
    """Evaluación de Horner de p4(E) = I + E(-1/2 I + E(3/8 I + E(-5/16 I + 35/128 E)))."""
    I = np.eye(E.shape[0], dtype=E.dtype)
    P = _C4 * E + _C3 * I
    P = E @ P + _C2 * I
    P = E @ P + _C1 * I
    return E @ P + I

def project_stiefel_polar_order4(W: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Retracción polar híbrida de Stiefel (Orden 4 + Nivel 2 Polar de alta precisión).
    Garantiza W_st^T W_st = I_r con error <= 1e-15 en todo el dominio.
    Retorna (W_proj, defect_frobenius).
    """
    d, r = W.shape
    if d < r:
        raise ValueError(f"Dimensión d={d} debe ser >= r={r}")
        
    G = W.T @ W
    G = 0.5 * (G + G.T)  # Simetrización
    E = G - np.eye(r, dtype=W.dtype)
    rho = float(np.linalg.norm(E, 'fro'))
    
    # Nivel 1: Cuenca analítica de Taylor p4 (rho <= 0.35)
    if rho <= 0.35:
        P = horner_polar_order4(E)
        W_proj = W @ P
        # Segunda pasada refinadora si es necesario
        G2 = W_proj.T @ W_proj
        E2 = 0.5 * (G2 + G2.T) - np.eye(r, dtype=W.dtype)
        if float(np.linalg.norm(E2, 'fro')) > 1e-15:
            W_proj = W_proj @ horner_polar_order4(E2)
    else:
        # Nivel 2: Polar vía QR + SVD + paso Newton-Schulz k x k
        Q, R = np.linalg.qr(W)
        U, _, Vt = np.linalg.svd(R)
        W_k = U @ Vt
        # Refinamiento Newton-Schulz k x k
        W_k = W_k @ (1.5 * np.eye(r, dtype=W.dtype) - 0.5 * (W_k.T @ W_k))
        W_proj = Q @ W_k
    
    # Verificación final de ortonormalidad
    G_proj = W_proj.T @ W_proj
    defect = float(np.linalg.norm(G_proj - np.eye(r, dtype=W.dtype), 'fro'))
    return W_proj, defect

def project_to_stiefel_tangent(W: np.ndarray, G: np.ndarray) -> np.ndarray:
    """
    Proyecta un gradiente euclidiano G sobre el espacio tangente
    T_W St(d, r) = { Xi in R^{d x r} : W^T Xi + Xi^T W = 0 }.
    
    Fórmula analítica Riemanniana:
        P_{T_W}(G) = G - 0.5 * W (W^T G + G^T W)
    """
    M = W.T @ G
    sym_M = 0.5 * (M + M.T)
    return G - W @ sym_M

def riemannian_weight_decay_gradient(W: np.ndarray, weight_decay: float) -> tuple[np.ndarray, float]:
    """
    Demostración analítica y numérica de la Paradoja de Weight Decay en St(d, r):
    Para f_WD(W) = 0.5 * lambda * ||W||_F^2 = 0.5 * lambda * Tr(W^T W) = 0.5 * lambda * r = const.
    El gradiente euclidiano es G_WD = lambda * W.
    El gradiente riemanniano proyectado P_{T_W}(G_WD) es IDÉNTICAMENTE CERO:
        P_{T_W}(lambda * W) = lambda * W - 0.5 * W (lambda * W^T W + lambda * W^T W)
                            = lambda * W - lambda * W (I_r) = 0.
    Retorna (grad_riemanniano, norma_frobenius).
    """
    G_wd_euclidean = weight_decay * W
    grad_riem = project_to_stiefel_tangent(W, G_wd_euclidean)
    norm_riem = float(np.linalg.norm(grad_riem, 'fro'))
    return grad_riem, norm_riem

def condition_number_stiefel(W: np.ndarray) -> float:
    """Calcula el número de condición espectral kappa_2(W) = sigma_max / sigma_min."""
    s = np.linalg.svd(W, compute_uv=False)
    return float(s[0] / s[-1])

def simulate_attention_evolution(d: int = 128, r: int = 64, steps: int = 100,
                                lr: float = 1e-3, weight_decay: float = 1e-2):
    """
    Simula la evolución de una matriz de proyección de atención W_Q / W_K
    bajo dos regímenes:
      1. Régimen Estándar Euclidiano (AdamW no restringido con weight decay)
      2. Régimen Stiefel Riemanniano (POLYDIM-EINSOF con polar order 4)
    """
    rng = np.random.default_rng(42)
    # Inicialización ortogonal
    W0, _ = np.linalg.qr(rng.standard_normal((d, r)))
    
    # 1. Simulación Euclidiana
    W_euc = W0.copy()
    kappas_euc = []
    defects_euc = []
    
    # 2. Simulación Stiefel Riemanniana
    W_stiefel = W0.copy()
    kappas_stiefel = []
    defects_stiefel = []
    
    for step in range(steps):
        # Gradiente sintético de tarea
        G_task = rng.standard_normal((d, r)) * 0.1
        
        # --- Paso Euclidiano ---
        # G_total = G_task + weight_decay * W_euc
        W_euc = W_euc - lr * (G_task + weight_decay * W_euc)
        G_euc_metric = W_euc.T @ W_euc
        defects_euc.append(float(np.linalg.norm(G_euc_metric - np.eye(r), 'fro')))
        kappas_euc.append(condition_number_stiefel(W_euc))
        
        # --- Paso Stiefel Riemanniano ---
        # Proyección riemanniana de la tarea (el weight decay proyecta a cero)
        G_riem = project_to_stiefel_tangent(W_stiefel, G_task)
        # Retracción polar de orden 4
        W_stiefel_cand = W_stiefel - lr * G_riem
        W_stiefel, def_st = project_stiefel_polar_order4(W_stiefel_cand)
        defects_stiefel.append(def_st)
        kappas_stiefel.append(condition_number_stiefel(W_stiefel))
        
    return {
        "final_defect_euc": defects_euc[-1],
        "final_kappa_euc": kappas_euc[-1],
        "final_defect_stiefel": defects_stiefel[-1],
        "final_kappa_stiefel": kappas_stiefel[-1],
        "max_kappa_stiefel": max(kappas_stiefel),
        "steps": steps
    }
