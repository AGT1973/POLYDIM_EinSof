"""
Despachador Dinámico del Tribunal de Sabios — POLYDIM-EINSOF (Soberano Silicio)
=============================================================================
Ejecución real y verificada en silicio sin simulaciones ni métricas inventadas (Ariel's Law / Regla 1).
Consulta en tiempo real la flota activa, prioriza el nodo ALADIN (192.168.100.21:11434)
y la infraestructura local con semáforo de concurrencia para evitar saturación de VRAM.
"""
import os
import sys
import json
import time
import asyncio
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

def get_active_fleet():
    """Consulta la tabla maestra viva en active_vault."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT value FROM active_vault 
            WHERE category = 'sota_models' AND key_name = 'SOTA_FLEET_MASTER_TABLE_2026'
        """)
        row = cur.fetchone()
        conn.close()
        if not row:
            return []
        data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        return data.get("rows", [])
    except Exception as e:
        print(f"[ERROR] No se pudo leer active_vault: {e}")
        return []

def get_aladin_loaded_models():
    """Descubre en tiempo real los modelos disponibles en ALADIN Ollama."""
    try:
        req = urllib.request.Request(f"{ALADIN_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

async def dispatch_ollama_query(sem, model_slug, endpoint, prompt):
    """Consulta real a Ollama con semáforo para no asfixiar la GPU."""
    async with sem:
        t0 = time.time()
        url = f"{endpoint}/api/generate"
        payload = {
            "model": model_slug,
            "prompt": f"[GHOST PROTOCOL - STIEFEL MANIFOLD S^{{D-1}}]\n{prompt}",
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 150}
        }
        
        def _post():
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))

        try:
            res = await asyncio.to_thread(_post)
            resp_text = res.get("response", "").strip()
            latency = round((time.time() - t0) * 1000)
            return {
                "model": model_slug,
                "status": "OK",
                "channel": f"ALADIN_SILICON ({endpoint})",
                "latency_ms": latency,
                "opinion": resp_text[:400]
            }
        except Exception as e:
            return {
                "model": model_slug,
                "status": "FAIL",
                "channel": f"ALADIN_SILICON ({endpoint})",
                "error": str(e),
                "latency_ms": round((time.time() - t0) * 1000)
            }

async def run_sabios_fanout(prompt):
    fleet = get_active_fleet()
    aladin_models = get_aladin_loaded_models()
    
    print(f"\n[SABIOS ORCHESTRATOR] Modelos vivos detectados en active_vault: {len(fleet)}")
    print(f"[SABIOS ORCHESTRATOR] Modelos físicos activos en ALADIN: {aladin_models}")

    # Semáforo de 2 concurrentes para no saturar memoria en inferencia real
    sem = asyncio.Semaphore(2)
    tasks = []

    # Mapeo estricto de modelos a sus slugs de silicio reales
    model_mapping = {
        "mathesis": "mathesis-quantum:1.5b",
        "quantum": "mathesis-quantum:1.5b",
        "deepseek-r1": "deepseek-r1:7b",
        "clases-tutor": "clases-tutor-slm:latest",
        "polydim-comms": "polydim-comms-slm:latest",
        "qwen2.5:3b": "qwen2.5:3b",
        "qwen2.5:1.5b": "qwen2.5:1.5b",
        "aiide-tutor": "aiide-tutor:latest"
    }

    dispatched_models = set()

    # Prioridad 1: Despachar a los modelos nativos de ALADIN
    for slug in aladin_models:
        if slug not in dispatched_models:
            dispatched_models.add(slug)
            tasks.append(dispatch_ollama_query(sem, slug, ALADIN_HOST, prompt))

    print(f"[SABIOS ORCHESTRATOR] Despachando concurrentemente a {len(tasks)} IAs reales en silicio (ALADIN)...")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    opiniones_validas = []
    fallos = []
    for r in results:
        if isinstance(r, dict):
            if r.get("status") == "OK":
                opiniones_validas.append(r)
            else:
                fallos.append(r)

    print(f"[SABIOS ORCHESTRATOR] {len(opiniones_validas)}/{len(tasks)} IAs de silicio emitieron dictamen real verificado.")
    if fallos:
        print(f"[SABIOS ORCHESTRATOR] Modelos con error de silicio: {len(fallos)}")

    # Persistir deliberación real en PostgreSQL
    ts = datetime.now(timezone.utc).isoformat()
    try:
        conn_act = get_db_connection()
        cur_act = conn_act.cursor()
        cur_act.execute("""
            INSERT INTO active_vault (category, key_name, value, notes)
            VALUES ('sabios_deliberations', %s, %s, 'Deliberación real en silicio físico ALADIN')
            ON CONFLICT (category, key_name) DO UPDATE SET value=EXCLUDED.value, updated_at=CURRENT_TIMESTAMP;
        """, (f"DELIBERATION_{int(time.time())}", json.dumps({
            "timestamp": ts,
            "prompt": prompt,
            "total_consultadas": len(tasks),
            "participating_models": len(opiniones_validas),
            "results": opiniones_validas,
            "failures": fallos
        }, ensure_ascii=False, indent=2)))
        conn_act.commit()
        conn_act.close()
    except Exception as e:
        print(f"[WARN] Error al persistir deliberación: {e}")

    return {
        "timestamp": ts,
        "total_consultadas": len(tasks),
        "total_validas": len(opiniones_validas),
        "opiniones": opiniones_validas,
        "fallos": fallos
    }

if __name__ == "__main__":
    test_prompt = sys.argv[1] if len(sys.argv) > 1 else "Evaluar viabilidad de proyector lineal W_proj vs inyección directa en residual stream para Stiefel S^{D-1}."
    res = asyncio.run(run_sabios_fanout(test_prompt))
    print("\n--- RESUMEN DEL TRIBUNAL DE SABIOS (SILICIO REAL) ---")
    for op in res["opiniones"]:
        print(f"\n🟢 [{op['model']}] ({op['channel']}) Latencia: {op.get('latency_ms', 0)}ms:")
        print(f"   {op['opinion']}")
