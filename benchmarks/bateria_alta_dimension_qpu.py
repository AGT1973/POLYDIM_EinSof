import time
import json
import psycopg
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

print("=== BATERIA AVANZADA DE ALTA DIMENSION QPU (8 QUBITS - PUERTA ADENTRO) ===")

conn = psycopg.connect('dbname=polydim_active_db user=postgres host=localhost port=5432')
cur = conn.cursor()
cur.execute("SELECT value FROM active_vault WHERE key_name = 'ibm_quantum_api_key' LIMIT 1;")
ibm_token = cur.fetchone()[0].strip()
conn.close()

service = QiskitRuntimeService(channel="ibm_quantum_platform", token=ibm_token)
backend = service.least_busy(simulator=False, operational=True)
print(f"[OK] Conectado a IBM Quantum: {backend.name} ({backend.num_qubits} qubits)")

pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
pubs = []
n_q = 8

# --- PROBLEMA 4: Estado GHZ de 8 Qubits (Coherencia Multipartita Global) ---
qc_ghz = QuantumCircuit(n_q)
qc_ghz.h(0)
for i in range(n_q - 1):
    qc_ghz.cx(i, i + 1)
# Observable: Fidelidad de coherencia global (Paridad Z...Z y testigo X...X)
obs_ghz = SparsePauliOp.from_list([
    ("Z" * n_q, 0.5),
    ("X" * n_q, 0.5)
])
isa_qc_ghz = pm.run(qc_ghz)
isa_obs_ghz = obs_ghz.apply_layout(isa_qc_ghz.layout)
pubs.append((isa_qc_ghz, isa_obs_ghz))
print(f"[OK] Problema 4 preparado: Coherencia Global GHZ ({n_q} Qubits)")

# --- PROBLEMA 5: Modelo XY con Campo Transversal (8 Qubits en Anillo - SO(8)) ---
qc_xy = QuantumCircuit(n_q)
for i in range(n_q):
    qc_xy.ry(0.5236 * (i + 1), i)
for i in range(n_q):
    qc_xy.cx(i, (i + 1) % n_q)
    qc_xy.rz(0.4, (i + 1) % n_q)
    qc_xy.cx(i, (i + 1) % n_q)

# Hamiltoniano XY: \sum (XX + YY) + h \sum Z
xy_terms = []
for i in range(n_q):
    j = (i + 1) % n_q
    # XX
    s_x = ["I"] * n_q
    s_x[i] = "X"
    s_x[j] = "X"
    xy_terms.append(("".join(s_x), 0.5))
    # YY
    s_y = ["I"] * n_q
    s_y[i] = "Y"
    s_y[j] = "Y"
    xy_terms.append(("".join(s_y), 0.5))
    # Z local
    s_z = ["I"] * n_q
    s_z[i] = "Z"
    xy_terms.append(("".join(s_z), 0.2))

obs_xy = SparsePauliOp.from_list(xy_terms)
isa_qc_xy = pm.run(qc_xy)
isa_obs_xy = obs_xy.apply_layout(isa_qc_xy.layout)
pubs.append((isa_qc_xy, isa_obs_xy))
print(f"[OK] Problema 5 preparado: Modelo XY Cuántico en Anillo ({n_q} Qubits, {len(xy_terms)} operadores)")

# --- PROBLEMA 6: Testigo de Entrelazamiento Topológico (Cadena Cluster 8Q) ---
qc_cluster = QuantumCircuit(n_q)
qc_cluster.h(range(n_q))
for i in range(n_q - 1):
    qc_cluster.cz(i, i + 1)
# Estabilizador K_i = X_{i-1} Z_i X_{i+1}
cluster_terms = []
for i in range(1, n_q - 1):
    s = ["I"] * n_q
    s[i - 1] = "X"
    s[i] = "Z"
    s[i + 1] = "X"
    cluster_terms.append(("".join(s), 1.0 / (n_q - 2)))
obs_cluster = SparsePauliOp.from_list(cluster_terms)
isa_qc_cluster = pm.run(qc_cluster)
isa_obs_cluster = obs_cluster.apply_layout(isa_qc_cluster.layout)
pubs.append((isa_qc_cluster, isa_obs_cluster))
print(f"[OK] Problema 6 preparado: Estado Cluster y Orden Topológico ({n_q} Qubits)")

# Enviar los 3 problemas avanzados a IBM Quantum
estimator = Estimator(mode=backend)
estimator.options.resilience_level = 1
estimator.options.default_shots = 10000

print(f"\n[INFO] Despachando lote avanzado de 8 Qubits a {backend.name}...")
job = estimator.run(pubs)
job_id = job.job_id()

print(f"\n========================================================")
print(f" [EXITO] LOTE AVANZADO DE 8 QUBITS ENVIADO A IBM")
print(f" Job ID Oficial: {job_id}")
print(f" Backend: {backend.name}")
print(f" Problemas: GHZ 8Q, Modelo XY en Anillo 8Q, Cluster Topologico 8Q")
print(f" Dimensión del espacio de Hilbert: D = 2^8 = 256 estados continuos")
print(f" Vueltas de fase en chip: 10.000 shots por problema (30.000 total)")
print(f" Reducción: 3 valores escalares de expectativa vs 30.000 lecturas 1D")
print(f" URL de Monitoreo: https://quantum.ibm.com/jobs/{job_id}")
print(f"========================================================\n")

# Guardar en PostgreSQL
conn_vec = psycopg.connect('dbname=polydim_vec_db user=postgres host=localhost port=5432')
cur_vec = conn_vec.cursor()
cur_vec.execute("""
    INSERT INTO session_context (conversation_id, summary, category, created_at)
    VALUES (%s, %s, %s, NOW());
""", (
    "8541d614-bf7f-4311-8da9-c9935f2f27c6",
    json.dumps({
        "job_id": job_id,
        "backend": backend.name,
        "qubits": 8,
        "hilbert_dim": 256,
        "problems": ["GHZ_8Q", "XY_RING_8Q", "CLUSTER_TOPOLOGICAL_8Q"],
        "shots_each": 10000,
        "status": "QUEUED"
    }),
    "REAL_IBM_QUANTUM_8QUBIT_BATCH"
))
conn_vec.commit()
conn_vec.close()
print("[OK] Lote avanzado registrado en PostgreSQL 16.")
