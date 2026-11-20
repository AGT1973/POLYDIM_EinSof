# 🧪 BENCHMARK POLYDIM SOTA: 10 DESAFÍOS DE ALTA COMPLEJIDAD PARA EVALUACIÓN MULTI-AGENTE (KAGGLE T4 / T4×2)

Este conjunto de 10 problemas está diseñado para estresar la capacidad de razonamiento en múltiples etapas. A diferencia de problemas unitarios directos (tipo LeetCode Easy/Medium), estos desafíos **fracasan en un solo paso (Single-Shot / Modo D)** porque requieren:
1. Análisis formal de invariantes y precondiciones.
2. Auditoría adversarial de casos límite (desbordes, NaNs, colisiones, condiciones de carrera).
3. Síntesis algorítmica con contratos formales.
4. Generación de código de bajo nivel optimizado.

En un pipeline tradicional de texto 1D (Modo A), resolver estos 10 problemas insume entre **40.000 y 75.000 tokens** en puro andamiaje conversacional. Con **PMTP Shared KV-Cache / Ghost IPC**, el ahorro medible de tokens de entrada escala al **75%–85%**.

---

### 1. Álgebra Numérica & Manifolds: Retracción Polar Stiefel Newton-Schulz Orden 5 con Suma Compensada Neumaier
* **Descripción:** Implementar la retracción polar ortogonal $W_{t+1} = W_t (a I_k + b W_t^T W_t + c (W_t^T W_t)^2)$ de orden 5 para matrices rectangulares $W \in \mathbb{R}^{D \times k}$ ($D=2048, k=64$) con precondicionamiento espectral $\alpha = 1 / \|W\|_F$ y acumulación compensada de Neumaier para preservar la isometría $\|W^T W - I_k\|_\infty \le 2 \times 10^{-15}$.
* **Por qué falla en 1 paso:** La aproximación ingenua acumula error de punto flotante en fp32/fp64, diverge si los autovalores iniciales superan $\sqrt{3}$, y colapsa la ortogonalidad en $<4$ iteraciones.
* **Invariantes requeridos:** Desviación de norma euclidiana máxima $\le 10^{-15}$, vectorización pura sin bucles Python (`np.einsum` o C++/BLAS), convergencia en máximo 6 iteraciones.

---

### 2. Algoritmia de Grafos: Flujo Máximo de Costo Mínimo con Potenciales de Johnson y Cancelación de Ciclos (Successive Shortest Path)
* **Descripción:** Implementar el algoritmo de Min-Cost Max-Flow para un grafo dirigido residual con capacidades enteras y costos arbitrarios (pueden ser negativos sin ciclos negativos). Requiere inicialización con Bellman-Ford-Moore para calcular potenciales duales $\pi(v)$, seguido de Dijkstra con montículos de Fibonacci/Binarios sobre costos reducidos $c^\pi(u, v) = c(u, v) + \pi(u) - \pi(v) \ge 0$.
* **Por qué falla en 1 paso:** Los LLMs confunden el reajuste de potenciales duales, entran en bucle infinito ante aristas residuales bidireccionales de costo negativo, o saturan la memoria de recursión.
* **Contratos:** Detección estricta de ciclos negativos (retornar excepción tipada), conservación estricta de flujo en nodos intermedios, complejidad acotada $O(F \cdot E \log V)$.

---

### 3. Sistemas & Concurrencia: Cola Concurrente Lock-Free Multi-Producer Multi-Consumer (MPMC) con Mitigación ABA
* **Descripción:** Implementar en Python (o C++ ctypes) la cola no bloqueante de Michael-Scott con punteros atómicos etiquetados (`tagged pointers` / versión monotónica empaquetada en enteros de 64 bits o tuplas atómicas). Operaciones `enqueue` y `dequeue` con CAS (`compare-and-swap`), manejo cooperativo del puntero `tail` rezagado (*helping mechanism*) y tolerancia a fallas de hilos intermedios.
* **Por qué falla en 1 paso:** Falla típica de condición de carrera ABA en `dequeue`, puntero `tail` que no avanza cuando otro hilo se suspende, fugas de memoria o excepciones `AttributeError` en nodos vacíos.
* **Test de estrés:** 16 workers concurrentes empujando y extrayendo $100.000$ elementos simultáneamente; verificación de invariante FIFO estricto y cero elementos perdidos o duplicados.

