# -*- coding: utf-8 -*-
"""
=============================================================================
POLYDIM / EINSOF — S=1 HALDANE SPIN CHAIN (N=10): ANTIPODAL STRING ORDER & GAP
=============================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Esto es una diagonalización matrix-free exacta por Stiefel-Lanczos en CPU local
  sobre cadenas antiferromagnéticas de espín entero S=1 de N=10 sitios (3^10 = 59.049
  estados totales; sectores S_z=0 de dim 8.953 y S_z=+1 de dim 8.350), NO una
  ejecución en QPU ni una prueba del límite termodinámico (Delta_H(inf) = 0.41048 J,
  White & Huse 1993). Referencias fundacionales: Haldane (1983), Affleck-Kennedy-
  Lieb-Tasaki (1987), den Nijs & Rommelse (1989), Kennedy & Tasaki (1992).

Correcciones matemáticas críticas frente a la versión defectuosa previa:
  1. Se corrigió el bug geométrico grave de evaluar O_string(0, N-1) en un anillo
     periódico (PBC): en PBC los sitios 0 y N-1 son VECINOS INMEDIATOS (r=1) a través
     de la frontera y sum_{m=0}^{N-1} S_m^z = 0 fuerza la identidad trivial
     O_string(0, N-1) == -<S_0^z S_{N-1}^z>! Ahora se evalúa en la verdadera
     separación ANTIPODAL máxima r = N/2 = 5 (`site_j=0, site_k=5`) y en todo el
     perfil espacial r = 1..5.
  2. Se eliminó el llamado a `np.linalg.eigh` denso: tanto el estado base singlete
     E_0 (sector S_z=0, D=8.953) como el primer estado excitado triplete de Haldane
     E_1 (estado base del sector S_z=+1, D=8.350) se obtienen puramente mediante el
     solver matrix-free `stiefel_lanczos_ground_state` con residuo <= 1e-11.
=============================================================================
"""

import os
import sys
import time
import math
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, "E:/POLYDIM_EINSOF/quantum")
sys.path.insert(0, "E:/PMTP")

from einsof_manifold_lanczos import stiefel_lanczos_ground_state, dot2_real_vec, neumaier_norm2


def build_spin1_sector_operator(n_spins: int = 10, target_sz: int = 0, pbc: bool = True):
    """
    Construye el operador matrix-free vectorizado del modelo de Heisenberg S=1:
      H = sum_b [ S_b^z S_{b+1}^z + (1/2)(S_b^+ S_{b+1}^- + S_b^- S_{b+1}^+) ]
    Codificando cada estado en base 3 con dígitos d_i = s_i + 1 in {0, 1, 2} (s_i in {-1, 0, +1}).
    """
    total_dim = 3 ** n_spins
    idx_all = np.arange(total_dim, dtype=np.int32)
    digits = np.zeros((total_dim, n_spins), dtype=np.int8)
    tmp = idx_all.copy()
    powers3 = [1] * n_spins
    for k in range(n_spins):
        if k > 0:
            powers3[k] = powers3[k - 1] * 3
        digits[:, k] = (tmp % 3) - 1  # s_k in {-1, 0, +1}
        tmp //= 3

    mask_sector = np.sum(digits, axis=1) == target_sz
    sec_codes = idx_all[mask_sector]
    sec_spins = digits[mask_sector]  # shape (D_sec, n_spins), valores en {-1, 0, +1}
    D_sec = len(sec_codes)

    code_to_pos = np.full(total_dim, -1, dtype=np.int32)
    code_to_pos[sec_codes] = np.arange(D_sec, dtype=np.int32)

    bonds = [(b, (b + 1) % n_spins) for b in range(n_spins if pbc else n_spins - 1)]
    diag = np.zeros(D_sec, dtype=np.float64)
    transitions = []

    # En S=1, <s+1|S^+|s> = sqrt(2) para s in {-1, 0}, y <s-1|S^-|s> = sqrt(2) para s in {0, +1}.
    # Por lo tanto, (1/2) S_a^+ S_b^- tiene elemento de matriz exactamente (1/2)*sqrt(2)*sqrt(2) = +1.0!
    for a, b in bonds:
        sa = sec_spins[:, a].astype(np.float64)
        sb = sec_spins[:, b].astype(np.float64)
        diag += sa * sb

        # Canal 1: S_a^+ S_b^- (válido donde s_a < +1 y s_b > -1)
        valid_pm = (sec_spins[:, a] < 1) & (sec_spins[:, b] > -1)
        src_pm = np.nonzero(valid_pm)[0]
        new_codes_pm = sec_codes[src_pm] + powers3[a] - powers3[b]
        dst_pm = code_to_pos[new_codes_pm]
        transitions.append((src_pm, dst_pm))

        # Canal 2: S_a^- S_b^+ (válido donde s_a > -1 y s_b < +1)
        valid_mp = (sec_spins[:, a] > -1) & (sec_spins[:, b] < 1)
        src_mp = np.nonzero(valid_mp)[0]
        new_codes_mp = sec_codes[src_mp] - powers3[a] + powers3[b]
        dst_mp = code_to_pos[new_codes_mp]
        transitions.append((src_mp, dst_mp))

    def matvec(v: np.ndarray) -> np.ndarray:
        out = diag * v
        for src, dst in transitions:
            out[dst] += v[src]
        return out

    return matvec, sec_spins, D_sec


