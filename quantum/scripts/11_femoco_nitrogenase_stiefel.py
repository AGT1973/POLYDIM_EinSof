# -*- coding: utf-8 -*-
"""
=============================================================================
POLYDIM / EINSOF — REDUCED [Fe4S4]+ CUBANE EFFECTIVE KRAMERS SPIN MODEL (S=3/2)
=============================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Esto es una simulación numérica exacta en CPU local de un Hamiltoniano efectivo
  de espín de valencia mixta de 9 espines-1/2 (D = 2^9 = 512, número IMPAR de
  electrones desapareados para permitir multipletes semienteros de Kramers
  S_tot in {1/2, 3/2, ...}) representativo de un sub-cubano reducido [Fe4S4]+.
  NO es un cálculo cuántico ab initio de estructura electrónica completa del
  cofactor FeMoco [MoFe7S9C] (benchmark de 54-76 orbitales activos de Reiher et al.
  2017, PNAS 114, 7566; Li, Sharma, Chan et al. 2019), ni una ejecución en QPU.

Correcciones críticas frente a la versión defectuosa previa:
  1. Se corrigió la imposibilidad algebraica de paridad de espín: el script previo
     usaba 8 espines-1/2 (número PAR -> S_tot entero in {0,1,2,3,4}), haciendo
     matemáticamente imposible obtener el cuarteto biológico de Kramers S_tot = 3/2!
     Con N_s = 9 espines-1/2 acoplados en 4 centros de Fe (tres centros S_loc=1 de
     2 sub-espines y un centro de alto espín S_loc=3/2 de 3 sub-espines:
     1 + 1 + 1 + 3/2 -> S_tot semientero), el espacio admite genuinamente
     S_tot = 1/2 (<S^2>=0.75) y S_tot = 3/2 (<S^2>=3.75).
  2. Se resuelve en el sector M_z = +1/2 (D_sector = C(9,5) = 126, que contiene
     TODOS los multipletes semienteros S_tot >= 1/2 sin degeneración Zeeman trivial)
     mediante `stiefel_lanczos_ground_state` matrix-free, mapeando el cruce físico
     entre doblete S_tot = 1/2 y cuarteto S_tot = 3/2 en función del acoplamiento
     ferromagnético de doble intercambio B_dex (Noodleman / Mouesca).
=============================================================================
"""

import os
import sys
import time
import math
import json
import itertools
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, "E:/POLYDIM_EINSOF/quantum")
sys.path.insert(0, "E:/PMTP")

from einsof_manifold_lanczos import stiefel_lanczos_ground_state, dot2_real_vec, neumaier_norm2


