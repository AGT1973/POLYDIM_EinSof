# -*- coding: utf-8 -*-
"""
ANÁLISIS ESPECTRAL EXACTO DE RAMSEY R(5, 5) Y OBSTRUCCIÓN EN PALEY(41)
======================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Este script ejecuta verificación espectral y combinatoria exacta sobre grafos
  finitos en CPU local. NO estrecha las cotas mundiales abiertas del problema de
  Ramsey: el estado del arte humano vigente es 43 <= R(5, 5) <= 46
  (cota inferior: Exoo 1989 / McKay-Radziszowski; cota superior: Angeltveit-McKay 2024).

Correcciones respecto a la versión defectuosa previa:
  1. Se corrigió el valor falso de la cota de Hoffman en Paley(41) (antes decía ~4.7;
     el valor algebraico y numérico exacto es sqrt(41) = 6.403124 > 5).
  2. Se construye explícitamente la matriz de adyacencia de Paley(41) sobre GF(41),
     se verifican sus autovalores en silicio y se exhibe constructivamente una
     5-clique (K_5) explícita dentro de Paley(41), demostrando por qué Paley(41)
     NO sirve siquiera para probar R(5,5) > 41.
  3. Se actualizó la cota superior vigente de 48 a 46 (Angeltveit-McKay 2024) y se
     eliminó la afirmación infundada sobre clases de Stiefel-Whitney en Gr(21, 42).
"""

import time
import math
import json
import itertools
import numpy as np
import psycopg2


def build_paley_adjacency(p: int) -> np.ndarray:
    assert p % 4 == 1
    qr = {(x * x) % p for x in range(1, p)}
    A = np.zeros((p, p), dtype=np.float64)
    for i in range(p):
        for j in range(i + 1, p):
            if ((j - i) % p) in qr:
                A[i, j] = 1.0
                A[j, i] = 1.0
    return A


def find_explicit_k_clique(A: np.ndarray, k_target: int = 5):
    """Busca determinísticamente una clique de tamaño `k_target` conteniendo el vértice 0."""
    n = A.shape[0]
    nbrs_0 = [v for v in range(1, n) if A[0, v] > 0.5]
    for comb in itertools.combinations(nbrs_0, k_target - 1):
        ok = True
        for u, v in itertools.combinations(comb, 2):
            if A[u, v] < 0.5:
                ok = False
                break
        if ok:
            return (0,) + comb
    return None


def run_ramsey_55_honest_audit():
    t0 = time.perf_counter()

    # 1. Construir y diagonalizar Paley(41) realmente en silicio
    p = 41
    A41 = build_paley_adjacency(p)
    evals = np.linalg.eigvalsh(A41)
    lam_max = float(evals[-1])
    lam_min = float(evals[0])
    lam_min_exact = (-1.0 - math.sqrt(p)) / 2.0
    spec_err = abs(lam_min - lam_min_exact)

    # Cota de Hoffman real: n * (-lam_min) / (k - lam_min) == sqrt(p)
    hoffman_41 = p * (-lam_min) / (lam_max - lam_min)
    assert abs(hoffman_41 - math.sqrt(41.0)) < 1e-12

    # Buscar 5-clique explícita en Paley(41)
    k5_witness = find_explicit_k_clique(A41, 5)
    assert k5_witness is not None, "Paley(41) contiene K_5 (omega(Paley(41)) = 5)"
    # Verificar que las 10 aristas de k5_witness son todas 1
    sub_A = A41[np.ix_(k5_witness, k5_witness)]
    edges_in_witness = int(np.sum(sub_A) // 2)
    assert edges_in_witness == 10

    latency_ms = (time.perf_counter() - t0) * 1000.0

    report = {
        "scope_disclaimer": "Exact spectral and combinatorial verification on Paley(41) in local CPU; does NOT tighten the open bounds 43 <= R(5,5) <= 46.",
        "problem_id": "RAMSEY_R55_PALEY41_EXACT_AUDIT",
        "world_sota_bounds": {
            "lower_bound": 43,
            "upper_bound": 46,
            "source_lower": "Exoo (1989) 42-vertex Ramsey(5,5)-good graph",
            "source_upper": "Angeltveit & McKay (2024), tightened from 48 to 46 via SDP/LP",
        },
        "paley_41_silicon_verification": {
            "vertices": p,
            "degree_k": int(round(lam_max)),
            "lambda_min_measured": round(lam_min, 10),
            "spectral_error_vs_weil": spec_err,
            "true_hoffman_clique_bound": round(hoffman_41, 8),
            "explicit_5_clique_found": list(k5_witness),
            "k5_edges_verified": edges_in_witness,
            "verdict": "Hoffman bound on Paley(41) is sqrt(41)=6.403124 (> 5), and Paley(41) explicitly contains K_5 (e.g. "
                       f"{list(k5_witness)}), so Paley(41) has omega = alpha = 5 and does NOT witness R(5,5) > 41.",
        },
        "bounds_tightened": False,
        "latency_ms": round(latency_ms, 3),
        "exit_code": 0,
    }

    try:
        conn = psycopg2.connect(dbname="polydim_vec_db", user="postgres", password="postgres", host="localhost", port=5432)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO session_context (conversation_id, summary, category, created_at) VALUES (%s, %s, %s, NOW())",
            ("3f34edfc-4b9c-4658-84fc-10d32ef4da9b", json.dumps(report, ensure_ascii=False), "REPAIRED_RAMSEY_R55_AUDIT"),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB WARN] {e}")

    print("=== AUDITORÍA COMBINATORIA EXACTA: RAMSEY R(5,5) Y PALEY(41) ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    run_ramsey_55_honest_audit()
