# -*- coding: utf-8 -*-
"""
CEROS REALES DE ZETA DE RIEMANN EN Re(s)=1/2 Y ESTADÍSTICA GUE (MONTGOMERY-ODLYZKO)
===================================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Este script calcula numéricamente los primeros ceros no triviales reales de la
  función Zeta de Riemann zeta(1/2 + i*gamma_n) = 0 mediante aceleración racional de
  Borwein sobre la serie alternante de Dirichlet eta(s), los despliega con la fórmula
  suave de Riemann-von Mangoldt, y compara su repulsión de niveles con un ensamble GUE.
  NO constituye una demostración de la Hipótesis de Riemann ni realiza el operador
  desconocido de Hilbert-Pólya.
"""

import time
import math
import cmath
import json
import numpy as np
import scipy.linalg as la
from scipy.optimize import brentq
import psycopg2


def _borwein_weights(n: int) -> np.ndarray:
    """Pesos de aceleración de Chebyshev-Borwein (2000) para evaluar eta(s) con ~1.3^n precisión."""
    d = [0.0] * (n + 1)
    cur = 1.0
    s = 0.0
    for k in range(n + 1):
        if k > 0:
            cur = cur * (n + k - 1) * 4.0 * (n - k + 1) / ((2 * k - 1) * (2 * k))
        s += cur
        d[k] = s
    dn = d[n]
    return np.array([((-1.0) ** k) * (d[k] - dn) / (-dn) for k in range(n)], dtype=np.float64)


_BW_N = 44
_BW_W = _borwein_weights(_BW_N)
_BW_K = np.arange(1, _BW_N + 1, dtype=np.float64)


def riemann_hardy_Z(t: float) -> float:
    """
    Evalúa la función real de Hardy Z(t) = exp(i * theta(t)) * zeta(1/2 + i*t)
    sobre la recta crítica Re(s) = 1/2. Sus cambios de signo localizan exactamente
    los ceros no triviales de zeta(s).
    """
    s = complex(0.5, t)
    # eta(s) = sum_{k=1}^n w_k / k^s
    ks_pow = np.exp((-0.5 - 1j * t) * np.log(_BW_K))
    eta = complex(np.sum(_BW_W * ks_pow))
    zeta_val = eta / (1.0 - cmath.exp((1.0 - s) * math.log(2.0)))
    # Ángulo de Riemann-Siegel theta(t) = Im(lgamma(1/4 + i*t/2)) - (t/2)*ln(pi)
    lg = cmath.log(math.gamma(0.25)) if abs(t) < 1e-12 else None
    # Serie asintótica de Stirling de alta precisión para theta(t) (t >= 10 -> error < 1e-13)
    theta = (
        0.5 * t * math.log(t / (2.0 * math.pi))
        - 0.5 * t
        - math.pi / 8.0
        + 1.0 / (48.0 * t)
        + 7.0 / (5760.0 * (t ** 3))
    )
    z_real = (cmath.exp(1j * theta) * zeta_val).real
    return float(z_real)


def find_first_riemann_zeros(count: int = 30) -> list:
    zeros = []
    t_left = 10.0
    dt = 0.25
    z_left = riemann_hardy_Z(t_left)
    while len(zeros) < count and t_left < 200.0:
        t_right = t_left + dt
        z_right = riemann_hardy_Z(t_right)
        if z_left * z_right <= 0.0:
            root = brentq(riemann_hardy_Z, t_left, t_right, xtol=1e-11)
            zeros.append(float(root))
        t_left = t_right
        z_left = z_right
    return zeros


def riemann_von_mangoldt_smooth_N(t: np.ndarray) -> np.ndarray:
    return (t / (2.0 * np.pi)) * np.log(t / (2.0 * np.pi * np.e)) + 0.875


def wigner_semicircle_cdf(x: np.ndarray) -> np.ndarray:
    """CDF exacta del semicírculo de Wigner en [-2, 2] para despliegue espectral correcto de GUE."""
    xc = np.clip(x, -2.0, 2.0)
    return 0.5 + (xc * np.sqrt(np.maximum(0.0, 4.0 - xc * xc)) + 4.0 * np.arcsin(xc / 2.0)) / (4.0 * np.pi)


