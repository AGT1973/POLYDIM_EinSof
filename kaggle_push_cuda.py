# ==============================================================================
# POLYDIM EINSOF — KAGGLE CUDA DUAL-GPU AUTOMATED PUSH, MONITOR & INGESTION
# ==============================================================================
# Target: agt1973gmailcom/polydim-cuda-t4-bench on NVIDIA Tesla T4 (sm_75)
# Uses official Kaggle CLI to push bundle, monitor execution, and download logs.
# Resolves Brecha 1: Physical Silicon Certification of CUDA C++20 + Triton V26250.
# ==============================================================================

import os
import sys
import json
import time
import subprocess
import shutil
import glob
from pathlib import Path

sys.path.append(r"E:\Mantenimiento")
try:
    import agent_vault_pg
    from agent_vault_pg import execute_statement, execute_query, DB_VEC
    HAS_PG = True
except ImportError:
    HAS_PG = False

KERNEL_SLUG = "polydim-cuda-t4-bench"
OWNER = "agt1973gmailcom"
KERNEL_ID = f"{OWNER}/{KERNEL_SLUG}"

BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "KAGGLE_CUDA_BUNDLE")
WORKER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kaggle_cuda_worker.py")
OUTPUT_LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_HISTORICO", "silicio_logs")


def prepare_bundle() -> str:
    os.makedirs(BUNDLE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_LOGS_DIR, exist_ok=True)

    dest_worker = os.path.join(BUNDLE_DIR, "kaggle_cuda_worker.py")
    shutil.copyfile(WORKER_SCRIPT, dest_worker)

    metadata = {
        "id": KERNEL_ID,
        "title": KERNEL_SLUG,
        "code_file": "kaggle_cuda_worker.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": True,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": []
    }

    meta_file = os.path.join(BUNDLE_DIR, "kernel-metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[*] Bundle preparado en : {BUNDLE_DIR}")
    print(f"[*] Target Kernel ID    : {KERNEL_ID}")
    print(f"[*] Acelerador          : GPU NVIDIA Tesla T4 (enable_gpu=True)")
    return BUNDLE_DIR


def push_kernel():
    cmd = [
        sys.executable, "-m", "kaggle", "kernels", "push",
        "-p", BUNDLE_DIR
    ]
    print(f"\n[+] Ejecutando push a Kaggle GPU: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(f"[*] Push stdout: {res.stdout.strip()}")
    if res.stderr.strip():
        print(f"[*] Push stderr: {res.stderr.strip()}")
    return res.returncode


def monitor_and_download(timeout_seconds: int = 600, poll_interval: int = 15):
    print(f"\n[+] Monitoreando ejecución en silicio físico de {KERNEL_ID}...")
    start_time = time.time()

    while (time.time() - start_time) < timeout_seconds:
        status_cmd = [sys.executable, "-m", "kaggle", "kernels", "status", KERNEL_ID]
        res = subprocess.run(status_cmd, capture_output=True, text=True, check=False)
        out = res.stdout.strip()
        timestamp_str = time.strftime("%H:%M:%S")
        print(f"  [{timestamp_str}] Estado: {out}")

        if "complete" in out.lower():
            print(f"\n[✓] ¡Ejecución COMPLETADA con éxito en silicio real!")
            break
        elif "error" in out.lower():
            print(f"\n[✗] Kernel falló con error en Kaggle.")
            break

        time.sleep(poll_interval)

    # Descargar logs
    out_dir = os.path.join(OUTPUT_LOGS_DIR, f"run_{int(time.time())}")
    os.makedirs(out_dir, exist_ok=True)
    down_cmd = [sys.executable, "-m", "kaggle", "kernels", "output", KERNEL_ID, "-p", out_dir]
    print(f"\n[+] Descargando evidencias crudas de silicio: {' '.join(down_cmd)}")
    subprocess.run(down_cmd, capture_output=True, text=True, check=False)
    print(f"[✓] Archivos descargados en: {out_dir}")
    return out_dir


if __name__ == "__main__":
    prepare_bundle()
    rc = push_kernel()
    if rc == 0:
        monitor_and_download()
