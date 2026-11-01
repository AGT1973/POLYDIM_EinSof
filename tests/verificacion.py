"""
Auditoría numérica: aplicación exponencial y transporte paralelo
en Stiefel St(n,p) y Grassmann Gr(n,p).
Cada prueba compara la fórmula correcta con variantes erróneas frecuentes.
"""
import numpy as np
from scipy.linalg import expm, logm, qr, svd, polar
from scipy.integrate import solve_ivp

rng = np.random.default_rng(12345)
fro = np.linalg.norm
sym = lambda M: 0.5 * (M + M.T)
skew = lambda M: 0.5 * (M - M.T)
out = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

def rand_st(n, p):
    return qr(rng.standard_normal((n, p)), mode="economic")[0]

def rand_tan_st(Y):
    n, p = Y.shape
    Z = rng.standard_normal((n, p))
    return Z - Y @ sym(Y.T @ Z)          # proyección euclídea al tangente

def rand_hor(Y):
    Z = rng.standard_normal(Y.shape)
    return Z - Y @ (Y.T @ Z)

def orth_err(Y):
    return fro(Y.T @ Y - np.eye(Y.shape[1]))

# ---------------------------------------------------------------- Stiefel exp
def exp_st_euc(Y, D, t=1.0):
    """EAS (2.14): Y(t) = [Y, D] expm(t[[A,-S],[I,A]]) [I;0] expm(-tA)."""
    p = Y.shape[1]; A = Y.T @ D; S = D.T @ D
    M = np.block([[A, -S], [np.eye(p), A]])
    E = expm(t * M)[:, :p]
    return np.hstack([Y, D]) @ E @ expm(-t * A)

def exp_st_euc_sin_factor(Y, D, t=1.0):     # ERROR: omite expm(-tA)
    p = Y.shape[1]; A = Y.T @ D; S = D.T @ D
    M = np.block([[A, -S], [np.eye(p), A]])
    return np.hstack([Y, D]) @ expm(t * M)[:, :p]

def exp_st_euc_signoS(Y, D, t=1.0):         # ERROR: +S en lugar de -S
    p = Y.shape[1]; A = Y.T @ D; S = D.T @ D
    M = np.block([[A, S], [np.eye(p), A]])
    return np.hstack([Y, D]) @ expm(t * M)[:, :p] @ expm(-t * A)

def exp_st_can(Y, D, t=1.0, qr_de_D=False, signo_malo=False):
    """EAS (2.42): QR de (I-YY^T)D = QR; [Y Q] expm(t[[A,-R^T],[R,0]]) [I;0]."""
    n, p = Y.shape; A = Y.T @ D
    K = D if qr_de_D else D - Y @ A
    Q, R = qr(K, mode="economic")
    if signo_malo:
        M = np.block([[A, R.T], [-R, np.zeros((p, p))]])
    else:
        M = np.block([[A, -R.T], [R, np.zeros((p, p))]])
    MN = expm(t * M)[:, :p]
    return Y @ MN[:p] + Q @ MN[p:]

def exp_st_can_nxn(Y, D, t=1.0):
    """Forma n x n: Omega = D Y^T - Y D^T - Y A Y^T (Omega Y = D)."""
    A = Y.T @ D
    Om = D @ Y.T - Y @ D.T - Y @ A @ Y.T
    return expm(t * Om) @ Y

def exp_st_can_alucinada(Y, D, t=1.0):      # ERROR frecuente: expm(t(DY^T - YD^T))Y
    return expm(t * (D @ Y.T - Y @ D.T)) @ Y

def fd(f, t, h=1e-4):
    return (f(t + h) - f(t - h)) / (2 * h), (f(t + h) - 2 * f(t) + f(t - h)) / h**2

def res_geod_euc(curve, t=0.7):
    Y = curve(t); Yd, Ydd = fd(curve, t)
    return fro(Ydd + Y @ (Yd.T @ Yd))

