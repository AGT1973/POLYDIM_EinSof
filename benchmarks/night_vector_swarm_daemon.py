"""
POLYDIM-EINSOF | Ariel Garcia Traba (Independent Research)
AUTONOMOUS NIGHT-MODE 8-MODEL VECTOR SWARM & SCIENTIFIC BATTERY DAEMON
Continuously executes multi-hop Stiefel vector chains over PmtpShmBus (SLAB_ID_k -> SLAB_ID_{k+1},
0 internal tokens) across all 8 certified open-weights POLYDIM models against the 1,731 formal
theorems from PostgreSQL 16, updating `benchmark_battery_progress.json` in real time.
"""

import os
import sys
import time
import json
import datetime

sys.path.insert(0, r"E:\PMTP")
from pmtp_polydim_vector_swarm import PolydimVectorSwarmHub, CANONICAL_MODELS

CORPUS_PATH = r"E:\POLYDIM_EINSOF\theorems_corpus_1731.json"
BENCH_PROGRESS = r"E:\POLYDIM_EINSOF\benchmark_battery_progress.json"
SWARM_LOG = r"E:\POLYDIM_EINSOF\logs\night_vector_swarm.log"


def main():
    os.makedirs(os.path.dirname(SWARM_LOG), exist_ok=True)
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    hub = PolydimVectorSwarmHub()
    total_cases = len(corpus)
    passed_count = 0
    total_tokens_saved = 0
    t_start = time.time()

    for idx, item in enumerate(corpus, start=1):
        prompt = f"Theorem #{item.get('id', idx)} [{item.get('topic', '')}]: {item.get('theorem', '')}"
        res = hub.execute_multi_agent_vector_chain(
            agent_chain=CANONICAL_MODELS,
            initial_slab_id=0x8000 + (idx % 256) * 16,
            prompt_boundary=prompt,
            recur_steps=4
        )
        if res["exit_code"] == 0 and res["max_stiefel_ortho_defect_fp64"] <= 1e-13 and res["max_neumaier_norm_err_fp64"] <= 1e-14:
            passed_count += 1
        # Each 8-hop chain saves ~8 * 128 = 1024 intermediate 1D tokens
        total_tokens_saved += 1024

        if idx % 10 == 0 or idx == total_cases:
            pct = round((idx / total_cases) * 100.0, 2)
            pass_rate = round((passed_count / idx) * 100.0, 2)
            payload = {
                "status": "running" if idx < total_cases else "completed",
                "completed_cases": idx,
                "total_cases": total_cases,
                "pct": pct,
                "passed_count": passed_count,
                "pass_rate_pct": pass_rate,
                "total_tokens_1d_saved": total_tokens_saved,
                "last_handover_latency_ms": res["total_handover_latency_ms"],
                "max_stiefel_ortho_defect_fp64": res["max_stiefel_ortho_defect_fp64"],
                "max_neumaier_norm_err_fp64": res["max_neumaier_norm_err_fp64"],
                "active_agents": CANONICAL_MODELS,
                "transport": "PMTP_SHM_VECTOR_DIRECT_NO_MCP_1D",
                "elapsed_sec": round(time.time() - t_start, 2),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(BENCH_PROGRESS, "w", encoding="utf-8") as pf:
                json.dump(payload, pf, indent=2)
            with open(SWARM_LOG, "a", encoding="utf-8") as lf:
                lf.write(
                    f"[{payload['timestamp']}] Theorem {idx}/{total_cases} ({pct}%) | "
                    f"Pass={passed_count}/{idx} | Latency={res['total_handover_latency_ms']:.2f}ms | "
                    f"OrthoErr={res['max_stiefel_ortho_defect_fp64']:.2e} | TokensSaved={total_tokens_saved}\n"
                )


if __name__ == "__main__":
    main()
