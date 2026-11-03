# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF: Verificación en Silicio de Matriz Turing=100 (Moda por Campo en PmtpShmBus)
+ Arbitraje Directo con Qwen 3.8 y DeepSeek-v4 (Regla 0 & Regla 44).
"""
import os
import sys
import time
import math
import json
import urllib.request
import urllib.error
from multiprocessing import shared_memory
import numpy as np
import psycopg2

sys.stdout.reconfigure(line_buffering=True)

def neumaier_sum(arr_1d):
    s = 0.0
    c = 0.0
    for x in arr_1d:
        xf = float(x)
        t = s + xf
        if abs(s) >= abs(xf):
            c += (s - t) + xf
        else:
            c += (xf - t) + s
        s = t
    return s + c

def neumaier_unit_normalize(vec):
    clean = np.where(np.isfinite(vec), vec, 0.0)
    sq = np.square(clean, dtype=np.float64).ravel()
    n_val = math.sqrt(max(0.0, neumaier_sum(sq)))
    return clean / n_val, n_val

def run_silicon_matrix_mode_test():
    t0 = time.perf_counter()
    T = 100
    D = 2048
    rng = np.random.default_rng(20261102)

    # Vector canónico verdadero en S^{D-1} (cuantizado a malla de alta precisión o exacto)
    raw_true = np.round(rng.standard_normal(D, dtype=np.float64), 6)
    v_true, _ = neumaier_unit_normalize(raw_true)
    # Redondeo de estados discretizados IEEE para moda exacta por columna
    v_true_grid = np.round(v_true, 7)

    # Construir matriz M de (100, 2048) en Shared Memory (PmtpShmBus)
    # 85 vectores tienen el estado verdadero, 15 vectores tienen basura aleatoria / corrupción severa
    M = np.tile(v_true_grid, (T, 1))
    corrupted_rows = rng.choice(T, size=15, replace=False)
    for r in corrupted_rows:
        M[r, :] = rng.uniform(-1.0, 1.0, size=D)

    shm = shared_memory.SharedMemory(create=True, size=M.nbytes)
    try:
        shm_mat = np.ndarray(M.shape, dtype=np.float64, buffer=shm.buf)
        shm_mat[:] = M[:]

        # 1. Promedio Lineal Ingenuo (Media por columna) -> Se contamina con los 15 vectores basura
        v_mean_raw = np.mean(shm_mat, axis=0)
        v_mean, _ = neumaier_unit_normalize(v_mean_raw)
        err_mean = float(np.max(np.abs(v_mean - v_true)))

        # 2. MODA POR CAMPO (Columna j = 0 .. D-1) sobre la matriz 100 x D
        # Discretizando / agrupando cada campo j en la matriz (T=100 filas)
        v_mode_grid = np.zeros(D, dtype=np.float64)
        rounded_mat = np.round(shm_mat, 7)
        for j in range(D):
            vals, counts = np.unique(rounded_mat[:, j], return_counts=True)
            v_mode_grid[j] = vals[np.argmax(counts)]

        # Retracción Neumaier a S^{D-1}
        v_mode_retracted, norm_mode = neumaier_unit_normalize(v_mode_grid)
        err_mode_grid = float(np.max(np.abs(v_mode_grid - v_true_grid)))
        err_mode_s_d = float(np.max(np.abs(v_mode_retracted - v_true)))
        neumaier_Check = abs( math.sqrt(neumaier_sum(np.square(v_mode_retracted))) - 1.0 )

        latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        return {
            "T": T,
            "D": D,
            "corrupted_vectors": 15,
            "valid_vectors": 85,
            "err_linear_mean": err_mean,
            "err_field_mode_exact_grid": err_mode_grid,
            "err_field_mode_retracted": err_mode_s_d,
            "neumaier_norm_error": neumaier_Check,
            "latency_ms": latency_ms,
            "slab_name": shm.name
        }
    finally:
        shm.close()
        shm.unlink()

def get_keys():
    conn = psycopg2.connect(dbname='polydim_active_db', user='postgres', host='localhost', port=5432)
    cur = conn.cursor()
    cur.execute("SELECT value FROM active_vault WHERE key_name IN ('deepseek_api_key', 'DeepSeek') LIMIT 1")
    r_ds = cur.fetchone()
    ds_key = r_ds[0].strip() if r_ds else None

    cur.execute("SELECT value FROM active_vault WHERE key_name IN ('Alibaba_Qwen_Paid', 'alibaba_api_key') LIMIT 1")
    r_qw = cur.fetchone()
    qw_key = r_qw[0].strip() if r_qw else "sk-sp-H.LYREI.SDg8.MEUCIEzc9kSo3fxx3cW6z0lnigSjw_LyEtsHvB-XKT94cAsnAiEAvNBSf_YPS693VYKy7bL4KOtZ4WSZiF9b-YvWBpQaeV4"
    cur.close()
    conn.close()
    return ds_key, qw_key

PROMPT_EN = """[MATHEMATICAL & SILICON EVALUATION: TURING=100 MATRIX COORDINATE-WISE MODE IN SHM]
Context: In POLYDIM-EINSOF, we hold a matrix M of shape (T=100, D=2048) in PmtpShmBus shared memory representing 100 parallel Turing state vectors on S^{D-1}.
Suppose 85-90 vectors converge to the true latent state and 10-15 vectors have random noise/degradation.
Question from Principal Investigator:
Can we compute the Coordinate-wise Mode (column-by-column mode across the 100 rows for each field j in 1..D) directly on the 100xD matrix in RAM so that each field outputs the modal value, completely discarding the random/corrupted vectors, followed by Neumaier normalization onto S^{D-1}?
Provide a concise, rigorous mathematical & C++20/SIMD silicon analysis (in Spanish) covering:
1. Why coordinate-wise Mode (with FP64 epsilon-binning / quantization or Half-Sample Mode) completely annihilates random outliers (0.0 residual contamination vs linear mean).
2. Exact formula for Coordinate-wise binned Mode + Neumaier Stiefel Retraction on S^{D-1}.
"""

def query_llm(url, key, models, label):
    for m in models:
        payload = {
            "model": m,
            "messages": [
                {"role": "system", "content": "You are a formal mathematical and high-performance silicon architect for POLYDIM-EINSOF. Respond concisely in Spanish with strict mathematical rigor and zero filler."},
                {"role": "user", "content": PROMPT_EN}
            ],
            "temperature": 0.1,
            "max_tokens": 900
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        })
        try:
            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                lat = round((time.perf_counter() - t0)*1000, 1)
                return m, lat, data['choices'][0]['message']['content']
        except Exception as e:
            print(f"[-] {label} ({m}) error: {e}")
    return None, 0, None

if __name__ == "__main__":
    print("[1] Ejecutando prueba física en silicio sobre matriz (100 x 2048) en PmtpShmBus...")
    silicon_res = run_silicon_matrix_mode_test()
    print("SILICON_METRICS:", json.dumps(silicon_res, indent=2))

    ds_key, qw_key = get_keys()
    print("\n[2] Consultando Qwen 3.8 (Alibaba DashScope)...")
    qw_model, qw_lat, qw_resp = query_llm(
        "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions",
        qw_key,
        ["qwen3.8-flash", "qwen-plus", "qwen-max"],
        "Qwen"
    )
    if qw_resp:
        print(f"\n=== DICTAMEN QWEN ({qw_model} | {qw_lat} ms) ===\n{qw_resp}")

    if ds_key:
        print("\n[3] Consultando DeepSeek-v4...")
        ds_model, ds_lat, ds_resp = query_llm(
            "https://api.deepseek.com/chat/completions",
            ds_key,
            ["deepseek-v4-pro", "deepseek-flash", "deepseek-chat"],
            "DeepSeek"
        )
        if ds_resp:
            print(f"\n=== DICTAMEN DEEPSEEK ({ds_model} | {ds_lat} ms) ===\n{ds_resp}")
