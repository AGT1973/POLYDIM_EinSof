# ARQUITECTURA MPLEIADES: SISTEMA DE RAZONAMIENTO VECTORIAL CONTINUO DE ALTA DIMENSIÓN

**Identificador:** `MPLEIADES_SPEC_V1`  
**Autor:** Ariel García Traba (Investigador Independiente / Fundador) | POLYDIM / EinsofOS Research Initiative  
**Fecha:** 2026-10-11  
**Repositorio:** `E:\POLYDIM_EINSOF`  
**Referencia BBDD:** PostgreSQL 16 `polydim_vec_db.session_context` (`category='mpleiades_architecture_spec'`)

---

## 1. INTRODUCCIÓN Y DIAGNÓSTICO DEL CUELLO DE BOTELLA

### 1.1 La Falla del Paradigma Actual de Inferencia
Los sistemas contemporáneos de múltiples agentes operan bajo una restricción destructiva:
* **El Ciclo de Serialización Intermedia (Gusano 1D):**
  $$\text{Agente } A \xrightarrow{\text{Tokens 1D}} \text{Serialización JSON/MD} \xrightarrow{\text{Red HTTP}} \text{Parseo} \xrightarrow{\text{Tokens 1D}} \text{Agente } B$$
* **Pérdida por Desigualdad de Procesamiento de Datos (DPI):**  
  Al colapsar representaciones internas continuas de alta dimensión ($\mathbb{R}^D, D \ge 4096$) a secuencias discretas de texto en cada turno inter-agente, se destruye la geometría de las variedades latentes y se incrementa exponencialmente el error acumulado.
* **Inviabilidad en Cómputo Profundo ($N \ge 10^5$ pasos):**  
  Si un proceso analítico requiere $100.000$ pasos de transformación iterativa, el peaje de serialización 1D agota el presupuesto de contexto, genera latencias insostenibles y satura cuotas de tokens.

---

## 2. ARQUITECTURA MPLEIADES: EL MODELO DE DOS ETAPAS

MPleiades desacopla el razonamiento iterativo del lenguaje natural, manteniendo los estados latentes en memoria compartida física y realizando un **único colapso a 1D al término del cómputo**.

