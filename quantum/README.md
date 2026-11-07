# EinsofOS Quantum Hardware Characterization: Reproducible Mermin & GHZ Benchmarks on 156-Qubit IBM QPUs

**Principal Investigator:** Ariel García Traba  
**Affiliation:** UTN Faculty / EinsofOS — POLYDIM Research Project  
**ORCID:** `0009-0001-2787-6067`  
**Host Environment:** AMD A4-6300 (2 CPU threads, 16 GB DDR3 RAM, 0 Local GPUs)  
**Quantum Processors:** IBM Quantum Superconducting QPUs (`ibm_fez` & `ibm_marrakesh`, 156-Qubit Heron/Eagle Architectures at 15 mK)

> [!IMPORTANT]
> **Scientific Audit & Governance Notice (2026-11-07):**
> Following an internal Red Team forensic audit, classical finite-cluster prototype scripts (`04` through `13`) that were previously committed without independent verification have been **withdrawn from this public release** due to methodological defects (including unaccelerated 30-step first-order gradient stops, missing Hermitian conjugate hopping in `07`, synthetic noise curves in `05`, real-valued statevectors on imaginary chirality in `06`, and hardcoded correlation constants in `13`).
> Only **physically executed, independently verifiable IBM Quantum QPU characterization experiments (`01`–`03`)** are published here. No script or claim may be added to this repository without passing full spectral-residual, Hermiticity, and statistical audit.

---

## 1. Official IBM Quantum Physical Job Verification

Every physical measurement reported below was executed on IBM Quantum superconducting transmon processors (`ibm_fez` and `ibm_marrakesh`) and carries an official IBM Quantum `Job ID`:

| # | Experiment | QPU Backend | Official IBM Job ID | Total Shots | Physical Measurement | Classical LHV / Separability Bound | Quantum Ideal | Verification Link |
| :-: | :--- | :---: | :---: | :-: | :---: | :---: | :---: | :---: |
| **1** | **Mermin $N=5$ ($\phi = \pi/2$, $S$-gate aligned)** | `ibm_fez` (156Q) | `dbmcj2l8mdtc73d7nuqg` | 64,000 | **$M_5 = +13.3640$** | $|M_5| \le 4.0000$ | $+16.0000$ | [IBM Job](https://quantum.ibm.com/jobs/dbmcj2l8mdtc73d7nuqg) |
| **2** | **Mermin $N=5$ ($\phi = 0$, unaligned GHZ control)** | `ibm_fez` (156Q) | `dbmbbf674qds73ds02jg` | 64,000 | $M_5 = -0.4790 \approx 0$ | $|M_5| \le 4.0000$ | $0.0000$ | [IBM Job](https://quantum.ibm.com/jobs/dbmbbf674qds73ds02jg) |
| **3** | **Mermin $N=3$ (Tripartite GHZ)** | `ibm_marrakesh` (156Q) | `dbm99558ft8s738ueesg` | 16,000 | **$M_3 = +3.6560$** | $|M_3| \le 2.0000$ | $+4.0000$ | [IBM Job](https://quantum.ibm.com/jobs/dbm99558ft8s738ueesg) |
| **4** | **GHZ Decoherence Scaling ($N \in \{3,5,8,12,16,20\}$)** | `ibm_marrakesh` (156Q) | `dbm9glpkbkrc73cp3igg` | 48,000 | $F_{3Q}=0.94,\; F_{5Q}=0.83,\; F_{8Q}=0.48$ | $F_{\text{GHZ}} \le 0.50$ (Biseparable) | $1.0000$ | [IBM Job](https://quantum.ibm.com/jobs/dbm9glpkbkrc73cp3igg) |

---

## 2. Theoretical Background & Scope Disclaimer

### Standard Mermin–Ardehali Phase Relation (Literature Attribution)
Following **Mermin (1990)** (*Phys. Rev. Lett.* 65, 1838) and **Ardehali (1992)** (*Phys. Rev. A* 46, 5375), for the 5-qubit odd-$Y$ Mermin operator

$$M_5 = \operatorname{Im}\!\left[(X + iY)^{\otimes 5}\right] = \frac{1}{2i}\left[(X + iY)^{\otimes 5} - (X - iY)^{\otimes 5}\right]$$

evaluated on a generalized 5-qubit GHZ state $|\psi(\phi)\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + e^{i\phi}|11111\rangle)$, standard Pauli algebra gives:

$$\langle \psi(\phi) | M_5 | \psi(\phi) \rangle = 16 \sin(\phi)$$

- **Scope Clarification:** This phase dependence is **standard quantum mechanics**, not a newly discovered theoretical theorem.
- **Experimental Purpose:** Comparing $\phi = 0$ (`Job dbmbbf674qds73ds02jg`, $M_5 = -0.4790$) against $\phi = \pi/2$ prepared via an $S = R_z(\pi/2)$ gate on the root qubit (`Job dbmcj2l8mdtc73d7nuqg`, $M_5 = +13.3640$, exceeding the classical LHV bound $4.0$ by $3.341\times$) provides a clean, reproducible hardware calibration and multipartite entanglement benchmark on `ibm_fez` (without closing locality or detection loopholes required for a loophole-free Bell test).
- **Local Shared-Memory Transport Note:** In `01_mermin_n5_phase_aligned_ibm.py`, the 16 measured correlators are normalized and stored in a local shared-memory slab (`PersistentMmapSlabBus`, `SLAB_ID = 0x504D0015`) *after* retrieving the 64,000 shot counts from IBM Quantum Runtime via HTTPS.

---

## 3. Audited Directory Layout

```
quantum/
├── README.md                                           # Audited hardware characterization overview
├── INFORME_EJECUTIVO_CUANTICO_EINSOF.md                # Audited technical report (Spanish)
├── data/                                               # Raw JSON telemetry from physical IBM Quantum jobs
│   ├── mermin_5q_fez_dbmcj2l8mdtc73d7nuqg.json
│   ├── mermin_3q_marrakesh_dbm99558ft8s738ueesg.json
│   └── ghz_scaling_marrakesh_dbm9glpkbkrc73cp3igg.json
└── scripts/                                            # Reproducible IBM Quantum Runtime scripts
    ├── 01_mermin_n5_phase_aligned_ibm.py               # Mermin N=5 QPU benchmark (phi=0 vs phi=pi/2)
    ├── 02_mermin_n3_ghz_ibm.py                         # Mermin N=3 GHZ QPU benchmark
    └── 03_ghz_scaling_decoherence_ibm.py               # GHZ 3Q..20Q fidelity & decoherence mapper
```

---

## 4. References

1. Mermin, N. D. (1990). "Extreme quantum entanglement in a superposition of macroscopically distinct states". *Physical Review Letters*, 65(15), 1838–1840.
2. Ardehali, M. (1992). "Bell inequalities with a magnitude of violation that grows exponentially with the number of particles". *Physical Review A*, 46(9), 5375–5378.
3. Sackett, C. A., et al. (2000). "Experimental entanglement of four particles". *Nature*, 404, 256–259.
4. Gühne, O., & Tóth, G. (2009). "Entanglement detection". *Physics Reports*, 474(1–6), 1–75.
