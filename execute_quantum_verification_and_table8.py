import sys
import os
import json
import numpy as np
from datetime import datetime
import psycopg2
from qiskit_ibm_runtime import QiskitRuntimeService

def run_verification():
    print("=" * 70)
    print(" [VERIFICACIÓN PERIÓDICA] TELEMETRÍA DE SILICIO IBM QUANTUM & TABLA 8")
    print("=" * 70)
    
    conn = psycopg2.connect(dbname='polydim_active_db', host='localhost', port=5432, user='postgres', user='postgres')
    cur = conn.cursor()
    cur.execute("SELECT value FROM active_vault WHERE key_name IN ('ibm_quantum_api_token', 'ibm_quantum_token', 'IBM_QUANTUM_TOKEN')")
    row = cur.fetchone()
    token = row[0] if row else None
    conn.close()

    if token:
        service = QiskitRuntimeService(channel='ibm_quantum_platform', token=token)
    else:
        service = QiskitRuntimeService()

    # Exact theoretical ground truths from Thesis Table 8
    # 17: Kissing D5 (16Q): E_exact = -12.0000 (48 contact edges, Stiefel ground state)
    # 18: Equiangular R14 (14Q): E_exact = -7.0000
    # 19: Red E8 S7 (12Q): E_exact = -14.0000
    # 20: ETF Welch R7 (14Q): E_exact = -9.0000
    # 21: Haldane Gap S=1 (8Q): E_exact = -6.1614
    # 22: FeMoco Nitrogenase [Fe4S4] (8Q): E_exact = -44.5637
    
    job_configs = [
        {
            'index': 17,
            'name': 'Kissing Number D5 (Red D5 en S^4)',
            'qubits': 16,
            'backend': 'ibm_kingston',
            'job_id': 'dbo6td8qtr0c73ae38i0',
            'e_exact': -12.0000
        },
        {
            'index': 18,
            'name': 'Líneas Equiangulares en R^14',
            'qubits': 14,
            'backend': 'ibm_kingston',
            'job_id': 'dbo75h0qtr0c73ae3jlg',
            'e_exact': -7.0000
        },
        {
            'index': 19,
            'name': 'Red Excepcional E8 en S^7',
            'qubits': 12,
            'backend': 'ibm_marrakesh',
            'job_id': 'dbo7ieoqtr0c73ae46ng',
            'e_exact': -14.0000
        },
        {
            'index': 20,
            'name': 'ETF Welch Bound en R^7',
            'qubits': 14,
            'backend': 'ibm_fez',
            'job_id': 'dbobv95t7fqc73akrtfg',
            'e_exact': -9.0000
        },
        {
            'index': 21,
            'name': 'Haldane Gap S=1 Chain (Topological String Order)',
            'qubits': 8,
            'backend': 'ibm_fez',
            'job_id': 'dbofnv44148s739svbag',
            'e_exact': -6.161438
        },
        {
            'index': 22,
            'name': 'FeMoco Nitrogenase Active Core [Fe4S4]',
            'qubits': 8,
            'backend': 'ibm_fez',
            'job_id': 'dbog4l5t7fqc7387qg70',
            'e_exact': -44.563714
        }
    ]

    # Check backends status
    print("\n[1/3] Estado de Procesadores Físicos:")
    for b_name in ['ibm_fez', 'ibm_kingston', 'ibm_marrakesh']:
        try:
            b = service.backend(b_name)
            stat = b.status()
            print(f" -> Backend {b_name} ({b.num_qubits}Q): Operational={stat.operational}, Pending Jobs={stat.pending_jobs}, Status='{stat.status_msg}'")
        except Exception as be:
            print(f" -> Backend {b_name} Error: {be}")

    print("\n[2/3] Auditoría de Jobs de la Tesis:")
    completed_jobs = []
    queued_jobs = []
    
    for cfg in job_configs:
        jid = cfg['job_id']
        label = f"Job {cfg['index']}: {cfg['name']} [{cfg['qubits']}Q @ {cfg['backend']}]"
        try:
            job = service.job(jid)
            st_raw = job.status()
            st_name = st_raw.name if hasattr(st_raw, 'name') else str(st_raw).upper()
            created = job.creation_date.isoformat() if hasattr(job, 'creation_date') and job.creation_date else 'N/A'
            
            print(f"\n--- {label} ---")
            print(f"  Job ID:   {jid}")
            print(f"  Estado:   {st_name}")
            print(f"  Creado:   {created}")
            
            if st_name == 'DONE':
                print("  >>> JOB COMPLETADO! Extrayendo datos del procesador cuántico...")
                res = job.result()
                if hasattr(res[0].data, 'evs'):
                    all_evs = []
                    all_stds = []
                    for pub in res:
                        ev = np.array(pub.data.evs)
                        std = np.array(pub.data.stds) if hasattr(pub.data, 'stds') else np.zeros_like(ev)
                        all_evs.extend(ev.flatten().tolist())
                        all_stds.extend(std.flatten().tolist())
                    
                    e_qpu = float(np.sum(all_evs))
                    std_qpu = float(np.sqrt(np.sum(np.array(all_stds)**2))) if len(all_stds) > 0 else 0.0
                    rel_err = abs((e_qpu - cfg['e_exact']) / cfg['e_exact']) * 100.0 if cfg['e_exact'] != 0 else 0.0
                    
                    print(f"  Observables medidos: {len(all_evs)}")
                    print(f"  <E_QPU>:             {e_qpu:+.4f} +/- {std_qpu:.4f}")
                    print(f"  E_exact:             {cfg['e_exact']:+.4f}")
                    print(f"  Error Relativo:      {rel_err:.2f}%")
                    
                    cfg['status'] = 'DONE'
                    cfg['e_qpu'] = e_qpu
                    cfg['std_qpu'] = std_qpu
                    cfg['rel_err'] = rel_err
                elif hasattr(res[0].data, 'meas'):
                    counts = res[0].data.meas.get_counts()
                    top_modes = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"  Sampler Medido (Shots={sum(counts.values())}, Modos={len(counts)}): Top: {top_modes}")
                    cfg['status'] = 'DONE'
                    cfg['sampler_counts'] = counts
                    cfg['top_modes'] = top_modes
                completed_jobs.append(cfg)
            elif st_name == 'RUNNING':
                print("  >>> JOB ESTÁ EJECUTÁNDOSE FÍSICAMENTE EN LA QPU!")
                cfg['status'] = 'RUNNING'
                queued_jobs.append(cfg)
            elif st_name == 'QUEUED':
                print("  >>> Job en cola de espera física.")
                cfg['status'] = 'QUEUED'
                queued_jobs.append(cfg)
            else:
                print(f"  >>> Estado alternativo: {st_name}")
                cfg['status'] = st_name
                queued_jobs.append(cfg)
                
        except Exception as je:
            print(f"  >>> Error inspeccionando job: {je}")
            cfg['status'] = 'ERROR'
            cfg['error'] = str(je)

    total_jobs = len(job_configs)
    print("\n[3/3] Resumen de Ejecución:")
    print(f" -> Jobs completados: {len(completed_jobs)} / {total_jobs}")
    print(f" -> Jobs en cola/ejecución: {len(queued_jobs)} / {total_jobs}")
    
    if len(completed_jobs) > 0:
        print(f"\n>>> Se detectaron {len(completed_jobs)} jobs completados.")
        return completed_jobs
    else:
        print(f"\n>>> Todos los {total_jobs} jobs continúan legalmente en cola en IBM Quantum.")
        print(">>> No hay falsificación de resultados (Corsé Anti-Mentira Gandalf).")
        return []

if __name__ == '__main__':
    completed = run_verification()
    sys.exit(0)
