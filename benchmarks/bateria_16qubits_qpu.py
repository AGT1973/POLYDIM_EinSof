import time
import json
import psycopg
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

print("=== BATERIA SOTA DE 16 QUBITS EN SILICIO CRIO (D = 65.536 - PUERTA ADENTRO) ===")

# 1. Recuperar token de bóveda segura en PostgreSQL
conn = psycopg.connect('dbname=polydim_active_db user=postgres host=localhost port=5432')
cur = conn.cursor()
cur.execute("SELECT value FROM active_vault WHERE key_name = 'ibm_quantum_api_key' LIMIT 1;")
ibm_token = cur.fetchone()[0].strip()
conn.close()

# 2. Conectar al servicio de IBM Quantum
service = QiskitRuntimeService(channel="ibm_quantum_platform", token=ibm_token, instance="open-instance")

# Priorizar ibm_marrakesh (156 Qubits)
try:
    backend = service.backend("ibm_marrakesh")
    if not backend.status().operational:
        backend = service.least_busy(simulator=False, operational=True, min_num_qubits=16)
except Exception:
    backend = service.least_busy(simulator=False, operational=True, min_num_qubits=16)

print(f"[OK] Backend asignado: {backend.name} ({backend.num_qubits} qubits fisicos superconductores)")
print(f"     Cola actual en chip: {backend.status().pending_jobs} jobs")

pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
pubs = []
n_q = 16

# --- PROBLEMA 8: Cadena Topológica de Kitaev / Majorana (16 Qubits) ---
# Modos de borde fermiónicos no locales y conservación de paridad
qc_kitaev = QuantumCircuit(n_q)
for i in range(n_q):
    qc_kitaev.ry(np.pi / 4.0, i)
for i in range(n_q - 1):
    qc_kitaev.cz(i, i + 1)
for i in range(0, n_q - 1, 2):
    qc_kitaev.cx(i, i + 1)

# Observable: Paridad global Z_0...Z_15 + Correlador no local de borde X_0 Z_1...Z_14 X_15
term_parity = "Z" * n_q
term_edge = "X" + ("Z" * (n_q - 2)) + "X"
obs_kitaev = SparsePauliOp.from_list([
    (term_parity, 0.5),
    (term_edge, 0.5)
])
isa_qc_kitaev = pm.run(qc_kitaev)
isa_obs_kitaev = obs_kitaev.apply_layout(isa_qc_kitaev.layout)
pubs.append((isa_qc_kitaev, isa_obs_kitaev))
print(f"[OK] Problema 8 preparado: Kitaev / Majorana 16Q (Paridad no local y bordes)")

# --- PROBLEMA 9: Estado Macroscópico GHZ (16 Qubits - Coherencia Global) ---
qc_ghz = QuantumCircuit(n_q)
qc_ghz.h(0)
for i in range(n_q - 1):
    qc_ghz.cx(i, i + 1)

# Testigo de coherencia macroscópica GHZ: 0.5 * Z^16 + 0.5 * X^16
obs_ghz = SparsePauliOp.from_list([
    ("Z" * n_q, 0.5),
    ("X" * n_q, 0.5)
])
isa_qc_ghz = pm.run(qc_ghz)
isa_obs_ghz = obs_ghz.apply_layout(isa_qc_ghz.layout)
pubs.append((isa_qc_ghz, isa_obs_ghz))
print(f"[OK] Problema 9 preparado: GHZ Macroscopico 16Q (Entrelazamiento 16 qubits)")

# --- PROBLEMA 10: Cadena Heisenberg Cuántica XXX (16 Qubits) ---
# Hamiltoniano de intercambio antiferromagnético continuo
qc_heisenberg = QuantumCircuit(n_q)
for i in range(n_q):
    qc_heisenberg.ry(0.3 * (i + 1), i)
for i in range(n_q - 1):
    qc_heisenberg.cx(i, i + 1)
    qc_heisenberg.rz(0.45, i + 1)
    qc_heisenberg.cx(i, i + 1)

# H_XXX = 1/15 * \sum (X_i X_{i+1} + Y_i Y_{i+1} + Z_i Z_{i+1})
heis_terms = []
num_links = n_q - 1
norm_factor = 1.0 / num_links
for i in range(num_links):
    j = i + 1
    for pauli in ["X", "Y", "Z"]:
        s = ["I"] * n_q
        s[i] = pauli
        s[j] = pauli
        heis_terms.append(("".join(s), norm_factor))

obs_heisenberg = SparsePauliOp.from_list(heis_terms)
isa_qc_heisenberg = pm.run(qc_heisenberg)
isa_obs_heisenberg = obs_heisenberg.apply_layout(isa_qc_heisenberg.layout)
pubs.append((isa_qc_heisenberg, isa_obs_heisenberg))
print(f"[OK] Problema 10 preparado: Heisenberg Cuantico XXX 16Q ({len(heis_terms)} terminos)")

# 3. Despacho a EstimatorV2 con mitigación TREX
estimator = Estimator(mode=backend)
estimator.options.resilience_level = 1
estimator.options.default_shots = 10000

print(f"\n[INFO] Despachando lote de 16 Qubits (D=65.536) a {backend.name}...")
job = estimator.run(pubs)
job_id = job.job_id()

print(f"\n========================================================")
print(f" [EXITO] LOTE SOTA DE 16 QUBITS DESPACHADO A IBM")
print(f" Job ID Oficial: {job_id}")
print(f" Backend: {backend.name}")
print(f" Dimension de Hilbert: D = 2^16 = 65.536 estados continuos")
print(f" Problemas: Kitaev Majorana 16Q, GHZ Macroscopico 16Q, Heisenberg XXX 16Q")
print(f" Disparos programados: 10.000 por problema (30.000 shots totales)")
print(f" Payload de respuesta: 3 floats (24 bytes) con mitigacion TREX")
print(f" Monitoreo en IBM: https://quantum.ibm.com/jobs/{job_id}")
print(f"========================================================\n")

# 4. Persistir registro atomico en PostgreSQL 16
conn_vec = psycopg.connect('dbname=polydim_vec_db user=postgres host=localhost port=5432')
cur_vec = conn_vec.cursor()
cur_vec.execute("""
    INSERT INTO session_context (conversation_id, summary, category, created_at)
    VALUES (%s, %s, %s, NOW());
""", (
    "6ffd5d25-4c7f-4425-8485-49e01b63fa05",
    json.dumps({
        "job_id": job_id,
        "backend": backend.name,
        "qubits": 16,
        "hilbert_dim": 65536,
        "problems": ["KITAEV_MAJORANA_16Q", "GHZ_MACROSCOPIC_16Q", "HEISENBERG_XXX_16Q"],
        "shots_each": 10000,
        "total_shots": 30000,
        "resilience_level": 1,
        "status": "QUEUED_IN_IBM_HARDWARE"
    }),
    "REAL_IBM_QUANTUM_16QUBIT_BATCH"
))
conn_vec.commit()
conn_vec.close()
print("[OK] Registro auditado y guardado en PostgreSQL 16 (polydim_vec_db).")
