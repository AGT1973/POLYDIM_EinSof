# INFORME EJECUTIVO Y TÉCNICO AUDITADO: EXPERIMENTOS EN QPU SUPERCONDUCTOR Y SOLVERS KRYLOV/MPS EN SILICIO
## Proyecto POLYDIM-EINSOF (Noviembre 2026 — Revisión Red Team Certificada)

**Investigador Principal:** Ariel García Traba  
**Institución:** Docente UTN / Investigador Independiente EinsofOS  
**Auditoría Red Team:** Gandalf (Antigravity System — Protocolo de Honestidad Radical)  
**Host de Silicio Local:** AMD A4-6300 (2 hilos CPU, 16 GB DDR3, 0 GPUs locales)  
**Hardware Cuántico Físico:** IBM Quantum (`ibm_fez` e `ibm_marrakesh`, 156 Qubits, Criostato a 15 mK)  
**Persistencia Transaccional:** PostgreSQL 16 (`polydim_vec_db.session_context` y `polydim_active_db`)

---

## 1. RESUMEN EJECUTIVO Y GOBERNANZA CIENTÍFICA

Este informe consolida dos líneas estrictamente diferenciadas bajo el **Corset de Honestidad Radical**:
1. **Mediciones Físicas Reales en Hardware Cuántico Superconductor (Scripts `01`–`03`):** Ejecuciones criogénicas verificables mediante identificadores públicos (`Job ID`) en procesadores IBM Quantum de 156 qubits (`ibm_fez` e `ibm_marrakesh`), incluyendo la verificación experimental de la dependencia de fase del operador impar de Mermin–Ardehali–Belinskii–Klyshko para $N=5$ qubits ($M_5 = +13.3640$ frente a la cota realista local $|M_5| \le 4.0$, con control sin fase $M_5 = -0.4790 \approx 0$).
2. **Solvers Numéricos Clásicos Exactos en CPU Local (Scripts `04`–`13`):** Implementación del motor `einsof_manifold_lanczos.py` basado en producto interno compensado de Ogita–Rump–Oishi (`Dot2`), **Stiefel-Lanczos matrix-free con doble reortogonalización DGKS** (residuo propio certificado $\|H|\psi\rangle - E_0|\psi\rangle\|_2 \le 10^{-11}$, validado contra `scipy.sparse.linalg.eigsh` / `ARPACK`) y **DMRG variacional de 2 sitios sobre isometrías MPS** para cadenas cuánticas de 24 qubits ($D = 2^{24} = 16.777.216$ en `236.5 KB`).

---

## 2. VERIFICACIÓN FÍSICA EN HARDWARE SUPERCONDUCTOR IBM QUANTUM