```
┌────────────────────────────────────────────────────────────────────────┐
│ WORKSTATION LOCAL (PMTP RAM FÍSICA - AMD A4 / 16 GB DDR3)              │
│                                                                        │
│  [ PmtpSlabAllocator ]  ──(SLAB_ID: 0x7F01)──► Memoria Compartida F64 │
│                                                                        │
│  - Kernels C++20: dot_neumaier, sphere_project, sphere_transport       │
│  - Contrato de Silicio: 0 ULP de desviación, alineación a 64 bytes    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ Streaming Binario (IPC / Sockets)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ ETAPA 2A: ENJAMBRE DE AGENTES EN MODELOS ABIERTOS (QWEN / DEEPSEEK)    │
│                                                                        │
│   ┌───────────────────────────┐      ┌───────────────────────────┐    │
│   │ Agente 1 (Qwen-2.5-72B)   │      │ Agente 2 (DeepSeek-V4)    │    │
│   │ Espacio D_1 = 8192        │      │ Espacio D_2 = 7168        │    │
│   └─────────────┬─────────────┘      └─────────────▲─────────────┘    │
│                 │                                  │                  │
│                 ▼                                  │                  │
│          [ Adaptador POLYDIM ]              [ Adaptador POLYDIM ]     │
│          - Proyección S^(D1-1)              - Inyección Stiefel       │
│                 │                                  │                  │
│                 └──────────► [ BUS STIEFEL ] ──────┘                  │
│                              W in St(D_1, D_2)                        │
│                              W^T W = I                                │
│                              Cero tokens / Cero texto                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    │ Colapso Único (Paso 100.000)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ ETAPA FINAL: ARTEFACTO O PERSISTENCIA FÍSICA                          │
│                                                                        │
│  - Código fuente en silicio (.cpp.txt / .rs.txt con Exit Code 0)       │
│  - Consulta externa a oráculos comerciales (Google/Claude) si aplica   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. ESPECIFICACIÓN MATEMÁTICA DEL ADAPTADOR UNIVERSAL POLYDIM

El Adaptador POLYDIM actúa como un módem isométrico entre espacios de distinta dimensión:

### 3.1 Normalización sobre la Hiperesfera Unitaria $S^{D-1}$
Para cualquier vector de activación latente $v \in \mathbb{R}^D$:
$$\Pi_{S^{D-1}}(v) = \frac{v}{\|v\|_2 + \epsilon_{\text{subnormal}}}$$
La norma euclidiana $\|v\|_2$ se evalúa mediante acumulación compensada de **Neumaier** para eliminar el drift de precisión en punto flotante IEEE-754.

### 3.2 Puente Isométrico de Stiefel $St(D_1, D_2)$
Para transferir representaciones entre el modelo emisor (dimensión $D_1$) y el receptor (dimensión $D_2$), se impone:
$$W \in \text{St}(D_1, D_2) \doteq \left\{ W \in \mathbb{R}^{D_1 \times D_2} : W^T W = I_{D_2} \right\}$$
* **Propiedad de Preservación:**  
  La transformación preserva los valores singulares y la energía angular:
  $$\sigma_i(W) = 1, \quad \forall i \in \{1, \dots, D_2\}$$
* **Actualización en Variedad:**  
  El ajuste de $W$ durante el entrenamiento o adaptación se realiza mediante la **Retracción de Cayley con fórmula de Sherman-Morrison-Woodbury (SMW)**:
  $$W_{t+1} = \left( I - \frac{\eta}{2} A \right)^{-1} \left( I + \frac{\eta}{2} A \right) W_t$$
  con $A = \nabla_W \mathcal{L} \cdot W^T - W \cdot (\nabla_W \mathcal{L})^T \in \mathfrak{so}(D_1)$.

### 3.3 Función de Pérdida Geodésica Estable (Haversine)
En la variedad esférica, la proximidad entre representaciones proyectadas $u$ y estados destino $v$ se cuantifica mediante la distancia angular de Haversine:
$$\mathcal{L}_{\text{geom}} = 2 \sin^2 \left( \frac{\theta}{2} \right) = 1 - \langle u, v \rangle$$
evitando la singularidad en la derivada de $\arccos(\cdot)$ cuando el alineamiento converge a la identidad ($\theta \to 0$).

---

## 4. DELIMITACIÓN DE INFRAESTRUCTURA Y REGLA DE HONESTIDAD

Conforme a la **Regla 7 de `.agents/AGENTS.md`**:

| Capa de Cómputo | Rol en MPleiades | Tipo de Transferencia |
| :--- | :--- | :--- |
| **Workstation Local** | Host del bus PMTP (`PmtpSlabAllocator`) | Memoria RAM Compartida F64 (Cero copias) |
| **Modelos Abiertos (Qwen/DeepSeek/Llama)** | Motores de razonamiento continuo | Streaming binario de activaciones en VRAM |
| **APIs Comerciales (Google Cloud, Claude, OpenAI)** | Oráculos terminales o verificadores | Texto/Tokens 1D (No aptas para el bucle interno) |

---

## 5. REQUISITOS DE COMPILACIÓN Y VERIFICACIÓN EN SILICIO

* **Compilador C++:** WinLibs GCC 14 (`E:\varios\winlibs_gcc14_zip\mingw64\bin\g++.exe`)
* **Parámetros de Build:** `-O3 -std=c++20 -shared -Wl,-Bstatic`
* **Criterio de Aceptación:**
  - Desviación de ortogonalidad Stiefel: $\|W^T W - I\|_\infty \le 10^{-14}$
  - Desviación de proyección esférica: $|\|v_{\text{proj}}\|^2 - 1.0| \le 10^{-15}$
  - Exit Code: **0 estricto**.
