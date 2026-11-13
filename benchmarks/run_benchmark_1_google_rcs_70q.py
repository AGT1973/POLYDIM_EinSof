# -*- coding: utf-8 -*-
"""
CONTRACCIÓN DE CIRCUITOS ALEATORIOS (RCS) EN MPS vs VECTOR DE ESTADO EXACTO (12Q)
=================================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Esto es una simulación clásica exacta en CPU local sobre N=12 qubits midiendo la
  fidelidad real XEB (Cross-Entropy Benchmarking) y el crecimiento de la entropía
  de entrelazamiento frente a la dimensión de enlace chi.
  NO simula 70 qubits ni "demuele" supercomputadoras: demuestra mecánicamente por qué
  en circuitos aleatorios profundos la dimensión de enlace crece exponencialmente
  con la profundidad (ley de volumen), impidiendo colapsar 2^70 amplitudes a 70 floats.
"""

import time
import math
import json
import numpy as np
import psycopg2


def random_su4_gate(rng: np.random.Generator) -> np.ndarray:
    z = rng.standard_normal((4, 4)) + 1j * rng.standard_normal((4, 4))
    q, r = np.linalg.qr(z)
    d = np.diag(r)
    ph = d / np.abs(d)
    return q * ph[None, :]


def apply_2q_statevec(psi: np.ndarray, U4: np.ndarray, q0: int, q1: int, n_q: int) -> np.ndarray:
    t = psi.reshape((2,) * n_q)
    ut = U4.reshape(2, 2, 2, 2)
    out = np.tensordot(ut, t, axes=([2, 3], [q0, q1]))
    out = np.moveaxis(out, [0, 1], [q0, q1])
    return out.reshape(-1)


def apply_2q_mps_adjacent(mps: list, U4: np.ndarray, i: int, chi_max: int):
    # mps[i]: (l, 2, m), mps[i+1]: (m, 2, r)
    theta = np.tensordot(mps[i], mps[i + 1], axes=([2], [0]))  # (l, s0, s1, r)
    ut = U4.reshape(2, 2, 2, 2)
    theta = np.tensordot(ut, theta, axes=([2, 3], [1, 2]))      # (s0', s1', l, r)
    theta = np.transpose(theta, (2, 0, 1, 3))                   # (l, s0', s1', r)
    sh = theta.shape
    u, s, vt = np.linalg.svd(theta.reshape(sh[0] * 2, 2 * sh[3]), full_matrices=False)
    keep = min(chi_max, len(s))
    u = u[:, :keep]
    s = s[:keep]
    vt = vt[:keep, :]
    s /= np.linalg.norm(s)
    mps[i] = u.reshape(sh[0], 2, keep)
    mps[i + 1] = (s[:, None] * vt).reshape(keep, 2, sh[3])


def contract_mps_to_statevec(mps: list) -> np.ndarray:
    cur = mps[0]
    for t in mps[1:]:
        cur = np.tensordot(cur, t, axes=([-1], [0]))
    return cur.reshape(-1)


def run_honest_rcs_scaling():
    t0 = time.perf_counter()
    n_qubits = 12
    dim = 1 << n_qubits  # 4,096 amplitudes complejas exactas
    depth_cycles = 14
    rng = np.random.default_rng(20261107)

    # Generar ladrillos brickwork de puertas Haar SU(4)
    circuit_layers = []
    for cyc in range(depth_cycles):
        offset = cyc % 2
        layer = [(q, q + 1, random_su4_gate(rng)) for q in range(offset, n_qubits - 1, 2)]
        circuit_layers.append(layer)

    # 1. Evolución exacta del vector de estado completo en C^{4096}
    psi_exact = np.zeros(dim, dtype=np.complex128)
    psi_exact[0] = 1.0
    for layer in circuit_layers:
        for q0, q1, U4 in layer:
            psi_exact = apply_2q_statevec(psi_exact, U4, q0, q1, n_qubits)

    # Entropía de entrelazamiento bipartita a mitad de cadena (corte 6|6: chi exacto máximo = 2^6 = 64)
    sv_mid = np.linalg.svd(psi_exact.reshape(1 << 6, 1 << 6), compute_uv=False)
    p_schmidt = (sv_mid ** 2)
    p_schmidt = p_schmidt[p_schmidt > 1e-30]
    bipartite_entropy_bits = float(-np.sum(p_schmidt * np.log2(p_schmidt)))
    p_ideal = np.abs(psi_exact) ** 2

    # 2. Contracción aproximada por MPS a distintos límites de dimensión de enlace chi_max
    chi_sweep = []
    for chi in (4, 8, 16, 32, 64):
        mps = [np.zeros((1, 2, 1), dtype=np.complex128) for _ in range(n_qubits)]
        for q in range(n_qubits):
            mps[q][0, 0, 0] = 1.0
        for layer in circuit_layers:
            for q0, q1, U4 in layer:
                apply_2q_mps_adjacent(mps, U4, q0, chi_max=chi)
        psi_mps = contract_mps_to_statevec(mps)
        psi_mps /= np.linalg.norm(psi_mps)
        overlap_fidelity = float(np.abs(np.vdot(psi_exact, psi_mps)) ** 2)
        p_mps = np.abs(psi_mps) ** 2
        # Fidelidad lineal XEB cruzada normalizada respecto al Porter-Thomas ideal
        xeb_ideal = float(dim * np.sum(p_ideal * p_ideal) - 1.0)
        xeb_mps = float((dim * np.sum(p_ideal * p_mps) - 1.0) / max(xeb_ideal, 1e-12))
        chi_sweep.append({
            "chi_max": chi,
            "state_overlap_fidelity": round(overlap_fidelity, 8),
            "normalized_fxeb": round(xeb_mps, 8),
        })

    latency_ms = (time.perf_counter() - t0) * 1000.0
    report = {
        "scope_disclaimer": "Exact 12-qubit brickwork RCS vs truncated MPS simulation on local CPU; demonstrates volume-law entanglement barrier (chi=64 needed at N=12), NOT a 70-qubit simulation.",
        "problem_id": "RCS_VOLUME_LAW_MPS_FIDELITY_BENCHMARK",
        "n_qubits": n_qubits,
        "depth_cycles": depth_cycles,
        "half_chain_entanglement_entropy_bits": round(bipartite_entropy_bits, 6),
        "max_possible_half_chain_entropy_bits": 6.0,
        "mps_bond_dimension_fidelity_curve": chi_sweep,
        "latency_ms": round(latency_ms, 2),
        "exit_code": 0,
    }

    try:
        conn = psycopg2.connect(dbname="polydim_vec_db", user="postgres", password="postgres", host="localhost", port=5432)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO session_context (conversation_id, summary, category, created_at) VALUES (%s, %s, %s, NOW())",
            ("3f34edfc-4b9c-4658-84fc-10d32ef4da9b", json.dumps(report, ensure_ascii=False), "REPAIRED_RCS_MPS_VOLUME_LAW"),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB WARN] {e}")

    print("=== BENCHMARK HONESTO RCS: LEY DE VOLUMEN Y FIDELIDAD XEB EN MPS (12Q) ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    run_honest_rcs_scaling()
