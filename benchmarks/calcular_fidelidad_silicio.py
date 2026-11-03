import json
import psycopg
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

print("=== COMPUTO DE SOLUCIONES EXACTAS CLASICAS (GROUND TRUTH TEORICO) ===")

# =========================================================================
# BATERIA 1: PROBLEMAS REALES (2Q y 4Q)
# =========================================================================
# Problema 1: H2 Molecular VQE (2 Qubits)
qc_h2 = QuantumCircuit(2)
qc_h2.ry(0.68, 0)
qc_h2.cx(0, 1)
h2_ham = SparsePauliOp.from_list([
    ("IZ", 0.397935),
    ("ZI", -0.397935),
    ("ZZ", -0.011280),
    ("XX", 0.180931)
])
sv_h2 = Statevector.from_instruction(qc_h2)
exp_h2_elec = float(sv_h2.expectation_value(h2_ham).real)
exp_h2_total = -1.052373 + exp_h2_elec

# Problema 2: Ising TFIM (4 Qubits)
qc_ising = QuantumCircuit(4)
for i in range(4):
    qc_ising.ry(np.pi / 4, i)
for i in range(3):
    qc_ising.cx(i, i + 1)
ising_ham = SparsePauliOp.from_list([
    ("ZZII", -1.0),
    ("IZZI", -1.0),
    ("IIZZ", -1.0),
    ("XIII", -0.8),
    ("IXII", -0.8),
    ("IIXI", -0.8),
    ("IIIX", -0.8)
])
sv_ising = Statevector.from_instruction(qc_ising)
exp_ising = float(sv_ising.expectation_value(ising_ham).real)

# Problema 3: QAOA MaxCut (4 Qubits)
qc_qaoa = QuantumCircuit(4)
qc_qaoa.h(range(4))
gamma, beta = 0.45, 0.35
for i in range(4):
    for j in range(i + 1, 4):
        qc_qaoa.cx(i, j)
        qc_qaoa.rz(2 * gamma, j)
        qc_qaoa.cx(i, j)
qc_qaoa.rx(2 * beta, range(4))
maxcut_obs = SparsePauliOp.from_list([
    ("ZZII", 0.5),
    ("ZIZI", 0.5),
    ("ZIIZ", 0.5),
    ("IZZI", 0.5),
    ("IZIZ", 0.5),
    ("IIZZ", 0.5)
])
sv_qaoa = Statevector.from_instruction(qc_qaoa)
exp_maxcut = float(sv_qaoa.expectation_value(maxcut_obs).real)

# =========================================================================
# BATERIA 2: ALTA DIMENSION (8 Qubits - D=256)
# =========================================================================
n8 = 8
# Problema 4: GHZ 8Q
qc_ghz8 = QuantumCircuit(n8)
qc_ghz8.h(0)
for i in range(n8 - 1):
    qc_ghz8.cx(i, i + 1)
obs_ghz8 = SparsePauliOp.from_list([
    ("Z" * n8, 0.5),
    ("X" * n8, 0.5)
])
sv_ghz8 = Statevector.from_instruction(qc_ghz8)
exp_ghz8 = float(sv_ghz8.expectation_value(obs_ghz8).real)

# Problema 5: Modelo XY Anillo 8Q
qc_xy8 = QuantumCircuit(n8)
for i in range(n8):
    qc_xy8.ry(0.5236 * (i + 1), i)
for i in range(n8):
    qc_xy8.cx(i, (i + 1) % n8)
    qc_xy8.rz(0.4, (i + 1) % n8)
    qc_xy8.cx(i, (i + 1) % n8)
xy_terms = []
for i in range(n8):
    j = (i + 1) % n8
    s_x = ["I"] * n8; s_x[i] = "X"; s_x[j] = "X"; xy_terms.append(("".join(s_x), 0.5))
    s_y = ["I"] * n8; s_y[i] = "Y"; s_y[j] = "Y"; xy_terms.append(("".join(s_y), 0.5))
    s_z = ["I"] * n8; s_z[i] = "Z"; xy_terms.append(("".join(s_z), 0.2))
