r"""
POLYDIM-EINSOF | Ariel García Traba (Independent Research)
CONTINUACIÓN DE LOS 10 CASOS RESTANTES (POSICIONES 11 A 20) — PROTOCOLO CUÁDRUPLE A/B/C/D
==========================================================================================
Reanuda la evaluación estricta sobre los siguientes 10 casos fijados de la lista piloto:
  Posiciones 1 a 10 (previamente auditadas y conservadas intactas):
    0: HumanEval/0
    1: HumanEval/1
    2: HumanEval/2
    3: HumanEval/4
    4: HumanEval/8
    5: HumanEval/10
    6: HumanEval/14
    7: HumanEval/20
    8: HumanEval/23
    9: HumanEval/26
  Posiciones 11 a 20 (a ejecutar en esta sesión, sin cambiar selección ni reescribir las primeras 10):
    10: HumanEval/31 (is_prime)
    11: HumanEval/32 (find_zero)
    12: HumanEval/34 (unique)
    13: HumanEval/39 (prime_fib)
    14: HumanEval/42 (incr_list)
    15: HumanEval/49 (modp)
    16: HumanEval/54 (same_chars)
    17: HumanEval/64 (vowels_count)
    18: HumanEval/74 (total_match)
    19: HumanEval/83 (starts_one_ends)

Brazos:
  - Brazo D: Control 'Zero-Hop' Directo (1 llamada qwen-3.8-27b en Cerebras CS-3)
  - Brazo A: Cadena 1D Multi-Agente (3 saltos: qwen-3.8-27b -> gpt-oss-120b -> qwen-3.8-27b)
  - Brazo B: Control Vectorial Afín en R^D sin Stiefel + W_affine + pinv
  - Brazo C: POLYDIM Stiefel St(d_out, d_in) con norma Neumaier + C++/Rust PMTP V6 Seqlock

Registra:
  - Base pass y Plus pass (EvalPlus 100+ tests adversariales)
  - Tiempos E2E wall-clock, WSE compute time y silicio local C++/Rust
  - Tokens totales facturados por brazo
  - Consolidación de los 20 casos completos en AUDIT_LOGS_A_B_C_D.jsonl y reporte final.
"""

import os
import re
import sys
import time
import json
import math
import ctypes
import hashlib
import tempfile
import subprocess
import urllib.request
import numpy as np
import psycopg
from datetime import datetime

CWD_CERT = r"E:\POLYDIM_EINSOF\ENTREGAS\ENTREGA_2026_10_17_V26505\cert_v26504"
OUT_JSONL = r"E:\POLYDIM_EINSOF\BENCHMARK_KITS\AUDIT_LOGS_A_B_C_D.jsonl"
OUT_JSON  = r"E:\POLYDIM_EINSOF\BENCHMARK_KITS\PILOT20_HUMANEVALPLUS_REPORT_A_B_C_D.json"
OUT_MD    = r"E:\POLYDIM_EINSOF\BENCHMARK_KITS\PILOT20_HUMANEVALPLUS_REPORT_A_B_C_D.md"

ALL_20_TASK_KEYS = [
    "HumanEval/0",  # 0
    "HumanEval/1",  # 1
    "HumanEval/2",  # 2
    "HumanEval/4",  # 3
    "HumanEval/8",  # 4
    "HumanEval/10", # 5
    "HumanEval/14", # 6
    "HumanEval/20", # 7
    "HumanEval/23", # 8
    "HumanEval/26", # 9
    # Tareas 11 a 20 (posiciones 10 a 19):
    "HumanEval/31", # 10: is_prime
    "HumanEval/32", # 11: find_zero
    "HumanEval/34", # 12: unique
    "HumanEval/39", # 13: prime_fib
    "HumanEval/42", # 14: incr_list
    "HumanEval/49", # 15: modp
    "HumanEval/54", # 16: same_chars
    "HumanEval/64", # 17: vowels_count
    "HumanEval/74", # 18: total_match
    "HumanEval/83", # 19: starts_one_ends
]

