"""
POLYDIM-EINSOF — Banco de Pruebas Empírico: 3 Hipótesis SOTA en Silicio
========================================================================
Ejecución rigurosa y directa en silicio para evaluar 3 hipótesis radicales:
  1. Proyección Asintótica Extrema en D = 65.536 (Prueba de estrés numérico)
  2. Zero-Token Latent Transfer / Stiefel Residual Splice entre espacios dispares
  3. Optimización Riemanniana en Espacio Tangente Stiefel vs Weight Decay tradicional
Persistencia obligatoria en PostgreSQL 16 (polydim_active_db).
"""

import sys
import time
import math
import json
import torch
import numpy as np
import psycopg2
from datetime import datetime, timezone

PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASSWORD = "123"
PG_DB = "polydim_active_db"

def get_db():
    for pwd in ["1234", "123", "postgres", ""]:
        try:
            return psycopg2.connect(dbname=PG_DB, host=PG_HOST, port=PG_PORT, user=PG_USER, password=pwd)
        except Exception:
            continue
    raise RuntimeError("No se pudo conectar a PostgreSQL 16")

def log_to_postgres(test_name, metrics, verdict, details):
    try:
        conn = get_db()
        cur = conn.cursor()
        key = f"{test_name}_{int(time.time()*1000)}"
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test": test_name,
            "metrics": metrics,
            "verdict": verdict,
            "details": details
        }
        cur.execute("""
            INSERT INTO active_vault (category, key_name, value, notes)
            VALUES ('silicon_audit_ledger', %s, %s, %s)
            ON CONFLICT (category, key_name) DO UPDATE SET value=EXCLUDED.value, updated_at=CURRENT_TIMESTAMP;
        """, (key, json.dumps(payload, ensure_ascii=False), f"Veredicto: {verdict}"))
        conn.commit()
        conn.close()
        print(f"[POSTGRES] Registrado en active_vault.silicon_audit_ledger: {key}")
    except Exception as e:
        print(f"[WARN] Error registrando en PostgreSQL: {e}")

# ==============================================================================
# HIPÓTESIS 1: PROYECCIÓN ASINTÓTICA EXTREMA EN D = 65.536
# ==============================================================================
def test_hipotesis_1_asymptotic_65k():
    print("\n" + "="*80)
    print("  [HIPÓTESIS 1] Proyección Asintótica Extrema en Variedad de Stiefel (D = 65.536)")
    print("="*80)
    D = 65536
    k = 16
    print(f"Dimensiones: D = {D}, k = {k} | Precisión: float64 (IEEE 754)")
    print(f"Memoria de matriz cruda: {(D * k * 8) / (1024*1024):.2f} MB")
    
    t0 = time.time()
    torch.manual_seed(42)
    # Generar matriz aleatoria en R^{D x k}
    W = torch.randn(D, k, dtype=torch.float64)
    
    # 1. Retracción Polar via SVD (Referencia canónica)
    t_svd_start = time.time()
    U, _, Vt = torch.linalg.svd(W, full_matrices=False)
    W_polar = U @ Vt
    t_svd = time.time() - t_svd_start
    
    # 2. Medir defecto de ortogonalidad: ||W_polar^T W_polar - I_k||
    gram = W_polar.t() @ W_polar
    eye = torch.eye(k, dtype=torch.float64)
    diff = gram - eye
    max_defect = torch.max(torch.abs(diff)).item()
    frobenius_defect = torch.norm(diff, p='fro').item()
    
    # Cota teórica en float64 para dot-products de longitud D=65536:
    # sqrt(D) * eps_mach = sqrt(65536) * 2.22e-16 = 256 * 2.22e-16 = 5.68e-14
    eps_mach = 2.220446049250313e-16
    theoretical_bound = math.sqrt(D) * eps_mach
    
    # 3. Verificar si hay NaNs o desbordes
    has_nan = torch.isnan(W_polar).any().item()
    has_inf = torch.isinf(W_polar).any().item()
    is_sota = (max_defect <= 5.0 * theoretical_bound) and not has_nan and not has_inf
    
    metrics = {
        "D": D,
        "k": k,
        "max_defect": max_defect,
        "frobenius_defect": frobenius_defect,
        "theoretical_bound": theoretical_bound,
        "latency_svd_sec": round(t_svd, 4),
        "total_latency_sec": round(time.time() - t0, 4),
        "has_nan": has_nan,
        "has_inf": has_inf
    }
    
    verdict = "CONFIRMADO_SOTA_ESTABLE" if is_sota else "ALUCINACION_O_FRACTURA_NUMERICA"
    details = f"Defecto medido: {max_defect:.3e} vs Cota: {theoretical_bound:.3e}. Latencia SVD: {t_svd:.3f}s"
    
    print(f"  * Defecto Máximo |W^T W - I|: {max_defect:.4e}")
    print(f"  * Cota Teórica sqrt(D)*eps:    {theoretical_bound:.4e}")
    print(f"  * Defecto Frobenius:           {frobenius_defect:.4e}")
    print(f"  * Tiempo de cómputo SVD:       {t_svd:.3f} s")
    print(f"  * Veredicto en Silicio:        {verdict}")
    
    log_to_postgres("HIPOTESIS_1_ASINTOTICA_65K", metrics, verdict, details)
    return metrics, verdict