def measure_correlations_profile(psi: np.ndarray, sec_spins: np.ndarray) -> list:
    """
    Mide para r = 1 .. N//2:
      - Correlación local de 2 puntos: C_zz(0, r) = <S_0^z S_r^z> y (-1)^r C_zz(0, r)
      - Orden de cuerda no-local de den Nijs-Rommelse:
          O_string(0, r) = - <psi | S_0^z * exp(i * pi * sum_{m=1}^{r-1} S_m^z) * S_r^z | psi>
        donde exp(i * pi * S_m^z) = (-1)^{|S_m^z|} en S_m^z in {-1, 0, +1}.
    """
    n_spins = sec_spins.shape[1]
    prob = psi * psi
    s0 = sec_spins[:, 0].astype(np.float64)
    profile = []

    for r in range(1, (n_spins // 2) + 1):
        sr = sec_spins[:, r].astype(np.float64)
        c_zz = dot2_real_vec(prob, s0 * sr)
        staggered_zz = ((-1.0) ** r) * c_zz

        if r == 1:
            phase = np.ones_like(s0)
        else:
            interior_abs_sum = np.sum(np.abs(sec_spins[:, 1:r]), axis=1)
            phase = np.where((interior_abs_sum % 2) == 0, 1.0, -1.0)
        o_str = -dot2_real_vec(prob, s0 * phase * sr)

        profile.append({
            "distance_r": r,
            "two_point_czz": round(c_zz, 8),
            "staggered_czz": round(staggered_zz, 8),
            "string_order": round(o_str, 8),
        })
    return profile


def main():
    t0 = time.perf_counter()
    N = 10
    r_antipodal = N // 2  # r = 5 (máxima separación real en anillo periódico de 10 sitios)

    print("=" * 80)
    print(f"POLYDIM / EINSOF — S=1 HALDANE CHAIN (N={N}, 3^10=59,049): MATRIX-FREE LANCZOS")
    print("[NOTA HONESTIDAD RADICAL]: Diagonalización exacta de cadena finita N=10 en CPU")
    print("local (sin eigh denso; O_string medido en separación antipodal real r = N/2 = 5).")
    print("=" * 80)

    # 1. Cadena Periódica (PBC): Estado base singlete (S_z=0) y excitado triplete de Haldane (S_z=+1)
    mv_pbc_sz0, spins_pbc_sz0, D_sz0 = build_spin1_sector_operator(N, target_sz=0, pbc=True)
    mv_pbc_sz1, _, D_sz1 = build_spin1_sector_operator(N, target_sz=1, pbc=True)

    res_pbc_0 = stiefel_lanczos_ground_state(mv_pbc_sz0, D_sz0, max_krylov=85, tol=1e-11, seed=42)
    res_pbc_1 = stiefel_lanczos_ground_state(mv_pbc_sz1, D_sz1, max_krylov=85, tol=1e-11, seed=42)

    e0_pbc = res_pbc_0["energy"]
    e1_pbc = res_pbc_1["energy"]
    haldane_gap_n10 = e1_pbc - e0_pbc  # Valor exacto literatura N=10 PBC (Golinelli-Jolicoeur-Lacaze 1994): 0.524808 J

    print(f"[1] Cadena Periódica PBC (N={N}, D_Sz0={D_sz0:,}, D_Sz1={D_sz1:,}):")
    print(f"    -> E_0 (Singlete S_z=0):         {e0_pbc:+.10f} J (res = {res_pbc_0['residual_norm']:.2e})")
    print(f"    -> E_1 (Triplete Haldane S_z=1): {e1_pbc:+.10f} J (res = {res_pbc_1['residual_norm']:.2e})")
    print(f"    -> Brecha finita N=10 Delta_H:   {haldane_gap_n10:.8f} J (Límite N->inf White 1993: 0.41048 J)")

    # 2. Perfil espacial completo r = 1..5: decaimiento de C_zz(0, r) vs persistencia de O_string(0, r)
    profile = measure_correlations_profile(res_pbc_0["psi"], spins_pbc_sz0)
    antipodal = profile[-1]  # r = 5

    print(f"\n[2] Perfil de Correlación en PBC (r = 1 .. {r_antipodal}, corrigiendo bug previo r=1 en (0,N-1)):")
    for row in profile:
        print(
            f"    r = {row['distance_r']} | (-1)^r <S_0^z S_r^z> = {row['staggered_czz']:+.6f} | "
            f"O_string(0, {row['distance_r']}) = {row['string_order']:+.6f}"
        )
    assert antipodal["string_order"] > 1.8 * antipodal["staggered_czz"], "O_string debe dominar sobre C_zz en r=N/2"

    # 3. Cadena Abierta (OBC): Cuasi-degeneración singlete-triplete de los modos fraccionarios de borde S=1/2
    mv_obc_sz0, _, _ = build_spin1_sector_operator(N, target_sz=0, pbc=False)
    mv_obc_sz1, _, _ = build_spin1_sector_operator(N, target_sz=1, pbc=False)
    res_obc_0 = stiefel_lanczos_ground_state(mv_obc_sz0, D_sz0, max_krylov=85, tol=1e-11, seed=108)
    res_obc_1 = stiefel_lanczos_ground_state(mv_obc_sz1, D_sz1, max_krylov=85, tol=1e-11, seed=108)
    edge_splitting_obc = abs(res_obc_1["energy"] - res_obc_0["energy"])

    print(f"\n[3] Cadena Abierta OBC (Modos de Borde Fraccionarios S=1/2 acoplados en cadena finita N={N}):")
    print(f"    -> E(S_z=0, OBC) = {res_obc_0['energy']:+.10f} J | E(S_z=1, OBC) = {res_obc_1['energy']:+.10f} J")
    print(f"    -> Desdoblamiento de borde |E_1 - E_0|_OBC = {edge_splitting_obc:.6f} J (<< Delta_H_PBC = {haldane_gap_n10:.6f} J)")

    t_total_ms = (time.perf_counter() - t0) * 1000.0
    output_data = {
        "scope_disclaimer": (
            "Exact matrix-free Stiefel-Lanczos diagonalization on local CPU for the N=10 spin-1 Heisenberg "
            "antiferromagnet (3^10=59,049 states; D_Sz0=8,953, D_Sz1=8,350). Evaluates den Nijs-Rommelse string "
            "order at true antipodal distance r=N/2=5 and finite-size Haldane gap without dense diagonalization; "
            "NOT a QPU run nor an infinite-chain proof."
        ),
        "problem": "HALDANE_SPIN1_CHAIN_N10_ANTIPODAL_STRING_ORDER_AND_GAP",
        "n_spins": N,
        "hilbert_dim_total": 3 ** N,
        "hilbert_dim_sz0": D_sz0,
        "hilbert_dim_sz1": D_sz1,
        "pbc_singlet_e0": round(e0_pbc, 10),
        "pbc_triplet_e1": round(e1_pbc, 10),
        "finite_size_haldane_gap_n10": round(haldane_gap_n10, 8),
        "thermodynamic_limit_reference_white1993": 0.41048,
        "pbc_e0_residual_norm": res_pbc_0["residual_norm"],
        "pbc_e1_residual_norm": res_pbc_1["residual_norm"],
        "antipodal_distance_r": r_antipodal,
        "antipodal_string_order": antipodal["string_order"],
        "antipodal_staggered_two_point": antipodal["staggered_czz"],
        "spatial_correlation_profile": profile,
        "obc_sz0_energy": round(res_obc_0["energy"], 10),
        "obc_sz1_energy": round(res_obc_1["energy"], 10),
        "obc_edge_mode_splitting": round(edge_splitting_obc, 8),
        "neumaier_drift": res_pbc_0["stiefel_state_drift"],
        "execution_ms": round(t_total_ms, 2),
        "exit_code": 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, "haldane_gap_string_order.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n[4] Datos guardados en {data_path}")

    try:
        from pmtp_polydim_vector_swarm import PersistentMmapSlabBus
        import psycopg2

        bus = PersistentMmapSlabBus()
        meta_slab = bus.write_tensor_slab(0x504D0107, res_pbc_0["psi"])
        conn = psycopg2.connect("dbname=polydim_vec_db user=postgres password=postgres host=localhost port=5432")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO session_context (conversation_id, summary, category, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id;
            """,
            ("c8f6b7cd-c96d-4bc0-9428-ccccee03234c", json.dumps(output_data, ensure_ascii=False), "REPAIRED_HALDANE_N10_ANTIPODAL_LANCZOS"),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"[5] PMTP Slab {meta_slab['slab_id_hex']} | PostgreSQL DB_ID: {row_id}")
    except Exception as e:
        print(f"[5] Aviso PMTP/DB opcional: {e}")

    print(f"[RESUMEN] Exit Code 0 | Latencia: {t_total_ms:.2f} ms | Delta_H(N=10)={haldane_gap_n10:.6f} J | O_str(0,5)={antipodal['string_order']:.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
