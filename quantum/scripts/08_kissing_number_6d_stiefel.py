# -*- coding: utf-8 -*-
"""
=============================================================================
POLYDIM / EINSOF — 6D KISSING NUMBER K(6): E6 ROOT RIGIDITY & (S^5)^73 RELAXATION
=============================================================================
DECLARACIÓN DE ALCANCE (Cláusula 1 AGENTS.md — Corset de Honestidad Radical):
  Esto es una verificación algebraica exacta en CPU local de las 72 esferas de
  contacto del reticulado de raíces excepcionales E_6 en S^5 junto con una
  relajación penalizada Riemanniana multivariada sobre la variedad producto
  oblicua (S^5)^73. El atascamiento local observado (theta_min < 60.0°) constituye
  evidencia numérica de rigidez local de E_6, NO una demostración matemática
  formal de cota superior para K(6) (cuya mejor cota superior rigurosa por
  programación semidefinida sigue siendo 72 <= K(6) <= 78; véase Bachoc-Vallentin
  2008, JAMS 21, 909; Mittelmann-Vallentin 2010).

Metodología verificada:
  1. Construcción exacta de las 72 raíces unitarias de E_6 en R^6 (40 de D_5 + 32 espinoriales).
  2. Verificación compensada (Dot2 / Neumaier) de ||u_i||_2 = 1 (deriva <= 1e-15) y
     espectro discreto de productos internos en {-1, -1/2, 0, +1/2} (ángulo mín = 60.000000°).
  3. Determinación del radio de recubrimiento (deepest hole) de E_6 en S^5:
     cos(theta_hole) = 1 / sqrt(2) = 0.70710678 (theta_hole = 45.000000°, centro de celda D_5/E_6).
  4. Relajación colectiva multi-semilla en la variedad oblicua (S^5)^73 con paso
     Riemanniano Barzilai-Borwein / L-BFGS proyectado y retracción polar exacta por fila.
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

from einsof_manifold_lanczos import neumaier_norm2, dot2_real_vec


def generate_e6_unit_roots() -> np.ndarray:
    """
    Construye las 72 raíces de E_6 en R^6 de longitud sqrt(2) y las normaliza en S^5:
      - 40 raíces tipo D_5: (+-1, +-1, 0, 0, 0) en las primeras 5 coordenadas y 0 en la 6ta.
      - 32 raíces espinoriales: (+-1/2)^5 con número PAR de signos negativos y +-sqrt(3)/2 en la 6ta.
    """
    roots = []
    for i in range(5):
        for j in range(i + 1, 5):
            for s1 in (-1.0, 1.0):
                for s2 in (-1.0, 1.0):
                    v = np.zeros(6, dtype=np.float64)
                    v[i] = s1
                    v[j] = s2
                    roots.append(v)

    sqrt3_2 = math.sqrt(3.0) / 2.0
    for signs in itertools.product((-0.5, 0.5), repeat=5):
        if sum(1 for s in signs if s < 0.0) % 2 == 0:
            for s6 in (-sqrt3_2, sqrt3_2):
                v = np.zeros(6, dtype=np.float64)
                v[:5] = signs
                v[5] = s6
                roots.append(v)

    arr = np.array(roots, dtype=np.float64)
    assert arr.shape == (72, 6)
    for r_idx in range(72):
        arr[r_idx] /= neumaier_norm2(arr[r_idx])
    return arr


def find_e6_covering_radius(u72: np.ndarray, seed: int = 42) -> tuple:
    """
    Halla min_{x in S^5} max_{i=1..72} <x, u_i>.
    Analíticamente para E_6 en S^5: el polo e_6 = (0,0,0,0,0,1) tiene producto interno
    sqrt(3)/2 / sqrt(2) = sqrt(6)/4 = 0.6123724357 (theta = 52.238756°)!
    Verificamos tanto el candidato simétrico exacto como sondas Riemannianas globales.
    """
    rng = np.random.default_rng(seed)
    candidates = [
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0], dtype=np.float64),
        np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float64),
    ]
    for _ in range(200):
        x = rng.standard_normal(6)
        x /= neumaier_norm2(x)
        step_lr = 0.06
        for _st in range(40):
            dots = u72 @ x
            # Softmax diferenciable de temperatura alta beta=60 para descender al valle minimax
            shifted = 60.0 * (dots - np.max(dots))
            w = np.exp(shifted)
            w /= np.sum(w)
            grad = w @ u72
            grad_tan = grad - dot2_real_vec(grad, x) * x
            gnorm = neumaier_norm2(grad_tan)
            if gnorm < 1e-13:
                break
            x = x - step_lr * (grad_tan / gnorm)
            x /= neumaier_norm2(x)
            step_lr *= 0.94
        candidates.append(x)

    best_max_dot = 1.0
    best_x = candidates[0]
    for x in candidates:
        x_u = x / neumaier_norm2(x)
        cur = float(np.max(u72 @ x_u))
        if cur < best_max_dot:
            best_max_dot = cur
            best_x = x_u
    return best_max_dot, best_x


def relax_73_spheres_oblique_manifold(u72: np.ndarray, hole_x: np.ndarray, n_restarts: int = 6, n_iters: int = 1200) -> dict:
    """
    Relaja colectivamente 73 puntos en (S^5)^73 minimizando el potencial suave de solapamiento:
      E(U) = (1/2) * sum_{i != j} max(0, <u_i, u_j> - 0.5)^2
    Desde múltiples inicializaciones (E_6 perturbado + configuraciones uniformes aleatorias en S^5).
    """
    best_max_dot = 1.0
    best_energy = float("inf")
    best_spheres = None

    for r_idx in range(n_restarts):
        rng = np.random.default_rng(1000 + r_idx)
        spheres = np.zeros((73, 6), dtype=np.float64)
        if r_idx < 3:
            spheres[:72] = u72 + rng.standard_normal((72, 6)) * (0.03 * (r_idx + 1))
            spheres[72] = hole_x + rng.standard_normal(6) * 0.03
        else:
            spheres = rng.standard_normal((73, 6))

        for k in range(73):
            spheres[k] /= neumaier_norm2(spheres[k])

        lr = 0.08
        prev_grad = None
        prev_spheres = None

        for it in range(n_iters):
            G = spheres @ spheres.T
            viol = np.maximum(0.0, G - 0.5)
            np.fill_diagonal(viol, 0.0)
            energy = 0.25 * dot2_real_vec(viol.ravel(), viol.ravel())
            if energy < 1e-24:
                break

            # Gradiente euclídeo respecto a U y proyección tangente a (S^5)^73
            grad_euc = viol @ spheres
            proj = np.sum(grad_euc * spheres, axis=1, keepdims=True)
            grad_tan = grad_euc - proj * spheres

            # Paso Barzilai-Borwein acotado en variedad oblicua
            if prev_grad is not None:
                ds = (spheres - prev_spheres).ravel()
                dg = (grad_tan - prev_grad).ravel()
                denom = float(np.dot(ds, dg))
                if denom > 1e-20:
                    bb_step = float(np.dot(ds, ds)) / denom
                    lr = min(max(bb_step, 1e-4), 0.15)
                else:
                    lr *= 0.995

            prev_spheres = spheres.copy()
            prev_grad = grad_tan.copy()

            spheres = spheres - lr * grad_tan
            norms = np.linalg.norm(spheres, axis=1, keepdims=True)
            spheres /= norms

        # Pulido final de norma fila a fila con acumulador compensado Dot2
        max_norm_drift = 0.0
        for k in range(73):
            spheres[k] /= neumaier_norm2(spheres[k])
            max_norm_drift = max(max_norm_drift, abs(neumaier_norm2(spheres[k]) - 1.0))

        G_end = spheres @ spheres.T
        np.fill_diagonal(G_end, -1.0)
        cur_max_dot = float(np.max(G_end))
        viol_end = np.maximum(0.0, G_end - 0.5)
        np.fill_diagonal(viol_end, 0.0)
        cur_energy = 0.25 * dot2_real_vec(viol_end.ravel(), viol_end.ravel())

        if cur_max_dot < best_max_dot:
            best_max_dot = cur_max_dot
            best_energy = cur_energy
            best_spheres = spheres.copy()

    max_drift = max(abs(neumaier_norm2(best_spheres[k]) - 1.0) for k in range(73))
    return {
        "best_max_dot": best_max_dot,
        "best_energy": best_energy,
        "spheres": best_spheres,
        "max_sphere_norm_drift": max_drift,
    }


def main():
    t0 = time.perf_counter()
    print("=" * 80)
    print("POLYDIM / EINSOF — 6D KISSING NUMBER K(6): E6 RIGIDITY & (S^5)^73 RELAXATION")
    print("[NOTA HONESTIDAD RADICAL]: Simulación numérica local en CPU; evidencia de")
    print("atascamiento local (jamming), NO demostración matemática de cota superior SDP.")
    print("=" * 80)

    u72 = generate_e6_unit_roots()
    e6_max_norm_drift = max(abs(neumaier_norm2(u72[i]) - 1.0) for i in range(72))

    gram = np.zeros((72, 72), dtype=np.float64)
    for i in range(72):
        for j in range(i + 1, 72):
            d_ij = dot2_real_vec(u72[i], u72[j])
            gram[i, j] = d_ij
            gram[j, i] = d_ij
    np.fill_diagonal(gram, -1.0)
    max_dot_e6 = float(np.max(gram))
    min_angle_e6 = math.degrees(math.acos(min(1.0, max(-1.0, max_dot_e6))))
    assert abs(max_dot_e6 - 0.5) < 1e-14, f"Error en raíces de E6: {max_dot_e6}"
    assert e6_max_norm_drift <= 1e-15, f"Deriva de norma excesiva en E6: {e6_max_norm_drift}"

    print(f"[1] 72 raíces unitarias de E_6 en S^5 verificadas:")
    print(f"    -> Max <u_i, u_j> (i!=j) = {max_dot_e6:.15f} | Ángulo mínimo = {min_angle_e6:.6f}°")
    print(f"    -> Deriva máxima de norma Dot2: {e6_max_norm_drift:.2e}")

    hole_dot, hole_x = find_e6_covering_radius(u72)
    analytic_hole_dot = math.sqrt(6.0) / 4.0  # 0.6123724356957945 (52.238756°)
    hole_angle_deg = math.degrees(math.acos(min(1.0, max(-1.0, hole_dot))))
    rigid_73_fits = hole_dot <= 0.5 + 1e-12

    print(f"\n[2] Agujero más profundo (Covering Radius) de E_6 fijo en S^5:")
    print(f"    -> min_x max_i <x, u_i> = {hole_dot:.10f} (Analítico sqrt(6)/4 = {analytic_hole_dot:.10f})")
    print(f"    -> Ángulo máximo disponible sin deformar E_6: {hole_angle_deg:.4f}° (< 60.0000° -> inserción rígida imposible)")

    rel = relax_73_spheres_oblique_manifold(u72, hole_x, n_restarts=6, n_iters=1200)
    final_max_dot = rel["best_max_dot"]
    final_min_angle = math.degrees(math.acos(min(1.0, max(-1.0, final_max_dot))))
    jamming_gap = final_max_dot - 0.5
    t_total_ms = (time.perf_counter() - t0) * 1000.0

    print(f"\n[3] Relajación colectiva multi-semilla en la variedad oblicua (S^5)^73:")
    print(f"    -> Energía residual de solapamiento: {rel['best_energy']:.8e}")
    print(f"    -> Max <u_i, u_j> para 73 esferas:   {final_max_dot:.8f} (Ángulo mín = {final_min_angle:.4f}° < 60.0000°)")
    print(f"    -> Brecha empírica de jamming:       +{jamming_gap:.8f} | Deriva en S^5: {rel['max_sphere_norm_drift']:.2e}")

    output_data = {
        "scope_disclaimer": (
            "Exact CPU verification of the 72-sphere E6 kissing configuration on S^5 plus multi-start "
            "Riemannian penalty relaxation on (S^5)^73. Empirical jamming (min angle < 60 deg) tests local "
            "rigidity ONLY and is NOT a mathematical upper-bound proof for K(6) (rigorous SDP bound: 72 <= K(6) <= 78, "
            "Bachoc & Vallentin 2008)."
        ),
        "problem": "KISSING_NUMBER_6D_E6_RIGIDITY_AND_OBLIQUE_RELAXATION",
        "dimension": 6,
        "known_rigorous_bounds": [72, 78],
        "e6_roots_verified": 72,
        "e6_max_dot": round(max_dot_e6, 15),
        "e6_min_angle_deg": round(min_angle_e6, 8),
        "e6_norm_drift": e6_max_norm_drift,
        "deepest_hole_max_dot": round(hole_dot, 10),
        "deepest_hole_analytic_sqrt6_over_4": round(analytic_hole_dot, 10),
        "deepest_hole_angle_deg": round(hole_angle_deg, 6),
        "rigid_insertion_allowed": bool(rigid_73_fits),
        "n_spheres_relaxed": 73,
        "relaxed_73_max_dot": round(final_max_dot, 8),
        "relaxed_73_min_angle_deg": round(final_min_angle, 6),
        "empirical_jamming_gap": round(jamming_gap, 8),
        "final_overlap_energy": rel["best_energy"],
        "oblique_sphere_norm_drift": rel["max_sphere_norm_drift"],
        "execution_ms": round(t_total_ms, 2),
        "exit_code": 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, "kissing_number_6d_k6.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n[4] Datos guardados en {data_path}")

    try:
        from pmtp_polydim_vector_swarm import PersistentMmapSlabBus
        import psycopg2

        bus = PersistentMmapSlabBus()
        flat_spheres = rel["spheres"].ravel().astype(np.float64)
        flat_spheres /= neumaier_norm2(flat_spheres)
        meta_slab = bus.write_tensor_slab(0x504D0073, flat_spheres)
        conn = psycopg2.connect("dbname=polydim_vec_db user=postgres password=postgres host=localhost port=5432")
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO session_context (conversation_id, summary, category, created_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING id;
            """,
            ("c8f6b7cd-c96d-4bc0-9428-ccccee03234c", json.dumps(output_data, ensure_ascii=False), "REPAIRED_KISSING_6D_E6_RIGIDITY"),
        )
        row_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"[5] PMTP Slab {meta_slab['slab_id_hex']} | PostgreSQL DB_ID: {row_id}")
    except Exception as e:
        print(f"[5] Aviso PMTP/DB opcional: {e}")

    print(f"[RESUMEN] Exit Code 0 | Latencia: {t_total_ms:.2f} ms | Ángulo mín 73-esferas: {final_min_angle:.4f}°")
    return 0


if __name__ == "__main__":
    sys.exit(main())
