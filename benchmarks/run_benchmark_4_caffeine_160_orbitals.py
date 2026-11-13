# -*- coding: utf-8 -*-
"""
OPTIMIZACIÓN RHF-SCF CONVERGIDA EN GRASSMANN Gr(40, 80) + CORRELACIÓN MP2
=========================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Este script ejecuta un ciclo autoconsistente Hartree-Fock Restringido (RHF-SCF)
  con aceleración DIIS de Pulay sobre M=80 orbitales espaciales (160 espín-orbitales,
  80 electrones) en la variedad de Grassmann Gr(40, 80), seguido de la corrección
  perturbativa de correlación electrónica de segundo orden de Møller-Plesset (MP2)
  sobre un Hamiltoniano modelo Cholesky-descompuesto positivo definido.
  NO resuelve Full Configuration Interaction (FCI, binom(160,80) ~ 3.6e46 estados)
  ni sustituye integrales ab initio multirreferenciales fuertes.
"""

import time
import math
import json
import numpy as np
import scipy.linalg as la
import psycopg2


def run_converged_rhf_and_mp2():
    t0 = time.perf_counter()
    n_spatial = 80       # 160 espín-orbitales
    n_occ = 40           # 80 electrones (capa cerrada)
    n_virt = n_spatial - n_occ
    n_chol = 60

    rng = np.random.default_rng(20261107)
    # Hamiltoniano 1-cuerpo H_core simétrico no diagonal (requiere optimización orbital real!)
    Q_rand, _ = np.linalg.qr(rng.standard_normal((n_spatial, n_spatial)))
    e_core = np.linspace(-3.5, 1.5, n_spatial)
    e_core[n_occ:] += 0.35
    H_core = Q_rand @ np.diag(e_core) @ Q_rand.T

    # Factores de Cholesky simétricos L^k para integrales de 2 electrones (pq|rs) = sum_k L^k_{pq} L^k_{rs}
    L_chol = rng.normal(0.0, 0.025, size=(n_chol, n_spatial, n_spatial))
    for k in range(n_chol):
        L_chol[k] = 0.5 * (L_chol[k] + L_chol[k].T)

    def build_fock_and_energy(P_spatial: np.ndarray):
        # En RHF (ocupación doble): D_tot = 2 * P, con P = C_occ C_occ^T in Gr(n_occ, n_spatial)
        # J_{pq} = 2 * sum_k L^k_{pq} Tr(L^k P),  K_{pq} = sum_k (L^k P L^k)_{pq}
        traces = np.einsum("kpq,pq->k", L_chol, P_spatial)
        J_mat = 2.0 * np.einsum("k,kpq->pq", traces, L_chol)
        LP = np.einsum("kpq,qr->kpr", L_chol, P_spatial)
        K_mat = np.einsum("kpr,krs->ps", LP, L_chol)
        F = H_core + J_mat - K_mat
        e_rhf = float(np.sum((H_core + F) * P_spatial))
        return F, e_rhf

    # Guess inicial: diagonalizar solo H_core (NO converge Fock todavía)
    _, C = la.eigh(H_core)
    P = C[:, :n_occ] @ C[:, :n_occ].T
    _, e_init = build_fock_and_energy(P)

    # Iteraciones RHF-SCF con DIIS de Pulay sobre el residuo tangente de Grassmann R = F P - P F
    fock_hist = []
    err_hist = []
    max_scf = 40
    scf_converged = False
    comm_norm = float("inf")
    e_rhf = e_init
    eps_orb = None

    for it in range(1, max_scf + 1):
        F, e_rhf = build_fock_and_energy(P)
        R_grad = F @ P - P @ F  # Gradiente en el espacio tangente de Gr(n_occ, n_spatial)
        comm_norm = float(np.linalg.norm(R_grad, ord="fro"))

        fock_hist.append(F)
        err_hist.append(R_grad.ravel())
        if len(fock_hist) > 6:
            fock_hist.pop(0)
            err_hist.pop(0)

        if comm_norm < 1e-11:
            eps_orb, C = la.eigh(F)
            P = C[:, :n_occ] @ C[:, :n_occ].T
            _, e_rhf = build_fock_and_energy(P)
            scf_converged = True
            scf_iters = it
            break

        if len(fock_hist) >= 2:
            m = len(fock_hist)
            B = np.zeros((m + 1, m + 1), dtype=np.float64)
            B[-1, :m] = -1.0
            B[:m, -1] = -1.0
            for a in range(m):
                for b in range(a, m):
                    val = float(np.dot(err_hist[a], err_hist[b]))
                    B[a, b] = val
                    B[b, a] = val
            rhs = np.zeros(m + 1, dtype=np.float64)
            rhs[-1] = -1.0
            try:
                coeffs = np.linalg.solve(B, rhs)[:m]
                F_extrap = sum(c * f_m for c, f_m in zip(coeffs, fock_hist))
            except np.linalg.LinAlgError:
                F_extrap = F
        else:
            F_extrap = F

        eps_orb, C = la.eigh(F_extrap)
        P = C[:, :n_occ] @ C[:, :n_occ].T
    else:
        scf_iters = max_scf

    assert scf_converged, f"RHF-SCF no convergió: ||[F,P]||_F = {comm_norm}"

    # Verificar idempotencia/ortonormalidad en St(40, 80)
    C_occ = C[:, :n_occ]
    C_virt = C[:, n_occ:]
    stiefel_ortho_err = float(np.linalg.norm(C_occ.T @ C_occ - np.eye(n_occ), ord="fro"))

    # Corrección de correlación electrónica post-HF real: Møller-Plesset de 2do orden (MP2)
    # Transformar Cholesky al bloque ocupado-virtual: B^k_{ia} = (C_occ^T L^k C_virt)_{ia}
    B_ia = np.einsum("pi,kpq,qa->kia", C_occ, L_chol, C_virt, optimize=True)
    # (ia|jb) = sum_k B^k_{ia} B^k_{jb}
    iajb = np.einsum("kia,kjb->iajb", B_ia, B_ia, optimize=True)
    ibja = np.swapaxes(iajb, 1, 3)  # (ib|ja)
    e_occ = eps_orb[:n_occ]
    e_virt = eps_orb[n_occ:]
    denom = e_occ[:, None, None, None] + e_occ[None, :, None, None] - e_virt[None, None, :, None] - e_virt[None, None, None, :]
    e_mp2 = float(np.sum(iajb * (2.0 * iajb - ibja) / denom))

    latency_ms = (time.perf_counter() - t0) * 1000.0
    report = {
        "scope_disclaimer": "Converged RHF-SCF (DIIS on Gr(40,80)) + MP2 correlation on synthetic positive-definite Cholesky Hamiltonian in local CPU; O(M^4-M^5) classical post-HF, NOT exponential Full CI nor real molecular basis integrals.",
        "problem_id": "GRASSMANN_RHF_DIIS_AND_MP2_CORRELATION",
        "spin_orbitals": 2 * n_spatial,
        "spatial_orbitals": n_spatial,
        "electrons": 2 * n_occ,
        "initial_core_guess_energy_Ha": round(e_init, 8),
        "converged_rhf_energy_Ha": round(e_rhf, 10),
        "scf_lowering_Ha": round(e_rhf - e_init, 10),
        "mp2_correlation_energy_Ha": round(e_mp2, 10),
        "total_rhf_plus_mp2_energy_Ha": round(e_rhf + e_mp2, 10),
        "scf_iterations": scf_iters,
        "brillouin_commutator_residual": comm_norm,
        "stiefel_orthonormality_err": stiefel_ortho_err,
        "homo_lumo_gap_Ha": round(float(eps_orb[n_occ] - eps_orb[n_occ - 1]), 6),
        "latency_ms": round(latency_ms, 2),
        "exit_code": 0,
    }

    try:
        conn = psycopg2.connect(dbname="polydim_vec_db", user="postgres", password="postgres", host="localhost", port=5432)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO session_context (conversation_id, summary, category, created_at) VALUES (%s, %s, %s, NOW())",
            ("3f34edfc-4b9c-4658-84fc-10d32ef4da9b", json.dumps(report, ensure_ascii=False), "REPAIRED_GRASSMANN_RHF_MP2"),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB WARN] {e}")

    print("=== OPTIMIZACIÓN CONVERGIDA RHF-SCF EN Gr(40,80) + CORRELACIÓN MP2 ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    run_converged_rhf_and_mp2()
