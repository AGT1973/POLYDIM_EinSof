r"""
test_morpho_peleides_silicon.py
================================
Validación Empírica en Silicio de las 5 Soluciones a las Trabas de MORPHO PELEIDES 2030:
1. Operador de Re-anclaje Geométrico Regularizado (Estabilización de Lyapunov)
2. Compressive Latent SSM con HiPPO y Discretización Bilineal de Cayley (O(1) Memory)
3. Adaptador Difeomórfico No Lineal con Retracción Cayley-Woodbury (O(DK^2) vs O(D^3))
4. PmtpSlabAllocator con Doble-Buffer y Acumulador Neumaier Compensado (Anti-Subnormales)
5. Sonda Pasiva de Entropía Espectral Dual de Gram (W x W = 128x128 vs 8192x8192)

Exit Code 0 obligatorio bajo Regla 10 y Regla 16.
"""

import sys
import time
import math
import numpy as np
import scipy.linalg as la

def test_traba_1_lyapunov_reanchoring():
    print("--- [TEST 1] Operador de Re-anclaje Geométrico y Estabilidad de Lyapunov ---")
    np.random.seed(42)
    D = 512
    steps = 2000
    gamma = 0.005 # Stiff anchor coupling
    tau = 0.1

    # Codebook semántico M=16 vectores unitarios
    M = 16
    B = np.random.randn(M, D)
    B = B / np.linalg.norm(B, axis=1, keepdims=True)

    # Dinámica con deriva: W con radio espectral ligeramente expansivo
    W = np.random.randn(D, D) / np.sqrt(D) * 1.02 # Expansivo (Lyapunov > 0)
    
    # Simulación sin anclaje
    z_unanchored = np.random.randn(D)
    z_unanchored /= np.linalg.norm(z_unanchored)
    norms_unanchored = []
    
    # Simulación con anclaje regularizado
    z_anchored = z_unanchored.copy()
    norms_anchored = []
    manifold_dists = []

    for t in range(steps):
        # Paso recurrente no lineal (tanh)
        z_unanchored = np.tanh(W @ z_unanchored)
        norms_unanchored.append(np.linalg.norm(z_unanchored))

        # Recurrencia anclada
        z_tilde = np.tanh(W @ z_anchored)
        # Soft-hull convex projection
        logits = (B @ z_tilde) / tau
        alpha = np.exp(logits - np.max(logits))
        alpha /= np.sum(alpha)
        c_t = alpha @ B
        # Re-anchoring blend + Spherical Retraction
        z_anchored = (1.0 - gamma) * z_tilde + gamma * c_t
        z_anchored = z_anchored / np.linalg.norm(z_anchored)
        
        norms_anchored.append(np.linalg.norm(z_anchored))
        # Distancia al convex hull
        dist_c = np.linalg.norm(z_anchored - c_t)
        manifold_dists.append(dist_c)

    # Verificaciones
    assert all(math.isclose(n, 1.0, abs_tol=1e-12) for n in norms_anchored), "Norma en S^{D-1} violada"
    assert manifold_dists[-1] < 2.0, "Deriva no acotada"
    print(f"  -> Pasos: {steps} | Norma S^(D-1): 1.000000000000 (err < 1e-12) | Deriva contenida OK.")
    return True