---

### 4. Estructuras de Datos Espaciales: Hierarchical Navigable Small World (HNSW) Vector Index desde Cero
* **Descripción:** Construir un índice vectorial HNSW para embeddings de dimensión $D=128$, con capas jerárquicas probabilísticas ($\ell \sim -\ln(\text{uniform}) \cdot m_L$), búsqueda voraz heurística (*heuristic neighbor selection*) que penalice la redundancia angular entre vecinos, y soporte dinámico para inserciones concurrentes.
* **Por qué falla en 1 paso:** El 95% de los modelos confunde la regla de poda de vecinos de la capa 0 con las capas superiores, o calcula la distancia coseno de forma no normalizada generando grafos desconectados.
* **Métrica de validación:** Recall@10 $\ge 0.98$ frente a fuerza bruta en un conjunto de $10.000$ vectores sintéticos gaussianos, con latencia de búsqueda $< 1.5$ ms.

---

### 5. Compiladores & AST: Motor de Inferencia de Tipos Hindley-Milner (Algoritmo W) para un Mini-Lenguaje Funcional
* **Descripción:** Implementar el Algoritmo W completo para un cálculo lambda con tipos polimórficos (`Let`-polymorphism), constructores de tipos, variables de tipo libres/ligadas y unificación de términos de Robinson con detección de ciclos (*occurs-check*).
* **Por qué falla en 1 paso:** El *occurs-check* suele ser omitido, provocando tipos infinitos $\tau = \tau \to \sigma$; la sustitución de tipos no se compone adecuadamente entre los subárboles de expresiones `LetRec`.
* **Prueba de fuego:** Tipado exitoso de funciones de orden superior como el combinador $Y$, `map`, `compose`, y rechazo formal determinista de términos recursivos no auto-aplicables como $(\lambda x.\, x\, x)$.

---

### 6. Geometría Diferencial: Transporte Paralelo de Levi-Civita y Geodésicas en la Variedad de Grassmann $\mathrm{Gr}(k, D)$
* **Descripción:** Dadas dos subespacios representados por matrices ortonormales $Y_0, Y_1 \in \mathbb{R}^{D \times k}$, calcular los ángulos principales de Jordan $\theta_i$, el logaritmo riemanniano $\Delta = \mathrm{Log}_{Y_0}(Y_1)$ sobre el espacio tangente horizontal, y transportar paralelamente un vector tangente $\xi \in T_{Y_0}\mathrm{Gr}$ a lo largo de la geodésica $Y(t) = \exp_{Y_0}(t \Delta)$ usando descomposición en valores singulares compacta (SVD).
* **Por qué falla en 1 paso:** Requiere coordinar el espacio tangente cociente $Y_\perp$, proyectores ortogonales de orden $D \times D$ sin materializar matrices gigantes en memoria, y evitar divergencias numéricas cuando $\theta_i \to 0$.
* **Invariante:** Preservación exacta de la norma riemanniana del vector transportado: $|\|\xi(1)\|_{\mathrm{Gr}} - \|\xi(0)\|_{\mathrm{Gr}}| \le 10^{-14}$.

---

### 7. Criptografía & Aritmética Arbitraria: Multiplicación Polinomial Rápida de Schönhage-Strassen con FFT sobre Anillos $\mathbb{Z}_m$
* **Descripción:** Implementar la multiplicación de enteros de precisión arbitraria ($> 65.536$ bits) o polinomios de grado $> 4096$ mediante la Transformada Rápida de Fourier en el dominio complejo con compensación de error de redondeo (o Number Theoretic Transform - NTT sobre primos de Fermat $F_n = 2^{2^n} + 1$).
* **Por qué falla en 1 paso:** Falla masiva en el redondeo de los coeficientes tras la IFFT, problemas con el ordenamiento bit-reversal in-place, y desborde de enteros en la aritmética de 64 bits.
* **Test de validación:** Multiplicación exacta de dos enteros de $10.000$ dígitos contrastada contra `int(a) * int(b)` nativo en Python en menos de $50$ ms.

---

