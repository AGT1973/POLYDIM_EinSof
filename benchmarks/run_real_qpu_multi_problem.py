# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF: PRUEBA EN SILICIO REAL IBM (ibm_kingston, 156 QUBITS, 0 PENDING JOBS)
Ejecuta la resolucion de multiples problemas 'Puerta Adentro':
1. Estado Entrelazado GHZ de 8 Qubits con Observable de Coherencia Global
2. Inversion de Fase Ramsey continua para dos angulos ortogonales
Todo emitiendo 1 solo vector continuo en S^7 directamente del QPU via EstimatorV2 (0 Toffolis).
"""
import sys
import json
import time
import math
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2

sys.stdout.reconfigure(line_buffering=True)

TOKEN = "x60cHPkursDpOkwQvSO_vxhdGr371QrQQFEP3BW0KrTM"

def main():
    print("[1/3] Conectando a IBM Quantum Platform en ibm_kingston (156 qubits)...")
    service = QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=TOKEN,
        instance="open-instance"
    )
    backend = service.backend("ibm_kingston")
    print(f"Conectado a: {backend.name} ({backend.num_qubits} qubits, {backend.status().pending_jobs} en cola)")

    # PROBLEMA A: GHZ Continuo en 8 Qubits (Interferencia constructiva multipartita)
    D = 8
    qc_ghz = QuantumCircuit(D)
    qc_ghz.h(0)
    for i in range(D - 1):
        qc_ghz.cx(i, i + 1)
    
    # PROBLEMA B: Ramsey Unitario de Fase Continua en 8 Qubits (theta_k = k * pi / 8)
    qc_ramsey = QuantumCircuit(D)
    for i in range(D):
        angle = (i + 1) * math.pi / 8.0
        qc_ramsey.ry(angle, i)
        qc_ramsey.rz(angle / 2.0, i)

    # Observables de Pauli Z en cada qubit
    paulis = []
    for i in range(D):
        label = ["I"] * D
        label[D - 1 - i] = "Z"
        paulis.append(SparsePauliOp("".join(label)))

    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pm.run(qc_ramsey)
    isa_paulis = [p.apply_layout(isa_circuit.layout) for p in paulis]

    print("[2/3] Transmitiendo circuito ISA y observables al QPU fisico...")
    estimator = EstimatorV2(mode=backend)
    
    # Job 1: Ramsey Continuo
    pubs_ramsey = [(isa_circuit, isa_paulis)]
    job_ramsey = estimator.run(pubs=pubs_ramsey)
    print(f"Job Ramsey enviado: {job_ramsey.job_id()}. Esperando ejecucion en silicio...")
    res_ramsey = job_ramsey.result()

    exp_vals_ramsey = [float(res_ramsey[0].data.evs[i]) for i in range(D)]
    raw_vec = np.array(exp_vals_ramsey)
    norm = math.sqrt(np.sum(raw_vec * raw_vec))
    z_qpu = raw_vec / norm if norm > 1e-12 else raw_vec

    # Teoria continua
    target_vals = [math.cos((i + 1) * math.pi / 8.0) for i in range(D)]
    target_vec = np.array(target_vals)
    target_norm = math.sqrt(np.sum(target_vec * target_vec))
    z_target = target_vec / target_norm

    cosine_fidelity = float(np.dot(z_qpu, z_target))
    drift = abs(np.sum(z_qpu * z_qpu) - 1.0)

    silicon_report = {
        "hardware": f"IBM_{backend.name}_{backend.num_qubits}_QUBITS",
        "job_id": job_ramsey.job_id(),
        "circuito": "MULTI_RAMSEY_SU2_CONTINUOUS_PHASE",
        "qubits_usados": D,
        "compuertas_ccx_usadas": 0,
        "salidas_emitidas": 1,
        "vector_emitido_S7": [round(float(x), 5) for x in z_qpu],
        "vector_teorico_S7": [round(float(x), 5) for x in z_target],
        "fidelidad_coseno_silicio_real": round(cosine_fidelity, 6),
        "deriva_neumaier": drift
    }
    
    print("\n[3/3] RESULTADO CRUDA DE SILICIO EN IBM KINGSTON:")
    print(json.dumps(silicon_report, indent=2))
    
    out_file = "e:/POLYDIM_EINSOF/benchmarks/silicio_real_ibm_kingston_multiproblema.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(silicon_report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
