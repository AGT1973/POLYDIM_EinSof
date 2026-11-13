"""
EXPERIMENTO REAL: DESIGUALDAD DE MERMIN N=5 CON 16 CORRELADORES COMPLETOS
=========================================================================
Preparación del estado GHZ genuino de 5 qubits en QPU física de IBM
y verificación de entrelazamiento cuántico genuino multipartito
mediante la desigualdad de Mermin para N=5.

Desigualdad de Mermin para N=5 qubits:
  M_5 = suma con signos de los 16 correladores con número impar de Y's.
  Los correladores con número par de Y's son 0 por simetría del GHZ.
  
  Correladores con 1 Y (C(5,1) = 5): signo -1
    XXYXX, XYXXX, YXXXX, XXXXY, XXXYX -> pero con la convención de Mermin:
    signo = (-1)^((n_Y - 1)/2) para n_Y impar
    n_Y=1: signo = (-1)^0 = +1 ... no, vamos a la fórmula correcta.

  Fórmula de Mermin recursiva:
    M_1 = X
    M_2 = XX - YY  (pero esto se usa en CHSH, no Mermin directo)
    
  Para N impar, la desigualdad de Mermin es:
    M_N = Real[ (X + iY)^⊗N ]
    
  Para N=5:
    (X + iY)^⊗5 expandido, tomando parte real:
    Correladores con n_Y Y's contribuyen con cos(n_Y * π/2):
    - n_Y=0: cos(0) = 1      -> +⟨XXXXX⟩
    - n_Y=1: cos(π/2) = 0    -> no contribuye
    - n_Y=2: cos(π) = -1     -> -⟨XXYY⟩ y todas las permutaciones
    - n_Y=3: cos(3π/2) = 0   -> no contribuye
    - n_Y=4: cos(2π) = 1     -> +⟨XYYYY⟩ y todas las permutaciones
    - n_Y=5: cos(5π/2) = 0   -> no contribuye
    
  Pero esto da la parte REAL. Para la desigualdad de Mermin óptima
  para GHZ con N impar, se usa la parte IMAGINARIA:
    M_N = Im[ (X + iY)^⊗N ] (que maximiza con GHZ)
    
  Contribuciones de Im[(X+iY)^⊗5]:
    - n_Y=0: sin(0) = 0
    - n_Y=1: sin(π/2) = 1    -> +⟨ todas C(5,1)=5 permutaciones ⟩
    - n_Y=2: sin(π) = 0
    - n_Y=3: sin(3π/2) = -1  -> -⟨ todas C(5,3)=10 permutaciones ⟩
    - n_Y=4: sin(2π) = 0
    - n_Y=5: sin(5π/2) = 1   -> +⟨YYYYY⟩

  Total: 5 + 10 + 1 = 16 correladores con signo.
  
  M_5 = Σ_{bases con 1 Y} ⟨base⟩ - Σ_{bases con 3 Y's} ⟨base⟩ + ⟨YYYYY⟩
  
  Cota clásica (LHV):   |M_5| ≤ 4
  Valor cuántico ideal:  M_5 = 16 (para GHZ de 5 qubits)

Referencia: Mermin, N.D. (1990) PRL 65, 1838.
            Werner & Wolf (2001) PRA 64, 032112.

Autor: Ariel García Traba (Independent Research / EinsofOS)
"""

import sys
import time
import json
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import psycopg2


def get_ibm_token():
    """Lee el token de IBM desde PostgreSQL 16 (active_vault)."""
    conn = psycopg2.connect(
        dbname='polydim_active_db', user='postgres',
        password='postgres', host='localhost', port=5432
    )
    cur = conn.cursor()
    cur.execute("SELECT value FROM active_vault WHERE key_name = 'ibm_quantum_api_key'")
    token = cur.fetchone()[0]
    cur.close()
    conn.close()
    return token


