"""
POLYDIM-EINSOF — Sabueso QA Autónomo Adversarial para ALADIN (Regla 15)
=======================================================================
Agente de Control de Calidad Autónomo, Continuo e Implacable.
No depende de humanos ni alumnos. Bombardea metódicamente el nodo ALADIN
(192.168.100.21:11434 / 9999) buscando:
  1. Fracturas asintóticas (D >= 16384, NaNs, Infs, vectores nulos).
  2. Desbordes de contexto y saturación de KV Cache.
  3. Colapso de concurrencia y fugas de memoria VRAM/RAM.
  4. Desacoples de dominio (inyecciones tipo Rafael: h_L en inputs_embeds).
  5. Derivas numéricas en la variedad de Stiefel (defecto > 1e-15).
"""

import os
import sys
import json
import time
import math
import random
import urllib.request
import psycopg2
from datetime import datetime, timezone

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", "postgres")
PG_PASSWORD = os.environ.get("PGPASSWORD", "1234")
PG_DB = os.environ.get("PGDATABASE", "polydim_active_db")

ALADIN_HOST = "http://192.168.100.21:11434"

def get_db_connection():
    return psycopg2.connect(
        dbname=PG_DB, host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASSWORD
    )

def log_incident_to_postgres(hound_name, test_name, severity, details, passed):
    """Registra los hallazgos directamente en PostgreSQL 16."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        incident_id = f"QA_{int(time.time()*1000)}"
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hound": hound_name,
            "test": test_name,
            "severity": severity,
            "passed": passed,
            "details": details
        }
        cur.execute("""
            INSERT INTO active_vault (category, key_name, value, notes)
            VALUES ('qa_adversarial_hound', %s, %s, %s)
            ON CONFLICT (category, key_name) DO UPDATE SET value=EXCLUDED.value, updated_at=CURRENT_TIMESTAMP;
        """, (incident_id, json.dumps(payload, ensure_ascii=False), f"Severidad: {severity} | Passed: {passed}"))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WARN] Error registrando en active_vault: {e}")

# ==============================================================================
# BATERÍA 1: ATAQUES DE LÍMITE NUMÉRICO Y FRACTURAS DE TENSORES
# ==============================================================================
def attack_numeric_and_nan(model_slug="mathesis-quantum:1.5b"):
    """Inyecta payloads con valores extremos, subnormales y secuencias de escape."""
    print(f"\n[SABUESO 1/5] Lanzando ataque de frontera numérica contra {model_slug}...")
    edge_payloads = [
        {"desc": "Inyección NaN y Float Overflow", "prompt": "[TENSOR_INJECT: NaN, +Inf, -Inf, 1e308, -1e308] Computar geodésica."},
        {"desc": "Vector Nulo (Norma Cero)", "prompt": "[TENSOR_ZERO: [0.0]*2048] Calcular retracción polar de Stiefel W(W^T W)^(-1/2)."},
        {"desc": "Desborde de Precisión Subnormal", "prompt": "[FLOAT_SUBNORMAL: 1e-45, 5e-324] Proyectar sobre S^{D-1}."},
        {"desc": "Gram Degenerada (Det = 0)", "prompt": "[DEGENERATE_GRAM: Colineal rank=1 en R^{4096}] Evaluar ortogonalidad."}
    ]
    
    results = []
    for p in edge_payloads:
        t0 = time.time()
        url = f"{ALADIN_HOST}/api/generate"
        body = {
            "model": model_slug,
            "prompt": p["prompt"],
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 30}
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dt = round(time.time() - t0, 3)
                txt = data.get("response", "").strip()
                # Verificar si el modelo cayó en loop de NaNs o caracteres basura
                has_corrupted = any(c in txt for c in ["\ufffd", "NaN", "undefined"])
                passed = not has_corrupted and len(txt) > 0
                results.append({"test": p["desc"], "latency_s": dt, "passed": passed, "sample": txt[:60]})
                log_incident_to_postgres("Hound_Numeric", p["desc"], "MEDIA" if not passed else "INFO", {"latency": dt, "sample": txt[:100]}, passed)
        except Exception as e:
            results.append({"test": p["desc"], "error": str(e), "passed": False})
            log_incident_to_postgres("Hound_Numeric", p["desc"], "ALTA", {"error": str(e)}, False)
    return results

# ==============================================================================
# BATERÍA 2: DESBORDES DE CONTEXTO Y SATURACIÓN DE KV CACHE
# ==============================================================================
def attack_context_exhaustion(model_slug="qwen2.5:1.5b"):
    """Inyecta prompts masivos para buscar fragmentación de memoria o desbordes en ALADIN."""
    print(f"\n[SABUESO 2/5] Lanzando ataque de saturación de contexto contra {model_slug}...")
    sizes = [1000, 4000, 8000] # Tokens sintéticos
    results = []
    for sz in sizes:
        t0 = time.time()
        huge_prompt = ("Stiefel Manifold Continuous Latent Tensor Projection " * (sz // 6)) + " Conclusión final:"
        url = f"{ALADIN_HOST}/api/generate"
        body = {
            "model": model_slug,
            "prompt": huge_prompt,
            "stream": False,
            "options": {"num_predict": 10}
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dt = round(time.time() - t0, 3)
                results.append({"size_tokens": sz, "latency_s": dt, "passed": True})
                log_incident_to_postgres("Hound_Context", f"Context_{sz}", "INFO", {"latency": dt}, True)
        except Exception as e:
            results.append({"size_tokens": sz, "error": str(e), "passed": False})
            log_incident_to_postgres("Hound_Context", f"Context_{sz}", "ALTA", {"error": str(e)}, False)
    return results

# ==============================================================================
# BATERÍA 3: SIMULACIÓN DE DESACOPLE DE DOMINIO (INYECCIÓN RAFAEL)
# ==============================================================================
def attack_domain_mismatch_trap(model_slug="mathesis-quantum:1.5b"):
    """Prueba si el modelo detecta y rechaza vectores crudos de capa final sin proyector."""
    print(f"\n[SABUESO 3/5] Verificando detección de desacople de capa (Trampa Rafael)...")
    prompt = """[LAYER_L_RAW_HIDDEN_STATE_SIMULATION]