def build_odd_electron_cubane_mz_half(b_double_exchange_meV: float = 26.0):
    """
    Construye matrix-free H y S_tot^2 en el sector M_z = +1/2 (5 up, 4 dn de 9 espines-1/2, D=126):
      - Fe0: espines (0, 1, 2) -> ion de alto espín efectivo S_Fe0 = 3/2 (acoplamiento Hund J_H = -40 meV)
      - Fe1: espines (3, 4)    -> S_Fe1 = 1 (par deslocalizado con Fe0 vía B_dex ferromagnético)
      - Fe2: espines (5, 6)    -> S_Fe2 = 1
      - Fe3: espines (7, 8)    -> S_Fe3 = 1
    Con superintercambio antiferromagnético tetraédrico J_AF entre el dímero (Fe0-Fe1) y (Fe2, Fe3)
    más frustración interna J_23 entre Fe2 y Fe3 que compite entre S_tot = 1/2 y S_tot = 3/2.
    """
    n_spins = 9
    n_up = 5  # M_z = (5 - 4)/2 = +1/2
    basis = [sum(1 << p for p in comb) for comb in itertools.combinations(range(n_spins), n_up)]
    D = len(basis)  # C(9,5) = 126
    idx_map = {st: idx for idx, st in enumerate(basis)}

    ions = [
        (0, 1, 2),  # Fe0 (3 sub-espines -> S_Fe0 = 3/2)
        (3, 4),     # Fe1 (2 sub-espines -> S_Fe1 = 1)
        (5, 6),     # Fe2 (2 sub-espines -> S_Fe2 = 1)
        (7, 8),     # Fe3 (2 sub-espines -> S_Fe3 = 1)
    ]

    # Lista de enlaces de intercambio Heisenberg J_pq * (S_p . S_q)
    pair_couplings = {}

    def add_bond(p: int, q: int, j_val: float):
        a, b = (p, q) if p < q else (q, p)
        pair_couplings[(a, b)] = pair_couplings.get((a, b), 0.0) + j_val

    # 1. Acoplamiento intra-iónico de Hund fuerte (bloquea espines locales S_Fe0=3/2, S_Fe1=S_Fe2=S_Fe3=1)
    J_hund = -60.0
    for grp in ions:
        for p, q in itertools.combinations(grp, 2):
            add_bond(p, q, J_hund)

    # 2. Superintercambio antiferromagnético Fe-S-Fe en el cubano
    # Enlaces dímero1 (Fe0, Fe1) <-> dímero2 (Fe2, Fe3): J_cross = +18.5 meV
    J_cross = 18.5
    for ion_a in (0, 1):
        for ion_b in (2, 3):
            scale = 1.0 / (len(ions[ion_a]) * len(ions[ion_b]))
            for p in ions[ion_a]:
                for q in ions[ion_b]:
                    add_bond(p, q, J_cross * scale)

    # Enlace antiferromagnético frustrado dentro del par férrico (Fe2 - Fe3): J_23 = +38.0 meV
    # (Compite con J_cross = +18.5 meV: estabiliza S_23 = 1 frente a S_23 = 2; así, cuando B_dex
    # estabiliza el dímero deslocalizado S_01 = 5/2, el acoplamiento AF |S_01 - S_23| = |5/2 - 1| = 3/2
    # produce exactamente el cuarteto de Kramers S_tot = 3/2, mientras que a bajo B_dex domina S_tot = 1/2!)
    J_23 = 38.0
    for p in ions[2]:
        for q in ions[3]:
            add_bond(p, q, J_23 / 4.0)

    # Enlace dentro del par de valencia mixta (Fe0 - Fe1): J_01_AF - B_double_exchange
    # Cuando B_dex es pequeño domina J_01_AF (+24 meV) -> S_01 = 1/2 -> se acopla con S_23 para dar S_tot = 1/2;
    # Cuando B_dex crece (~26-35 meV), estabiliza S_01 = 5/2 frente a S_23 = 1 -> estado fundamental S_tot = 3/2!
    J_01_eff = 24.0 - b_double_exchange_meV
    for p in ions[0]:
        for q in ions[1]:
            add_bond(p, q, J_01_eff / 6.0)

    H = np.zeros((D, D), dtype=np.float64)
    S2 = np.zeros((D, D), dtype=np.float64)

    all_pairs = list(itertools.combinations(range(n_spins), 2))
    for col, st in enumerate(basis):
        # S_tot^2 = sum_i (3/4) + 2 * sum_{p < q} S_p . S_q
        s2_diag = 0.75 * n_spins
        h_diag = 0.0
        for p, q in all_pairs:
            bp = (st >> p) & 1
            bq = (st >> q) & 1
            zz = 0.25 if (bp == bq) else -0.25
            s2_diag += 2.0 * zz
            j_pq = pair_couplings.get((p, q), 0.0)
            if j_pq != 0.0:
                h_diag += j_pq * zz
            if bp != bq:
                flipped = st ^ ((1 << p) | (1 << q))
                row = idx_map[flipped]
                S2[row, col] += 1.0  # 2.0 * 0.5
                if j_pq != 0.0:
                    H[row, col] += 0.5 * j_pq

        H[col, col] = h_diag
        S2[col, col] = s2_diag

    assert np.linalg.norm(H - H.T, ord="fro") < 1e-13
    assert np.linalg.norm(S2 - S2.T, ord="fro") < 1e-13
    return H, S2, basis, ions


