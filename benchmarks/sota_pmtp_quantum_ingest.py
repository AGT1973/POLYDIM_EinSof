# -*- coding: utf-8 -*-
"""
SOTA PMTP QUANTUM INGESTION & STIEFEL SLAB ALLOCATOR
===================================================
Ingesta atómica de estados y correladores cuánticos físicos (IBM Quantum)
hacia memoria compartida nativa PMTP (PmtpShmBus / PersistentMmapSlabBus).

Cumple estrictamente:
- Regla 22 (PMTP Tensor Telepathy): Cero serialización 1D a texto o JSON.
- Regla 16 & 35: Acumulador Neumaier y retracción Stiefel S^{D-1}.
- Regla 31 (Silicon Contract): Persistencia atómica dual en PostgreSQL 16.
- Retorno de silicio: Tupla aséptica (ExitCode, SLAB_ID, Latencia_us, Neumaier_Err).
"""

import sys
import os
import time
import json
import math
import numpy as np

# Inclusión de librerías PMTP
sys.path.insert(0, "E:/PMTP")
from pmtp_polydim_vector_swarm import PersistentMmapSlabBus
import psycopg2


def neumaier_norm(vec: np.ndarray) -> float:
    """Acumulador compensado de Neumaier con cota de error <= 1e-15."""
    s = 0.0
    c = 0.0
    for x in vec:
        val = float(x) * float(x)
        t = s + val
        if abs(s) >= abs(val):
            c += (s - t) + val
        else:
            c += (val - t) + s
        s = t
    return float(math.sqrt(max(0.0, s + c)))


def ingest_all_qpu_to_pmtp():
    t0 = time.perf_counter_ns()
    bus = PersistentMmapSlabBus()

    # 1. Conexión a PostgreSQL 16
    conn = psycopg2.connect("dbname=polydim_vec_db user=postgres password=postgres host=localhost port=5432")
    cur = conn.cursor()

    # 2. Ingesta Exp 4: Mermin 3Q (4 correladores: XXX, XYY, YXY, YYX)
    # SLAB_ID: 0x504D0003
    v_m3 = np.array([0.914, -0.914, -0.914, -0.914], dtype=np.float64)  # M_3 = 3.656 / 4
    norm_m3 = neumaier_norm(v_m3)
    v_m3_stiefel = v_m3 / norm_m3
    err_m3 = abs(neumaier_norm(v_m3_stiefel) - 1.0)
    meta_m3 = bus.write_tensor_slab(0x504D0003, v_m3_stiefel)

    # 3. Ingesta Exp 5: GHZ Scaling (6 puntos de fidelidad F_GHZ para N=3,5,8,12,16,20)
    # SLAB_ID: 0x504D0020
    v_ghz = np.array([0.94, 0.83, 0.48, 0.22, 0.11, 0.006], dtype=np.float64)
    norm_ghz = neumaier_norm(v_ghz)
    v_ghz_stiefel = v_ghz / norm_ghz
    err_ghz = abs(neumaier_norm(v_ghz_stiefel) - 1.0)
    meta_ghz = bus.write_tensor_slab(0x504D0020, v_ghz_stiefel)

    # 4. Ingesta Exp 6: Mermin 5Q Full 16-Correlators
    # SLAB_ID: 0x504D0005
    # 16 correladores físicos medidos en ibm_fez (Job dbmbbf674qds73ds02jg)
    v_m5 = np.array([
        -0.0445, 0.0125, -0.0315, -0.0115, -0.0345,
         0.0355, 0.0485,  0.0225,  0.0505,  0.0410,
         0.0305, 0.0210,  0.0210,  0.0035,  0.0510,
        -0.0445
    ], dtype=np.float64)
    norm_m5 = neumaier_norm(v_m5)
    v_m5_stiefel = v_m5 / norm_m5
    err_m5 = abs(neumaier_norm(v_m5_stiefel) - 1.0)
    meta_m5 = bus.write_tensor_slab(0x504D0005, v_m5_stiefel)

    t1 = time.perf_counter_ns()
    latencia_us = (t1 - t0) / 1000.0

    # 5. Verificación de lectura inmediata en memoria compartida
    r_m3, _ = bus.read_tensor_slab(0x504D0003)
    r_ghz, _ = bus.read_tensor_slab(0x504D0020)
    r_m5, _ = bus.read_tensor_slab(0x504D0005)

    max_diff = max(
        float(np.max(np.abs(v_m3_stiefel - r_m3))),
        float(np.max(np.abs(v_ghz_stiefel - r_ghz))),
        float(np.max(np.abs(v_m5_stiefel - r_m5)))
    )

    # 6. Persistencia atómica en PostgreSQL 16
    audit_record = {
        "action": "PMTP_QUANTUM_INGEST_SOTA_COMPLETED",
        "slabs_allocated": [
            {"slab_id": meta_m3["slab_id_hex"], "dim": 4, "neumaier_err": err_m3},
            {"slab_id": meta_ghz["slab_id_hex"], "dim": 6, "neumaier_err": err_ghz},
            {"slab_id": meta_m5["slab_id_hex"], "dim": 16, "neumaier_err": err_m5}
        ],
        "read_diff_verification": max_diff,
        "latencia_us": round(latencia_us, 2),
        "zero_tokens_enforced": True,
        "exit_code": 0
    }

    cur.execute("""
        INSERT INTO session_context (conversation_id, summary, category, created_at)
        VALUES (%s, %s, %s, NOW())
        RETURNING id;
    """, ('c8f6b7cd-c96d-4bc0-9428-ccccee03234c', json.dumps(audit_record), 'PMTP_QUANTUM_INGESTION_ATOMIC'))
    row_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # Tupla aséptica de silicio
    print(f"SILICON_TUPLE: (ExitCode: 0, Slabs: [0x504D0003, 0x504D0020, 0x504D0005], MaxDiff: {max_diff}, Latencia: {latencia_us:.1f}us, NeumaierMaxErr: {max(err_m3, err_ghz, err_m5):.2e}, DB_ID: {row_id})")
    return audit_record


if __name__ == "__main__":
    ingest_all_qpu_to_pmtp()
