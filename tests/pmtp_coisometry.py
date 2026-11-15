"""
pmtp_coisometry.py (v2.0 — Remediated REM-14, REM-15, REM-21)
Modulo reutilizable: proyeccion co-isometrica segura para PmtpShmBus.
Implementa safe_coisometry_projection() y batch_coisometry_projection()
sobre la variedad de Stiefel / esfera unitaria S^{k-1}:
  1. Modo 'canonical': fallback determinista e_1 cuando s in ker(W) (||W s|| <= eps * max(||s||, 1)).
  2. Modo 'tikhonov': regularizacion suave globalmente Lipschitz:
         u_eta(s) = (W s) / sqrt(||W s||_2^2 + eta^2)
     con constante global de Lipschitz exacta L <= ||W||_2 / eta = 1 / eta.

Referencias:
  - REM-14: Regularizacion de ker(W) en Teorema 3.
  - REM-15: Correccion de autotest QR completo (mode='complete') probando los n-k
            vectores no nulos reales del complemento ortogonal ker(W).
  - REM-21: Validacion estricta de entradas finitas (NaN/Inf), eps > 0, ortonormalidad
            de filas W W^T = I_k, umbral inmune a ruido FP64 (1e-12) y broadcasting 2D.
"""
import numpy as np
from typing import Dict, Union


def verify_coisometry_matrix(W: np.ndarray, tol: float = 1e-10) -> float:
    """
    Verifica que W in R^{k x n} (k <= n) cumpla W W^T = I_k dentro de tolerancia.
    Retorna el error de Frobenius ||W W^T - I_k||_F.
    """
    if not isinstance(W, np.ndarray) or W.ndim != 2:
        raise ValueError(f"W debe ser un np.ndarray 2D; recibido {type(W)} ndim={getattr(W, 'ndim', None)}")
    k, n = W.shape
    if k < 1 or n < k:
        raise ValueError(f"Co-isometria requiere 1 <= k <= n; recibido W.shape=({k}, {n})")
    if not np.all(np.isfinite(W)):
        raise ValueError("W contiene valores NaN o Inf")
    gram = W.astype(np.float64, copy=False) @ W.astype(np.float64, copy=False).T
    err = float(np.linalg.norm(gram - np.eye(k, dtype=np.float64), ord="fro"))
    if err > tol:
        raise ValueError(f"W no es fila-ortonormal: ||W W^T - I_k||_F = {err:.3e} > tol={tol:.1e}")
    return err


