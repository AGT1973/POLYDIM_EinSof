# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF: PRUEBA FÍSICA EN IBM QUANTUM (156 QUBITS)
PROGRAMACIÓN DEL FILTRO MATEMÁTICO TURING-EINSOF 100% ADENTRO DEL QPU (CERO PROCESADOR EXTERNO).

Demostración:
1. Los T Turings cuánticos (q_turing[0..T-1]) se ejecutan ADENTRO del QPU y JAMÁS se miden ni salen del chip.
2. El cálculo matemático de Moda / Umbral (Quantum Majority / Threshold Network mediante compuertas cuánticas
   reversibles CCX/CX) está programado DENTRO del circuito cuántico del QPU, volcando el estado limpio en
   un único registro de salida (q_puerta_salida).
3. El QPU ejecuta `measure` ÚNICAMENTE sobre `q_puerta_salida` (con shots=1: literalmente 1 SOLA SALIDA física
   cruzando la puerta del QPU hacia afuera, sin ningún cálculo en procesador externo).
"""
import sys
import time
import json
import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

sys.stdout.reconfigure(line_buffering=True)

TOKEN = "x60cHPkursDpOkwQvSO_vxhdGr371QrQQFEP3BW0KrTM"

def build_intra_qpu_einsof_program(d_vector_dim: int = 3) -> QuantumCircuit:
    """
    Programa el cálculo de Turing = 3 por cada coordenada j in [0..d_vector_dim-1]
    100% ADENTRO del QPU usando compuertas cuánticas nativas:
    - Por cada coordenada j del vector (d_vector_dim = 3, estado objetivo verdadero = |111> con perturbación de fase/ruido RX(0.55)):
      * 3 qubits internos de Turing: turing_j[0], turing_j[1], turing_j[2] (NUNCA SE MIDEN, quedan adentro del QPU).
      * 1 qubit de Puerta de Salida: salida[j].
      * Las compuertas cuánticas ADENTRO del QPU calculan la Moda/Umbral (>= 2 de 3 coinciden):
        |salida_j> = QuantumMode(|turing_j[0]>, |turing_j[1]>, |turing_j[2]>)
        usando el operador unitario cuántico de mayoría coherente (CCX + CX) adentro del QPU.
    - Al final, SOLO se mide el registro `salida` (los qubits de Turing jamás salen del QPU).
    """
    q_turing = QuantumRegister(3 * d_vector_dim, "turing_interno_no_medido")
    q_salida = QuantumRegister(d_vector_dim, "unica_salida_puerta")
    c_puerta = ClassicalRegister(d_vector_dim, "puerta_qpu")

    qc = QuantumCircuit(q_turing, q_salida, c_puerta)

    # Ángulo con ruido/incertidumbre individual (~7.5% de probabilidad de error por cada línea individual)
    # P_error_individual = sin^2(0.55 / 2) = 0.0737 (Fidelidad individual = 92.6%)
    # Al aplicar la matemática de Moda/Umbral ADENTRO del QPU sobre 3 Turings:
    # P_error_intra_qpu = 3 * p^2 * (1-p) + p^3 = 0.0155 (Fidelidad teórica sube al ~98.5% adentro del chip!)
    theta_ruido = 0.55

    for j in range(d_vector_dim):
        t0 = q_turing[3 * j + 0]
        t1 = q_turing[3 * j + 1]
        t2 = q_turing[3 * j + 2]
        out_j = q_salida[j]

        # 1. Los 3 Turings internos evalúan el estado |1> con incertidumbre física theta_ruido adentro del QPU
        qc.x(t0)
        qc.rx(theta_ruido, t0)

        qc.x(t1)
        qc.rx(theta_ruido, t1)

        qc.x(t2)
        qc.rx(theta_ruido, t2)

        # 2. MATEMÁTICA DE MODA / UMBRAL PROGRAMADA ADENTRO DEL QPU (Con compuertas cuánticas antes de salir):
        # Ecuación booleana-cuántica reversible de la Moda de 3 estados:
        # Mode(t0, t1, t2) = (t0 AND t1) XOR (t0 AND t2) XOR (t1 AND t2)
        # Implementada con 3 compuertas Toffoli (CCX) directamente sobre el qubit de salida `out_j`:
        qc.ccx(t0, t1, out_j)
        qc.ccx(t0, t2, out_j)
        qc.ccx(t1, t2, out_j)

        # 3. ÚNICAMENTE el qubit `out_j` (ya filtrado y calculado adentro del QPU) cruza la puerta de medición:
        # Los qubits t0, t1, t2 JAMÁS tienen instrucción measure()!
        qc.measure(out_j, c_puerta[j])

    return qc

def build_raw_unfiltered_qpu_program(d_vector_dim: int = 3) -> QuantumCircuit:
    """
    Circuito estándar sin programación de filtro Turing interno:
    Cada qubit sale crudo directamente por la puerta de medición.
    """
    q_raw = QuantumRegister(d_vector_dim, "q_crudo")
    c_raw = ClassicalRegister(d_vector_dim, "puerta_qpu")
    qc = QuantumCircuit(q_raw, c_raw)
    theta_ruido = 0.55
    for j in range(d_vector_dim):
        qc.x(q_raw[j])
        qc.rx(theta_ruido, q_raw[j])
        qc.measure(q_raw[j], c_raw[j])
    return qc

if __name__ == "__main__":
    print("[1/4] Conectando a IBM Quantum Platform...")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN, instance="open-instance")
    backend = service.least_busy(operational=True)
    print(f"    [+] QPU Física Asignada: {backend.name} ({backend.num_qubits} Qubits)")

    qc_einsof_inside = build_intra_qpu_einsof_program(d_vector_dim=3)
    qc_standard_raw = build_raw_unfiltered_qpu_program(d_vector_dim=3)

    print(f"    [+] Circuito Einsof Intra-QPU: {qc_einsof_inside.num_qubits} qubits en chip, pero SOLO {qc_einsof_inside.num_clbits} bits cruzan la puerta de salida.")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    isa_einsof = pm.run(qc_einsof_inside)
    isa_raw = pm.run(qc_standard_raw)

    sampler = SamplerV2(backend)

    # PRUEBA A: Literally 1 SINGLE OUTPUT (shots=1) saliendo por la puerta del QPU con toda la matemática ya hecha adentro!
    print("[2/4] Despachando Job 1: EINSOF CON SHOTS = 1 (Literalmente 1 SOLA SALIDA cruzando la puerta del QPU, 0 cálculo externo)...")
    job_1shot = sampler.run([isa_einsof], shots=1)
    print(f"    [+] Job 1-Shot ID: {job_1shot.job_id()}")

    # PRUEBA B: Comparativa de fidelidad en lote para medir la ganancia física del cálculo interno vs crudo
    print("[3/4] Despachando Job 2: Verificación comparativa en QPU (Einsof Intra-QPU vs Estándar Crudo)...")
    job_cmp = sampler.run([isa_einsof, isa_raw], shots=1024)
    print(f"    [+] Job Comparativo ID: {job_cmp.job_id()}")

    print("[4/4] Esperando respuesta física del procesador cuántico de IBM...")
    res_1shot = job_1shot.result()
    unica_salida_qpu = list(res_1shot[0].data.puerta_qpu.get_counts().keys())[0]

    res_cmp = job_cmp.result()
    counts_einsof = res_cmp[0].data.puerta_qpu.get_counts()
    counts_raw = res_cmp[1].data.puerta_qpu.get_counts()

    report = {
        "exit_code": 0,
        "qpu_hardware": backend.name,
        "qpu_total_qubits": backend.num_qubits,
        "job_id_1_unica_salida": job_1shot.job_id(),
        "job_id_comparativa": job_cmp.job_id(),
        "arquitectura_einsof_dentro_del_qpu": {
            "qubits_turing_internos_no_medidos": 9,
            "qubits_que_cruzan_la_puerta": 3,
            "cantidad_de_salidas_en_job_1shot": 1,
            "unica_salida_recibida_de_la_puerta_qpu": unica_salida_qpu,
            "calculos_en_procesador_externo": "CERO (0 operaciones externas; moda calculada por compuertas CCX adentro del QPU)",
            "respuesta_objetivo_correcta": "111"
        },
        "verificacion_estadistica_1024_disparos": {
            "fidelidad_estandar_sin_turing_interno": round(counts_raw.get("111", 0) / 1024.0, 5),
            "fidelidad_einsof_con_moda_dentro_del_qpu": round(counts_einsof.get("111", 0) / 1024.0, 5),
            "conteos_einsof_intra_qpu": counts_einsof,
            "conteos_estandar_crudo": counts_raw
        }
    }
    print("\n=== RESULTADO OFICIAL IBM QUANTUM: MATEMÁTICA PROGRAMADA ADENTRO DEL QPU ===")
    print(json.dumps(report, indent=2))
    with open(r"e:\POLYDIM_EINSOF\benchmarks\prueba_ibm_dentro_del_qpu.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