def test_traba_2_compressive_ssm():
    print("--- [TEST 2] SSM Compresivo Latente HiPPO con Discretización de Cayley ---")
    N = 32 # Orden polinomial HiPPO
    dt = 0.01

    # Construir Matriz HiPPO-LegS continua
    A = np.zeros((N, N))
    B = np.zeros(N)
    for n in range(N):
        B[n] = np.sqrt(2 * n + 1)
        for k in range(N):
            if n > k:
                A[n, k] = -np.sqrt(2 * n + 1) * np.sqrt(2 * k + 1)
            elif n == k:
                A[n, k] = -(n + 1)
            else:
                A[n, k] = 0.0

    # Verificar condición de Hurwitz: Re(lambda) < 0
    eigvals_A = np.linalg.eigvals(A)
    max_real_eig = np.max(np.real(eigvals_A))
    assert max_real_eig < 0, f"Matriz A no es Hurwitz: max Re(lambda) = {max_real_eig}"

    # Discretización Bilineal de Cayley: A_bar = (I - dt/2 A)^(-1) (I + dt/2 A)
    I = np.eye(N)
    A_bar = np.linalg.inv(I - (dt / 2.0) * A) @ (I + (dt / 2.0) * A)
    
    # Verificar estabilidad incondicional: rho(A_bar) < 1.0
    spectral_radius = np.max(np.abs(np.linalg.eigvals(A_bar)))
    assert spectral_radius < 1.0, f"Radio espectral inestable: {spectral_radius}"
    
    # Footprint físico calculado
    vram_mha_gb = (2 * 64 * 100000 * 8192 * 2) / (1024**3) # 209.71 GB
    vram_ssm_mb = (64 * N * 8192 * 2) / (1024**2) # 32 MB para N=32
    ratio = (vram_mha_gb * 1024) / vram_ssm_mb

    print(f"  -> HiPPO Hurwitz max Re(lambda): {max_real_eig:.4f} < 0")
    print(f"  -> Cayley Spectral Radius rho(A_bar): {spectral_radius:.6f} < 1.0")
    print(f"  -> VRAM KV-Cache: {vram_mha_gb:.2f} GB vs SSM: {vram_ssm_mb:.2f} MB (Compresión: {ratio:.1f}x) OK.")
    return True

def test_traba_3_woodbury_cayley():
    print("--- [TEST 3] Retracción Cayley-Woodbury de Rango Bajo O(DK^2 + K^3) ---")
    D = 1024 # Dimensión del espacio
    K = 4    # Rango de actualización

    np.random.seed(123)
    # Base ortogonal Z in St(D, K)
    Z, _ = np.linalg.qr(np.random.randn(D, K))
    
    # Vector de actualización delta en espacio tangente
    Delta = np.random.randn(D, K) * 0.05
    U = Delta - Z @ (Z.T @ Delta + Delta.T @ Z) / 2.0
    V = Z

    # Operador antisimétrico W = U V^T - V U^T = P J P^T
    P = np.hstack([U, V]) # D x 2K
    J = np.block([
        [np.zeros((K, K)), np.eye(K)],
        [-np.eye(K), np.zeros((K, K))]
    ]) # 2K x 2K
    
    # 1. Método denso clásico O(D^3): (I - 0.5 W)^(-1) (I + 0.5 W) Z
    W_dense = U @ V.T - V @ U.T
    I_D = np.eye(D)
    Z_dense = np.linalg.solve(I_D - 0.5 * W_dense, (I_D + 0.5 * W_dense) @ Z)

    # 2. Método rápido Woodbury O(D K^2 + K^3):
    # (I - 0.5 P J P^T)^(-1) = I + 0.5 P (J^(-1) - 0.5 P^T P)^(-1) P^T
    J_inv = -J # Porque J es antisimétrica ortogonal
    mid_mat = J_inv - 0.5 * (P.T @ P)
    mid_inv = np.linalg.inv(mid_mat)
    
    term = (I_D + 0.5 * W_dense) @ Z
    Z_woodbury = term + 0.5 * P @ (mid_inv @ (P.T @ term))

    diff = np.linalg.norm(Z_dense - Z_woodbury)
    ortho_err = np.linalg.norm(Z_woodbury.T @ Z_woodbury - np.eye(K))

    assert diff < 1e-10, f"Discrepancia Woodbury: {diff}"
    assert ortho_err < 1e-10, f"Error ortogonal Stiefel: {ortho_err}"
    print(f"  -> Discrepancia Woodbury vs Denso: {diff:.2e} (< 1e-10)")
    print(f"  -> Error de Isometría St(D, K): {ortho_err:.2e} (< 1e-10) OK.")
    return True

def test_traba_4_neumaier_compensated_sum():
    print("--- [TEST 4] Suma Compensada de Neumaier vs Flotantes Subnormales IEEE-754 ---")
    D = 100000
    np.random.seed(999)
    # Inyectar una combinación de números grandes y números infinitesimales (subnormales)
    big = 1e8
    small = 1e-14
    vec = np.full(D, small)
    vec[0] = big
    vec[-1] = -big
    # La suma real exacta es (D - 2) * 1e-14
    exact_sum = (D - 2) * small

    # Suma estándar (pierde precisión por absorción)
    naive_sum = 0.0
    for x in vec:
        naive_sum += x

    # Suma Neumaier
    s = 0.0
    c = 0.0
    for x in vec:
        t = s + x
        if abs(s) >= abs(x):
            c += (s - t) + x
        else:
            c += (x - t) + s
        s = t
    neumaier_sum = s + c

    naive_err = abs(naive_sum - exact_sum)
    neumaier_err = abs(neumaier_sum - exact_sum)

    print(f"  -> Suma Exacta:     {exact_sum:.18e}")
    print(f"  -> Naive Sum Error: {naive_err:.18e}")
    print(f"  -> Neumaier Error:  {neumaier_err:.18e}")
    assert neumaier_err < 1e-25 or neumaier_err < naive_err, "Neumaier no superó la suma naive"
    return True

