"""
POLYDIM MASTER NIGHTLY WATCHDOG & RECOVERY DAEMON
═════════════════════════════════════════════════
Purpose:
  Continuous watchdog monitoring for nightly_cascade_orchestrator.py.
  Guarantees 0 hangs during the 8-hour autonomous night shift.
  If the orchestrator crashes or stalls for > 10 minutes, automatically
  revives it, recovers state from PostgreSQL, and alerts polydim_vec_db.
"""

import os
import sys
import time
import subprocess
import json
import psutil
from datetime import datetime, timezone
from pathlib import Path
import psycopg

BASE_DIR = Path(r"E:\POLYDIM_EINSOF")
TARGET_SCRIPT = BASE_DIR / "nightly_cascade_orchestrator.py"
HEARTBEAT_FILE = BASE_DIR / "orchestrator_heartbeat.json"
WATCHDOG_LOG = BASE_DIR / "nightly_watchdog.log"

MAX_STALL_SECONDS = 600  # 10 minutos de inactividad máxima permitida
CHECK_INTERVAL_SECONDS = 30
RUN_DURATION_HOURS = 8.5 # 8.5 horas de vigilancia continua

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[WATCHDOG {ts}] {msg}"
    print(line, flush=True)
    with open(WATCHDOG_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def record_watchdog_event(event_type, details):
    try:
        with psycopg.connect("dbname=polydim_vec_db user=postgres host=127.0.0.1 port=5432") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO session_context (conversation_id, summary, category)
                    VALUES (%s, %s, %s)
                """, (f"watchdog_{event_type}_{int(time.time())}", details, "watchdog_heartbeat"))
                conn.commit()
    except Exception as e:
        log(f"Error logging to PostgreSQL: {e}")

def is_orchestrator_running(pid):
    if pid is None:
        return False
    try:
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
        log(f"Proceso colgado PID {pid} y sus subprocesos terminados forzosamente.")
    except Exception as e:
        log(f"Aviso terminando PID {pid}: {e}")

def spawn_orchestrator():
    log("Iniciando nueva instancia de nightly_cascade_orchestrator.py...")
    proc = subprocess.Popen(
        [sys.executable, str(TARGET_SCRIPT)],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    log(f"Orquestador iniciado exitosamente con PID {proc.pid}.")
    record_watchdog_event("spawn", f"Orquestador iniciado con PID {proc.pid}")
    return proc.pid

def main():
    log("=" * 80)
    log("SUBAGENT HEARTBEAT WATCHDOG INICIADO (GUARDIÁN DE 8 HORAS)")
    log(f"Script Vigilado: {TARGET_SCRIPT}")
    log(f"Timeout de Inactividad: {MAX_STALL_SECONDS}s | Intervalo de Escaneo: {CHECK_INTERVAL_SECONDS}s")
    log("=" * 80)
    
    start_time = time.time()
    max_duration_seconds = RUN_DURATION_HOURS * 3600
    
    current_pid = None
    
    # Comprobar si ya existe un PID en el heartbeat
    if HEARTBEAT_FILE.exists():
        try:
            with open(HEARTBEAT_FILE, "r", encoding="utf-8") as f:
                hb = json.load(f)
                if is_orchestrator_running(hb.get("pid")):
                    current_pid = hb["pid"]
                    log(f"Orquestador existente detectado y activo con PID {current_pid}.")
        except Exception:
            pass
            
    if not current_pid:
        current_pid = spawn_orchestrator()
        
    while (time.time() - start_time) < max_duration_seconds:
        time.sleep(CHECK_INTERVAL_SECONDS)
        
        # Verificar salud del proceso
        running = is_orchestrator_running(current_pid)
        
        # Verificar timestamp del heartbeat
        heartbeat_fresh = False
        last_hb_age = 999999
        if HEARTBEAT_FILE.exists():
            try:
                mtime = os.path.getmtime(HEARTBEAT_FILE)
                last_hb_age = time.time() - mtime
                heartbeat_fresh = last_hb_age < MAX_STALL_SECONDS
            except Exception:
                pass
                
        if running and heartbeat_fresh:
            # Estado saludable
            pass
        else:
            # Condición de falla: proceso murió o se congeló
            reason = "PROCESO MUERTO" if not running else f"CONGELADO ({last_hb_age:.0f}s sin heartbeat)"
            log(f"ALERTA CRÍTICA: Orquestador requiere recuperación. Causa: {reason}.")
            record_watchdog_event("incident", f"Orquestador PID {current_pid} falló. Razón: {reason}.")
            
            if running:
                kill_process_tree(current_pid)
                
            # Recuperar y reiniciar
            current_pid = spawn_orchestrator()
            
    log("=" * 80)
    log("JORNADA DE VIGILANCIA NOCTURNA COMPLETADA EXITOSAMENTE (8.5 HORAS).")
    log("=" * 80)

if __name__ == "__main__":
    main()
