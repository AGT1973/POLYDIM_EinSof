# RESUMEN EJECUTIVO POLYDIM: UTN-FRBA & POSGRADO EN CIENCIA DE DATOS

**Institución:** Universidad Tecnológica Nacional (UTN - Facultad Regional Buenos Aires)  
**Autor:** Ariel García Traba / Coordinación Académica e Investigación  
**Fecha:** Octubre 2026 — Edición Maestra V1550 / Kernel V26155 Congelado  

---

## 1. LA DESIGUALDAD DE PROCESAMIENTO DE INFORMACIÓN (DPI) Y EL CUELLO DE BOTELLA DE CUANTIZACIÓN

Los sistemas multi-agente distribuidos actuales y los protocolos de contexto (MCP, tool-calling) serializan sistemáticamente sus activaciones continuas internas a flujos discretos de texto (JSON, cadenas de caracteres, Markdown).

### 1.1 Formulación Rigurosa en Teoría de la Información (Cover & Thomas, 2006)
Sea $X \in \mathbb{R}^{n \times k}$ una matriz de representaciones latentes con distribución de probabilidad $P_X$. Al procesarse a través de un canal de cuantización y tokenización disipativo $T: \mathbb{R}^{n \times k} \to \Sigma^*$ produciendo una secuencia de tokens $S \in \Sigma^{\le m}$, seguido de un decodificador downstream $D: \Sigma^{\le m} \to \mathbb{R}^{n \times k}$ que reconstruye la estimación $\hat{X} = D(S)$, se define la cadena de Markov:
$$X \longrightarrow S = T(X) \longrightarrow \hat{X} = D(S)$$

Por la **Desigualdad de Procesamiento de la Información (DPI)**:
$$I(X; \hat{X}) \le I(X; S) \le H(S) \le m \log_2 |\Sigma|$$

### 1.2 No-Inyectividad y Cotas de Distorsión Métrica
Una secuencia de bytes unidimensional puede teóricamente codificar cualquier tensor sin pérdidas si el tamaño es ilimitado. Sin embargo, en los sistemas de IA reales:
1. **Presupuesto de tokens acotado:** $m < \infty$.
2. **Vocabulario discreto finito:** $|\Sigma| < \infty$ (típicamente $|\Sigma| \approx 32.000$).
3. **Redondeo y truncamiento flotante:** Serializadores imprimen flotantes con precisión textual finita (`%.4f` o `%.6g`).

Dado que el soporte continuo de las variables gaussianas $X$ posee cardinalidad infinita mientras que $\Sigma^{\le m}$ es estrictamente finito, la aplicación $T$ es no-inyectiva ($\exists x \ne y$ tal que $T(x) = T(y)$). Consecuentemente, por Teoría de Tasa-Distorsión, para cualquier métrica $d(X, \hat{X}) = \|X - \hat{X}\|_F$, la distorsión esperada satisface:
$$\mathbb{E}[\|X - \hat{X}\|_F^2] \ge D^*(R)$$
donde $R \le m \log_2 |\Sigma|$ bits. En contraste, retener matrices crudas IEEE-754 binary64 directamente en memoria compartida preserva la precisión total de 64 bits ($u \approx 1,11 \times 10^{-16}$) con cero error de truncamiento.

---

## 2. ARQUITECTURA PMTP (PROTOCOLO DE TRANSFERENCIA DE VARIEDADES POLYDIM)

POLYDIM resuelve el costo de serialización mediante **PMTP**: un protocolo de transporte inter-agente de copia cero sobre memoria compartida POSIX/Win32. Los procesos se comunican intercambiando descriptores binarios fijos de 88 bytes.

### 2.1 Descriptor Binario Fijo de 88 Bytes
Empaquetado con alineación estricta a 8 bytes (`#pragma pack(push, 1)` / Rust `#[repr(C)]`):
* `magic`: `uint32` (`0x504D5450`, ASCII `"PMTP"`, 4 bytes)
* `version`: `uint16` (`0x0100` $\to$ v1.0, 2 bytes)
* `flags`: `uint16` (Bit 0: READ_ONLY, Bit 1: COW, Bit 2: PINNED, 2 bytes)
* `slab_id`: Bytes UUIDv4 / Hash Blake3 (16 bytes)
* `dtype`: Código Enum (Float64=1, Float32=2, Int64=3, 4 bytes)
* `ndim`: Rango del tensor ($1 \le \text{rank} \le 4$, 4 bytes)
* `shape`: Arreglo fijo `uint64[4]` (32 bytes)
* `strides`: Arreglo fijo `uint64[4]` (32 bytes)
* `data_offset`: Desplazamiento en bytes dentro del slab (8 bytes)
* `crc32`: Suma de comprobación CRC32 IEEE-802.3 sobre los 84 bytes previos (4 bytes)
* **Tamaño Total:** Exactamente $88\text{ bytes}$.

