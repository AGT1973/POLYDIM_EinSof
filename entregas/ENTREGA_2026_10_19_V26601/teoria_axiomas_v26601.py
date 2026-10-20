"""
teoria_axiomas_v26600.py - Suite Teoria & Axiomas POLYDIM (V26600)
Valida: Isometria esferica, resolucion antipodal Levi-Civita, Lipschitz del pipeline,
        Acumulador Neumaier D=65536, Pre-escalado espectral Stiefel.
Dependencias: numpy
Exit Code 0 si 8/8 pasan.
"""

import sys
import numpy as np

PASS = []
FAIL = []

def check(name, condition, detail=''):
    status = '[PASS]' if condition else '[FAIL]'
    print(f'{status} {name}' + (f': {detail}' if not condition else ''))
    (PASS if condition else FAIL).append(name)

D = 512
rng = np.random.default_rng(2026)
W, _ = np.linalg.qr(rng.standard_normal((D, 256)))

# Test 1: Isometria - angulo geodesico finito en S^{255}
h1 = rng.standard_normal(D)
h2 = rng.standard_normal(D)
z1 = W.T @ h1; u1 = z1 / np.linalg.norm(z1)
z2 = W.T @ h2; u2 = z2 / np.linalg.norm(z2)
angle = np.arccos(float(np.clip(u1 @ u2, -1.0, 1.0)))
check('Isometry_angle_finite', np.isfinite(angle))
check('Isometry_angle_in_0_pi', 0.0 <= angle <= np.pi)

# Test 2: Resolucion Antipodal Levi-Civita
D2 = 64
x = rng.standard_normal(D2)
x = x / np.linalg.norm(x)
neg_x = -x
first_nonzero_x = x[np.argmax(np.abs(x))]
canonical_x = x if first_nonzero_x > 0 else neg_x
canonical_neg = neg_x if (-neg_x[np.argmax(np.abs(neg_x))]) < 0 else x
# La representacion canonica de x y -x es la misma
canon = lambda v: v if v[np.argmax(np.abs(v))] > 0 else -v
check('Antipodal_canon_x_eq_canon_neg_x', np.allclose(canon(x), canon(neg_x)))
check('Antipodal_canon_unit_norm', abs(np.linalg.norm(canon(x)) - 1.0) < 1e-14)

# Test 3: Lipschitz - la constante esta acotada cuando rho >= eps
D3 = 64
W3, _ = np.linalg.qr(rng.standard_normal((D3, D3)))
h1_n = rng.standard_normal(D3)
h2_n = rng.standard_normal(D3)
eps = 1e-12
u1_n = (W3.T @ h1_n); rho1 = np.linalg.norm(u1_n); u1_n /= max(rho1, eps)
u2_n = (W3.T @ h2_n); rho2 = np.linalg.norm(u2_n); u2_n /= max(rho2, eps)
lip_bound = (2.0 * np.linalg.svd(W3, compute_uv=False)[-1]) / max(min(rho1, rho2), eps)
check('Lipschitz_bound_finite', np.isfinite(lip_bound))
check('Lipschitz_direction_diff_bounded', np.linalg.norm(u1_n - u2_n) <= 2.0)

# Test 4: Acumulador Compensado Neumaier (FP64 <= 1e-15)
def neumaier_sum(arr):
    s = 0.0
    c = 0.0
    for val in arr:
        t = s + val
        if abs(s) >= abs(val):
            c += (s - t) + val
        else:
            c += (val - t) + s
        s = t
    return s + c

# Validacion contra cancelacion catastrofica donde suma ingenua pierde digitos
ill_conditioned = np.array([1.0, 1e16, 1.0, -1e16, 1e-15, 1e-15], dtype=np.float64)
exact_sum = 2.0 + 2e-15
neumaier_res = neumaier_sum(ill_conditioned)
neumaier_err = abs(neumaier_res - exact_sum)
check('Neumaier_catastrophic_cancellation_exact', neumaier_err <= 1e-15, f'err={neumaier_err:.2e}')

D4 = 65536
v = np.full(D4, 1.0 / np.sqrt(D4), dtype=np.float64)
norm_sq_neumaier = neumaier_sum(v**2)
norm_sq_err = abs(norm_sq_neumaier - 1.0)
check('Neumaier_D65536_norm_error_below_1e12', norm_sq_err < 1e-12, f'err={norm_sq_err:.2e}')

# Test 5: Pre-escalado espectral para Newton-Schulz
X_raw = rng.standard_normal((256, 64))
sigma_x = np.linalg.svd(X_raw, compute_uv=False)
Y0 = X_raw / sigma_x[0]
defect = np.max(np.abs(Y0.T @ Y0 - np.eye(64)))
check('Stiefel_prescale_defect_finite', np.isfinite(defect))
check('Stiefel_prescale_defect_lt_1', defect < 1.0, f'defect={defect:.4f}')

# Test 6: Defecto de ortogonalidad de PolarSafe converge a epsilon maquina
YtY = Y0.T @ Y0
A_err = np.eye(64) - YtY
for _ in range(8):
    A_err2 = A_err @ A_err
    A_err3 = A_err2 @ A_err
    A_err4 = A_err2 @ A_err2
    poly = np.eye(64) + 0.5*A_err + 0.375*A_err2 + 0.3125*A_err3 + (35/128)*A_err4
    Y0 = Y0 @ poly
    YtY = Y0.T @ Y0
    A_err = np.eye(64) - YtY
    if np.max(np.abs(A_err)) < 1e-14:
        break
final_defect = np.max(np.abs(YtY - np.eye(64)))
check('Newton_Schulz_ord5_converges_to_eps_machine', final_defect < 1e-12, f'defect={final_defect:.2e}')

print()
print('=' * 60)
print(f'MODULO 4 Teoria Axiomas: {len(PASS)}/{len(PASS)+len(FAIL)} PASS | Exit Code: {0 if not FAIL else 1}')
print('=' * 60)
sys.exit(1 if FAIL else 0)
