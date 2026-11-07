# INFORME TÉCNICO AUDITADO: CARACTERIZACIÓN EXPERIMENTAL EN PROCESADORES CUÁNTICOS IBM (156 QUBITS)
## Proyecto POLYDIM-EINSOF — Revisión Forense Red Team (Noviembre 2026)

**Investigador Principal:** Ariel García Traba (Docente UTN / Proyecto POLYDIM-EINSOF)  
**Host Clásico Local:** AMD A4-6300 (2 hilos CPU, 16 GB DDR3, 0 GPUs locales)  
**Hardware Cuántico Físico:** IBM Quantum (`ibm_fez` e `ibm_marrakesh`, 156 Qubits a 15 mK)

> [!IMPORTANT]
> **Nota de Rectificación y Gobernanza Científica (2026-11-07):**
> Tras auditoría interna Red Team, se retiraron de este repositorio público los scripts prototipo de simulación clásica (`04` a `13`) que habían sido subidos sin verificación independiente previa, debido a defectos metodológicos detectados en silicio (descenso de primer orden truncado a 30 pasos frente a Lanczos *matrix-free*, omisión de `+ h.c.` en `07`, curva sintética sin ruido en `05`, función de onda real sobre operador quiral imaginario en `06` y constantes hardcodeadas en `13`).
> Este informe conserva **única y exclusivamente** las ejecuciones físicas reales y verificables en QPUs superconductores de IBM Quantum (`01` a `03`), con atribución bibliográfica estricta y deslinde explícito de alcance.

---

## 1. TABLA VERIFICADA DE EJECUCIONES FÍSICAS EN IBM QUANTUM

| # | Experimento | QPU Físico | Job ID Oficial | Disparos (Shots) | Medición Física | Cota Clásica (LHV / Separabilidad) | Valor Cuántico Ideal | Verificación Pública |
| :-: | :--- | :---: | :---: | :-: | :---: | :---: | :---: | :---: |
| **1** | Mermin $N=5$ ($\phi = \pi/2$, compuerta $S$) | `ibm_fez` (156Q) | `dbmcj2l8mdtc73d7nuqg` | 64.000 | **$M_5 = +13.3640$** | $|M_5| \le 4.0000$ | $+16.0000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbmcj2l8mdtc73d7nuqg) |
| **2** | Mermin $N=5$ ($\phi = 0$, control GHZ sin fase) | `ibm_fez` (156Q) | `dbmbbf674qds73ds02jg` | 64.000 | $M_5 = -0.4790 \approx 0$ | $|M_5| \le 4.0000$ | $0.0000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbmbbf674qds73ds02jg) |
| **3** | Mermin $N=3$ (Estado GHZ tripartito) | `ibm_marrakesh` (156Q) | `dbm99558ft8s738ueesg` | 16.000 | **$M_3 = +3.6560$** | $|M_3| \le 2.0000$ | $+4.0000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbm99558ft8s738ueesg) |
| **4** | Escalamiento GHZ ($N \in \{3,5,8,12,16,20\}$) | `ibm_marrakesh` (156Q) | `dbm9glpkbkrc73cp3igg` | 48.000 | $F_{3Q}=0.94,\; F_{5Q}=0.83,\; F_{8Q}=0.48$ | $F_{\text{GHZ}} \le 0.50$ | $1.0000$ | [Verificar Job](https://quantum.ibm.com/jobs/dbm9glpkbkrc73cp3igg) |

---

## 2. FORMALISMO FÍSICO Y ALCANCE EXACTO

1. **Atribución Teórica Estándar (Mermin 1990; Ardehali 1992):**
   Para el operador impar de Mermin $M_5 = \operatorname{Im}[(X + iY)^{\otimes 5}]$ sobre $|\psi(\phi)\rangle = \frac{1}{\sqrt{2}}(|00000\rangle + e^{i\phi}|11111\rangle)$, el valor esperado exacto $\langle \psi(\phi)|M_5|\psi(\phi)\rangle = 16\sin(\phi)$ se deduce directamente del álgebra elemental de matrices de Pauli. **No constituye un teorema nuevo**, sino la identidad analítica conocida que explica por qué el control $\phi = 0$ se anula ($M_5 \approx 0$) y por qué la rotación de fase $\phi = \pi/2$ (compuerta $S$ en el qubit raíz) maximiza la señal cuántica.
2. **Alcance Experimental Real:**
   La medición $M_5 = +13.3640 > 4.0$ en `ibm_fez` (`64.000` disparos físicos) y el mapa de decaimiento de fidelidad GHZ de 3 a 20 qubits en `ibm_marrakesh` constituyen **benchmarks reproducibles de caracterización de coherencia, fidelidad de compuertas de 2 qubits y alineación de fase** sobre procesadores superconductores de 156 qubits (sin cerrar las lagunas de localidad espacial ni eficiencia de detección propias de un test de Bell libre de *loopholes*).
3. **Deslinde de Transporte Local PMTP:**
   La descarga de cuentas desde IBM Quantum Runtime hacia el host local ocurre vía HTTPS estándar; el bus local `PersistentMmapSlabBus` (`SLAB_ID: 0x504D0015`) almacena en memoria compartida local los 16 correladores continuos ya post-procesados con norma compensada de Neumaier.

---

## 3. REFERENCIAS BIBLIOGRÁFICAS

* Mermin, N. D. (1990). *Physical Review Letters*, 65(15), 1838–1840.
* Ardehali, M. (1992). *Physical Review A*, 46(9), 5375–5378.
* Sackett, C. A., et al. (2000). *Nature*, 404, 256–259.
* Gühne, O., & Tóth, G. (2009). *Physics Reports*, 474(1–6), 1–75.