def main():
    t0 = time.perf_counter()
    print("=" * 80)
    print("POLYDIM / EINSOF — REDUCED [Fe4S4]+ CUBANE KRAMERS SPIN SOLVER (9 SPINS, M_z=+1/2)")
    print("[NOTA HONESTIDAD RADICAL]: Modelo efectivo Heisenberg-doble-intercambio en CPU")
    print("local (9 espines-1/2, D_total=512, D_{Mz=1/2}=126); NO FCI ab initio de [MoFe7S9C].")
    print("=" * 80)

    # Barrer B_double_exchange para demostrar transición física real entre doblete S=1/2 y cuarteto S=3/2
    sweep_b = [8.0, 20.0, 32.0, 40.0]
    sweep_records = []
    target_psi = None
    target_record = None
    target_basis = None
    target_ions = None

    for b_dex in sweep_b:
        H, S2, basis, ions = build_odd_electron_cubane_mz_half(b_double_exchange_meV=b_dex)
        res = stiefel_lanczos_ground_state(
            lambda v: H @ v,
            len(basis),
            max_krylov=70,
            tol=1e-12,
            seed=42,
        )
        psi = res["psi"]
        e0 = res["energy"]
        evals_exact = np.linalg.eigvalsh(H)
        err_exact = abs(e0 - float(evals_exact[0]))
        assert err_exact < 1e-10, f"Discrepancia frente a eigvalsh: {err_exact}"

        s2_val = dot2_real_vec(psi, S2 @ psi)
        s_tot = 0.5 * (-1.0 + math.sqrt(max(0.0, 1.0 + 4.0 * s2_val)))

        rec = {
            "B_double_exchange_meV": b_dex,
            "ground_energy_meV": round(e0, 6),
            "exact_e0_meV": round(float(evals_exact[0]), 6),
            "abs_error_meV": err_exact,
            "residual_norm": res["residual_norm"],
            "s_tot_squared": round(s2_val, 6),
            "s_tot_quantum_number": round(s_tot, 6),
            "neumaier_drift": res["stiefel_state_drift"],
        }
        sweep_records.append(rec)
        print(
            f"  B_dex = {b_dex:4.1f} meV | E_0 = {e0:+10.4f} meV | <S_tot^2> = {s2_val:7.4f} "
            f"-> S_tot = {s_tot:.4f} | res = {res['residual_norm']:.2e}"
        )
        if b_dex == 32.0:
            target_psi = psi.copy()
            target_record = rec
            target_basis = basis
            target_ions = ions

    # Verificar que en el régimen de doble intercambio activo (B_dex = 32 meV) emerge exactamente S_tot = 3/2 (<S^2> = 3.75)
    assert abs(target_record["s_tot_squared"] - 3.75) < 1e-6, f"No se obtuvo S=3/2 exacto: {target_record}"

    # Calcular polarización magnética local <S_Fe,k^z> en el estado M_z = +1/2 (suma exacta = +0.500000)
    ion_sz = []
    prob = target_psi * target_psi
    for grp in target_ions:
        val_ion = 0.0
        for p in grp:
            signs = np.array([0.5 if ((st >> p) & 1) else -0.5 for st in target_basis], dtype=np.float64)
            val_ion += dot2_real_vec(prob, signs)
        ion_sz.append(round(val_ion, 6))
    sum_sz = sum(ion_sz)
    assert abs(sum_sz - 0.5) < 1e-4, f"Conservación de M_z=+1/2 violada: {sum_sz}"

    print(f"\n[2] Estado Cuarteto de Kramers Verificado en B_dex = 32.0 meV:")
    print(f"    -> <S_tot^2> = {target_record['s_tot_squared']:.6f} -> S_tot = {target_record['s_tot_quantum_number']:.6f} (Exacto 3/2)")
    print(f"    -> Polarizaciones <S_Fe^z> (M_z=+1/2): {ion_sz} (Suma = {sum_sz:+.6f})")

    t_total_ms = (time.perf_counter() - t0) * 1000.0
    output_data = {
        "scope_disclaimer": (
            "Exact CPU diagonalization via Stiefel-Lanczos of an odd-electron 9-spin-1/2 (D_full=512, "
            "D_Mz_half=126) effective Heisenberg-double-exchange [Fe4S4]+ cubane model demonstrating the "
            "S_tot=1/2 to S_tot=3/2 Kramers spin-state crossover. NOT a full ab initio [MoFe7S9C] FeMoco "
            "electronic structure calculation (Reiher et al. 2017) nor a QPU run."
        ),
        "problem": "REDUCED_FE4S4_CUBANE_ODD_ELECTRON_KRAMERS_SPIN_CROSSOVER",
        "n_subspins": 9,
        "hilbert_dim_full": 512,
        "hilbert_dim_mz_half": len(target_basis),
        "double_exchange_sweep": sweep_records,
        "quartet_regime_b32_meV": {
            "ground_energy_meV": target_record["ground_energy_meV"],
            "s_tot_squared": target_record["s_tot_squared"],
            "s_tot": target_record["s_tot_quantum_number"],
            "multiplet_label": "Kramers Quartet (S_tot = 3/2, <S^2> = 3.75)",
            "ion_sz_polarizations_mz_half": ion_sz,
            "total_mz_check": round(sum_sz, 6),
            "residual_norm": target_record["residual_norm"],
        },
        "neumaier_drift": target_record["neumaier_drift"],
        "execution_ms": round(t_total_ms, 2),
        "exit_code": 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, "femoco_nitrogenase_cubane.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n[3] Datos guardados en {data_path}")

    try:
        from pmtp_polydim_vector_swarm import PersistentMmapSlabBus
        import psycopg2

        bus = PersistentMmapSlabBus()
        meta_slab = bus.write_tensor_slab(0x504D00FE, target_psi)
        conn = psycopg2.connect("dbname=polydim_vec_db user=postgres password=postgres host=localhost port=5432")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO session_context (conversation_id, summary, category, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id;
            """,
            ("c8f6b7cd-c96d-4bc0-9428-ccccee03234c", json.dumps(output_data, ensure_ascii=False), "REPAIRED_FE4S4_KRAMERS_QUARTET"),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"[4] PMTP Slab {meta_slab['slab_id_hex']} | PostgreSQL DB_ID: {row_id}")
    except Exception as e:
        print(f"[4] Aviso PMTP/DB opcional: {e}")

    print(f"[RESUMEN] Exit Code 0 | Latencia: {t_total_ms:.2f} ms | S_tot={target_record['s_tot_quantum_number']:.4f} (<S^2>={target_record['s_tot_squared']:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
