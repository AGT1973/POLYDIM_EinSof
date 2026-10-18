import psycopg
import json
import os
import psutil
from datetime import datetime, timezone

DB_CONFIG = "dbname=polydim_vec_db user=postgres host=localhost port=5432"

def get_connection():
    return psycopg.connect(DB_CONFIG)

def record_fact(barrier, test_harness, metric_key, metric_val, metric_unit, exit_code, peak_ram_mb, latency_ms, checks_passed, checks_total, notes=""):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pmtp_v4_facts (
                    barrier, test_harness, metric_key, metric_val, metric_unit,
                    exit_code, peak_ram_mb, latency_ms, checks_passed, checks_total,
                    notes, certified_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                barrier, test_harness, metric_key, float(metric_val), metric_unit,
                int(exit_code), float(peak_ram_mb), float(latency_ms), int(checks_passed), int(checks_total),
                notes, datetime.now(timezone.utc)
            ))
            fact_id = cur.fetchone()[0]
            conn.commit()
            return fact_id

def record_theorem(barrier, cycle, version, topic, theorem, status, redteam_note, code_ref, script_verified, script_exit_code, script_output):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pmtp_v4_theorems (
                    barrier, cycle, version, topic, theorem, status,
                    redteam_note, code_ref, script_verified, script_exit_code,
                    script_output, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                barrier, int(cycle), version, topic, theorem, status,
                redteam_note, code_ref, bool(script_verified), int(script_exit_code),
                script_output, datetime.now(timezone.utc)
            ))
            th_id = cur.fetchone()[0]
            conn.commit()
            return th_id

def record_checkpoint(conversation_id, summary, category="night_loop_checkpoint"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO session_context (
                    conversation_id, summary, category, created_at
                ) VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (
                conversation_id, summary, category, datetime.now(timezone.utc)
            ))
            cp_id = cur.fetchone()[0]
            conn.commit()
            return cp_id

def get_status_summary():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*), MIN(id), MAX(id) FROM pmtp_v4_theorems;")
            t_row = cur.fetchone()
            cur.execute("SELECT COUNT(*), MIN(id), MAX(id) FROM pmtp_v4_facts;")
            f_row = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM session_context WHERE category = 'night_loop_checkpoint';")
            c_row = cur.fetchone()
            return {
                "theorems": {"count": t_row[0], "min_id": t_row[1], "max_id": t_row[2]},
                "facts": {"count": f_row[0], "min_id": f_row[1], "max_id": f_row[2]},
                "checkpoints": {"count": c_row[0]}
            }

if __name__ == "__main__":
    print("PMTP-v4 DB Status:", get_status_summary())
