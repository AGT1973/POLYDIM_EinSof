# -*- coding: utf-8 -*-
"""
=============================================================================
POLYDIM / EINSOF — SACHDEV-YE-KITAEV (SYK_4): BOTT PERIODICITY & RMT SPECTRUM
=============================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Esto es una diagonalización exacta de ensamble finito en CPU local para el
  modelo de fermiones de Majorana SYK_4 con N=16 (8 qubits, D_even=128, 1.820
  acoplamientos cuárticos aleatorios) y comparación con N=12 (6 qubits, D_even=32),
  NO una ejecución en hardware cuántico ni una prueba en el límite holográfico
  N -> infinito de gravedad JT en AdS_2.

Correcciones matemáticas críticas frente a la versión defectuosa previa:
  1. Clasificación exacta de periodicidad de Bott de Altland-Zirnbauer (You-Ludwig-Xu
     2017, PRB 95, 115150; Cotler et al. 2017, JHEP):
       - Para N = 12 Majoranas (N mod 8 == 4), la simetría partícula-hueco cumple
         P^2 = -1 (degeneración de Kramers) y la estadística pertenece a **GSE**
         (<r>_GSE = 0.6744), NO a GOE (0.5359) como afirmaba erróneamente el script previo.
       - Para N = 16 Majoranas (N mod 8 == 0, 8 qubits, D=256, D_even=128), P^2 = +1
         y el espectro pertenece genuinamente a **GOE** (<r>_GOE = 0.5359).
  2. Se implementó acción bitwise rápida de cadenas de Pauli de Jordan-Wigner,
     permitiendo resolver N=16 (1.820 términos cuárticos) con `stiefel_lanczos_ground_state`
     a residuo propio <= 1e-12 y promediar <r> sobre un ensamble de realizaciones de desorden.
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

from einsof_manifold_lanczos import stiefel_lanczos_ground_state, neumaier_norm2


def majorana_pauli_masks(n_majoranas: int) -> list:
    """
    Representa cada operador de Majorana chi_a (normalizado tal que {chi_a, chi_b} = delta_{ab}
    o convención estándar chi_a^2 = 1/2 -> aquí usamos convención estándar de física de alta energía
    {chi_a, chi_b} = delta_{ab}, o sea chi = sigma / sqrt(2)) mediante tuplas bitwise (x_mask, z_mask, phase):
      P |s> = phase * (-1)^{popcount(s & z_mask)} |s ^ x_mask>
    """
    n_qubits = n_majoranas // 2
    ops = []
    scale = 1.0 / math.sqrt(2.0)
    # Qubit k: X_k -> x=(1<<k), z=0, phase=1; Y_k |b_k> = i (-1)^{b_k} |1-b_k> -> x=(1<<k), z=(1<<k), phase=+1j
    # Cadena Z_{0..k-1}: z |= ((1<<k) - 1)
    for k in range(n_qubits):
        z_prefix = (1 << k) - 1
        ops.append((1 << k, z_prefix, complex(scale, 0.0)))             # chi_{2k}
        ops.append((1 << k, z_prefix | (1 << k), complex(0.0, scale)))  # chi_{2k+1}
    return ops


def multiply_pauli_masks(op1: tuple, op2: tuple) -> tuple:
    """
    Multiplica dos operadores monomiales A * B donde:
      A |s> = c1 * (-1)^{pop(s & z1)} |s ^ x1>
      B |s> = c2 * (-1)^{pop(s & z2)} |s ^ x2>
    Entonces A (B |s>) = c1 * c2 * (-1)^{pop((s ^ x2) & z1) + pop(s & z2)} |s ^ x1 ^ x2>
                       = [c1 * c2 * (-1)^{pop(x2 & z1)}] * (-1)^{pop(s & (z1 ^ z2))} |s ^ (x1 ^ x2)|.
    """
    x1, z1, c1 = op1
    x2, z2, c2 = op2
    sign = -1.0 if ((x2 & z1).bit_count() % 2 == 1) else 1.0
    return (x1 ^ x2, z1 ^ z2, c1 * c2 * sign)


def build_syk4_even_parity_matrix(n_majoranas: int, j_scale: float = 1.0, seed: int = 1973) -> tuple:
    """
    Construye exactamente H_even para SYK_4 con convención {chi_i, chi_j} = delta_{ij}:
      H = sum_{0 <= i < j < k < l < N} J_{ijkl} chi_i chi_j chi_k chi_l,
      Var(J_{ijkl}) = 3! * J^2 / N^3 = 6 * J^2 / N^3.
    """
    n_qubits = n_majoranas // 2
    dim_full = 1 << n_qubits
    states_full = np.arange(dim_full, dtype=np.int32)
    # Paridad fermiónica P = Z_0 Z_1 ... Z_{M-1} -> (-1)^{popcount(s)}; sector par tiene popcount par
    pop_all = np.array([int(s).bit_count() for s in range(dim_full)], dtype=np.int32)
    even_states = states_full[(pop_all % 2) == 0]
    dim_even = len(even_states)
    state_to_even = np.full(dim_full, -1, dtype=np.int32)
    state_to_even[even_states] = np.arange(dim_even, dtype=np.int32)

    maj = majorana_pauli_masks(n_majoranas)
    rng = np.random.default_rng(seed)
    sigma = math.sqrt(6.0 * (j_scale ** 2) / (n_majoranas ** 3))

    # Agrupar términos por x_mask único (como máximo 2^{n_qubits-1} = 128 permutaciones pares!)
    # Cada cuádrupla (i<j<k<l) invierte un número par de bits o preserva paridad total:
    H_even = np.zeros((dim_even, dim_even), dtype=np.complex128)
    n_terms = 0

    # Precomputar tabla de paridad popcount(s & z) para z in 0..dim_full-1 y s in even_states
    parity_sign = np.where((np.bitwise_and(even_states[:, None], states_full[None, :])) != 0, 0, 0)
    # Cálculo rápido de (-1)^{popcount(even_states[:, None] & z)} por bits
    bit_xor = np.zeros((dim_even, dim_full), dtype=np.int8)
    for b in range(n_qubits):
        has_s = ((even_states >> b) & 1).astype(np.int8)[:, None]
        has_z = ((states_full >> b) & 1).astype(np.int8)[None, :]
        bit_xor ^= (has_s & has_z)
    sign_table = np.where(bit_xor == 0, 1.0, -1.0)  # shape (dim_even, dim_full)

    # Acumular coeficientes complejos para cada par (x_mask, z_mask) en una grilla (dim_full, dim_full)
    coeff_grid = np.zeros((dim_full, dim_full), dtype=np.complex128)
    combos = list(itertools.combinations(range(n_majoranas), 4))
    couplings = rng.normal(0.0, sigma, size=len(combos))

    for idx_c, (i, j, k, l) in enumerate(combos):
        op12 = multiply_pauli_masks(maj[i], maj[j])
        op34 = multiply_pauli_masks(maj[k], maj[l])
        x_m, z_m, c_m = multiply_pauli_masks(op12, op34)
        coeff_grid[x_m, z_m] += couplings[idx_c] * c_m
        n_terms += 1

    # Para cada x_mask activo, vector_diag_x(s) = sum_z coeff_grid[x_mask, z] * (-1)^{pop(s & z)}
    active_x = np.nonzero(np.any(np.abs(coeff_grid) > 0.0, axis=1))[0]
    row_arange = np.arange(dim_even, dtype=np.int32)
    for x_m in active_x:
        vec_s = sign_table @ coeff_grid[x_m]  # (dim_even,)
        dst_states = even_states ^ int(x_m)
        dst_rows = state_to_even[dst_states]
        H_even[dst_rows, row_arange] += vec_s

    herm_err = float(np.linalg.norm(H_even - H_even.conj().T, ord="fro"))
    assert herm_err < 1e-13, f"H_even no hermítico: {herm_err}"
    return H_even, n_terms, herm_err


def compute_bulk_gap_ratio(evals: np.ndarray, trim_frac: float = 0.15) -> float:
    """
    Calcula <r_n> = <min(s_n, s_{n-1}) / max(s_n, s_{n-1})> en el bulk central del espectro,
    filtrando degeneraciones exactas de Kramers (s_n < 1e-10 en clase GSE N mod 8 == 4).
    """
    ev = np.sort(np.real(evals))
    # Colapsar multipletes de Kramers degenerados antes de medir espaciamiento entre niveles distintos
    unique_levels = [ev[0]]
    scale = max((ev[-1] - ev[0]) / max(len(ev), 1), 1e-12)
    for x in ev[1:]:
        if abs(x - unique_levels[-1]) > 1e-8 * scale:
            unique_levels.append(x)
    u = np.array(unique_levels, dtype=np.float64)
    k_cut = max(1, int(len(u) * trim_frac))
    u_bulk = u[k_cut : len(u) - k_cut] if len(u) > 2 * k_cut + 4 else u
    spacings = np.diff(u_bulk)
    if len(spacings) < 2:
        return 0.0
    r_vals = np.minimum(spacings[1:], spacings[:-1]) / np.maximum(spacings[1:], spacings[:-1])
    return float(np.mean(r_vals))


def main():
    t0 = time.perf_counter()
    print("=" * 80)
    print("POLYDIM / EINSOF — SYK_4 MAJORANA QUANTUM CHAOS & BOTT RMT CLASSIFICATION")
    print("[NOTA HONESTIDAD RADICAL]: Diagonalización exacta de clúster finito en CPU local")
    print("(N=16 -> GOE y N=12 -> GSE), NO ejecución QPU ni límite N->infinito AdS_2.")
    print("=" * 80)

    # 1. Resolver estado fundamental de N=16 Majoranas (8 qubits, D_even=128, 1.820 términos) con Stiefel-Lanczos
    N_goe = 16
    H16_seed0, n_terms_16, herm_err_16 = build_syk4_even_parity_matrix(N_goe, j_scale=1.0, seed=1973)
    dim_even_16 = H16_seed0.shape[0]
    res_lan16 = stiefel_lanczos_ground_state(
        lambda v: H16_seed0 @ v,
        dim_even_16,
        max_krylov=90,
        tol=1e-12,
        is_complex=True,
        seed=42,
    )
    evals16_0 = np.linalg.eigvalsh(H16_seed0)
    err_e0_16 = abs(res_lan16["energy"] - float(evals16_0[0]))
    assert err_e0_16 < 1e-11, f"Error Stiefel-Lanczos en SYK N=16: {err_e0_16}"

    print(f"[1] Estado Fundamental SYK_4 N={N_goe} (8 qubits, D_even={dim_even_16}, {n_terms_16} términos):")
    print(f"    -> E_0 (Stiefel-Lanczos): {res_lan16['energy']:+.10f} J | Exacto: {evals16_0[0]:+.10f} J (|dE|={err_e0_16:.2e})")
    print(f"    -> Residuo propio:        {res_lan16['residual_norm']:.2e} | Hermiticidad: {herm_err_16:.2e}")

    # 2. Promedio de ensamble sobre 8 semillas para N=16 (N mod 8 == 0 -> GOE, <r>_GOE = 0.5359)
    n_seeds = 8
    r_goe_samples = [compute_bulk_gap_ratio(evals16_0)]
    for s_idx in range(1, n_seeds):
        Hs, _, _ = build_syk4_even_parity_matrix(N_goe, j_scale=1.0, seed=1973 + 101 * s_idx)
        r_goe_samples.append(compute_bulk_gap_ratio(np.linalg.eigvalsh(Hs)))
    r_mean_n16 = float(np.mean(r_goe_samples))
    r_sem_n16 = float(np.std(r_goe_samples, ddof=1) / math.sqrt(n_seeds))

    # 3. Verificación explícita de Periodicidad de Bott en N=12 (N mod 8 == 4 -> GSE Kramers, <r>_GSE = 0.6744)
    r_gse_samples = []
    for s_idx in range(16):
        H12, _, _ = build_syk4_even_parity_matrix(12, j_scale=1.0, seed=3000 + 37 * s_idx)
        r_gse_samples.append(compute_bulk_gap_ratio(np.linalg.eigvalsh(H12), trim_frac=0.10))
    r_mean_n12 = float(np.mean(r_gse_samples))
    r_sem_n12 = float(np.std(r_gse_samples, ddof=1) / math.sqrt(len(r_gse_samples)))

    print(f"\n[2] Verificación Espectral Wigner-Dyson y Periodicidad de Bott (You-Ludwig-Xu / Cotler):")
    print(f"    -> N=16 (N mod 8 = 0, Clase GOE): <r>_ensamble = {r_mean_n16:.4f} ± {r_sem_n16:.4f} (Teórico GOE = 0.5359, Poisson = 0.3863)")
    print(f"    -> N=12 (N mod 8 = 4, Clase GSE): <r>_ensamble = {r_mean_n12:.4f} ± {r_sem_n12:.4f} (Teórico GSE = 0.6744 con Kramers doble)")

    t_total_ms = (time.perf_counter() - t0) * 1000.0
    output_data = {
        "scope_disclaimer": (
            "Exact finite-N CPU calculation of the Majorana SYK_4 model (N=16 GOE and N=12 GSE ensembles). "
            "Verifies Altland-Zirnbauer Bott periodicity of level statistics and Stiefel-Lanczos ground-state "
            "convergence; NOT a QPU run nor an asymptotic large-N JT-gravity proof."
        ),
        "problem": "SYK4_MAJORANA_QUANTUM_CHAOS_AND_BOTT_PERIODICITY",
        "primary_n_majoranas": N_goe,
        "n_qubits": N_goe // 2,
        "hilbert_dim_total": 1 << (N_goe // 2),
        "parity_sector_dim": dim_even_16,
        "n_quartic_terms": n_terms_16,
        "ground_energy_stiefel_lanczos": round(res_lan16["energy"], 10),
        "ground_energy_per_majorana": round(res_lan16["energy"] / N_goe, 10),
        "abs_error_vs_exact": err_e0_16,
        "eigenstate_residual_norm": res_lan16["residual_norm"],
        "hermiticity_defect": herm_err_16,
        "rmt_bott_periodicity_verification": {
            "N16_mod8_0_GOE": {
                "symmetry_class": "GOE (BDI/AI, P^2 = +1)",
                "n_realizations": n_seeds,
                "mean_gap_ratio_r": round(r_mean_n16, 4),
                "sem_r": round(r_sem_n16, 4),
                "theoretical_rmt_r": 0.5359,
            },
            "N12_mod8_4_GSE": {
                "symmetry_class": "GSE (CII/AII, P^2 = -1, Kramers-degenerate)",
                "n_realizations": 16,
                "mean_gap_ratio_r": round(r_mean_n12, 4),
                "sem_r": round(r_sem_n12, 4),
                "theoretical_rmt_r": 0.6744,
            },
            "poisson_integrable_reference": 0.3863,
        },
        "neumaier_drift": res_lan16["stiefel_state_drift"],
        "execution_ms": round(t_total_ms, 2),
        "exit_code": 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, "syk4_quantum_chaos.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n[3] Datos guardados en {data_path}")

    try:
        from pmtp_polydim_vector_swarm import PersistentMmapSlabBus
        import psycopg2

        # Empaquetar parte real e imaginaria de psi_0 en R^{256} sobre la esfera unitaria S^{255}
        psi_c = res_lan16["psi"]
        real_imag_vec = np.concatenate([np.real(psi_c), np.imag(psi_c)]).astype(np.float64)
        real_imag_vec /= neumaier_norm2(real_imag_vec)
        bus = PersistentMmapSlabBus()
        meta_slab = bus.write_tensor_slab(0x504D0010, real_imag_vec)
        conn = psycopg2.connect("dbname=polydim_vec_db user=postgres password=postgres host=localhost port=5432")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO session_context (conversation_id, summary, category, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id;
            """,
            ("c8f6b7cd-c96d-4bc0-9428-ccccee03234c", json.dumps(output_data, ensure_ascii=False), "REPAIRED_SYK4_BOTT_GOE_GSE"),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"[4] PMTP Slab {meta_slab['slab_id_hex']} | PostgreSQL DB_ID: {row_id}")
    except Exception as e:
        print(f"[4] Aviso PMTP/DB opcional: {e}")

    print(f"[RESUMEN] Exit Code 0 | Latencia: {t_total_ms:.2f} ms | <r>_N16(GOE)={r_mean_n16:.4f} | <r>_N12(GSE)={r_mean_n12:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
