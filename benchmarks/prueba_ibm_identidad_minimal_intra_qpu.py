# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF: IDENTIDAD CUÁNTICA MINIMAL DE MODA INTRA-QPU (1 SOLA COMPUERTA CCX POR CAMPO)
Identidad algebraica en GF(2) dentro del QPU:
  CNOT(t0, t1); CNOT(t0, t2); CCX(t1, t2, t0)
  ==> t0 = t0 XOR ((t0 XOR t1) AND (t0 XOR t2)) = (t0 AND t1) XOR (t0 AND t2) XOR (t1 AND t2) = Moda(t0, t1, t2)
Reduce en 66% las compuertas cuánticas y elimina el registro ancilla extra.
"""
import sys
import json
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

sys.stdout.reconfigure(line_buffering=True)
TOKEN = "x60cHPkursDpOkwQvSO_vxhdGr371QrQQFEP3BW0KrTM"

def build_minimal_intra_qpu_einsof(d_dim: int = 3, theta_err: float = 0.85) -> QuantumCircuit:
    q_turing = QuantumRegister(3 * d_dim, "turing_qpu")
    c_puerta = ClassicalRegister(d_dim, "unica_puerta")
    qc = QuantumCircuit(q_turing, c_puerta)

    for j in range(d_dim):
        t0 = q_turing[3 * j + 0]
        t1 = q_turing[3 * j + 1]
        t2 = q_turing[3 * j + 2]

        # 3 Turings internos con error físico individual theta_err
        for tq in (t0, t1, t2):
            qc.x(tq)
            qc.rx(theta_err, tq)

        # Identidad Cuántica Minimal de Moda ADENTRO del QPU (2 CX + 1 sola CCX):
        # t1 y t2 quedan adentro sin medirse; t0 sale por la puerta con la Moda exacta!
        qc.cx(t0, t1)
        qc.cx(t0, t2)
        qc.ccx(t1, t2, t0)

        # Solo se mide t0 (que ya contiene la Moda de los 3 Turings)
        qc.measure(t0, c_puerta[j])
    return qc

def build_raw_qpu(d_dim: int = 3, theta_err: float = 0.85) -> QuantumCircuit:
    q = QuantumRegister(d_dim, "raw_q")
    c = ClassicalRegister(d_dim, "unica_puerta")
    qc = QuantumCircuit(q, c)
    for j in range(d_dim):
        qc.x(q[j])
        qc.rx(theta_err, q[j])
        qc.measure(q[j], c[j])
    return qc

if __name__ == "__main__":
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN, instance="open-instance")
    backend = service.least_busy(operational=True)

    qc_einsof = build_minimal_intra_qpu_einsof(d_dim=3, theta_err=0.85)
    qc_raw = build_raw_qpu(d_dim=3, theta_err=0.85)

    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    isa_einsof = pm.run(qc_einsof)
    isa_raw = pm.run(qc_raw)

    sampler = SamplerV2(backend)
    job_1 = sampler.run([isa_einsof], shots=1)
    job_cmp = sampler.run([isa_einsof, isa_raw], shots=1024)

    out_1shot = list(job_1.result()[0].data.unica_puerta.get_counts().keys())[0]
    res_cmp = job_cmp.result()
    c_einsof = res_cmp[0].data.unica_puerta.get_counts()
    c_raw = res_cmp[1].data.unica_puerta.get_counts()

    fid_raw = c_raw.get("111", 0) / 1024.0
    fid_einsof = c_einsof.get("111", 0) / 1024.0

    print(json.dumps({
        "exit_code": 0,
        "qpu": backend.name,
        "job_1_shot_id": job_1.job_id(),
        "job_cmp_id": job_cmp.job_id(),
        "unica_salida_1_shot_puerta_qpu": out_1shot,
        "respuesta_correcta_objetivo": "111",
        "fidelidad_cruda_sin_turing_intra_qpu": round(fid_raw, 5),
        "fidelidad_einsof_con_moda_dentro_del_qpu": round(fid_einsof, 5),
        "ganancia_neta_fidelidad_intra_qpu_pct": round((fid_einsof - fid_raw) * 100.0, 2)
    }, indent=2))