def safe_coisometry_projection(
    W: np.ndarray,
    s: np.ndarray,
    eps: float = 1e-12,
    return_debug: bool = False,
    mode: str = "canonical",
    eta: float = 1e-6,
    check_orthonormal: bool = False,
) -> Union[np.ndarray, Dict[str, Union[np.ndarray, float, bool, str]]]:
    """
    Proyeccion co-isometrica segura para inyeccion latente (Teorema 3 remediado).

    Dados W in R^{k x n} (1 <= k <= n) con filas ortonormales (W W^T = I_k)
    y un vector latente s in R^n:
      - En modo 'canonical' (por defecto, preserva ||p||_2 = 1.0 exacto):
            p = W s / ||W s||_2   si ||W s||_2 > threshold,
            p = e_1               si ||W s||_2 <= threshold (s in ker(W) o s = 0).
        Nota matematica explicita: toda aplicacion de R^n \\ {0} a S^{k-1} cuando n > k
        tiene una discontinuidad topologica inevitable en ker(W); el fallback e_1
        garantiza determinismo y ausencia total de NaN/division por cero.
      - En modo 'tikhonov' (suave y globalmente Lipschitz en todo R^n):
            p = W s / sqrt(||W s||_2^2 + eta^2)
        con ||p||_2 < 1 y constante global de Lipschitz exacta ||J_p(s)||_2 <= 1 / eta.

    Args:
        W:                 Matriz co-isometrica de forma (k, n), 1 <= k <= n.
        s:                 Vector de entrada de forma (n,).
        eps:               Umbral relativo/absoluto de deteccion de kernel (default 1e-12 > eps_mach).
        return_debug:      Si True, retorna diccionario con metricas de diagnostico.
        mode:              'canonical' (unitario en S^{k-1}) o 'tikhonov' (globalmente Lipschitz).
        eta:               Parametro de suavizado para mode='tikhonov' (eta > 0).
        check_orthonormal: Si True, verifica ||W W^T - I_k||_F <= 1e-10.
    """
    W_arr = np.asarray(W, dtype=np.float64)
    s_arr = np.asarray(s, dtype=np.float64)

    if W_arr.ndim != 2 or s_arr.ndim != 1:
        raise ValueError(f"W debe ser 2D y s 1D. Recibido W.ndim={W_arr.ndim}, s.ndim={s_arr.ndim}")
    k, n = W_arr.shape
    if k < 1 or n < 1:
        raise ValueError(f"Dimensiones invalidas: W.shape=({k}, {n})")
    if s_arr.shape[0] != n:
        raise ValueError(f"Dimension incompatible: W es ({k},{n}), s es ({s_arr.shape[0]},)")
    if not (np.isfinite(eps) and eps > 0.0):
        raise ValueError(f"eps debe ser finito y > 0; recibido {eps}")
    if not np.all(np.isfinite(W_arr)) or not np.all(np.isfinite(s_arr)):
        raise ValueError("Entradas no finitas detectadas (NaN o Inf rechazados por protocolo)")
    if check_orthonormal:
        verify_coisometry_matrix(W_arr)

    # Escalado seguro contra overflow/underflow en vectores extremos o subnormales
    max_abs = float(np.max(np.abs(s_arr)))
    if max_abs == 0.0:
        norm_s = 0.0
        Ws = np.zeros(k, dtype=np.float64)
        norm_ws = 0.0
    else:
        s_scaled = s_arr / max_abs
        norm_s = max_abs * float(np.linalg.norm(s_scaled))
        Ws_scaled = W_arr @ s_scaled
        norm_ws_scaled = float(np.linalg.norm(Ws_scaled))
        Ws = Ws_scaled * max_abs
        norm_ws = norm_ws_scaled * max_abs

    threshold = eps * norm_s if norm_s > 1.0 else (eps * max(norm_s, 1e-300) if norm_s > 0.0 else eps)
    # Si s != 0 pero ||W s|| <= eps * ||s||, s pertenece numericamente a ker(W)
    in_kernel = (max_abs == 0.0) or (norm_ws <= eps * max(norm_s, 1e-300))

    if mode == "canonical":
        if in_kernel:
            p = np.zeros(k, dtype=np.float64)
            p[0] = 1.0
        else:
            # Usar Ws_scaled / norm_ws_scaled evita underflow cuando ||s|| ~ 1e-308
            p = Ws_scaled / norm_ws_scaled
    elif mode == "tikhonov":
        if not (np.isfinite(eta) and eta > 0.0):
            raise ValueError(f"eta debe ser finito y > 0; recibido {eta}")
        denom = float(np.hypot(norm_ws, eta))
        p = Ws / denom
    else:
        raise ValueError(f"Modo desconocido '{mode}'; use 'canonical' o 'tikhonov'")

    if return_debug:
        return {
            "p": p,
            "norm_ws": norm_ws,
            "norm_s": norm_s,
            "threshold": threshold,
            "in_kernel": bool(in_kernel),
            "mode": mode,
            "output_norm": float(np.linalg.norm(p)),
        }
    return p


def batch_coisometry_projection(
    W: np.ndarray,
    S: np.ndarray,
    eps: float = 1e-12,
    check_orthonormal: bool = False,
) -> np.ndarray:
    """
    Version vectorizada segura: aplica safe_coisometry_projection a cada fila de S (m, n).
    Maneja lotes mixtos (vectores normales, subnormales, nulos y en ker(W)) sin errores de broadcasting.
    """
    W_arr = np.asarray(W, dtype=np.float64)
    S_arr = np.asarray(S, dtype=np.float64)
    if W_arr.ndim != 2 or S_arr.ndim != 2:
        raise ValueError(f"W y S deben ser 2D; recibido W.ndim={W_arr.ndim}, S.ndim={S_arr.ndim}")
    k, n = W_arr.shape
    m, n_s = S_arr.shape
    if k < 1 or n != n_s:
        raise ValueError(f"Dimensiones incompatibles: W=({k},{n}), S=({m},{n_s})")
    if not (np.isfinite(eps) and eps > 0.0):
        raise ValueError(f"eps debe ser finito y > 0; recibido {eps}")
    if not np.all(np.isfinite(W_arr)) or not np.all(np.isfinite(S_arr)):
        raise ValueError("W o S contienen NaN o Inf")
    if check_orthonormal:
        verify_coisometry_matrix(W_arr)

    P = np.zeros((m, k), dtype=np.float64)
    if m == 0:
        return P

    row_max = np.max(np.abs(S_arr), axis=1)  # (m,)
    nonzero_mask = row_max > 0.0

    if np.any(nonzero_mask):
        S_nz = S_arr[nonzero_mask] / row_max[nonzero_mask, None]
        norms_s_scaled = np.linalg.norm(S_nz, axis=1)  # (m_nz,)
        WS_nz = S_nz @ W_arr.T  # (m_nz, k)
        norms_ws_scaled = np.linalg.norm(WS_nz, axis=1)  # (m_nz,)

        valid_local = norms_ws_scaled > (eps * norms_s_scaled)
        nz_indices = np.flatnonzero(nonzero_mask)
        valid_global = nz_indices[valid_local]
        kernel_global = nz_indices[~valid_local]

        if valid_global.size > 0:
            P[valid_global] = WS_nz[valid_local] / norms_ws_scaled[valid_local, None]
        if kernel_global.size > 0:
            P[kernel_global, 0] = 1.0

    P[~nonzero_mask, 0] = 1.0
    return P