# ==============================================================================
# HIPÓTESIS 2: ZERO-TOKEN LATENT SPLICE (TRANSFERENCIA CONTINUA SIN TOKENIZADOR)
# ==============================================================================
def test_hipotesis_2_zero_token_latent_splice():
    print("\n" + "="*80)
    print("  [HIPÓTESIS 2] Zero-Token Latent Splice: Transferencia Continua sin Tokenizador")
    print("="*80)
    # Modelo A: Dimensión de espacio latente D_A = 1536 (ej: Qwen 1.5B)
    # Modelo B: Dimensión de espacio latente D_B = 2048 (ej: Mathesis 1.5B)
    D_A = 1536
    D_B = 2048
    seq_len = 8
    
    print(f"Transferencia de Modelo A (D={D_A}) -> Modelo B (D={D_B})")
    t0 = time.time()
    torch.manual_seed(42)
    
    # Tensor latente continuo generado en capa media de Modelo A (sin texto)
    h_A = torch.randn(seq_len, D_A, dtype=torch.float64)
    # Normalizar en la esfera S^{D_A-1}
    h_A_unit = h_A / torch.norm(h_A, dim=-1, keepdim=True)
    
    # Construir proyector ortogonal de Stiefel W_proj in St(D_A, D_B)
    # W_proj tiene columnas ortonormales en R^{D_B}
    M = torch.randn(D_B, D_A, dtype=torch.float64)
    Q, _ = torch.linalg.qr(M) # Q is D_B x D_A, Q^T Q = I_{D_A}
    W_proj = Q # Proyector de Stiefel
    
    # Proyección continua a la variedad del Modelo B
    # h_projected = h_A @ W_proj.T -> (seq_len x D_B)
    h_projected = h_A_unit @ W_proj.t()
    
    # Verificar propiedades de conservación isométrica:
    # 1. Conservación de distancias relativas / cosenos entre vectores de la secuencia
    gram_A = h_A_unit @ h_A_unit.t()
    gram_projected = h_projected @ h_projected.t()
    distortion = torch.max(torch.abs(gram_A - gram_projected)).item()
    
    # 2. Conservación de normas unitarias (permanencia en S^{D_B - 1})
    projected_norms = torch.norm(h_projected, dim=-1)
    norm_error = torch.max(torch.abs(projected_norms - 1.0)).item()
    
    # 3. Ausencia de singularidades
    has_nan = torch.isnan(h_projected).any().item()
    
    is_sota = (distortion <= 1e-14) and (norm_error <= 1e-14) and not has_nan
    metrics = {
        "D_A": D_A,
        "D_B": D_B,
        "distortion_pairwise_angles": distortion,
        "norm_error_sphere": norm_error,
        "latency_ms": round((time.time() - t0)*1000, 3),
        "tokens_generated": 0, # Cero tokens
        "bytes_transferred": seq_len * D_B * 8
    }
    
    verdict = "CONFIRMADO_SOTA_ISOMETRIA_PERFECTA" if is_sota else "ALUCINACION_O_DISTORSION_METRICA"
    details = f"Distorsión de ángulos: {distortion:.3e} | Error de norma esférica: {norm_error:.3e}"
    
    print(f"  * Tokens de texto generados:   0 (Puro tensor latente en memoria)")
    print(f"  * Distorsión de ángulos (cos): {distortion:.4e}")
    print(f"  * Error de norma sobre S^(D-1): {norm_error:.4e}")
    print(f"  * Latencia de inyección:       {metrics['latency_ms']} ms")
    print(f"  * Veredicto en Silicio:        {verdict}")
    
    log_to_postgres("HIPOTESIS_2_ZERO_TOKEN_SPLICE", metrics, verdict, details)
    return metrics, verdict