def generate_mermin_5q_bases():
    """
    Genera las 16 bases de medición para la desigualdad de Mermin N=5.
    
    M_5 = Im[(X + iY)^⊗5]
    
    Contribuyen los términos con n_Y impar:
    - n_Y=1: 5 bases, signo +1     [sin(π/2) = +1]
    - n_Y=3: 10 bases, signo -1    [sin(3π/2) = -1]
    - n_Y=5: 1 base, signo +1      [sin(5π/2) = +1]
    
    Total: 16 bases con sus signos.
    """
    bases_with_signs = []
    n = 5
    positions = list(range(n))
    
    # n_Y = 1: C(5,1) = 5 bases, sign = +1
    for y_positions in combinations(positions, 1):
        basis = ['X'] * n
        for p in y_positions:
            basis[p] = 'Y'
        bases_with_signs.append((tuple(basis), +1))
    
    # n_Y = 3: C(5,3) = 10 bases, sign = -1
    for y_positions in combinations(positions, 3):
        basis = ['X'] * n
        for p in y_positions:
            basis[p] = 'Y'
        bases_with_signs.append((tuple(basis), -1))
    
    # n_Y = 5: C(5,5) = 1 base, sign = +1
    bases_with_signs.append((('Y', 'Y', 'Y', 'Y', 'Y'), +1))
    
    return bases_with_signs


def create_ghz_and_measure(n_qubits, bases):
    """
    Crea un circuito que:
    1. Prepara el estado GHZ: (|00...0⟩ + |11...1⟩) / √2
    2. Rota a la base de medición indicada (X o Y por qubit)
    3. Mide todos los qubits
    """
    qc = QuantumCircuit(n_qubits)

    # Paso 1: Preparar GHZ
    qc.h(0)
    for i in range(1, n_qubits):
        qc.cx(0, i)

    qc.barrier()

    # Paso 2: Rotar a la base de medición
    for q, basis in enumerate(bases):
        if basis == 'X':
            qc.h(q)
        elif basis == 'Y':
            qc.sdg(q)
            qc.h(q)

    # Paso 3: Medir
    qc.measure_all()
    return qc