obs_xy8 = SparsePauliOp.from_list(xy_terms)
sv_xy8 = Statevector.from_instruction(qc_xy8)
exp_xy8 = float(sv_xy8.expectation_value(obs_xy8).real)

# Problema 6: Cluster Topológico 8Q
qc_cl8 = QuantumCircuit(n8)
qc_cl8.h(range(n8))
for i in range(n8 - 1):
    qc_cl8.cz(i, i + 1)
cluster_terms = []
for i in range(1, n8 - 1):
    s = ["I"] * n8; s[i - 1] = "X"; s[i] = "Z"; s[i + 1] = "X"
    cluster_terms.append(("".join(s), 1.0 / (n8 - 2)))
obs_cl8 = SparsePauliOp.from_list(cluster_terms)
sv_cl8 = Statevector.from_instruction(qc_cl8)
exp_cl8 = float(sv_cl8.expectation_value(obs_cl8).real)

# =========================================================================
# BATERIA 3: ALTA DIMENSION 16 QUBITS (D=65.536)
# =========================================================================
n16 = 16
# Problema 8: Kitaev / Majorana 16Q
qc_kit16 = QuantumCircuit(n16)
for i in range(n16):
    qc_kit16.ry(np.pi / 4.0, i)
for i in range(n16 - 1):
    qc_kit16.cz(i, i + 1)
for i in range(0, n16 - 1, 2):
    qc_kit16.cx(i, i + 1)
obs_kit16 = SparsePauliOp.from_list([
    ("Z" * n16, 0.5),
    ("X" + ("Z" * (n16 - 2)) + "X", 0.5)
])
sv_kit16 = Statevector.from_instruction(qc_kit16)
exp_kit16 = float(sv_kit16.expectation_value(obs_kit16).real)

# Problema 9: GHZ Macroscópico 16Q
qc_ghz16 = QuantumCircuit(n16)
qc_ghz16.h(0)
for i in range(n16 - 1):
    qc_ghz16.cx(i, i + 1)
obs_ghz16 = SparsePauliOp.from_list([
    ("Z" * n16, 0.5),
    ("X" * n16, 0.5)
])
sv_ghz16 = Statevector.from_instruction(qc_ghz16)
exp_ghz16 = float(sv_ghz16.expectation_value(obs_ghz16).real)

# Problema 10: Heisenberg XXX 16Q
qc_heis16 = QuantumCircuit(n16)
for i in range(n16):
    qc_heis16.ry(0.3 * (i + 1), i)
for i in range(n16 - 1):
    qc_heis16.cx(i, i + 1)
    qc_heis16.rz(0.45, i + 1)
    qc_heis16.cx(i, i + 1)
heis_terms = []
num_links = n16 - 1
norm_factor = 1.0 / num_links
for i in range(num_links):
    j = i + 1
    for pauli in ["X", "Y", "Z"]:
        s = ["I"] * n16; s[i] = pauli; s[j] = pauli
        heis_terms.append(("".join(s), norm_factor))
obs_heis16 = SparsePauliOp.from_list(heis_terms)
sv_heis16 = Statevector.from_instruction(qc_heis16)
exp_heis16 = float(sv_heis16.expectation_value(obs_heis16).real)

# Resultados consolidados
exact_results = {
    "P1_H2_elec": exp_h2_elec,
    "P1_H2_total": exp_h2_total,
    "P2_Ising_TFIM": exp_ising,
    "P3_QAOA_MaxCut": exp_maxcut,
    "P4_GHZ_8Q": exp_ghz8,
    "P5_XY_Ring_8Q": exp_xy8,
    "P6_Cluster_8Q": exp_cl8,
    "P8_Kitaev_16Q": exp_kit16,
    "P9_GHZ_16Q": exp_ghz16,
    "P10_Heisenberg_16Q": exp_heis16
}

print("\n--- VALORES TEORICOS EXACTOS (STATEVECTOR PURO EN HOST) ---")
for k, v in exact_results.items():
    print(f" {k:<20} = {v:+.6f}")

with open("exact_solutions_qpu.json", "w") as f:
    json.dump(exact_results, f, indent=2)
print("\n[OK] Guardado en exact_solutions_qpu.json")