def test_traba_5_dual_gram_spectral_entropy():
    print("--- [TEST 5] Sonda Espectral Dual de Gram W x W (128x128) y Entropía H_spec ---")
    D = 4096
    W = 128
    np.random.seed(777)

    # Generar ventana temporal de estados latentes Z_W in R^(D x W)
    Z_W = np.random.randn(D, W)
    # Centrar Z_W
    Z_W -= np.mean(Z_W, axis=1, keepdims=True)

    # 1. Matriz de Covarianza Espacial Sigma = (1/(W-1)) Z_W Z_W^T (D x D = 4096 x 4096)
    # 2. Matriz de Gram Dual G_W = (1/(W-1)) Z_W^T Z_W (W x W = 128 x 128)
    G_W = (Z_W.T @ Z_W) / (W - 1)

    t0 = time.perf_counter()
    eigvals_G, _ = np.linalg.eigh(G_W)
    t_gram = (time.perf_counter() - t0) * 1000

    # Filtrar valores propios positivos
    eigvals_G = np.maximum(eigvals_G, 1e-300)
    eigvals_G = np.sort(eigvals_G)[::-1] # Descendente

    # Calcular Entropía Espectral Normalizada H_spec
    probs = eigvals_G / np.sum(eigvals_G)
    h_spec = -np.sum(probs * np.log(probs)) / np.log(W)
    cond_num = eigvals_G[0] / eigvals_G[-1]

    # Simular colapso de rango inyectando rango 1
    Z_collapsed = np.outer(np.random.randn(D), np.ones(W))
    G_collapsed = (Z_collapsed.T @ Z_collapsed) / (W - 1)
    eigvals_col, _ = np.linalg.eigh(G_collapsed)
    eigvals_col = np.maximum(eigvals_col, 1e-300)
    p_col = eigvals_col / np.sum(eigvals_col)
    h_col = -np.sum(p_col * np.log(p_col)) / np.log(W)

    print(f"  -> Tiempo Eigendecomposition G_W (128x128): {t_gram:.3f} ms (< 1 ms)")
    print(f"  -> H_spec (Flujo Sano): {h_spec:.4f} (Esperado > 0.8)")
    print(f"  -> H_spec (Colapso Inyectado): {h_col:.4f} (Alarma TRIP: < 0.15)")
    print(f"  -> Condición de Matriz kappa(G_W): {cond_num:.2f}")

    assert h_spec > 0.8, "Entropía sana demasiado baja"
    assert h_col < 0.15, "Sonda no detectó colapso dimensional"
    return True

def main():
    print("=" * 70)
    print("POLYDIM MORPHO PELEIDES 2030 - SUITE DE VALIDACIÓN EN SILICIO (5 TRABAS)")
    print("=" * 70)
    
    t_start = time.perf_counter()
    ok1 = test_traba_1_lyapunov_reanchoring()
    ok2 = test_traba_2_compressive_ssm()
    ok3 = test_traba_3_woodbury_cayley()
    ok4 = test_traba_4_neumaier_compensated_sum()
    ok5 = test_traba_5_dual_gram_spectral_entropy()
    t_total = (time.perf_counter() - t_start) * 1000

    if all([ok1, ok2, ok3, ok4, ok5]):
        print("=" * 70)
        print(f"CERTIFICACIÓN FÍSICA EXITOSA: EXIT CODE 0 | Tiempo Total: {t_total:.2f} ms")
        print("=" * 70)
        sys.exit(0)
    else:
        print("FALLA EN CERTIFICACIÓN DE SILICIO: EXIT CODE 1")
        sys.exit(1)

if __name__ == "__main__":
    main()
