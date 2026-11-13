import psycopg2
from qiskit_ibm_runtime import QiskitRuntimeService

conn = psycopg2.connect(
    dbname='polydim_active_db', user='postgres',
    password='postgres', host='localhost', port=5432
)
cur = conn.cursor()
cur.execute("SELECT value FROM active_vault WHERE key_name = 'ibm_quantum_api_key'")
token = cur.fetchone()[0]
conn.close()

service = QiskitRuntimeService(channel='ibm_quantum_platform', token=token, instance='open-instance')
print("=== ESTADO DE COLAS EN QPUs ===")
for b in service.backends():
    st = b.status()
    print(f"{b.name:20} | {b.num_qubits:3}Q | Operacional: {st.operational!s:5} | Cola: {st.pending_jobs:3d}")