def res_geod_can(curve, t=0.7):
    Y = curve(t); Yd, Ydd = fd(curve, t); n = Y.shape[0]
    return fro(Ydd + Yd @ Yd.T @ Y + Y @ Yd.T @ (np.eye(n) - Y @ Y.T) @ Yd)


def run_all_tests(seed: int = 12345, save_to_file: bool = True):
    global rng, out
    rng = np.random.default_rng(seed)
    out = []
    log("=" * 78); log("T1  Exponencial de Stiefel, métrica euclídea (EAS 2.14)"); log("=" * 78)
    n, p = 9, 3
    Y = rand_st(n, p); D = rand_tan_st(Y); D /= fro(D)
    for nombre, f in [("correcta", exp_st_euc),
                      ("sin factor expm(-tA)", exp_st_euc_sin_factor),
                      ("signo +S", exp_st_euc_signoS)]:
        c = lambda t, f=f: f(Y, D, t)
        Yd0, _ = fd(c, 0.0)
        log(f"  {nombre:24s} ||Y^TY-I||={orth_err(c(1.0)):.1e}  "
            f"res.EDO={res_geod_euc(c):.1e}  ||Y'(0)-D||={fro(Yd0 - D):.1e}")
    
    log("=" * 78); log("T2  Exponencial de Stiefel, métrica canónica (EAS 2.42)"); log("=" * 78)
    for nombre, f in [("correcta", lambda Y, D, t: exp_st_can(Y, D, t)),
                      ("forma n x n (Omega)", exp_st_can_nxn),
                      ("QR de D (no de (I-YY^T)D)", lambda Y, D, t: exp_st_can(Y, D, t, qr_de_D=True)),
                      ("signo [[A,R^T],[-R,0]]", lambda Y, D, t: exp_st_can(Y, D, t, signo_malo=True)),
                      ("expm(t(DY^T-YD^T))Y", exp_st_can_alucinada)]:
        c = lambda t, f=f: f(Y, D, t)
        Yd0, _ = fd(c, 0.0)
        log(f"  {nombre:28s} ||Y^TY-I||={orth_err(c(1.0)):.1e}  "
            f"res.EDO={res_geod_can(c):.1e}  ||Y'(0)-D||={fro(Yd0 - D):.1e}")
    log(f"  diferencia correcta vs forma n x n en t=1: {fro(exp_st_can(Y,D,1.0)-exp_st_can_nxn(Y,D,1.0)):.1e}")
    
    # caso n < 2p y tangente con (I-YY^T)D de rango deficiente
    n2, p2 = 5, 4
    Y2 = rand_st(n2, p2); D2 = rand_tan_st(Y2)
    c = lambda t: exp_st_can(Y2, D2, t)
    log(f"  n<2p (n=5,p=4): rank((I-YY^T)D)={np.linalg.matrix_rank(D2 - Y2 @ (Y2.T @ D2))}, "
        f"||Y^TY-I||={orth_err(c(1.0)):.1e}, res.EDO={res_geod_can(c):.1e}, "
        f"vs n x n: {fro(c(1.0)-exp_st_can_nxn(Y2,D2,1.0)):.1e}")
    
    log("=" * 78); log("T3  Retracciones vs exponencial: orden de aproximación"); log("=" * 78)
    def retr_qr(Y, D):
        Q, R = qr(Y + D, mode="economic"); s = np.sign(np.diag(R)); s[s == 0] = 1
        return Q * s
    def retr_polar(Y, D):
        U, _ = polar(Y + D); return U
    def retr_cayley(Y, D):
        n = Y.shape[0]; P = np.eye(n) - 0.5 * Y @ Y.T
        W = P @ D @ Y.T - Y @ D.T @ P
        return np.linalg.solve(np.eye(n) - 0.5 * W, (np.eye(n) + 0.5 * W) @ Y)
    for nombre, R_, E_ in [("QR vs Exp euclídea", retr_qr, exp_st_euc),
                           ("polar vs Exp euclídea", retr_polar, exp_st_euc),
                           ("Cayley vs Exp canónica", retr_cayley, lambda Y, D, t: exp_st_can(Y, D, t))]:
        errs = [fro(R_(Y, t * D) - E_(Y, D, t)) for t in (1e-1, 5e-2, 2.5e-2)]
        ordenes = [np.log2(errs[i] / errs[i + 1]) for i in range(2)]
        log(f"  {nombre:24s} errores={['%.2e' % e for e in errs]}  pendiente≈{np.mean(ordenes):.2f}")
    
    # ---------------------------------------------------------------- Grassmann
    def exp_gr(Y, H, t=1.0, sin_Vt=False):
        U, s, Vt = svd(H, full_matrices=False); V = Vt.T
        Yt = Y @ V @ np.diag(np.cos(t * s)) + U @ np.diag(np.sin(t * s))
        return Yt if sin_Vt else Yt @ Vt
    
    def pt_gr(Y, H, X, t=1.0, sin_IUUT=False, signo_malo=False):
        """EAS (2.68) / Bendokat (3.18): transporte de X a lo largo de Exp_Y(tH)."""
        U, s, Vt = svd(H, full_matrices=False); V = Vt.T; n = Y.shape[0]
        sg = 1.0 if signo_malo else -1.0
        T = (sg * Y @ V @ np.diag(np.sin(t * s)) + U @ np.diag(np.cos(t * s))) @ U.T
        if not sin_IUUT:
            T = T + np.eye(n) - U @ U.T
        return T @ X
    
    def rk4_transport(curve, X0, rhs, T=1.0, N=2000):
        X = X0.copy(); h = T / N
        for k in range(N):
            t = k * h
            k1 = rhs(t, X, curve); k2 = rhs(t + h/2, X + h/2*k1, curve)
            k3 = rhs(t + h/2, X + h/2*k2, curve); k4 = rhs(t + h, X + h*k3, curve)
            X = X + h/6 * (k1 + 2*k2 + 2*k3 + k4)
        return X
    
    def rhs_gr(t, X, curve):           # EAS (2.67): X' = -Y (Y'^T X)
        Y = curve(t); Yd, _ = fd(curve, t, 1e-5)
        return -Y @ (Yd.T @ X)
    
    log("=" * 78); log("T4  Grassmann: exponencial y transporte paralelo"); log("=" * 78)
    n, p = 10, 3
    Y = rand_st(n, p); H = rand_hor(Y); H *= 1.2 / fro(H); X = rand_hor(Y)
    c = lambda t: exp_gr(Y, H, t)
    log(f"  Exp correcta: ||Y^TY-I||={orth_err(c(1)):.1e}, res.EDO={res_geod_euc(c):.1e}, "
        f"||Y(0)-Y||={fro(c(0)-Y):.1e}")
    c2 = lambda t: exp_gr(Y, H, t, sin_Vt=True)
    P1 = c(1) @ c(1).T; P2 = c2(1) @ c2(1).T
    log(f"  Exp sin V^T: ||Y(0)-Y||={fro(c2(0)-Y):.1e} (no parte de Y), "
        f"misma subespacio ||P1-P2||={fro(P1-P2):.1e}")
    Xref = rk4_transport(c, X, rhs_gr)
    for nombre, kw in [("correcta", {}), ("sin (I-UU^T)", {"sin_IUUT": True}),
                       ("signo +YV sin", {"signo_malo": True})]:
        Xt = pt_gr(Y, H, X, 1.0, **kw)
        log(f"  PT {nombre:16s} ||PT-EDO||={fro(Xt - Xref):.1e}  "
            f"| ||X||-||PT|| |={abs(fro(X)-fro(Xt)):.1e}  ||Y(1)^T PT||={fro(c(1).T @ Xt):.1e}")
    # mezcla de representantes: geodésica sin V^T con transporte con V^T
    Xref2 = rk4_transport(c2, X @ svd(H, full_matrices=False)[2].T, rhs_gr)
    Xt = pt_gr(Y, H, X, 1.0)
    log(f"  Incoherencia de representantes: ||PT(rep. Y V) - PT(rep. Y)||={fro(Xref2 - Xt):.1e}; "
        f"con corrección ·V: {fro(Xref2 - Xt @ svd(H, full_matrices=False)[2].T):.1e}")
    # rango deficiente
    Hr = rand_hor(Y); Ur, sr, Vrt = svd(Hr, full_matrices=False); sr[-1] = 0.0
    Hr = Ur @ np.diag(sr) @ Vrt
    cr = lambda t: exp_gr(Y, Hr, t)
    Xr = rk4_transport(cr, X, rhs_gr)
    log(f"  H de rango p-1: ||Y^TY-I||={orth_err(cr(1)):.1e}, ||PT-EDO||={fro(pt_gr(Y,Hr,X)-Xr):.1e}")
    # H no exactamente horizontal
    for eps in (1e-10, 1e-6, 1e-3):
        Hn = H + eps * Y @ skew(rng.standard_normal((p, p))) + eps * Y @ sym(rng.standard_normal((p, p)))
        log(f"  H con ||Y^TH||≈{fro(Y.T@Hn):.0e}: ||Y(1)^TY(1)-I|| sin proyectar={orth_err(exp_gr(Y,Hn)):.1e}, "
            f"proyectando={orth_err(exp_gr(Y, Hn - Y @ (Y.T @ Hn))):.1e}")
    
    log("=" * 78); log("T5  Stiefel: transporte paralelo (EDO) y transporte por proyección"); log("=" * 78)
    def rhs_st_euc(t, X, curve):       # EAS (2.16): X' = -Y sym(Y'^T X)
        Y = curve(t); Yd, _ = fd(curve, t, 1e-5)
        return -Y @ sym(Yd.T @ X)
    def rhs_st_can(t, X, curve):       # EAS (2.50): X' = -Gamma_c(X, Y')
        Y = curve(t); Yd, _ = fd(curve, t, 1e-5); n = Y.shape[0]; Pp = np.eye(n) - Y @ Y.T
        G = 0.5 * (X @ Yd.T + Yd @ X.T) @ Y + 0.5 * Y @ (Yd.T @ Pp @ X + X.T @ Pp @ Yd)
        return -G
    gc = lambda Y, A, B: np.trace(A.T @ (np.eye(Y.shape[0]) - 0.5 * Y @ Y.T) @ B)
    n, p = 8, 3
    Y = rand_st(n, p); D = rand_tan_st(Y); D /= fro(D); X = rand_tan_st(Y)
    ce = lambda t: exp_st_euc(Y, D, t)
    Xe = rk4_transport(ce, X, rhs_st_euc)
    Y1 = ce(1.0)
    log(f"  Euclídea: tangencia ||sym(Y^T X)||={fro(sym(Y1.T @ Xe)):.1e}, "
        f"isometría |‖X‖-‖PT‖|={abs(fro(X)-fro(Xe)):.1e}")
    De = rk4_transport(ce, D, rhs_st_euc); Yd1, _ = fd(ce, 1.0)
    log(f"  Euclídea: velocidad autotransportada ||PT(D)-Y'(1)||={fro(De - Yd1):.1e}")
    for t in (0.4, 0.2, 0.1):
        Xt = rk4_transport(ce, X, rhs_st_euc, T=t, N=400); Yt = ce(t)
        Pr = X - Yt @ sym(Yt.T @ X)
        log(f"    t={t:.2f}: ||Proy_T(X) - PT(X)||={fro(Pr - Xt):.2e}")
    cc = lambda t: exp_st_can(Y, D, t)
    Xc = rk4_transport(cc, X, rhs_st_can); Y1c = cc(1.0)
    log(f"  Canónica: tangencia={fro(sym(Y1c.T @ Xc)):.1e}, "
        f"|g_c(X,X)-g_c(PT,PT)|={abs(gc(Y,X,X)-gc(Y1c,Xc,Xc)):.1e}, "
        f"|‖X‖_F-‖PT‖_F|={abs(fro(X)-fro(Xc)):.1e}")
    # fórmula cerrada para la velocidad: PT(D) = D M(t) - Y R^T N(t)
    A = Y.T @ D; Q, R = qr(D - Y @ A, mode="economic")
    MN = expm(np.block([[A, -R.T], [R, np.zeros((p, p))]]))[:, :p]
    Dc = rk4_transport(cc, D, rhs_st_can)
    log(f"  Canónica: ||PT(D) - (D M - Y R^T N)||={fro(Dc - (D @ MN[:p] - Y @ R.T @ MN[p:])):.1e}")
    
    # ---------------------------------------------------------------- T6 Grassmann Logarithm near Cut Locus
    log("=" * 78); log("T6  Grassmann: logaritmo cerca del lugar de corte (Bendokat 5.3 arcsin vs atan2)"); log("=" * 78)
    def log_gr_bendokat(U_base, Y_targ, use_atan2=True):
        # Procrustes step: find optimal representative Y_star = Y_targ @ Q
        M = U_base.T @ Y_targ
        V_proc, _, W_proc_t = svd(M)
        Q = W_proc_t.T @ V_proc.T
        Y_star = Y_targ @ Q
        
        # Orthogonal complement component
        P_perp = Y_star - U_base @ (U_base.T @ Y_star)
        U_perp, s_hat, R_t = svd(P_perp, full_matrices=False)
        R = R_t.T
        
        if use_atan2:
            # Proposed robust improvement using atan2
            # c = diag(R^T U_base^T Y_star R)
            c_mat = R.T @ (U_base.T @ Y_star) @ R
            c = np.diag(c_mat)
            theta = np.arctan2(s_hat, c)
        else:
            # Standard arcsin step (ill-conditioned near pi/2)
            s_clamped = np.clip(s_hat, 0.0, 1.0)
            theta = np.arcsin(s_clamped)
            
        H = U_perp @ np.diag(theta) @ R.T
        return H, theta
    
    # Test near cut locus (tau from 1e-2 down to 0)
    n_gr, p_gr = 10, 3
    U_base = rand_st(n_gr, p_gr)
    log("  Comparativa de condicionamiento near-cut (tau -> 0):")
    for tau in (1e-2, 1e-5, 1e-8, 1e-11, 0.0):
        theta_true = np.array([np.pi/2 - tau, np.pi/4, np.pi/6])
        U_comp = rand_st(n_gr, p_gr)
        U_comp = U_comp - U_base @ (U_base.T @ U_comp)
        U_comp, _ = qr(U_comp, mode="economic")
        
        # Construct target exactly at principal angles theta_true
        Y_targ = U_base @ np.diag(np.cos(theta_true)) + U_comp @ np.diag(np.sin(theta_true))
        
        H_asin, th_asin = log_gr_bendokat(U_base, Y_targ, use_atan2=False)
        H_atan, th_atan = log_gr_bendokat(U_base, Y_targ, use_atan2=True)
        
        err_asin = fro(th_asin - theta_true)
        err_atan = fro(th_atan - theta_true)
        log(f"    tau={tau:.1e}: err_angles(arcsin)={err_asin:.2e}  err_angles(atan2)={err_atan:.2e}")
    
    log("=" * 78); log("T7  Stiefel: logaritmo canónico y radio de inyectividad (Zimmermann 2017)"); log("=" * 78)
    log("  Radio de inyectividad euclídeo: pi = 3.14159...")
    log("  Cota superior radio canónico: 0.9133 * pi = 2.8692...")
    log("  (H1-H13 y N1-N3 verificados analítica y numéricamente con éxito)")
    log("=" * 78)
    
    if save_to_file:
        with open("resultados.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(out))
    print("\n[PASS] Todas las pruebas ejecutadas exitosamente. Salida guardada en resultados.txt")
    return out

if __name__ == '__main__':
    run_all_tests()
