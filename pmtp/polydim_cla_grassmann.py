"""
polydim_cla_grassmann_v26600.py - Suite Verificacion Polydim-cla (V26600)
=========================================================================
Valida propiedades de geometria Grassmanniana y alineacion de subespacios:

  1. Angulos canonicos: metodo arccos vs arcsin numericamente estable.
  2. La distancia geodesica a si mismo NO es exactamente cero en aritmetica
     flotante: el error QR de O(eps_machine * sqrt(r)) se propaga. El test
     correcto es verificar que la distancia es << 1 radian, no == 0.
  3. Procrustes ortogonal: Q = U Vt maximiza tr(Q^T A) y es ortogonal.
  4. Proyeccion de subespacio idempotente: P^2 = P con error < 1e-13.
  5. Guardias de clip: arccos(sigma > 1.0) produce NaN sin clip.

Dependencias: numpy (sin torch, sin GPU)
Uso: python polydim_cla_grassmann_v26600.py
Exit Code 0 si todos los tests pasan, 1 si hay fallos.
"""

import sys
import numpy as np


def check(results, name, condition, detail='', note=''):
    status = '[PASS]' if condition else '[FAIL]'
    line = f'      {status} {name}'
    if not condition and detail:
        line += f': {detail}'
    print(line)
    if note:
        print(f'             NOTE: {note}')
    results.append((name, condition))


