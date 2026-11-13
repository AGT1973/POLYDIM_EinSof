# -*- coding: utf-8 -*-
"""
TEST DE ESPEJO LOSCHMIDT (6 QUBITS): EXPONENCIAL DE MATRIZ EXACTA vs RUIDO CPTP NISQ
====================================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Esto es una simulación numérica clásica en CPU local de un circuito espejo de
  6 qubits (D=64) comparando exponenciación unitaria exacta `scipy.linalg.expm`
  frente a decaimiento depolarizante CPTP. NO simula un circuito entrelazado de
  156 qubits ni reemplaza corrección cuántica de errores (QEC).
"""

import time
import json
import numpy as np
import scipy.linalg as la
import psycopg2


def run_loschmidt_mirror_6q():
    t0 = time.perf_counter()
    n_qubits = 6
    dim = 1 << n_qubits  # 64
    rng = np.random.default_rng(20261107)

    # Generador Hamiltoniano aleatorio fijo hermítico H en C^{64x64} para pasos unitarios exactos U = exp(-i dt H)
    G = rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))
    H = 0.5 * (G + G.conj().T) / np.sqrt(dim)
    U_step = la.expm(-0.25j * H)
    U_dag = U_step.conj().T

    psi0 = np.zeros(dim, dtype=np.complex128)
    psi0[0] = 1.0
    p_dep_per_layer = 0.012  # 1.2% error depolarizante efectivo por capa

    depths = [10, 20, 40, 60, 80, 100]
    curve = []
    for d in depths:
        # 1. Evolución unitaria numérica exacta ida y vuelta (Loschmidt echo: U_dag^d U^d |0>)
        psi = psi0.copy()
        for _ in range(d):
            psi = U_step @ psi
        for _ in range(d):
            psi = U_dag @ psi
        return_fidelity_exact = float(np.abs(psi[0]) ** 2)
        unitarity_norm_drift = abs(float(np.linalg.norm(psi)) - 1.0)

        # 2. Evolución de matriz de densidad con canal depolarizante global por paso (2*d capas en ida+vuelta)
        rho = np.outer(psi0, psi0.conj())
        for _ in range(d):
            rho = U_step @ rho @ U_dag
            rho = (1.0 - p_dep_per_layer) * rho + (p_dep_per_layer / dim) * np.eye(dim, dtype=np.complex128)
        for _ in range(d):
            rho = U_dag @ rho @ U_step
            rho = (1.0 - p_dep_per_layer) * rho + (p_dep_per_layer / dim) * np.eye(dim, dtype=np.complex128)
        return_fidelity_nisq = float(np.real(rho[0, 0]))

        curve.append({
            "one_way_depth": d,
            "total_mirror_layers": 2 * d,
            "nisq_return_fidelity": round(return_fidelity_nisq, 6),
            "exact_expm_return_fidelity": round(return_fidelity_exact, 15),
            "exact_norm_drift": unitarity_norm_drift,
        })

    latency_ms = (time.perf_counter() - t0) * 1000.0
    report = {
        "scope_disclaimer": "Exact 6-qubit (D=64) Loschmidt mirror simulation in local CPU comparing `scipy.linalg.expm` vs CPTP depolarizing noise; NOT a 156-qubit quantum simulation.",
        "problem_id": "LOSCHMIDT_MIRROR_6Q_EXPM_VS_CPTP",
        "n_qubits": n_qubits,
        "depolarizing_rate_per_layer": p_dep_per_layer,
        "mirror_curve": curve,
        "latency_ms": round(latency_ms, 2),
        "exit_code": 0,
    }

    try:
        conn = psycopg2.connect(dbname="polydim_vec_db", user="postgres", password="postgres", host="localhost", port=5432)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO session_context (conversation_id, summary, category, created_at) VALUES (%s, %s, %s, NOW())",
            ("3f34edfc-4b9c-4658-84fc-10d32ef4da9b", json.dumps(report, ensure_ascii=False), "REPAIRED_LOSCHMIDT_MIRROR_6Q"),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB WARN] {e}")

    print("=== TEST DE ESPEJO LOSCHMIDT 6Q (EXACT EXPM vs CPTP NOISE) ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    run_loschmidt_mirror_6q()