def compute_correlator(counts, n_qubits):
    """
    Calcula ⟨O_1 ⊗ O_2 ⊗ ... ⊗ O_N⟩.
    Cada bit b_i → eigenvalue (-1)^b_i.
    Correlador = promedio de (-1)^(paridad del bitstring).
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0

    expectation = 0.0
    for bitstring, count in counts.items():
        bits = bitstring.replace(' ', '')
        parity = bits.count('1') % 2
        expectation += count * ((-1) ** parity)

    return expectation / total


def run_ideal_simulation(bases_with_signs, shots):
    """Simulación ideal (sin ruido) como referencia teórica."""
    from qiskit.primitives import StatevectorSampler
    
    print(f"\n--- Simulación ideal (sin ruido, {shots} shots) ---")
    
    sampler = StatevectorSampler(seed=42)
    n_qubits = 5
    
    circuits = [create_ghz_and_measure(n_qubits, bases) 
                for bases, sign in bases_with_signs]
    pubs = [(circ,) for circ in circuits]
    job = sampler.run(pubs, shots=shots)
    result = job.result()
    
    ideal_correlators = {}
    m5_ideal = 0.0
    
    for i, (bases, sign) in enumerate(bases_with_signs):
        label = ''.join(bases)
        counts = result[i].data.meas.get_counts()
        corr = compute_correlator(counts, n_qubits)
        ideal_correlators[label] = round(corr, 6)
        contribution = sign * corr
        m5_ideal += contribution
        print(f"    ⟨{label}⟩ = {corr:+.6f}  (sign={sign:+d}, "
              f"contribution={contribution:+.6f})")
    
    print(f"\n    M_5 (ideal) = {m5_ideal:.4f}  (teórico = 16.000)")
    return ideal_correlators, round(m5_ideal, 6)


def run_real_qpu(bases_with_signs, shots, backend_name="ibm_marrakesh"):
    """Envía los 16 circuitos al QPU real de IBM."""
    n_qubits = 5
    
    print(f"\n--- Ejecución REAL en QPU físico de IBM ---")
    
    # 1. Conectar a IBM
    token = get_ibm_token()
    print("[1/5] Conectando a IBM Quantum Platform...")
    
    service = QiskitRuntimeService(
        channel="ibm_quantum_platform",
        token=token,
        instance="open-instance"
    )
    
    print(f"[2/5] Seleccionando QPU: {backend_name}...")
    backend = service.backend(backend_name)
    status = backend.status()
    print(f"       operational={status.operational}, "
          f"pending_jobs={status.pending_jobs}, "
          f"total_qubits={backend.num_qubits}")
    
    if not status.operational:
        print(f"       {backend_name} no operacional, buscando alternativa...")
        for b in service.backends():
            s = b.status()
            if s.operational and b.num_qubits >= n_qubits:
                backend = b
                backend_name = b.name
                print(f"       Usando: {backend_name} ({b.num_qubits}Q)")
                break
        else:
            raise RuntimeError("No hay backend operacional disponible.")
    
    # 2. Crear circuitos
    print(f"[3/5] Creando {len(bases_with_signs)} circuitos GHZ(5) "
          f"+ medición Mermin...")
    circuits = []
    labels = []
    signs = []
    for bases, sign in bases_with_signs:
        circuits.append(create_ghz_and_measure(n_qubits, bases))
        labels.append(''.join(bases))
        signs.append(sign)
    
    # 3. Transpilar para hardware real
    print("[4/5] Transpilando para topología física del chip...")
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
    transpiled = pm.run(circuits)
    
    total_2q = 0
    for i, tc in enumerate(transpiled):
        ops = tc.count_ops()
        ecr_count = sum(v for k, v in ops.items() 
                       if k in ['ecr', 'cx', 'cz', 'rzz'])
        total_2q += ecr_count
        if i < 3 or i == len(transpiled) - 1:
            print(f"       [{i:2d}] '{labels[i]}': depth={tc.depth()}, "
                  f"2Q_gates={ecr_count}")
        elif i == 3:
            print(f"       ... ({len(transpiled) - 4} circuitos más) ...")
    
    print(f"       Total 2Q gates en batch: {total_2q}")
    
    # 4. Enviar al QPU real
    print(f"[5/5] Enviando {len(transpiled)} circuitos al QPU real "
          f"({shots} shots cada uno)...")
    sampler = SamplerV2(mode=backend)
    pubs = [(tc,) for tc in transpiled]
    job = sampler.run(pubs, shots=shots)
    job_id = job.job_id()
    ibm_url = f"https://quantum.ibm.com/jobs/{job_id}"
    
    print(f"       Job ID:  {job_id}")
    print(f"       URL IBM: {ibm_url}")
    print(f"       Esperando resultados del QPU físico...")
    
    result = job.result()
    print(f"       ¡Resultados recibidos!")
    
    # 5. Analizar resultados físicos
    print(f"\n{'='*70}")
    print("RESULTADOS FÍSICOS: 16 CORRELADORES DE MERMIN (N=5)")
    print(f"{'='*70}")
    print(f"{'#':>3} | {'Base':>7} | {'n_Y':>3} | {'Signo':>5} | "
          f"{'⟨base⟩':>10} | {'Contribución':>12}")
    print("-" * 70)
    
    correlators = {}
    details = {}
    m5_qpu = 0.0
    
    for i, (label, sign) in enumerate(zip(labels, signs)):
        counts = result[i].data.meas.get_counts()
        corr = compute_correlator(counts, n_qubits)
        contribution = sign * corr
        m5_qpu += contribution
        n_y = label.count('Y')
        
        correlators[label] = round(corr, 6)
        
        top = dict(sorted(counts.items(), key=lambda x: -x[1])[:4])
        details[label] = {
            "correlator_measured": round(corr, 6),
            "mermin_sign": sign,
            "contribution": round(contribution, 6),
            "n_Y": n_y,
            "top_bitstrings": top,
            "total_counts": sum(counts.values())
        }
        
        print(f"{i+1:3d} | {label:>7} | {n_y:3d} | {sign:+5d} | "
              f"{corr:+10.6f} | {contribution:+12.6f}")
    
    m5_qpu = round(m5_qpu, 6)
    
    # Desglose por categoría de n_Y
    print(f"\n--- Desglose por número de Y's ---")
    for n_y_target, expected_sign, count_expected in [(1, +1, 5), (3, -1, 10), (5, +1, 1)]:
        subset = [(l, d) for l, d in details.items() if d["n_Y"] == n_y_target]
        sum_contrib = sum(d["contribution"] for _, d in subset)
        avg_corr = np.mean([abs(d["correlator_measured"]) for _, d in subset])
        print(f"    n_Y={n_y_target}: {len(subset)} correladores, "
              f"signo={expected_sign:+d}, "
              f"⟨|corr|⟩_avg = {avg_corr:.4f}, "
              f"suma contribuciones = {sum_contrib:+.4f}")
    
    # Resultado final
    print(f"\n{'='*70}")
    print(f"  RESULTADO DESIGUALDAD DE MERMIN N=5")
    print(f"{'='*70}")
    print(f"  M_5 (QPU real)     = {m5_qpu:+.4f}")
    print(f"  Cota clásica (LHV) = 4.0000")
    print(f"  Valor cuántico ideal = 16.0000")
    
    violation = abs(m5_qpu) > 4.0
    ratio = m5_qpu / 16.0 if m5_qpu != 0 else 0.0
    sigma_violation = (abs(m5_qpu) - 4.0) / (4.0 / np.sqrt(shots))
    
    print(f"  Ratio real/ideal   = {ratio:.4f} ({ratio*100:.1f}%)")
    print(f"  VIOLACIÓN:           {'SÍ ✓' if violation else 'NO ✗'}")
    if violation:
        print(f"  → Evidencia física de entrelazamiento cuántico "
              f"genuino 5-partito.")
        print(f"  → Excede la cota clásica por "
              f"{abs(m5_qpu) - 4.0:.4f} unidades.")
    else:
        print(f"  → La decoherencia del chip impidió una violación clara.")
        print(f"  → M_5/M_classical = {abs(m5_qpu)/4.0:.4f}")
    
    return {
        "backend_name": backend_name,
        "backend_qubits": backend.num_qubits,
        "job_id": job_id,
        "job_url": ibm_url,
        "n_qubits": n_qubits,
        "n_correlators": len(correlators),
        "correlators": correlators,
        "details": details,
        "mermin_value": m5_qpu,
        "classical_bound": 4.0,
        "quantum_ideal": 16.0,
        "violation": violation,
        "ratio_real_over_ideal": round(ratio, 6)
    }


def main():
    t0 = time.perf_counter()
    shots = 4000
    
    print("=" * 70)
    print("EXPERIMENTO REAL: MERMIN N=5 — 16 CORRELADORES COMPLETOS")
    print("=" * 70)
    print(f"Estado: GHZ de 5 qubits")
    print(f"Mediciones: {shots} shots por circuito")
    print(f"Circuitos: 16 (todos los correladores con n_Y impar)")
    print(f"Desigualdad: M_5 = Im[(X+iY)^⊗5]")
    print(f"Cota clásica: |M_5| ≤ 4")
    print(f"Valor cuántico ideal: M_5 = 16")
    print(f"Referencia: Mermin (1990) PRL 65, 1838")
    
    # Generar las 16 bases
    bases_with_signs = generate_mermin_5q_bases()
    print(f"\nBases generadas: {len(bases_with_signs)}")
    for bases, sign in bases_with_signs:
        label = ''.join(bases)
        n_y = label.count('Y')
        print(f"    {label}  n_Y={n_y}  sign={sign:+d}")
    
    # Paso A: Simulación ideal (referencia)
    ideal_corr, ideal_m5 = run_ideal_simulation(bases_with_signs, shots)
    
    # Paso B: Ejecución en QPU real
    backend_target = sys.argv[1] if len(sys.argv) > 1 else "ibm_fez"
    qpu_result = run_real_qpu(bases_with_signs, shots, 
                               backend_name=backend_target)
    
    t1 = time.perf_counter()
    
    # Compilar reporte final
    report = {
        "experiment_type": "REAL_QUANTUM_PHYSICS_MEASUREMENT",
        "title": "Full Mermin Inequality N=5 (16 Correlators) on Physical QPU",
        "description": (
            "Complete measurement of the Mermin inequality for 5-qubit GHZ "
            "state using all 16 correlators (terms with odd number of Y "
            "measurements). M_5 = Im[(X+iY)^⊗5]. A violation |M_5| > 4 "
            "constitutes physical evidence of genuine 5-partite quantum "
            "entanglement that CANNOT be explained by any local hidden "
            "variable theory."
        ),
        "references": [
            "Mermin, N.D. (1990) PRL 65, 1838",
            "Werner, R.F. & Wolf, M.M. (2001) PRA 64, 032112",
            "Gühne, O. & Tóth, G. (2009) Physics Reports 474, 1-75"
        ],
        "ghz_qubits": 5,
        "total_correlators": 16,
        "shots_per_circuit": shots,
        "total_shots": shots * 16,
        "ideal_simulation": {
            "correlators": ideal_corr,
            "mermin_value": ideal_m5,
            "note": "Simulación local sin ruido como referencia teórica"
        },
        "physical_qpu": qpu_result,
        "comparison": {
            "ideal_mermin": ideal_m5,
            "physical_mermin": qpu_result["mermin_value"],
            "decoherence_loss": round(ideal_m5 - qpu_result["mermin_value"], 4),
            "fidelity_ratio": qpu_result["ratio_real_over_ideal"]
        },
        "previous_experiments": {
            "mermin_3q": {
                "job_id": "dbm99558ft8s738ueesg",
                "url": "https://quantum.ibm.com/jobs/dbm99558ft8s738ueesg",
                "result": "M_3 = 3.656, violation YES"
            },
            "ghz_scaling": {
                "job_id": "dbm9glpkbkrc73cp3igg",
                "url": "https://quantum.ibm.com/jobs/dbm9glpkbkrc73cp3igg",
                "result": "Entanglement confirmed at 3Q (F=0.94), 5Q (F=0.83)"
            }
        },
        "total_experiment_time_seconds": round(t1 - t0, 2)
    }
    
    # Persistir en PostgreSQL 16
    try:
        conn = psycopg2.connect(
            dbname='polydim_vec_db', user='postgres',
            password='postgres', host='localhost', port=5432
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO session_context (conversation_id, summary, category, created_at)
            VALUES (%s, %s, %s, NOW())
        """, ('a9c79c56-9fe9-42ad-bb67-80d40e88c44e',
              json.dumps(report), 'REAL_QPU_MERMIN_5Q_FULL_16_CORRELATORS'))
        conn.commit()
        cur.close()
        conn.close()
        print("\n[DB] Persistido en PostgreSQL 16 (session_context).")
    except Exception as e:
        print(f"\n[DB WARN] Error al persistir: {e}")
    
    print("\n=== LINKS DE VERIFICACIÓN EN IBM QUANTUM ===")
    print(f"Mermin 3Q (anterior):      https://quantum.ibm.com/jobs/dbm99558ft8s738ueesg")
    print(f"GHZ Scaling (anterior):    https://quantum.ibm.com/jobs/dbm9glpkbkrc73cp3igg")
    print(f"Mermin 5Q Full (este):     {qpu_result['job_url']}")
    print(f"Dashboard IBM:             https://quantum.ibm.com")
    
    print("\n=== REPORTE FINAL ===")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