if __name__ == "__main__":
    print("=" * 72)
    print("pmtp_coisometry.py v2.0 — Adversarial Verification (REM-14/15/21)")
    print("=" * 72)
    rng = np.random.default_rng(42)
    n, k = 128, 32

    # REM-15 FIX: mode='complete' produce Q in O(128) completa -> null_basis tiene 96 columnas reales
    A = rng.standard_normal((n, k))
    Q_full, _ = np.linalg.qr(A, mode="complete")
    W = Q_full[:, :k].T  # (32, 128)
    null_basis = Q_full[:, k:]  # (128, 96) — 96 vectores ortonormales NO NULOS en ker(W)
    assert null_basis.shape == (n, n - k), f"null_basis invalida: {null_basis.shape}"
    ortho_err = verify_coisometry_matrix(W)
    print(f"  [INIT] W shape={W.shape}, null_basis shape={null_basis.shape}, ||WW^T - I||_F={ortho_err:.2e}")

    # Combinacion lineal aleatoria no nula en ker(W) con ||s||_2 = 10.0
    weights = rng.standard_normal(n - k)
    s_ker_combo = null_basis @ weights
    s_ker_combo = s_ker_combo * (10.0 / np.linalg.norm(s_ker_combo))

    cases = {
        "normal_random":       (rng.standard_normal(n), False),
        "subnormal_1e-305":    (rng.standard_normal(n) * 1e-305, False),
        " near_zero_1e-16":    (rng.standard_normal(n) * 1e-16, False),
        "exact_zero_s":        (np.zeros(n), True),
        "exact_kernel_basis0": (null_basis[:, 0], True),
        "exact_kernel_combo":  (s_ker_combo, True),
    }

    all_pass = True
    for name, (s_vec, expect_ker) in cases.items():
        res = safe_coisometry_projection(W, s_vec, return_debug=True, check_orthonormal=True)
        norm_out = res["output_norm"]
        ok = (abs(norm_out - 1.0) < 1e-14) and (res["in_kernel"] == expect_ker)
        if not ok:
            all_pass = False
        print(
            f"  [{'PASS' if ok else 'FAIL'}] {name.strip():20s} | ||s||={res['norm_s']:.2e} "
            f"| ||Ws||={res['norm_ws']:.2e} | in_ker={str(res['in_kernel']):5s} | ||p||={norm_out:.15f}"
        )

    # Hound 2: Batch mixto con normales, ceros, subnormales y 50 vectores de ker(W)
    S_ker_50 = (null_basis @ rng.standard_normal((n - k, 50))).T
    S_mixed = np.vstack([
        rng.standard_normal((100, n)),
        np.zeros((20, n)),
        rng.standard_normal((30, n)) * 1e-300,
        S_ker_50,
    ])
    P_mixed = batch_coisometry_projection(W, S_mixed, check_orthonormal=True)
    batch_norms = np.linalg.norm(P_mixed, axis=1)
    batch_ok = bool(np.allclose(batch_norms, 1.0, atol=1e-14))
    all_pass = all_pass and batch_ok
    print(f"  [{'PASS' if batch_ok else 'FAIL'}] mixed_batch(200)     | max|norm-1|={np.max(np.abs(batch_norms - 1.0)):.2e}")

    # Hound 3: Tikhonov Lipschitz continuity across ker(W)
    eta = 1e-3
    delta = rng.standard_normal(n) * 1e-7
    u1 = safe_coisometry_projection(W, s_ker_combo, mode="tikhonov", eta=eta)
    u2 = safe_coisometry_projection(W, s_ker_combo + delta, mode="tikhonov", eta=eta)
    emp_lip = float(np.linalg.norm(u2 - u1) / np.linalg.norm(delta))
    lip_ok = emp_lip <= (1.0 / eta) * (1.0 + 1e-9)
    all_pass = all_pass and lip_ok
    print(f"  [{'PASS' if lip_ok else 'FAIL'}] tikhonov_lipschitz   | emp_L={emp_lip:.2f} <= bound={1.0/eta:.2f}")

    # Hound 4: Rechazo determinista de NaN / Inf
    nan_rejected = False
    try:
        bad = np.zeros(n)
        bad[0] = np.nan
        safe_coisometry_projection(W, bad)
    except ValueError:
        nan_rejected = True
    all_pass = all_pass and nan_rejected
    print(f"  [{'PASS' if nan_rejected else 'FAIL'}] nan_inf_guard        | NaN deterministicamente rechazado={nan_rejected}")

    print("=" * 72)
    if all_pass:
        print("[SUCCESS] pmtp_coisometry.py v2.0 — 9/9 controles adversariales PASS (Exit Code 0)")
        raise SystemExit(0)
    print("[FAILURE] Fallo en pmtp_coisometry.py v2.0")
    raise SystemExit(1)