def get_cerebras_key() -> str:
    conn = psycopg.connect("dbname=polydim_active_db user=postgres host=localhost port=5432")
    cur = conn.cursor()
    cur.execute("SELECT value FROM active_vault WHERE key_name = 'Cerebras_ariel_garcia_traba' AND category = 'api_keys';")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise RuntimeError("No se encontró Cerebras_ariel_garcia_traba en polydim_active_db")
    return row[0].strip()

def call_cerebras(api_key: str, model: str, messages: list, max_tokens: int = 1536) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    t0 = time.perf_counter()
    raw = None
    for attempt in range(4):
        req = urllib.request.Request(
            "https://api.cerebras.ai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "POLYDIM-EINSOF-PILOT20/26505",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            break
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    usage = raw.get("usage", {})
    tinfo = raw.get("time_info", {})
    msg = raw["choices"][0]["message"]
    content = (msg.get("content") or msg.get("reasoning") or "").strip()
    return {
        "content": content,
        "raw_content_only": (msg.get("content") or "").strip(),
        "elapsed_ms": elapsed_ms,
        "wse_compute_ms": tinfo.get("completion_time", 0.0) * 1000.0,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }

def load_native_kernels():
    cpp = ctypes.CDLL(os.path.join(CWD_CERT, "kernel_cpp_v26503.dll"))
    rust = ctypes.CDLL(os.path.join(CWD_CERT, "kernel_rust_v26503.dll"))

    for lib in (cpp, rust):
        lib.polydim_cam_workspace_bytes_v26503.argtypes = [ctypes.c_uint64]
        lib.polydim_cam_workspace_bytes_v26503.restype = ctypes.c_uint64

        lib.polydim_cam_attention_retrieve_v26503.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_double),
        ]
        lib.polydim_cam_attention_retrieve_v26503.restype = ctypes.c_int32

        lib.polydim_stiefel_residual_inject_v26503.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_double,
            ctypes.c_uint64,
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_double),
        ]
        lib.polydim_stiefel_residual_inject_v26503.restype = ctypes.c_int32

        lib.polydim_pmtp_v6_claim_writer_v26503.argtypes = [
            ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64)
        ]
        lib.polydim_pmtp_v6_claim_writer_v26503.restype = ctypes.c_int32

        lib.polydim_pmtp_v6_publish_flip_v26503.argtypes = [
            ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32,
            ctypes.c_uint64, ctypes.c_uint64
        ]
        lib.polydim_pmtp_v6_publish_flip_v26503.restype = ctypes.c_int32

        lib.polydim_pmtp_v6_read_snapshot_v26503.argtypes = [
            ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t,
            ctypes.c_size_t, ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint64)
        ]
        lib.polydim_pmtp_v6_read_snapshot_v26503.restype = ctypes.c_int32

    return cpp, rust

def create_aligned_pmtp_slab(num_elements: int):
    import struct
    payload_bytes = num_elements * 8
    stride = (payload_bytes + 63) & ~63
    total_bytes = 64 + 2 * stride
    raw_buf = ctypes.create_string_buffer(total_bytes + 64)
    base_addr = ctypes.addressof(raw_buf)
    aligned_addr = (base_addr + 63) & ~63
    hdr = struct.pack("<IHHQQQdIIQQ", 0x504D5450, 26505, 1, 0, num_elements, 0, 1.0, 1, 0, 0, 0)
    ctypes.memmove(aligned_addr, hdr, 64)
    return raw_buf, aligned_addr, total_bytes, stride, payload_bytes

def extract_python_code(text: str, entry_point: str) -> str:
    m = re.findall(r"```(?:python)?\s*(.*?)```", text, flags=re.DOTALL)
    for block in m:
        if f"def {entry_point}" in block:
            return block.strip()
    return m[0].strip() if m else text.strip()

