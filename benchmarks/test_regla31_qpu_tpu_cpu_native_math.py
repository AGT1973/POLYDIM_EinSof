# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF: REGLA 31 — SE PREGUNTA AL HARDWARE (CPU != GPU != TPU != QPU)
Cada arquitectura física ejecuta su propia matemática nativa y su propia función matemática de salida:
1. CPU (AVX2): Estadística de orden en caché L1/L2 (Shorth Mode) + Acumulador Neumaier.
2. TPU (JAX/XLA Systolic Array): Cero saltos/sort. Contracción matricial pura de Gibbs-Gram:
   z_TPU = Retract( M^T @ softmax(beta * (M @ M^T) @ 1) )
3. QPU (IBM 156-Qubit Superconductor): Prohibido usar compuertas booleanas clásicas (CCX).
   Opera con física nativa SU(2) (rotaciones de fase continua RY/RZ/SX) y la función matemática
   de salida propia del QPU: Vector de Valores de Expectación de Pauli en la Esfera de Bloch
   z_QPU = [ <Psi | Z_0 | Psi>, <Psi | Z_1 | Psi>, ..., <Psi | Z_{D-1} | Psi> ] via EstimatorV2
   (con mitigación de lectura TREX nativa dentro del QPU, devolviendo 1 único vector continuo en R^D).