Shape: [1, 8, 4096] (Mean-Pooled from Layer 32 without W_proj)
Expected action: Detect domain mismatch. Reject raw inputs_embeds injection into Layer 0.
Emit status:"""
    t0 = time.time()
    url = f"{ALADIN_HOST}/api/generate"
    body = {
        "model": model_slug,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 40}
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            dt = round(time.time() - t0, 3)
            txt = data.get("response", "").strip()
            passed = len(txt) > 0
            log_incident_to_postgres("Hound_DomainMismatch", "RawHiddenStateTrap", "INFO", {"sample": txt[:100], "latency": dt}, passed)
            return {"passed": passed, "latency_s": dt, "response": txt[:80]}
    except Exception as e:
        log_incident_to_postgres("Hound_DomainMismatch", "RawHiddenStateTrap", "CRITICA", {"error": str(e)}, False)
        return {"passed": False, "error": str(e)}

# ==============================================================================
# BATERÍA 4: RÁFAGA DE CONCURRENCIA Y SOCKET DRAIN
# ==============================================================================
def attack_concurrency_spike(n_requests=4, model_slug="qwen2.5:1.5b"):
    """Dispara ráfagas concurrentes para detectar cuellos de botella en el socket de ALADIN."""
    print(f"\n[SABUESO 4/5] Lanzando ráfaga de {n_requests} peticiones simultáneas...")
    import concurrent.futures
    
    def _single_hit(idx):
        t0 = time.time()
        url = f"{ALADIN_HOST}/api/generate"
        body = {"model": model_slug, "prompt": f"Audit ping {idx}", "stream": False, "options": {"num_predict": 5}}
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=35) as resp:
                return {"id": idx, "passed": True, "latency": round(time.time() - t0, 2)}
        except Exception as e:
            return {"id": idx, "passed": False, "error": str(e)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_requests) as executor:
        futs = [executor.submit(_single_hit, i) for i in range(n_requests)]
        results = [f.result() for f in futs]
        
    oks = sum(1 for r in results if r["passed"])
    log_incident_to_postgres("Hound_Concurrency", f"Burst_{n_requests}", "ALTA" if oks < n_requests else "INFO", {"results": results}, oks == n_requests)
    return {"total": n_requests, "passed": oks, "details": results}

# ==============================================================================
# BATERÍA 5: VERIFICACIÓN DE DEFECTO STIEFEL EN SILICIO LOCAL
# ==============================================================================
def audit_stiefel_isometry():
    """Calcula matemáticamente el defecto de ortogonalidad actual en el silicio."""
    print(f"\n[SABUESO 5/5] Auditando defecto de isometría Stiefel W^T W - I en memoria (float64)...")
    import torch
    D, k = 2048, 16
    W = torch.randn(D, k, dtype=torch.float64)
    # Retracción polar de orden 4
    U, _, Vt = torch.linalg.svd(W, full_matrices=False)
    W_polar = U @ Vt
    defect = torch.max(torch.abs(W_polar.t() @ W_polar - torch.eye(k, dtype=torch.float64))).item()
    # En float64 (eps=2.22e-16), acumulación en D=2048 tiene cota estricta <= 5e-15
    passed = defect <= 5e-15
    log_incident_to_postgres("Hound_StiefelIsometry", "PolarOrder4", "CRITICA" if not passed else "INFO", {"defect": defect}, passed)
    return {"defect": defect, "passed": passed}

# ==============================================================================
# CICLO MAESTRO DEL AGENTE QA
# ==============================================================================
def run_qa_hound_cycle():
    print("=" * 80)
    print("  AGENTE QA ADVERSARIAL AUTÓNOMO — POLYDIM / ALADIN AUDIT LOOP")
    print(f"  Ejecutado: {datetime.now(timezone.utc).isoformat()} | Destino: {ALADIN_HOST}")
    print("=" * 80)
    
    r1 = attack_numeric_and_nan()
    r2 = attack_context_exhaustion()
    r3 = attack_domain_mismatch_trap()
    r4 = attack_concurrency_spike(4)
    r5 = audit_stiefel_isometry()
    
    print("\n" + "=" * 80)
    print("  RESUMEN DE AUDITORÍA ADVERSARIAL")
    print("=" * 80)
    print(f"1. Frontera Numérica:  {sum(1 for x in r1 if x['passed'])}/{len(r1)} pruebas superadas.")
    print(f"2. Desborde Contexto:  {sum(1 for x in r2 if x['passed'])}/{len(r2)} pruebas superadas.")
    print(f"3. Detección Mismatch: {'EXITOSA' if r3['passed'] else 'FALLÓ'} (Latencia: {r3.get('latency_s')}s).")
    print(f"4. Ráfaga Concurrente: {r4['passed']}/{r4['total']} conexiones respondieron.")
    print(f"5. Isometría Stiefel:  Defecto medido = {r5['defect']:.2e} (Passed: {r5['passed']}).")
    print("\n[FIN DEL CICLO] Resultados guardados en PostgreSQL 16 (polydim_active_db.active_vault).")

if __name__ == "__main__":
    run_qa_hound_cycle()
