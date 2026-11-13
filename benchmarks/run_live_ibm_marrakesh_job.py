"""
LIVE EXECUTION ON IBM MARRAKESH (156 QUBITS, QUEUE=0)
Ejecución en silicio cuántico físico real de IBM Quantum:
Proyección continua en variedad de Stiefel S^7 / SU(2) con EstimatorV2.
"""

import time
import json
import numpy as np
import psycopg2
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

def neumaier_norm_fp64(v: np.ndarray) -> float:
    s = 0.0
    c = 0.0
    for x in v:
        val = x * x
        t = s + val
        if abs(s) >= abs(val):
            c += (s - t) + val
        else:
            c += (val - t) + s
        s = t
    return float(np.sqrt(s + c))

def execute_on_ibm_marrakesh():
    # 1. Recuperar credencial segura de PostgreSQL 16
    conn = psycopg2.connect(dbname='polydim_active_db', user='postgres', password='postgres', host='localhost', port=5432)
    cur = conn.cursor()
    cur.execute("SELECT value FROM active_vault WHERE key_name = 'ibm_quantum_api_key'")
    token = cur.fetchone()[0]
    cur.close()
    conn.close()

    # 2. Conectar al servicio IBM Quantum Platform
    print("[1/5] Conectando a IBM Quantum Platform...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance="open-instance")
    
    backend_name = "ibm_marrakesh"
    print(f"[2/5] Seleccionando QPU de 156 qubits: {backend_name}...")
    backend = service.backend(backend_name)
    status = backend.status()
    print(f"      Estado: operacional={status.operational}, trabajos_pendientes={status.pending_jobs}")

    # 3. Vector objetivo continuo en la variedad de Stiefel S^7 (8 dimensiones)
    d_dim = 8
    rng = np.random.default_rng(20261103)
    v_target = rng.uniform(-0.9, 0.9, size=d_dim)
    v_target /= neumaier_norm_fp64(v_target)

    thetas = np.arccos(np.clip(v_target, -1.0, 1.0))

    # Circuito nativo SU(2) Ramsey continuo (0 compuertas CCX booleanas)
    qc = QuantumCircuit(d_dim)
    for j in range(d_dim):
        qc.ry(float(thetas[j] / 2.0), j)
        qc.rz(0.0, j)
        qc.ry(float(thetas[j] / 2.0), j)

    # Observables de Pauli Z_j para extraer el vector continuo
    observables = []
    for j in range(d_dim):
        pauli_list = ["I"] * d_dim
        pauli_list[d_dim - 1 - j] = "Z"
        observables.append(SparsePauliOp("".join(pauli_list)))

    # 4. Transpilación ISA para la topología de acoplamiento de ibm_marrakesh
    print("[3/5] Transpilando a arquitectura nativa ISA de ibm_marrakesh (optimization_level=3)...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    isa_qc = pm.run(qc)
    isa_obs = [obs.apply_layout(isa_qc.layout) for obs in observables]

    # 5. Encolamiento y ejecución en el procesador físico
    print("[4/5] Despachando trabajo con EstimatorV2 al procesador cuántico...")
    t0 = time.perf_counter()
    estimator = EstimatorV2(mode=backend)
    job = estimator.run([(isa_qc, isa_obs)])
    job_id = job.job_id()
    print(f"      JOB ID EN SILICIO CUÁNTICO: {job_id}")
    print("      Esperando resultado físico de las compuertas superconductoras...")

    res = job.result()[0]
    t1 = time.perf_counter()
    latency_total_s = t1 - t0

    # Extracción del vector continuo
    v_qpu_raw = np.array(res.data.evs, dtype=np.float64).ravel()
    nrm_qpu = neumaier_norm_fp64(v_qpu_raw)
    v_qpu_unit = v_qpu_raw / nrm_qpu

    cosine_fidelity = float(np.dot(v_qpu_unit, v_target))
    neumaier_drift = abs(neumaier_norm_fp64(v_qpu_unit) - 1.0)

    print(f"[5/5] Trabajo {job_id} COMPLETADO con éxito.")
    print(f"      Fidelidad cosenoidal continua en S^7: {cosine_fidelity:.6f}")
    print(f"      Deriva ortonormal Neumaier FP64: {neumaier_drift:.2e}")

    result_payload = {
        "hardware": f"QPU_{backend_name}_156_QUBITS",
        "job_id": job_id,
        "status": "COMPLETED",
        "latency_total_seconds": round(latency_total_s, 2),
        "math_function": "SU2_STIEFEL_S7_RAMSEY_EXPECTATION",
        "boolean_ccx_gates_used": 0,
        "vector_dimension_D": d_dim,
        "outputs_crossed_door": 1,
        "target_vector_S7": [round(float(x), 5) for x in v_target],
        "qpu_physical_output_S7": [round(float(x), 5) for x in v_qpu_unit],
        "cosine_fidelity": round(cosine_fidelity, 6),
        "neumaier_orthonormal_drift": neumaier_drift,
        "queue_at_submission": status.pending_jobs
    }

    # Persistir en PostgreSQL 16
    conn_vec = psycopg2.connect(dbname='polydim_vec_db', user='postgres', password='postgres', host='localhost', port=5432)
    cur_vec = conn_vec.cursor()
    cur_vec.execute("""
        INSERT INTO session_context (conversation_id, summary, category, created_at)
        VALUES (%s, %s, %s, NOW())
    """, ('a9c79c56-9fe9-42ad-bb67-80d40e88c44e', json.dumps(result_payload), 'LIVE_QPU_IBM_MARRAKESH_RUN'))
    conn_vec.commit()
    cur_vec.close()
    conn_vec.close()
    print("      Resultado persistido atómicamente en PostgreSQL 16 (session_context).")

    return result_payload

if __name__ == "__main__":
    rep = execute_on_ibm_marrakesh()
    print("\n=== TUPLA DE SILICIO REAL: IBM MARRAKESH 156Q ===")
    print(json.dumps(rep, indent=2))