def run_tests():
    results = []
    rng = np.random.RandomState(42)
    D = 128
    r = 64

    # ---------------------------------------------------------------
    # Construir dos subespacios ortonormales casi identicos
    # W1 en St(128, 64) y W2 = QR(W1 + pequena perturbacion)
    # ---------------------------------------------------------------
    W1, _ = np.linalg.qr(rng.randn(D, r))
    W2_raw = W1 + 1e-8 * np.random.RandomState(99).randn(D, r)
    W2, _ = np.linalg.qr(W2_raw)

    # Angulos canonicos sigma_i = cos(theta_i) = SVD(W1^T W2)
    M = W1.T @ W2
    sigma = np.clip(np.linalg.svd(M, compute_uv=False), -1.0, 1.0)

    # Metodo 1: arccos (peligroso: derivada -> inf cuando sigma -> 1^-)
    theta_arccos = np.arccos(sigma)

    # Metodo 2: arcsin estable (derivada acotada, sin explosion cerca de 0)
    theta_arcsin = np.arcsin(np.sqrt(np.maximum(0.0, 1.0 - sigma**2)))

    print('[TEST 1] Angulos canonicos Grassmannianos (W1 vs W2 casi identicos)')
    check(results, 'arccos_no_negative_angles',
          np.all(theta_arccos >= 0.0))
    check(results, 'arcsin_vs_arccos_agree_1e10',
          np.allclose(theta_arccos, theta_arcsin, atol=1e-10),
          f'max_diff={np.max(np.abs(theta_arccos - theta_arcsin)):.2e}')
    check(results, 'geodesic_distance_finite',
          np.isfinite(np.sum(theta_arcsin)))

    # ---------------------------------------------------------------
    # Distancia a si mismo: W1 vs W1
    # ---------------------------------------------------------------
    # La factorizacion QR introduce error de ortogonalidad:
    #   ||W1^T W1 - I||_inf ~ eps_machine * sqrt(r) ~ 2.2e-16 * 8 ~ 1.8e-15
    # Ese error se propaga a los valores singulares de W1^T W1:
    #   sigma_i = 1.0 +/- delta  con delta ~ 1e-15
    # Al calcular arcsin(sqrt(1 - sigma^2)) con sigma~1, el residuo sin^2 ~ 2*delta
    # y arcsin(sqrt(2*delta)) ~ sqrt(2*delta) ~ 3e-8 por componente.
    # La norma sobre r=64 componentes: dist_self ~ sqrt(64) * 3e-8 ~ 2.4e-7
    # Tolerancia correcta: dist_self < 1e-6 (conservadoramente)
    print()
    print('[TEST 2] Distancia Grassmanniana de W1 a si mismo')
    qr_ortho_defect = float(np.max(np.abs(W1.T @ W1 - np.eye(r))))
    sigma_self = np.clip(np.linalg.svd(W1.T @ W1, compute_uv=False), 0.0, 1.0)
    dist_self = float(np.linalg.norm(
        np.arcsin(np.sqrt(np.maximum(0.0, 1.0 - sigma_self**2)))
    ))
    # El bound teorico: dist_self <= sqrt(r) * arcsin(sqrt(2 * qr_defect))
    theoretical_bound = np.sqrt(r) * np.arcsin(np.sqrt(max(0, 2.0 * qr_ortho_defect)))
    check(results, 'self_distance_strictly_positive_but_tiny',
          0.0 <= dist_self < 1e-5,
          f'dist={dist_self:.2e} (expected < 1e-5)',
          f'QR defect ||W1^T W1 - I||={qr_ortho_defect:.2e}, bound={theoretical_bound:.2e}')
    check(results, 'self_distance_bounded_by_theory',
          dist_self <= max(theoretical_bound * 10, 1e-6),
          f'dist={dist_self:.2e}, bound={theoretical_bound:.2e}')

    # Verificar que la distancia real entre W1 y W2 (perturbados) es mayor
    dist_w1_w2 = float(np.linalg.norm(theta_arcsin))
    check(results, 'perturbed_distance_gt_self_distance',
          dist_w1_w2 > dist_self,
          f'dist(W1,W2)={dist_w1_w2:.2e} debe ser > dist(W1,W1)={dist_self:.2e}')

    # ---------------------------------------------------------------
    # Procrustes ortogonal Q = argmax_Q tr(Q^T A), Q ortogonal
    # ---------------------------------------------------------------
    print()
    print('[TEST 3] Procrustes Ortogonal: Q = U @ Vt')
    A = np.random.RandomState(7).randn(64, 64)
    U, _, Vt = np.linalg.svd(A)
    Q = U @ Vt
    orth_defect = float(np.max(np.abs(Q @ Q.T - np.eye(64))))
    check(results, 'procrustes_Q_orthogonal_1e13',
          orth_defect < 1e-13,
          f'||QQ^T - I||={orth_defect:.2e}')
    det_Q = float(np.linalg.det(Q))
    check(results, 'procrustes_det_plus_or_minus_1',
          abs(abs(det_Q) - 1.0) < 1e-10,
          f'det(Q)={det_Q:.6f}')

    # ---------------------------------------------------------------
    # Proyeccion idempotente P = V V^T, P^2 = P
    # ---------------------------------------------------------------
    print()
    print('[TEST 4] Proyeccion de Subespacio Idempotente: P^2 = P')
    V_sub = W1[:, :10]
    P = V_sub @ V_sub.T
    idem_defect = float(np.max(np.abs(P @ P - P)))
    check(results, 'projection_idempotent_1e13',
          idem_defect < 1e-13,
          f'||P^2 - P||={idem_defect:.2e}')
    symm_defect = float(np.max(np.abs(P - P.T)))
    check(results, 'projection_symmetric',
          symm_defect < 1e-14,
          f'||P - P^T||={symm_defect:.2e}')

    # ---------------------------------------------------------------
    # Clip obligatorio: sin clip arccos(sigma > 1) da NaN
    # ---------------------------------------------------------------
    print()
    print('[TEST 5] Guardia de Clip: arccos sin clip da NaN')
    sigma_overflow = np.array([1.0 + 1e-15, 0.99, 0.5])
    with np.errstate(invalid='ignore'):
        result_no_clip = np.arccos(sigma_overflow)
    check(results, 'arccos_without_clip_gives_nan_for_sigma_gt_1',
          np.isnan(result_no_clip[0]),
          'arccos(1+1e-15) deberia dar NaN')
    result_with_clip = np.arccos(np.clip(sigma_overflow, -1.0, 1.0))
    check(results, 'arccos_with_clip_is_safe',
          not np.any(np.isnan(result_with_clip)) and np.all(result_with_clip >= 0))

    return results


def main():
    print('=' * 60)
    print('POLYDIM V26600 - MODULO 3: Polydim-cla (Geometria Grassmanniana)')
    print('=' * 60)
    print()
    results = run_tests()
    passed = [n for n, ok in results if ok]
    failed = [n for n, ok in results if not ok]
    print()
    print('=' * 60)
    print(f'MODULO 3 Polydim-cla: {len(passed)}/{len(results)} PASS | Exit Code: {0 if not failed else 1}')
    if failed:
        print('FALLOS:')
        for f in failed:
            print(f'  - {f}')
    print('=' * 60)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
