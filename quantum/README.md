# EinsofOS Quantum & Many-Body Research: Physical IBM QPU Verifications & Audited Manifold Krylov/MPS Benchmarks

**Author / Principal Investigator:** Ariel García Traba  
**Institution / Affiliation:** UTN Faculty / EinsofOS Sovereign Research Initiative  
**Contact:** `Ariel.Garcia.Traba@gmail.com`  
**ORCID:** `0009-0001-2787-6067`  
**Host Machine:** AMD A4-6300 (2 CPU threads, 16 GB DDR3 RAM, 0 Local GPUs)  
**Quantum Hardware:** IBM Quantum Superconducting Processors (`ibm_fez` & `ibm_marrakesh`, 156-Qubit Heron/Eagle Architectures at 15 mK)

---

## 🔬 1. Official IBM Quantum Physical Job Verification (Cryogenic QPU Hardware)

Every physical quantum experiment reported in Section 1 was executed directly on IBM Quantum superconducting dilution cryostats via the IBM Quantum Platform. Third-party researchers can independently inspect the Job IDs below:

| Experiment | QPU Backend | Official IBM Job ID | Physical Measurement | Classical Bound (LHV) | Quantum Ideal | Public Verification Link |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mermin–Ardehali $N=5$ ($S$-Phase Aligned, $\phi=\pi/2$)** | `ibm_fez` (156Q) | `dbmcj2l8mdtc73d7nuqg` | **$M_5 = \mathbf{+13.3640}$** | $\|M_5\| \le 4.0000$ | $16.0000$ | [Verify on IBM Quantum](https://quantum.ibm.com/jobs/dbmcj2l8mdtc73d7nuqg) |
| **Mermin–Ardehali $N=5$ (Unaligned Control, $\phi=0$)** | `ibm_fez` (156Q) | `dbmbbf674qds73ds02jg` | $M_5 = -0.4790 \approx 0$ | $\|M_5\| \le 4.0000$ | $0.0000$ | [Verify on IBM Quantum](https://quantum.ibm.com/jobs/dbmbbf674qds73ds02jg) |
| **Mermin Inequality $N=3$ (GHZ State)** | `ibm_marrakesh` (156Q) | `dbm99558ft8s738ueesg` | **$M_3 = \mathbf{+3.6560}$** | $\|M_3\| \le 2.0000$ | $4.0000$ | [Verify on IBM Quantum](https://quantum.ibm.com/jobs/dbm99558ft8s738ueesg) |
| **GHZ Multipartite Scaling ($N \in \{3..20\}$)** | `ibm_marrakesh` (156Q) | `dbm9glpkbkrc73cp3igg` | $F_{3Q}=0.94, F_{5Q}=0.83, F_{8Q}=0.48$ | $F \le 0.50$ (Biseparable) | $1.0000$ | [Verify on IBM Quantum](https://quantum.ibm.com/jobs/dbm9glpkbkrc73cp3igg) |

### Phase Alignment in 5-Qubit Mermin–Ardehali–Belinskii–Klyshko Tests
Following Mermin (*Phys. Rev. Lett.* **65**, 1838, 1990), Ardehali (*Phys. Rev. A* **46**, 5375, 1992), and Belinskii & Klyshko (*Phys. Usp.* **36**, 653, 1993), the odd-$Y$ 5-qubit Mermin polynomial $M_5 = \operatorname{Im}[(X + iY)^{\otimes 5}]$ evaluated on $|\psi(\phi)\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + e^{i\phi}|11111\rangle)$ satisfies:
$$\langle \psi(\phi) | M_5 | \psi(\phi) \rangle = 16 \sin(\phi)$$
* **Control ($\phi = 0$, canonical real GHZ):** $\langle M_5 \rangle = 16\sin(0) = 0$ (verified experimentally on `ibm_fez`: $M_5 = -0.4790$, Job `dbmbbf674qds73ds02jg`).
* **Phase-aligned ($\phi = \pi/2$, root $S$ gate prior to CNOT fanout):** $\langle M_5 \rangle = +16$ ideal; measured physically on `ibm_fez` across $64,000$ shots ($16 \times 4,000$) at **$M_5 = +13.3640$** ($3.341\times$ above the local-hidden-variable bound of $4.0$, Job `dbmcj2l8mdtc73d7nuqg`).

---

## 💻 2. Audited Classical CPU Solvers: Matrix-Free Stiefel-Lanczos & 2-Site MPS/DMRG

> **Scope & Epistemological Notice (Radical Honesty Contract):** Scripts `04` through `13` are **classical numerical solvers executed on local CPU (`AMD A4-6300`)**, NOT executions on physical quantum processors and NOT proofs in the infinite thermodynamic limit or mathematical upper-bound proofs. Every eigensolver is certified mechanically by operator Hermiticity ($\|H - H^\dagger\| / \|H\| \le 10^{-14}$), eigenpair residual ($\|H|\psi\rangle - E_0|\psi\rangle\|_2 \le 10^{-11}$), and compensated Ogita–Rump–Oishi `Dot2` / Neumaier norm preservation ($\le 10^{-15}$).

| Script | Finite Cluster / Numerical Model | Dimension | Audited Classical Result (`Exit Code 0`) | Residual / Cross-Check |
| :---: | :--- | :---: | :--- | :---: |
| `04` | **16Q Frustrated Heisenberg + 24Q 1D MPS/DMRG** | $D_{16}=65,536$<br>$D_{24}=16,777,216$ | $E_0(16\text{Q}) = -9.352934259602$ (matches `ARPACK eigsh`); $E_0(24\text{Q MPS}) = -11.0121533354$ in **`236.5 KB`** ($\chi \le 32$) | $\|\Delta E_{\text{ARPACK}}\| = 5.33 \times 10^{-15}$<br>res $= 2.03 \times 10^{-12}$ |
| `05` | **CPTP Kraus Gate-Folding ZNE + Shot Noise** | $\rho \in \mathbb{C}^{2^N \times 2^N}$<br>($N \in \{3,5,8\}$) | Explicit $(\text{CNOT})^\lambda$ ($\lambda \in \{1,3,5\}$) depolarizing + $T_2$ channels, $16,384$ multinomial shots, Richardson $\sigma$ inflation $2.2845\times$ | $F_{8\text{Q}}: 0.7156 \to 0.8274$ (exp ZNE) |
| `06` | **12-Spin Kagome Star ($\mathbb{C}^{4096}$)** | $D = 4,096$ | $J_\chi=0 \implies E_0 = -4.5000000000\,J$, $\langle\chi\rangle = 0.0$; $T$-broken $J_\chi=-0.30 \implies E_0 = -4.6896089815\,J$, $\langle \vec{S}_i\cdot(\vec{S}_j\times\vec{S}_k)\rangle = +0.16812194$ | res $= 6.10 \times 10^{-13}$ |
| `07` | **1D Half-Filled Hubbard Ring (8 sites)** | $D = 4,900$ | Exact $+ \text{h.c.}$ kinetic symmetry; $U=0$ Bloch match err $0.00$; $U/t=4 \implies E_0 = -4.60352630\,t$, $\langle n_\uparrow n_\downarrow\rangle = 0.094926$ | res $= 1.54 \times 10^{-13}$ |
| `08` | **6D Kissing Configuration ($E_6$ + $(S^5)^{73}$ Flow)** | $(S^5)^{73}$ | Exact 72-root $E_6$ contact ($\theta_{\min}=60.000000^\circ$), covering hole $\arccos(\sqrt{6}/4)=52.2388^\circ$; local 73-sphere jamming $\theta_{\min}=56.4081^\circ$ *(not SDP upper-bound proof)* | Norm drift $1.11 \times 10^{-16}$ |
| `09` | **4-Orbital $[\text{Cu}_2\text{O}_2]^{2+}$ Hubbard-PPP FCI** | $D_{\text{Fock}}=70$<br>($D_{S_z=0}=36, D_{S_z=1}=16$) | Spin-resolved singlet ($\langle \hat{S}^2\rangle = 0$) vs triplet ($\langle \hat{S}^2\rangle = 2$) Lanczos across $\theta \in [75^\circ, 105^\circ]$ ($\Delta_{ST}(95^\circ) = +304.18\text{ meV}$) | res $\le 3.02 \times 10^{-14}$ |
| `10` | **Majorana $\text{SYK}_4$ & Bott RMT Periodicity** | $N=16$ ($D_{\text{even}}=128$)<br>$N=12$ ($D_{\text{even}}=32$) | $N=16$ ($N \equiv 0 \bmod 8$, **GOE**): $\langle r \rangle = 0.5340 \pm 0.0112$ (th. $0.5359$); $N=12$ ($N \equiv 4 \bmod 8$, **GSE**): $\langle r \rangle = 0.6666 \pm 0.0205$ (th. $0.6744$) | $\|\Delta E_0\| = 2.22 \times 10^{-16}$ |
| `11` | **Odd-Electron $[\text{Fe}_4\text{S}_4]^+$ Cubane Spin Cluster** | $9$ spins-$1/2$<br>($D=512, D_{M_z=1/2}=126$) | Reproduces $S_{\text{tot}} = 1/2 \to S_{\text{tot}} = 3/2$ Kramers quartet crossover ($\langle \hat{S}_{\text{tot}}^2\rangle = 3.750000$ at $B_{\text{dex}}=32\text{ meV}$) *(effective spin model, not full FeMoco FCI)* | res $= 5.16 \times 10^{-14}$ |
| `12` | **$S=1$ Haldane Chain ($N=10$, Antipodal $r=5$)** | $3^{10}=59,049$<br>($D_{S_z=0}=8,953$) | Matrix-free Lanczos gap $\Delta_H(N=10) = 0.52480795\,J$; antipodal string order $O_{\text{str}}(0,5) = +0.371959$ vs local $(-1)^5\langle S_0^z S_5^z\rangle = +0.181800$ | res $= 3.54 \times 10^{-12}$ |
| `13` | **2D Betts $\sqrt{8}\times\sqrt{8}$ Hubbard Pairing** | $D = 3,136$ | $U/t=6, \delta=25\%$: $E_0 = -6.18129100\,t$; disjoint interaction vertex $\Delta P_d = +0.071391$ (enhanced) vs $\Delta P_s = -0.033915$ (suppressed) | res $= 4.85 \times 10^{-14}$ |

---

## 📂 3. Directory Layout

```text
quantum/
├── README.md                                         # Overview, IBM Job IDs & audited solver table
├── INFORME_EJECUTIVO_CUANTICO_EINSOF.md              # Executive & technical report (Spanish)
├── einsof_manifold_lanczos.py                        # Compensated Dot2 + thick-restart Stiefel-Lanczos + 2-site MPS/DMRG
├── data/                                             # Verified JSON outputs (QPU jobs + audited CPU solvers)
│   ├── mermin_5q_fez_dbmcj2l8mdtc73d7nuqg.json
│   ├── mermin_3q_marrakesh_dbm99558ft8s738ueesg.json
│   ├── ghz_scaling_marrakesh_dbm9glpkbkrc73cp3igg.json
│   ├── heisenberg_16q_stiefel_benchmark.json
│   ├── zne_ghz_mitigation.json
│   ├── kagome_spin_liquid.json
│   ├── mott_hubbard_model.json
│   ├── kissing_number_6d_k6.json
│   ├── dicopper_cu2o2_isomerization.json
│   ├── syk4_quantum_chaos.json
│   ├── femoco_nitrogenase_cubane.json
│   ├── haldane_gap_string_order.json
│   └── cuprate_dwave_superconductivity.json
└── scripts/
    ├── 01_mermin_n5_phase_aligned_ibm.py             # Physical QPU Mermin-Ardehali N=5 runner
    ├── 02_mermin_n3_ghz_ibm.py                       # Physical QPU Mermin N=3 GHZ runner
    ├── 03_ghz_scaling_decoherence_ibm.py             # Physical QPU GHZ 3Q..20Q decoherence mapper
    ├── 04_heisenberg_16q_stiefel_vs_dense.py         # 16Q Stiefel-Lanczos vs ARPACK + 24Q MPS/DMRG
    ├── 05_zne_error_mitigation_stiefel.py            # CPTP Kraus CNOT-folding ZNE + shot noise
    ├── 06_kagome_spin_liquid_stiefel.py              # 12-spin Kagome complex Lanczos & scalar chirality
    ├── 07_mott_hubbard_stiefel.py                    # 8-site 1D Hubbard Hermitian Lanczos
    ├── 08_kissing_number_6d_stiefel.py               # 6D E6 kissing configuration & (S^5)^73 flow
    ├── 09_dicopper_catalysis_stiefel.py              # 4-orbital [Cu2O2]^2+ spin-resolved Lanczos FCI
    ├── 10_syk_quantum_chaos_stiefel.py               # SYK4 Majorana N=16 (GOE) & N=12 (GSE) Bott RMT
    ├── 11_femoco_nitrogenase_stiefel.py              # 9-spin [Fe4S4]+ Kramers S=3/2 cubane model
    ├── 12_haldane_gap_topological_stiefel.py         # N=10 S=1 Haldane gap & antipodal string order
    └── 13_cuprate_dwave_superconductivity_stiefel.py # 8-site 2D Betts Hubbard exact singlet pairing
```

---

## ⚙️ 4. Reproducibility

```bash
pip install numpy scipy psutil qiskit qiskit-ibm-runtime
python einsof_manifold_lanczos.py
python scripts/04_heisenberg_16q_stiefel_vs_dense.py
python scripts/12_haldane_gap_topological_stiefel.py
```

---

## 🧭 5. Epistemological Distinction: Superconducting QPU vs. CMOS Silicon
EinsofOS strictly separates:
1. **Superconducting Quantum Hardware (Scripts `01`–`03`):** Transmon qubits ($\text{Al}/\text{AlO}_x/\text{Al}$ Josephson junctions) cooled to $15\text{ mK}$ at IBM Quantum, audited via public `Job ID`s.
2. **Classical CMOS Silicon Solvers (Scripts `04`–`13`):** Matrix-free Krylov (`Stiefel-Lanczos` with compensated `Dot2`) and tensor-network (`MPS/DMRG`) algorithms executed deterministically on room-temperature CPU hardware.
