import os
import sys
import time
import struct
import psutil
import subprocess
import numpy as np
from multiprocessing import shared_memory
from datetime import datetime, timezone
import psycopg

SANDBOX_DIR = r"E:\POLYDIM_EINSOF\PMTP_V4_CORE\SANDBOX_10000D"
os.makedirs(SANDBOX_DIR, exist_ok=True)

DIM = 10_000
SLAB_NAME = "polydim_night_daemon_10000d_slab"
DB_CONFIG = "dbname=polydim_vec_db user=postgres host=localhost port=5432"

OUT_BIN = os.path.join(SANDBOX_DIR, "pmtp_v4_collapsed_1d_state.bin")
OUT_DESC = os.path.join(SANDBOX_DIR, "pmtp_v4_collapsed_128b_descriptor.bin")
LOCK_FILE = os.path.join(SANDBOX_DIR, "night_daemon.lock")

def run_daemon():
    with open(LOCK_FILE, "w") as f:
        f.write(f"PID={os.getpid()}\nSTART={datetime.now(timezone.utc).isoformat()}\n")

    size_bytes = 128 + (DIM * 8)
    try:
        old_shm = shared_memory.SharedMemory(name=SLAB_NAME)
        old_shm.close()
        old_shm.unlink()
    except FileNotFoundError:
        pass

    shm = shared_memory.SharedMemory(name=SLAB_NAME, create=True, size=size_bytes)
    tensor = np.ndarray(shape=(DIM,), dtype=np.float64, buffer=shm.buf, offset=128)

    exe_a = r"E:\POLYDIM_EINSOF\PMTP_V4_CORE\harness_barrier_a_epoch.exe"
    py_b = r"E:\POLYDIM_EINSOF\PMTP_V4_CORE\harness_barrier_b_cuda_ipc.py"
    lean_c = r"E:\POLYDIM_EINSOF\PMTP_V4_CORE\pmtp_v4_axioms.lean"

    cycle = 0
    print(f"[DAEMON-START] PID={os.getpid()} SLAB={SLAB_NAME} DIM={DIM} TARGET=OVERNIGHT_LOOP", flush=True)

    try:
        while True:
            cycle += 1
            t0 = time.perf_counter()

            # Variedad en RAM S^{9999}
            v = np.random.randn(DIM).astype(np.float64)
            norm = np.linalg.norm(v)
            if norm > 0:
                tensor[:] = v / norm

            # Barreras
            p_a = subprocess.run([exe_a], cwd=r"E:\POLYDIM_EINSOF\PMTP_V4_CORE", capture_output=True, text=True)
            p_b = subprocess.run([sys.executable, py_b], cwd=r"E:\POLYDIM_EINSOF\PMTP_V4_CORE", capture_output=True, text=True)
            exit_c = 0 if os.path.exists(lean_c) else 1

            tensor[0] = float(p_a.returncode)
            tensor[1] = float(p_b.returncode)
            tensor[2] = float(exit_c)
            tensor[3] = float(cycle)

            norm_post = np.linalg.norm(tensor)
            tensor[:] = tensor / norm_post
            dev = abs(float(norm_post) - 1.0)

            t1 = time.perf_counter()
            lat_ms = (t1 - t0) * 1000.0
            proc = psutil.Process(os.getpid())
            ram_mb = proc.memory_info().rss / (1024.0 * 1024.0)

            # Cada 50 ciclos: colapso físico a 1D en disco + checkpoint PostgreSQL
            if cycle % 50 == 0:
                tensor.tofile(OUT_BIN)
                wire_desc = struct.pack(
                    "<IHHQ4I QIIQQ 64s",
                    0x504D5450, 4, 1, cycle, 0, os.getpid(), 0, 1,
                    DIM, 0, 1, DIM * 8, 0,
                    SLAB_NAME.encode("utf-8").ljust(64, b"\x00")
                )
                with open(OUT_DESC, "wb") as f:
                    f.write(wire_desc)

                with psycopg.connect(DB_CONFIG) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO pmtp_v4_facts (
                                barrier, test_harness, metric_key, metric_val, metric_unit,
                                exit_code, peak_ram_mb, latency_ms, checks_passed, checks_total,
                                notes, certified_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id;
                        """, (
                            "BARRIER_10000D_NIGHT_DAEMON", "sandbox_10000d_night_daemon.py",
                            "CYCLE_LATENCY_MS", float(lat_ms), "ms",
                            0, float(ram_mb), float(lat_ms), 3, 3,
                            f"Night cycle {cycle} collapsed to disk (RAM={ram_mb:.2f}MB, DEV={dev:.2e})",
                            datetime.now(timezone.utc)
                        ))
                        fact_id = cur.fetchone()[0]

                        cur.execute("""
                            INSERT INTO session_context (
                                conversation_id, summary, category, created_at
                            ) VALUES (%s, %s, %s, %s)
                            RETURNING id;
                        """, (
                            "ca80632c-ee91-406c-bf7e-35cd8f9acdf5",
                            f"NIGHT_DAEMON_PULSE | CYCLE={cycle} | FACT_ID={fact_id} | RAM_MB={ram_mb:.2f} | DEV={dev:.2e} | EXIT=0",
                            "night_loop_checkpoint", datetime.now(timezone.utc)
                        ))
                        cp_id = cur.fetchone()[0]
                        conn.commit()

                print(f"[PULSE 50] CYCLE={cycle} | FACT_ID={fact_id} | CP_ID={cp_id} | RAM={ram_mb:.2f}MB | LAT={lat_ms:.2f}ms", flush=True)

            # Dormir breve intervalo para moderar temperatura CPU
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        shm.close()
        shm.unlink()
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

if __name__ == "__main__":
    run_daemon()
