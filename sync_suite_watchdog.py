#!/usr/bin/env python3
"""
sync_suite_watchdog.py — POLYDIM SUITE Opportunistic & Daily Sync Watchdog
Handles irregular workstation uptime (powered on at 6, 7, 8, 9, 10, 11, 12 or 14 hs).
Executes on boot / session start and at 14:00 hs, with an 18-hour smart cooldown.
"""

import os
import subprocess
import json
import psycopg2
from datetime import datetime, timezone, timedelta

SUITE_DIR = r"E:\SUITE"
REMOTE_REPO = "https://github.com/AGT1973/polydim-suite.git"
COOLDOWN_HOURS = 18

def run_cmd(cmd, cwd=SUITE_DIR):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def check_git_status():
    rc, out, err = run_cmd("git status --porcelain")
    return out

def get_last_run_timestamp():
    try:
        conn = psycopg2.connect(dbname="polydim_active_db", user="postgres", host="localhost")
        cur = conn.cursor()
        cur.execute("SELECT value FROM active_vault WHERE category='MONITORING_STATE' AND key_name='SUITE_DAILY_WATCHDOG_LAST_RUN';")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0]:
            data = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            ts_str = data.get("timestamp")
            if ts_str:
                return datetime.fromisoformat(ts_str)
    except Exception as e:
        print(f"[WARN] Error reading last run from PostgreSQL: {e}")
    return None

def audit_suite_files():
    required_files = [
        os.path.join(SUITE_DIR, "README.md"),
        os.path.join(SUITE_DIR, "INSTALL_FOR_AI.md"),
        os.path.join(SUITE_DIR, "ui", "suite_cockpit.html"),
        os.path.join(SUITE_DIR, "introduction", "index.html")
    ]
    missing = [f for f in required_files if not os.path.exists(f)]
    return missing

def sync_to_github():
    status = check_git_status()
    if not status:
        return "No local changes in E:\\SUITE. Repository is clean and synchronized."
    
    run_cmd("git add .")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    msg = f"chore(sync): automated suite maintenance and student asset sync [{timestamp}]"
    rc, out, err = run_cmd(f'git commit -m "{msg}"')
    if rc != 0 and "nothing to commit" not in out:
        return f"Commit failed: {err}"
    
    rc_push, out_push, err_push = run_cmd("git push origin main")
    if rc_push == 0:
        return f"Successfully synchronized and pushed to GitHub ({timestamp})."
    else:
        return f"Push error: {err_push}"

def log_to_postgres(log_message, status="OK"):
    try:
        conn = psycopg2.connect(dbname="polydim_active_db", user="postgres", host="localhost")
        cur = conn.cursor()
        payload = json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "message": log_message
        })
        cur.execute("""
            INSERT INTO active_vault (category, key_name, value, updated_at)
            VALUES ('MONITORING_STATE', 'SUITE_DAILY_WATCHDOG_LAST_RUN', %s, clock_timestamp())
            ON CONFLICT (category, key_name)
            DO UPDATE SET value = EXCLUDED.value, updated_at = clock_timestamp();
        """, (payload,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[WARN] PostgreSQL log error: {e}")

def main(force=False):
    now = datetime.now(timezone.utc)
    print(f"[{now.isoformat()}] Starting POLYDIM SUITE watchdog check...")
    
    last_run = get_last_run_timestamp()
    if not force and last_run:
        time_since_last = now - last_run
        if time_since_last < timedelta(hours=COOLDOWN_HOURS):
            print(f"[COOLDOWN] Last sync was {time_since_last.total_seconds() / 3600:.1f}h ago (< {COOLDOWN_HOURS}h). Skipping redundant sync.")
            return 0
    
    missing = audit_suite_files()
    if missing:
        msg = f"CRITICAL: Missing required suite files: {missing}"
        print(msg)
        log_to_postgres(msg, status="ERROR")
        return 1
    
    sync_result = sync_to_github()
    print(f"Result: {sync_result}")
    log_to_postgres(sync_result, status="OK")
    return 0

if __name__ == "__main__":
    import sys
    force_run = "--force" in sys.argv
    exit(main(force=force_run))