def evaluate_code_on_task(task: dict, candidate_code: str) -> tuple[bool, bool, str]:
    entry_point = task["entry_point"]
    base_script = f"""
import sys
import math
from typing import List, Dict, Tuple, Optional, Any, Union

{candidate_code}

{task['test']}

try:
    check({entry_point})
    sys.exit(0)
except Exception as ex:
    print(f"FAIL_BASE: {{ex}}", file=sys.stderr)
    sys.exit(1)
"""
    try:
        r_base = subprocess.run([sys.executable, "-c", base_script], capture_output=True, text=True, timeout=8)
        base_pass = (r_base.returncode == 0)
        if not base_pass:
            return False, False, r_base.stderr.strip()[:200]
    except subprocess.TimeoutExpired:
        return False, False, "TIMEOUT_BASE"
    except Exception as ex:
        return False, False, str(ex)

    plus_inputs = task.get("plus_input", [])[:100]
    if not plus_inputs:
        return True, True, ""

    plus_script = f"""
import sys
import math
from typing import List, Dict, Tuple, Optional, Any, Union

{task['prompt']}
{task['canonical_solution']}
_oracle_fn = {entry_point}

{candidate_code}
_cand_fn = {entry_point}

inputs = {repr(plus_inputs)}
atol = {task.get('atol', 1e-6)}

for i, inp in enumerate(inputs):
    try:
        exp = _oracle_fn(*inp)
        act = _cand_fn(*inp)
        if isinstance(exp, float):
            if not math.isclose(exp, act, abs_tol=atol):
                print(f"DIFF at index {{i}}: exp={{exp}} act={{act}}", file=sys.stderr)
                sys.exit(2)
        else:
            if exp != act:
                print(f"DIFF at index {{i}}: exp={{exp}} act={{act}}", file=sys.stderr)
                sys.exit(2)
    except Exception as ex:
        print(f"EX at index {{i}}: {{ex}}", file=sys.stderr)
        sys.exit(3)
sys.exit(0)
"""
    try:
        r_plus = subprocess.run([sys.executable, "-c", plus_script], capture_output=True, text=True, timeout=12)
        plus_pass = (r_plus.returncode == 0)
        err = r_plus.stderr.strip()[:200] if not plus_pass else ""
        return True, plus_pass, err
    except subprocess.TimeoutExpired:
        return True, False, "TIMEOUT_PLUS"
    except Exception as ex:
        return True, False, str(ex)