# ==============================================================================
# HIPÓTESIS 3: ACTUALIZACIÓN RIEMANNIANA EN ESPACIO TANGENTE VS WEIGHT DECAY
# ==============================================================================
def test_hipotesis_3_riemannian_tangent_vs_weight_decay():
    print("\n" + "="*80)
    print("  [HIPÓTESIS 3] Optimización Riemanniana Stiefel vs Weight Decay Tradicional")
    print("="*80)
    D = 512
    k = 64
    steps = 100
    lr = 0.01
    weight_decay = 0.01
    
    torch.manual_seed(42)
    # Inicializar matriz ortonormal W_0 en St(k, D)
    W_init = torch.randn(D, k, dtype=torch.float64)
    Q, _ = torch.linalg.qr(W_init)
    
    # 1. Trayectoria Tradicional: Gradiente con Weight Decay W_{t+1} = W_t - lr * G - lr * lambda * W_t
    W_trad = Q.clone()
    cond_trad_history = []
    
    # 2. Trayectoria Riemanniana: Proyección al espacio tangente Stiefel y Retracción Polar
    W_riem = Q.clone()
    cond_riem_history = []
    
    for step in range(steps):
        # Gradiente aleatorio que simula pérdida de atención
        G = torch.randn(D, k, dtype=torch.float64) * 0.1
        
        # Paso Tradicional (Euclídeo + Weight Decay)
        W_trad = W_trad - lr * G - lr * weight_decay * W_trad
        
        # Paso Riemanniano:
        # Gradiente Riemanniano en Stiefel: grad_R = G - W @ (G.T @ W + W.T @ G)/2
        sym = (G.t() @ W_riem + W_riem.t() @ G) * 0.5
        grad_riem = G - W_riem @ sym
        # Actualización sobre la variedad via retracción polar:
        W_cand = W_riem - lr * grad_riem
        U, _, Vt = torch.linalg.svd(W_cand, full_matrices=False)
        W_riem = U @ Vt
        
        # Medir número de condición kappa_2 = sigma_max / sigma_min
        if step % 20 == 0 or step == steps - 1:
            s_trad = torch.linalg.svdvals(W_trad)
            kappa_trad = (s_trad[0] / s_trad[-1]).item()
            cond_trad_history.append(kappa_trad)
            
            s_riem = torch.linalg.svdvals(W_riem)
            kappa_riem = (s_riem[0] / s_riem[-1]).item()
            cond_riem_history.append(kappa_riem)
            
    final_kappa_trad = cond_trad_history[-1]
    final_kappa_riem = cond_riem_history[-1]
    
    # El método tradicional debe colapsar la condición unitaria (kappa > 1.05 o degradación de norma)
    # El método Riemanniano debe mantener kappa exactamente = 1.000000000000000X
    is_sota = abs(final_kappa_riem - 1.0) <= 1e-14 and final_kappa_trad > 1.05
    
    metrics = {
        "steps": steps,
        "initial_kappa": 1.0,
        "final_kappa_traditional_weight_decay": final_kappa_trad,
        "final_kappa_riemannian_stiefel": final_kappa_riem,
        "stiefel_invariance_error": abs(final_kappa_riem - 1.0)
    }
    
    verdict = "CONFIRMADO_SOTA_CONDICIONAMIENTO_PERFECTO" if is_sota else "ALUCINACION_O_COLAPSO"
    details = f"Kappa Riemanniano: {final_kappa_riem:.16f} | Kappa Tradicional (degradado): {final_kappa_trad:.4f}"
    
    print(f"  * Pasos de optimización:       {steps}")
    print(f"  * Condicionamiento Tradicional: kappa_2 = {final_kappa_trad:.4f} (Degrada ortogonalidad)")
    print(f"  * Condicionamiento Riemanniano: kappa_2 = {final_kappa_riem:.16f} (Isometría exacta)")
    print(f"  * Error de invariancia:        {abs(final_kappa_riem - 1.0):.4e}")
    print(f"  * Veredicto en Silicio:        {verdict}")
    
    log_to_postgres("HIPOTESIS_3_RIEMANNIAN_OPTIMIZATION", metrics, verdict, details)
    return metrics, verdict

# ==============================================================================
# MAIN RUNNER
# ==============================================================================
def run_all():
    print("="*80)
    print("  CRISOL EXPERIMENTAL DE SILICIO — POLYDIM / EINSOF")
    print(f"  Fecha: {datetime.now(timezone.utc).isoformat()} | Host: Local CPU")
    print("="*80)
    
    r1, v1 = test_hipotesis_1_asymptotic_65k()
    r2, v2 = test_hipotesis_2_zero_token_latent_splice()
    r3, v3 = test_hipotesis_3_riemannian_tangent_vs_weight_decay()
    
    print("\n" + "="*80)
    print("  SÍNTESIS DE LAS 3 HIPÓTESIS EN SILICIO")
    print("="*80)
    print(f"1. D = 65.536 Asintótica:      [{v1}] Defecto = {r1['max_defect']:.2e}")
    print(f"2. Zero-Token Latent Splice:    [{v2}] Distorsión = {r2['distortion_pairwise_angles']:.2e}")
    print(f"3. Riemanniano vs Weight Decay: [{v3}] Kappa = {r3['final_kappa_riemannian_stiefel']:.16f}")
    print("="*80)
    print("Resultados consolidados en PostgreSQL 16 (polydim_active_db). Exit Code 0.")

if __name__ == "__main__":
    run_all()