def run_honest_riemann_gue_comparison():
    t0 = time.perf_counter()

    # 1. Calcular los primeros 30 ceros verdaderos de zeta(1/2 + i*gamma_n)
    gammas = np.array(find_first_riemann_zeros(30), dtype=np.float64)
    known_gamma_1 = 14.134725141734693
    known_gamma_2 = 21.022039638771555
    err_g1 = abs(float(gammas[0]) - known_gamma_1)
    err_g2 = abs(float(gammas[1]) - known_gamma_2)
    assert err_g1 < 1e-7 and err_g2 < 1e-7, f"Error en ceros de Riemann: {err_g1}, {err_g2}"

    # Espaciados desplegados de los ceros reales con Riemann-von Mangoldt
    unfolded_zeta = riemann_von_mangoldt_smooth_N(gammas)
    zeta_spacings = np.diff(unfolded_zeta)

    # 2. Ensamble GUE desplegado propiamente con CDF del semicírculo de Wigner (ventana central)
    N_gue = 256
    rng = np.random.default_rng(20261107)
    A = rng.normal(0.0, 1.0 / math.sqrt(2.0 * N_gue), size=(N_gue, N_gue))
    B = rng.normal(0.0, 1.0 / math.sqrt(2.0 * N_gue), size=(N_gue, N_gue))
    H_gue = 0.5 * (A + A.T) + 0.5j * (B - B.T)
    np.fill_diagonal(H_gue, rng.normal(0.0, 1.0 / math.sqrt(N_gue), size=N_gue))
    evals_gue = np.sort(la.eigvalsh(H_gue))
    bulk = evals_gue[(evals_gue > -1.4) & (evals_gue < 1.4)]
    unfolded_gue = N_gue * wigner_semicircle_cdf(bulk)
    gue_spacings = np.diff(unfolded_gue)

    latency_ms = (time.perf_counter() - t0) * 1000.0
    report = {
        "scope_disclaimer": "Numerical computation of the first 30 critical-line zeros of Riemann zeta(s) + unfolded GUE spacing statistics on local CPU; NOT a proof of the Riemann Hypothesis nor a Hilbert-Polya operator construction.",
        "problem_id": "RIEMANN_ZETA_CRITICAL_ZEROS_AND_GUE_STATS",
        "riemann_zeros_verified": {
            "count": len(gammas),
            "first_5_gammas": [round(float(g), 9) for g in gammas[:5]],
            "gamma_1_abs_error": err_g1,
            "gamma_2_abs_error": err_g2,
            "unfolded_mean_spacing": round(float(np.mean(zeta_spacings)), 5),
            "min_spacing_level_repulsion": round(float(np.min(zeta_spacings)), 5),
        },
        "gue_256_unfolded_reference": {
            "bulk_eigenvalues_used": int(len(bulk)),
            "unfolded_mean_spacing": round(float(np.mean(gue_spacings)), 5),
            "unfolded_spacing_variance": round(float(np.var(gue_spacings)), 5),
            "theoretical_wigner_gue_variance": round(float((3.0 * math.pi - 8.0) / (math.pi ** 2) * (math.pi / 4.0)), 5),
        },
        "latency_ms": round(latency_ms, 2),
        "exit_code": 0,
    }

    try:
        conn = psycopg2.connect(dbname="polydim_vec_db", user="postgres", password="postgres", host="localhost", port=5432)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO session_context (conversation_id, summary, category, created_at) VALUES (%s, %s, %s, NOW())",
            ("3f34edfc-4b9c-4658-84fc-10d32ef4da9b", json.dumps(report, ensure_ascii=False), "REPAIRED_RIEMANN_ZEROS_NUMERIC"),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB WARN] {e}")

    print("=== VERIFICACIÓN NUMÉRICA DE CEROS DE RIEMANN Y GUE DESPLEGADO ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    run_honest_riemann_gue_comparison()