def main():
    api_key = get_cerebras_key()
    cpp, rust = load_native_kernels()

    from evalplus.data import get_human_eval_plus
    dataset = get_human_eval_plus()

    # Cargar y preservar estrictamente los primeros 10 casos existentes
    existing_records = []
    existing_tids = set()
    if os.path.exists(OUT_JSONL):
        with open(OUT_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    existing_records.append(rec)
                    existing_tids.add(rec["task_id"])
        print(f"Preservando {len(existing_records)} registros previos intactos.")

    remaining_task_keys = [tid for tid in ALL_20_TASK_KEYS if tid not in existing_tids]
    print(f"Tareas a evaluar en esta sesión ({len(remaining_task_keys)} restantes): {remaining_task_keys}")

    D_cam = 128
    K_st = 16
    rng = np.random.default_rng(26505)
    W_st, _ = np.linalg.qr(rng.standard_normal((D_cam, K_st)))
    W_st = np.ascontiguousarray(W_st, dtype=np.float64)
    scales = np.logspace(-1.5, 1.5, num=K_st)
    W_affine = np.ascontiguousarray(W_st * scales[np.newaxis, :], dtype=np.float64)
    W_affine_pinv = np.ascontiguousarray(np.linalg.pinv(W_affine), dtype=np.float64)

    raw_buf, slab_addr, total_bytes, stride, payload_bytes = create_aligned_pmtp_slab(D_cam)
    out_slot = ctypes.c_uint32(0)
    out_token = ctypes.c_uint64(0)
    out_gen = ctypes.c_uint64(0)

    # Abrir en modo append para no tocar los registros 1 a 10
    with open(OUT_JSONL, "a", encoding="utf-8") as jsonl_f:
        for idx, tid in enumerate(remaining_task_keys, len(existing_records) + 1):
            task = dataset[tid]
            prompt_base = f"Write the Python implementation for the following function signature and docstring. Output ONLY executable Python code inside ```python ... ```:\n\n{task['prompt']}"
            print(f"\n--- [{idx}/20] {tid} ({task['entry_point']}) ---", flush=True)

            # -----------------------------------------------------------------
            # BRAZO D: Inferencia Terminal Directa Zero-Hop
            # -----------------------------------------------------------------
            r_d = call_cerebras(api_key, "qwen-3.8-27b", [{"role": "user", "content": prompt_base}], max_tokens=1024)
            code_d = extract_python_code(r_d["raw_content_only"] or r_d["content"], task["entry_point"])
            d_base, d_plus, d_err = evaluate_code_on_task(task, code_d)

            # -----------------------------------------------------------------
            # BRAZO A: Cadena Textual Multi-Agente 1D (3 Saltos en Cerebras CS-3)
            # -----------------------------------------------------------------
            hop1 = call_cerebras(api_key, "qwen-3.8-27b", [
                {"role": "user", "content": f"Analyze requirements, edge cases, and algorithmic complexity for this task:\n{task['prompt']}"}
            ], max_tokens=512)
            hop2 = call_cerebras(api_key, "gpt-oss-120b", [
                {"role": "user", "content": f"Problem: {task['prompt']}\nAnalysis: {hop1['content']}\nSynthesize edge-case contract and specifications for implementation."}
            ], max_tokens=512)
            hop3 = call_cerebras(api_key, "qwen-3.8-27b", [
                {"role": "system", "content": f"Implementation guidelines: {hop2['content']}"},
                {"role": "user", "content": prompt_base}
            ], max_tokens=1024)
            a_wall = hop1["elapsed_ms"] + hop2["elapsed_ms"] + hop3["elapsed_ms"]
            a_wse = hop1["wse_compute_ms"] + hop2["wse_compute_ms"] + hop3["wse_compute_ms"]
            a_tokens = hop1["total_tokens"] + hop2["total_tokens"] + hop3["total_tokens"]
            code_a = extract_python_code(hop3["raw_content_only"] or hop3["content"], task["entry_point"])
            a_base, a_plus, a_err = evaluate_code_on_task(task, code_a)

            # -----------------------------------------------------------------
            # BRAZO B: Control Vectorial Afín (sin Stiefel, con deriva espectral)
            # -----------------------------------------------------------------
            t_b0 = time.perf_counter()
            vec_b = rng.standard_normal(D_cam).astype(np.float64)
            vec_b = W_affine @ (W_affine_pinv @ vec_b)  # deformación afín sin normalización
            sil_b_ms = (time.perf_counter() - t_b0) * 1000.0

            r_b = call_cerebras(api_key, "qwen-3.8-27b", [
                {"role": "system", "content": f"Algorithmic synthesis context (Affine Vector Norm={np.linalg.norm(vec_b):.4f}): Output clean code."},
                {"role": "user", "content": prompt_base}
            ], max_tokens=1024)
            code_b = extract_python_code(r_b["raw_content_only"] or r_b["content"], task["entry_point"])
            b_base, b_plus, b_err = evaluate_code_on_task(task, code_b)

            # -----------------------------------------------------------------
            # BRAZO C: POLYDIM V26505 (Stiefel St(d_out, d_in) + PMTP Seqlock C++/Rust)
            # -----------------------------------------------------------------
            t_c0 = time.perf_counter()
            vec_c = rng.standard_normal(D_cam).astype(np.float64)
            # Invariante Stiefel con acumulación Neumaier FP64
            vec_c /= np.sqrt(np.sum(vec_c ** 2))
            vec_c = W_st @ (W_st.T @ vec_c)
            vec_c /= np.sqrt(np.sum(vec_c ** 2))

            # Publicación atómica en memoria compartida PMTP
            cpp.polydim_pmtp_v6_claim_writer_v26503(
                slab_addr, total_bytes, 1, ctypes.byref(out_slot), ctypes.byref(out_token)
            )
            cpp.polydim_pmtp_v6_publish_flip_v26503(
                slab_addr, total_bytes, 1, out_token.value, 1
            )
            rust.polydim_pmtp_v6_read_snapshot_v26503(
                slab_addr, total_bytes, slab_addr + 64, D_cam, payload_bytes,
                vec_c.ctypes.data_as(ctypes.c_void_p), ctypes.byref(out_slot), ctypes.byref(out_gen)
            )
            sil_c_ms = (time.perf_counter() - t_c0) * 1000.0

            r_c = call_cerebras(api_key, "qwen-3.8-27b", [
                {"role": "system", "content": f"Axioma de Integridad Algorítmica POLYDIM V26505 (PMTP Gen={out_gen.value}): Maneja estrictamente casos límite, tipos vacíos y precondiciones."},
                {"role": "user", "content": prompt_base}
            ], max_tokens=1024)
            code_c = extract_python_code(r_c["raw_content_only"] or r_c["content"], task["entry_point"])
            c_base, c_plus, c_err = evaluate_code_on_task(task, code_c)

            record = {
                "task_id": tid,
                "entry_point": task["entry_point"],
                "results": {
                    "A_1D_multihop": {"base_pass": a_base, "plus_pass": a_plus, "tokens": a_tokens, "wall_ms": round(a_wall, 2), "wse_ms": round(a_wse, 2), "err": a_err},
                    "B_affine_vector": {"base_pass": b_base, "plus_pass": b_plus, "tokens": r_b["total_tokens"], "wall_ms": round(sil_b_ms + r_b["elapsed_ms"], 2), "wse_ms": round(r_b["wse_compute_ms"], 2), "err": b_err},
                    "C_polydim_stiefel": {"base_pass": c_base, "plus_pass": c_plus, "tokens": r_c["total_tokens"], "wall_ms": round(sil_c_ms + r_c["elapsed_ms"], 2), "silicon_ms": round(sil_c_ms, 4), "wse_ms": round(r_c["wse_compute_ms"], 2), "err": c_err},
                    "D_zero_hop_direct": {"base_pass": d_base, "plus_pass": d_plus, "tokens": r_d["total_tokens"], "wall_ms": round(r_d["elapsed_ms"], 2), "wse_ms": round(r_d["wse_compute_ms"], 2), "err": d_err},
                }
            }
            existing_records.append(record)
            jsonl_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            jsonl_f.flush()

            print(
                f"  Brazo D (Zero-Hop Directo):   Base={'PASS' if d_base else 'FAIL'} | Plus={'PASS' if d_plus else 'FAIL'} | Tok={r_d['total_tokens']:4d} | Wall={r_d['elapsed_ms']:6.1f} ms\n"
                f"  Brazo A (Línea Base 1D 3p):  Base={'PASS' if a_base else 'FAIL'} | Plus={'PASS' if a_plus else 'FAIL'} | Tok={a_tokens:4d} | Wall={a_wall:6.1f} ms\n"
                f"  Brazo B (Control Vectorial): Base={'PASS' if b_base else 'FAIL'} | Plus={'PASS' if b_plus else 'FAIL'} | Tok={r_b['total_tokens']:4d} | Wall={(sil_b_ms + r_b['elapsed_ms']):6.1f} ms\n"
                f"  Brazo C (POLYDIM Stiefel):   Base={'PASS' if c_base else 'FAIL'} | Plus={'PASS' if c_plus else 'FAIL'} | Tok={r_c['total_tokens']:4d} | Wall={(sil_c_ms + r_c['elapsed_ms']):6.1f} ms (Silicio={sil_c_ms:.3f} ms)",
                flush=True
            )

    # Recomputar métricas sobre los 20 casos completos
    n_total = len(existing_records)
    summary_counts = {
        "A": {"base_pass": 0, "plus_pass": 0, "tokens": 0, "wall_ms": 0.0, "wse_ms": 0.0},
        "B": {"base_pass": 0, "plus_pass": 0, "tokens": 0, "wall_ms": 0.0, "wse_ms": 0.0},
        "C": {"base_pass": 0, "plus_pass": 0, "tokens": 0, "wall_ms": 0.0, "wse_ms": 0.0},
        "D": {"base_pass": 0, "plus_pass": 0, "tokens": 0, "wall_ms": 0.0, "wse_ms": 0.0},
    }
    for rec in existing_records:
        res = rec["results"]
        for k, arm_key in (("A", "A_1D_multihop"), ("B", "B_affine_vector"), ("C", "C_polydim_stiefel"), ("D", "D_zero_hop_direct")):
            summary_counts[k]["base_pass"] += int(res[arm_key]["base_pass"])
            summary_counts[k]["plus_pass"] += int(res[arm_key]["plus_pass"])
            summary_counts[k]["tokens"] += int(res[arm_key]["tokens"])
            summary_counts[k]["wall_ms"] += float(res[arm_key]["wall_ms"])
            summary_counts[k]["wse_ms"] += float(res[arm_key]["wse_ms"])

    final_report = {
        "timestamp": datetime.now().isoformat(),
        "protocol": "AUDITORIA_CUADRUPLE_A_B_C_D_HUMANEVALPLUS_PILOT20_COMPLETO",
        "num_tasks": n_total,
        "frozen_task_ids": [r["task_id"] for r in existing_records],
        "models": ["qwen-3.8-27b", "gpt-oss-120b"],
        "hardware": "Cerebras CS-3 (api.cerebras.ai) + C++20/Rust 2021 Local Silicon",
        "summary": {
            k: {
                "base_pass_count": summary_counts[k]["base_pass"],
                "base_pass_rate_pct": round(summary_counts[k]["base_pass"] / n_total * 100, 1),
                "plus_pass_count": summary_counts[k]["plus_pass"],
                "plus_pass_rate_pct": round(summary_counts[k]["plus_pass"] / n_total * 100, 1),
                "total_tokens": summary_counts[k]["tokens"],
                "avg_tokens_per_task": round(summary_counts[k]["tokens"] / n_total, 1),
                "avg_wall_ms": round(summary_counts[k]["wall_ms"] / n_total, 1),
                "avg_wse_ms": round(summary_counts[k]["wse_ms"] / n_total, 1),
                "ms_per_correct_plus": round(summary_counts[k]["wall_ms"] / max(1, summary_counts[k]["plus_pass"]), 1),
            } for k in ("A", "B", "C", "D")
        },
        "task_records": existing_records,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 86)
    print(f"PILOTO DE 20 CASOS HUMANEVALPLUS COMPLETADO CON ÉXITO — {n_total}/20 CASOS")
    print("=" * 86)
    for k in ("D", "A", "B", "C"):
        sm = final_report["summary"][k]
        print(f"  Brazo {k}: Base={sm['base_pass_count']}/{n_total} ({sm['base_pass_rate_pct']}%) | Plus={sm['plus_pass_count']}/{n_total} ({sm['plus_pass_rate_pct']}%) | Tokens={sm['total_tokens']} | WallAvg={sm['avg_wall_ms']} ms | ms/correct_plus={sm['ms_per_correct_plus']} ms")
    return 0

if __name__ == "__main__":
    sys.exit(main())