| # | Experimento | QPU Físico | Job ID Oficial | Shots | Resultado Físico | Cota Clásica (LHV) | Verificación Pública |
| :-: | :--- | :---: | :---: | :-: | :---: | :---: | :---: |
| **1** | Mermin–Ardehali $N=5$ ($\phi=\pi/2$, compuerta $S$) | `ibm_fez` (156Q) | `dbmcj2l8mdtc73d7nuqg` | 64.000 | **$M_5 = \mathbf{+13.3640}$** | $4.0000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbmcj2l8mdtc73d7nuqg) |
| **2** | Mermin–Ardehali $N=5$ (Control $\phi=0$) | `ibm_fez` (156Q) | `dbmbbf674qds73ds02jg` | 64.000 | $M_5 = -0.4790 \approx 0$ | $4.0000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbmbbf674qds73ds02jg) |
| **3** | Desigualdad de Mermin $N=3$ (GHZ) | `ibm_marrakesh` (156Q) | `dbm99558ft8s738ueesg` | 16.000 | **$M_3 = \mathbf{+3.6560}$** | $2.0000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbm99558ft8s738ueesg) |
| **4** | Escalamiento GHZ ($N \in \{3..20\}$) | `ibm_marrakesh` (156Q) | `dbm9glpkbkrc73cp3igg` | 48.000 | $F_{3Q}=0.94, F_{5Q}=0.83, F_{8Q}=0.48$ | $0.5000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbm9glpkbkrc73cp3igg) |
| **5** | Tomografía $S^3$ con mitigación TREX | `ibm_marrakesh` (156Q) | `dbl1j2hkdqps7393dqag` | 10.000 | $\vec{\mu} = [-0.05, 0.22, 0.66, -0.05]$ | N/A | [Verificar Job](https://quantum.ibm.com/jobs/dbl1j2hkdqps7393dqag) |
| **6** | Batería $\text{H}_2$, Ising, MaxCut | `ibm_marrakesh` (156Q) | `dbl1kn5gg49c73djsf00` | 30.000 | $E_{\text{H2}} = -0.934\text{ Ha}, E_{\text{Ising}} = -3.764$ | N/A | [Verificar Job](https://quantum.ibm.com/jobs/dbl1kn5gg49c73djsf00) |
| **7** | Coherencia GHZ 8Q + cadena XY 8Q | `ibm_marrakesh` (156Q) | `dbl1shonceqs73ams940` | 30.000 | $\langle W_{\text{GHZ}} \rangle = 0.9707$ | N/A | [Verificar Job](https://quantum.ibm.com/jobs/dbl1shonceqs73ams940) |

### Identidad Analítica de Fase (Mermin 1990; Ardehali 1992)
Para el operador impar de 16 correladores $M_5 = \operatorname{Im}[(X + iY)^{\otimes 5}]$ evaluado sobre $|\psi(\phi)\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + e^{i\phi}|11111\rangle)$:
$$\langle \psi(\phi) | M_5 | \psi(\phi) \rangle = 16 \sin(\phi)$$
Con $\phi = 0$ el valor esperado es idénticamente nulo; al insertar una compuerta $S$ ($\phi = \pi/2$) en el qubit raíz antes de la cascada de `CNOT`s se alinea el estado con el autoespacio maximal ($+16$ ideal), obteniéndose **$+13.3640$** en el procesador criogénico `ibm_fez`.

---

## 3. AUDITORÍA DE SOLVERS CLÁSICOS EN SILICIO (`AMD A4-6300`, `Exit Code 0`)

*Declaración de Alcance (Cláusula 1 AGENTS.md): Todas las filas de esta tabla son simulaciones clásicas exactas de clúster finito en CPU local; no son ejecuciones en QPU ni pruebas asintóticas en el límite termodinámico.*

| Script | Modelo Físico / Matemático | Espacio | Resultado Certificado en Silicio | Verificación de Rigor |
| :---: | :--- | :---: | :--- | :--- |
| `04` | Heisenberg Frustrado 16Q + Cadena 24Q MPS/DMRG | $D_{16}=65.536$<br>$D_{24}=16.777.216$ | $E_0(16\text{Q}) = -9.352934259602$; $E_0(24\text{Q}) = -11.0121533354$ en **`236.5 KB`** | $\|\Delta E_{\text{ARPACK}}\| = 5.33 \times 10^{-15}$, res $2.03 \times 10^{-12}$ |
| `05` | ZNE con Canales CPTP de Kraus y Ruido de Disparo | $\rho \in \mathbb{C}^{2^N \times 2^N}$ | Plegado real $(\text{CNOT})^\lambda$ ($\lambda \in \{1,3,5\}$), $16.384$ shots, inflación $\sigma = 2.2845\times$ | $F_{8\text{Q}}: 0.7156 \pm 0.0034 \to 0.8274$ (exp) |
| `06` | Estrella de Kagome de 12 Espines ($\mathbb{C}^{4096}$) | $D = 4.096$ | $J_\chi=0 \implies E_0 = -4.50\,J, \langle\chi\rangle=0$; $J_\chi=-0.30 \implies E_0 = -4.68960898\,J$ | Quiralidad real $\langle \vec{S}_i\cdot(\vec{S}_j\times\vec{S}_k)\rangle = +0.168122$ |
| `07` | Anillo de Hubbard 1D a Medio Llenado (8 sitios) | $D = 4.900$ | Salto hermítico $+ \text{h.c.}$; error en $U=0$ vs Bloch `0.00e+00`; $E_0(U=4) = -4.60352630\,t$ | Hermiticidad $7.67 \times 10^{-19}$, res $1.54 \times 10^{-13}$ |
| `08` | Contacto Esférico 6D ($E_6$ y flujo en $(S^5)^{73}$) | $(S^5)^{73}$ | 72 raíces de $E_6$ a $60.000000^\circ$; hueco $\arccos(\sqrt{6}/4)=52.2388^\circ$; jamming 73 esferas a $56.4081^\circ$ | Deriva Dot2 $1.11 \times 10^{-16}$ *(no es prueba SDP)* |
| `09` | Modelo Efectivo 4-Orbital $[\text{Cu}_2\text{O}_2]^{2+}$ | $D_{\text{Fock}}=70$<br>($36_{S_z=0}, 16_{S_z=1}$) | FCI resuelta por espín: singlete $\langle\hat{S}^2\rangle=0$ vs triplete $\langle\hat{S}^2\rangle=2$ ($\Delta_{ST}(95^\circ)=+304.18\text{ meV}$) | Residuo propio $\le 3.02 \times 10^{-14}$ |
| `10` | Caos Cuántico $\text{SYK}_4$ y Periodicidad de Bott | $N=16$ ($D_{\text{even}}=128$)<br>$N=12$ ($D_{\text{even}}=32$) | $N=16$ (**GOE**): $\langle r \rangle = 0.5340 \pm 0.0112$ (ref. $0.5359$); $N=12$ (**GSE**): $\langle r \rangle = 0.6666 \pm 0.0205$ (ref. $0.6744$) | $\|\Delta E_0\| = 2.22 \times 10^{-16}$, res $1.98 \times 10^{-14}$ |
| `11` | Cubano Impar $[\text{Fe}_4\text{S}_4]^+$ (Kramers $S=3/2$) | $9$ espines-$1/2$<br>($D_{M_z=1/2}=126$) | Cruce $S_{\text{tot}} = 1/2 \to S_{\text{tot}} = 3/2$ ($\langle\hat{S}_{\text{tot}}^2\rangle = 3.750000$ en $B_{\text{dex}}=32\text{ meV}$) | Residuo $5.16 \times 10^{-14}$ *(modelo efectivo de espín)* |
| `12` | Cadena de Haldane $S=1$ ($N=10$, Antipodal $r=5$) | $3^{10}=59.049$<br>($D_{S_z=0}=8.953$) | Brecha matrix-free $\Delta_H(10) = 0.52480795\,J$; orden de cuerda antipodal $O_{\text{str}}(0,5) = +0.371959$ | Decaimiento local $(-1)^5\langle S_0^z S_5^z\rangle = +0.181800$ |
| `13` | Clúster Hubbard 2D Betts $\sqrt{8}\times\sqrt{8}$ ($U/t=6$) | $D = 3.136$ | $E_0 = -6.18129100\,t$; vértice intrínseco disjunto $P(U=6)-P(U=0)$: $\Delta P_d = +0.071391$ vs $\Delta P_s = -0.033915$ | Residuo $4.85 \times 10^{-14}$, cero constantes fijas |