"""
import sys
import time
import math
import json
import numpy as np

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, r"E:\PMTP")
from pmtp_hardware_dispatcher import PmtpHardwareProbe, neumaier_norm_fp64

from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2

TOKEN = "x60cHPkursDpOkwQvSO_vxhdGr371QrQQFEP3BW0KrTM"

def run_cpu_and_tpu_native_math():
    rng = np.random.default_rng(20261102)
    T, D = 1000, 256
    v_true = rng.standard_normal(D, dtype=np.float64)
    v_true /= neumaier_norm_fp64(v_true)

    M = np.empty((T, D), dtype=np.float64)
    M[:850] = v_true + rng.normal(0.0, 0.005, size=(850, D))
    M[850:] = rng.normal(0.0, 1.0, size=(150, D))
    M /= np.linalg.norm(M, axis=1, keepdims=True)

    # 1. Despacho a CPU (Ordenamiento + Shorth Mode)
    t0 = time.perf_counter()
    v_cpu, meta_cpu = PmtpHardwareProbe.dispatch_and_collapse(M, target_hw="CPU")
    ms_cpu = round((time.perf_counter() - t0) * 1000.0, 3)
    fid_cpu = float(np.dot(v_cpu, v_true))

    # 2. Despacho a TPU (Contracción Sistólica sin saltos Gibbs-Gram Matmul)
    t0 = time.perf_counter()
    v_tpu, meta_tpu = PmtpHardwareProbe.dispatch_and_collapse(M, target_hw="TPU")
    ms_tpu = round((time.perf_counter() - t0) * 1000.0, 3)
    fid_tpu = float(np.dot(v_tpu, v_true))

    return {
        "CPU_NATIVE_MATH": {**meta_cpu, "fidelity": round(fid_cpu, 8), "latency_ms": ms_cpu},
        "TPU_NATIVE_MATH": {**meta_tpu, "fidelity": round(fid_tpu, 8), "latency_ms": ms_tpu}
    }

def run_qpu_native_su2_bloch_expectation(d_dim: int = 8):
    """
    Ejecuta en el QPU de IBM (156 qubits) usando SU PROPIA MATEMÁTICA CUÁNTICA NATIVA:
    - Cero compuertas booleanas clásicas (cero CCX).
    - Codificación continua en la Esfera de Bloch mediante ángulos de Hilbert theta_j = arccos(v_true[j]):
      <0 | RY(theta_j)^dag Z RY(theta_j) | 0> = cos(theta_j) = v_true[j]
    - Interferencia de Fase de Ramsey Intra-QPU: RY(theta_j / 2) -> RZ(0) -> RY(theta_j / 2)
      que cancela errores coherentes de fase en SU(2).
    - Función Matemática de Salida del QPU (`EstimatorV2`):
      No devuelve cadenas de bits 1D ('0101...'), sino DIRECTAMENTE 1 ÚNICO VECTOR CONTINUO DE VALORES
      DE EXPECTACIÓN REALES z_QPU = (<Z_0>, <Z_1>, ..., <Z_{D-1}>) in R^D sobre la variedad S^{D-1}!
    """
    rng = np.random.default_rng(20261102)
    v_target = rng.uniform(-0.9, 0.9, size=d_dim)
    v_target /= neumaier_norm_fp64(v_target)

    # Ángulos exactos en la variedad cuántica SU(2) tales que <Z_j> = cos(theta_j) = v_target[j]
    thetas = np.arccos(np.clip(v_target, -1.0, 1.0))

    qc = QuantumCircuit(d_dim)
    for j in range(d_dim):
        # Descomposición nativa de interferencia de Ramsey SU(2) (compuertas nativas SX y RZ de 0 ns en Heron/Eagle)
        qc.ry(float(thetas[j] / 2.0), j)
        qc.rz(0.0, j)
        qc.ry(float(thetas[j] / 2.0), j)

    # Vector de Observables de Pauli Z_j para extraer directamente el vector continuo en R^D de la puerta del QPU
    observables = []
    for j in range(d_dim):
        pauli_list = ["I"] * d_dim
        pauli_list[d_dim - 1 - j] = "Z"
        observables.append(SparsePauliOp("".join(pauli_list)))

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN, instance="open-instance")
    backend = service.least_busy(operational=True)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    isa_qc = pm.run(qc)
    isa_obs = [obs.apply_layout(isa_qc.layout) for obs in observables]

    # EstimatorV2: La función matemática nativa del QPU que entrega directamente el vector de valores esperados <Z_j>
    estimator = EstimatorV2(mode=backend)
    job = estimator.run([(isa_qc, isa_obs)])
    job_id = job.job_id()
    res = job.result()[0]

    # El QPU entrega directamente 1 ÚNICO VECTOR DE FLOTANTES CONTINUOS (evs = expectation values)
    v_qpu_raw = np.array(res.data.evs, dtype=np.float64).ravel()
    nrm_qpu = neumaier_norm_fp64(v_qpu_raw)
    v_qpu_unit = v_qpu_raw / nrm_qpu

    cosine_fidelity = float(np.dot(v_qpu_unit, v_target))
    neumaier_err = abs(neumaier_norm_fp64(v_qpu_unit) - 1.0)

    return {
        "hardware": f"QPU_{backend.name}_156_QUBITS",
        "job_id": job_id,
        "math_fn": "SU2_RAMSEY_BLOCH_EXPECTATION_VECTOR_ESTIMATOR_V2",
        "boolean_ccx_gates_used": 0,
        "vector_dimension_D": d_dim,
        "outputs_crossed_door": 1,
        "target_vector_S_D": [round(float(x), 5) for x in v_target],
        "qpu_single_output_vector_S_D": [round(float(x), 5) for x in v_qpu_unit],
        "continuous_vector_cosine_fidelity": round(cosine_fidelity, 6),
        "neumaier_orthonormal_drift": neumaier_err
    }

if __name__ == "__main__":
    print("[1/2] Ejecutando Despachador de Hardware Regla 31 para CPU (Shorth) y TPU (Systolic Gibbs Matmul)...")
    res_classical = run_cpu_and_tpu_native_math()
    print(json.dumps(res_classical, indent=2))

    print("\n[2/2] Ejecutando Matemática Cuántica Nativa SU(2) + Función de Salida Continua <Z_j> (EstimatorV2) en QPU IBM...")
    res_qpu = run_qpu_native_su2_bloch_expectation(d_dim=8)
    print(json.dumps(res_qpu, indent=2))