### 8. Métodos Formales & Lógica: Solucionador DPLL SAT con Propagación Unitaria y Aprendizaje de Cláusulas (CDCL Básico)
* **Descripción:** Implementar un solver SAT para fórmulas en Forma Clausal Conjuntiva (CNF) con:
  1. Propagación Unitaria basada en literales vigilados (*Two-Watched Literals*).
  2. Heurística dinámica de ramificación VSIDS (*Variable State Independent Decaying Sum*).
  3. Análisis de conflictos de primer corte único (*1-UIP: First Unique Implication Point*) para derivar y añadir cláusulas aprendidas (*conflict-driven clause learning*).
* **Por qué falla en 1 paso:** Mantener los punteros de los dos literales vigilados durante el *backtracking* sin reconstruir el estado entero es una de las trampas de implementación más complejas para LLMs.
* **Validación:** Resolver instancias DIMACS estándar de 100 variables / 430 cláusulas (en la transición de fase de satisfacibilidad) sin entrar en loops de resolución redundante.

---

### 9. Optimización & Simulación Física: Integrador Simpléctico de Ruth-Forest-Yoshida de Orden 4 para Dinámica Molecular N-Cuerpos
* **Descripción:** Implementar un integrador numérico geodésico simpléctico de orden 4 para un sistema gravitatorio o molecular de $N=256$ cuerpos con potencial de Lennard-Jones y barreras periódicas. El esquema debe preservar la forma simpléctica $d\mathbf{p} \wedge d\mathbf{q}$ y conservar el Hamiltoniano del sistema sin deriva secular de energía en $100.000$ pasos temporales.
* **Por qué falla en 1 paso:** Un integrador estándar de Runge-Kutta de orden 4 (RK4) disipa energía acumulativa ($O(t)$); los coeficientes de Yoshida involucran raíces algebraicas complejas ($w_1 = \frac{1}{2 - 2^{1/3}}$) que los modelos truncan o asignan a subpasos incorrectos.
* **Invariante:** Error de conservación de energía $|\Delta H / H_0| \le 10^{-7}$ tras $10^5$ iteraciones.

---

### 10. Sistemas Distribuidos: Algoritmo de Consenso Raft Minimalista con Elección de Líder y Replicación de Log a Prueba de Particiones
* **Descripción:** Implementar una máquina de estados de consenso Raft en memoria con 5 nodos asíncronos. Debe modelar: timers de elección con jitter aleatorio, RPC `RequestVote` con chequeo de log más actualizado (`lastLogTerm`, `lastLogIndex`), RPC `AppendEntries` con chequeo de consistencia, y recuperación determinista ante una partición de red de split-brain (nodo líder aislado con minoría vs. mayoría de 3 nodos que elige nuevo líder).
* **Por qué falla en 1 paso:** Manejo incorrecto del término (`currentTerm`) al recibir respuestas obsoletas; violación del invariante de compromiso (*leader never commits an entry from a previous term by counting replicas*).
* **Test de estrés:** Simular partición $3-2$, verificar que la partición minoritaria rechaza commits y que, al restablecer la red, el log minoritario se trunca y adopta el log de la mayoría sin inconsistencia de estado.

---

### Protocolo de Evaluación Recomendado para Rafael en Kaggle

Para cada uno de estos 10 problemas, contrastar 3 configuraciones en Kaggle (T4 o T4×2):

1. **Brazo D (Single-Shot / Direct Call):** Un solo prompt con el enunciado. (Se medirá la tasa de fallo catastrófico por falta de razonamiento y diseño).
2. **Brazo A (Multi-Agent 1D Text Chained - 3 Pasos):**
   - Agente 1: Especificación matemática y análisis causal de fallas (1.500 tokens).
   - Agente 2: Contratos de precondición e invariantes formales (1.200 tokens).
   - Agente 3: Código final ejecutable.
   - *Métrica esperada:* Aprobación alta, pero **consumo acumulado de 6.000 a 10.000 tokens por problema**.
3. **Brazo C (Ghost / PMTP Shared KV Cache):**
   - Mismo pipeline de 3 etapas, pero la comunicación entre Agente 1 $\to$ Agente 2 $\to$ Agente 3 se transmite mediante el **KV-Cache continuo congelado en memoria compartida** (sin re-serializar el andamiaje a texto).
   - *Métrica esperada:* Idéntica tasa de aprobación algorítmica, con un **ahorro medido de tokens de entrada del 75% al 85%**.
