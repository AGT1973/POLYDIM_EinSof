import json
import psycopg
from qiskit_ibm_runtime import QiskitRuntimeService

conn = psycopg.connect('dbname=polydim_active_db user=postgres host=localhost port=5432')
cur = conn.cursor()
cur.execute("SELECT value FROM active_vault WHERE key_name = 'ibm_quantum_api_key' LIMIT 1;")
ibm_token = cur.fetchone()[0].strip()
conn.close()

service = QiskitRuntimeService(channel="ibm_quantum_platform", token=ibm_token, instance="open-instance")
job_id = "dbl2gk5gg49c73djtgt0"
job = service.job(job_id)
status = job.status()
print(f"=== ESTADO DEL JOB 16 QUBITS EN IBM MARRAKESH ({job_id}) ===")
print(f"Status actual: {status}")
print(f"Backend: {job.backend().name}")
print(f"Creacion: {job.creation_date}")

if status == "DONE" or getattr(status, "name", "") == "DONE":
    result = job.result()
    print("\n[RESULTADOS FISICOS RECUPERADOS DEL CHIP CUANTICO 16Q]")
    
    # P8: Kitaev Majorana 16Q
    pub0 = result[0]
    ev0 = float(pub0.data.evs)
    std0 = float(pub0.data.stds)
    print(f"\n1. CADENA KITAEV / MAJORANA (16 Qubits - D=65.536):")
    print(f"   Expectacion experimental <P_Majorana> = {ev0:.6f} +/- {std0:.6f}")
    
    # P9: GHZ Macroscópico 16Q
    pub1 = result[1]
    ev1 = float(pub1.data.evs)
    std1 = float(pub1.data.stds)
    print(f"\n2. ESTADO GHZ MACROSCOPICO (16 Qubits - D=65.536):")
    print(f"   Coherencia y Fidelidad <O_GHZ> = {ev1:.6f} +/- {std1:.6f}")
    
    # P10: Heisenberg XXX 16Q
    pub2 = result[2]
    ev2 = float(pub2.data.evs)
    std2 = float(pub2.data.stds)
    print(f"\n3. CADENA DE HEISENBERG CUANTICA XXX (16 Qubits - D=65.536):")
    print(f"   Energia de intercambio media <H_XXX> = {ev2:.6f} +/- {std2:.6f}")
    
    # Guardar en base de datos
    conn_vec = psycopg.connect('dbname=polydim_vec_db user=postgres host=localhost port=5432')
    cur_vec = conn_vec.cursor()
    cur_vec.execute("""
        INSERT INTO session_context (conversation_id, summary, category, created_at)
        VALUES (%s, %s, %s, NOW());
    """, (
        "6ffd5d25-4c7f-4425-8485-49e01b63fa05",
        json.dumps({
            "job_id": job_id,
            "backend": "ibm_marrakesh",
            "qubits": 16,
            "hilbert_dim": 65536,
            "kitaev_majorana_16q": ev0,
            "kitaev_std": std0,
            "ghz_macroscopic_16q": ev1,
            "ghz_std": std1,
            "heisenberg_xxx_16q": ev2,
            "heisenberg_std": std2,
            "total_shots": 30000,
            "status": "DONE"
        }),
        "REAL_QPU_SILICON_16QUBIT_EXECUTION_COMPLETED"
    ))
    conn_vec.commit()
    conn_vec.close()
    print("\n[OK] Resultados 16Q persistidos en PostgreSQL 16 (polydim_vec_db).")