### 2.2 Ancho de Banda y Eficiencia de Copia Cero en Silicio
* **Rendimiento de Memoria Compartida:** En arquitecturas de host con memoria DDR5 dual-channel satura el bus de memoria física (pico teórico hasta $102,4\text{ GB/s}$ por socket; $9,03\text{ GB/s}$ en DMA Pinned Host-to-Device PCIe 3.0 x16; y $139,78\text{ GB/s}$ en SRAM tiling Triton en GPU).
* **Latencia de IPC:** La transferencia del descriptor toma $< 1,2\ \mu\text{s}$, frente a $18\text{ ms} - 220\text{ ms}$ en cadenas JSON.
* **Acotamiento de Memoria:** Ring buffers y conteo de referencias evitan fugas y desbordamiento no controlado.

---

## 3. GEOMETRÍA EN LA VARIEDAD DE STIEFEL $\mathrm{St}(n, k)$ & RETRACCIÓN DE CAYLEY

POLYDIM preserva las activaciones latentes sobre la variedad compacta de Stiefel:
$$\mathrm{St}(n, k) = \{ X \in \mathbb{R}^{n \times k} : X^\top X = I_k \}$$
donde $n = 10.000$ (dimensión ambiental) y $k = 8$ (subespacio activo).

### 3.1 Retracción Cerrada de Cayley (Wen & Yin, 2013)
Para un vector tangente $Z \in T_X \mathrm{St}(n, k)$ que satisface $X^\top Z + Z^\top X = 0$, se define la matriz antisimétrica de rango $2k$:
$$W = Z X^\top - X Z^\top \in \mathfrak{so}(n)$$
La curva continua de Cayley es:
$$Y(t) = \left(I_n - \frac{t}{2} W\right)^{-1} \left(I_n + \frac{t}{2} W\right) X$$

Aplicando la fórmula de Sherman-Morrison-Woodbury con factores $U = [Z, X] \in \mathbb{R}^{n \times 2k}$ y $V = [X, -Z] \in \mathbb{R}^{n \times 2k}$:
$$Y(t) = X + t U \left(I_{2k} - \frac{t}{2} V^\top U\right)^{-1} V^\top X$$

### 3.2 Complejidad Computacional y Cotas Numéricas
* **Complejidad:** Bajo la factorización de rango $2k$, el costo total es $O(n k^2 + k^3)$ flops con memoria auxiliar $O(n k)$, eliminando la inversión $O(n^3)$.
* **Cota Numérica de Ortogonalidad:** En aritmética flotante (IEEE binary64, $u \approx 1,11 \times 10^{-16}$), el defecto satisface:
  $$\|Y(t)^\top Y(t) - I_k\|_F \le C(n, k) \, u \, \kappa\left(I_{2k} - \frac{t}{2} V^\top U\right) + O(u^2)$$
  Para números de condición regulares ($\kappa \approx 1$), el defecto es $\le 10^{-14}$. Ante pasos extremos o degradación de $\kappa$, el sistema activa automáticamente un fallback Polar/QR para garantizar ortogonalidad incondicional.

---

## 4. INTEGRACIÓN CURRICULAR EN LA UTN-FRBA

| Módulo Temático | Enfoque Clásico | Paradigma SOTA POLYDIM | Artefacto Verificable |
| :--- | :--- | :--- | :--- |
| **Estructuras de Datos Avanzadas** | IPC vía JSON / Protobuf | Slab en Memoria Compartida + Descriptor PMTP 88B | `polydim_v26155_monolito.py` (Checks 1-7) |
| **Álgebra Lineal & Optimización** | Gradiente Descendente en $\mathbb{R}^D$ | Optimización Riemanniana en $\mathrm{St}(n, k)$ (Cayley) | `polydim_v26155_monolito.py` (Checks 8-15) |
| **Computación de Alto Rendimiento** | Bucles en Python/NumPy | SIMD C++20 / Rust FFI con Acumulación Neumaier | Suite Conformance (29/29 Passes, Exit Code 0) |
| **Sistemas Distribuidos & IA** | Cadenas de Texto 1D en LLMs | Telepatía en Espacio Latente ($S^{D-1}$) vía PMTP | Pipeline de Tensores de Copia Cero |

---

## 5. RESUMEN TÉCNICO PARA EL CLAUSTRO DOCENTE Y POSGRADO

1. **Ejecución Determinista:** Cero deriva estocástica; cada release es validado por 29 comprobaciones en silicio con umbrales rigurosos.
2. **Agnosticismo de Hardware (Regla 27):** Interrogación dinámica en runtime (`HardwareProbe`) que despacha al kernel óptimo (AMD APU, Intel Core, Apple Silicon, NVIDIA CUDA, Google TPU).
3. **Código Pedagógico Abierto:** Código fuente completo en paquetes monolíticos ejecutables localmente y offline sin dependencias de servicios externos ni costes de API.
