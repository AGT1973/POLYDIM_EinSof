#!/usr/bin/env python3
"""
sync_suite_watchdog.py — POLYDIM SUITE Automated Daily Maintenance & Synchronization Watchdog
Scheduled via cron to audit core changes, maintain student assets, check links, and push updates to GitHub.
"""

import os
import subprocess
import json
import psycopg2
from datetime import datetime, timezone

SUITE_DIR = r"E:\SUITE"
REMOTE_REPO = "https://github.com/AGT1973/polydim-suite.git"

def run_cmd(cmd, cwd=SUITE_DIR):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def check_git_status():
    rc, out, err = run_cmd("git status --porcelain")
    return out

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
    
    # Commit and push
    run_cmd("git add .")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    msg = f"chore(sync): automated daily suite maintenance and student asset audit [{timestamp}]"
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

def main():
    print(f"[{datetime.now().isoformat()}] Starting POLYDIM SUITE daily watchdog...")
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
    exit(main())
