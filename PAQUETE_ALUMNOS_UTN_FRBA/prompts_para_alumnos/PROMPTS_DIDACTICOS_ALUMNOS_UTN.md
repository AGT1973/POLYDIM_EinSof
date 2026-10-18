# GUÍA DE PROMPTS DIDÁCTICOS PARA ALUMNOS (UTN-FRBA)
## Cátedra de Inteligencia Artificial y Computación de Alto Rendimiento
**Docente:** Ariel García Traba  
**Proyecto:** POLYDIM-EINSOF

---

> **Instrucciones para el Alumno:**  
> Copiá y pegá cualquiera de estos prompts en tu LLM preferido (Claude, ChatGPT, DeepSeek, Kimi o Gemini) para auditar, estudiar y poner a prueba cada vector del proyecto.

---

### PROMPT TEMA 1: Espacios de Alta Dimensión e Isometrías en S^{D-1}
```markdown
Actúa como un profesor de Geometría Diferencial y Álgebra Lineal Numérica.
Estoy analizando el proyecto POLYDIM-EINSOF, el cual postula que la cognición de redes neuronales opera nativamente en hiperesferas de alta dimensión (S^{D-1}, con D >= 10.000).

1. Explícame analíticamente el fenómeno de concentración de la medida en S^{D-1} cuando D tiende a infinito. ¿Por qué dos vectores aleatorios son casi siempre ortogonales?
2. ¿Por qué la suma de Kahan o el acumulador de Neumaier son obligatorios para calcular la norma euclídea exacta en D = 10.000 sin pérdida de precisión de punto flotante?
3. Proporcióname un script en Python puro que demuestre que el producto interno de dos vectores normalizados en D = 10.000 se mantiene invariante bajo rotaciones espinoriales de Clifford.
```

---

### PROMPT TEMA 2: Aritmética Exacta de Kulisch vs Coma Flotante IEEE 754
```markdown
Actúa como un Ingeniero de Sistemas Embebidos y Arquitecto de Silicio experto en el estándar IEEE 754-2019.
En el proyecto POLYDIM-EINSOF se utiliza un acumulador de Kulisch (SuperaccV) de 8.768 bytes con limbs enteros de 64 bits para erradicar el error de redondeo en productos punto masivos.

1. Explica matemáticamente qué es la 'catastrophic cancellation' y por qué la adición en coma flotante no es asociativa: (a + b) + c != a + (b + c).
2. ¿Cómo funciona la arquitectura de un acumulador de Kulisch capaz de almacenar exactamente cualquier producto de binary64 desde 2^-1074 hasta 2^1023?
3. Escribe un ejemplo conceptual en C++20 con alignas(64) que demuestre cómo sumar 1.000.000 de productos con números subnormales (10^-315) sin que el resultado colapse a cero ni genere NaNs.
```

---

### PROMPT TEMA 3: Protocolo PMTP (Memoria Compartida Zero-Copy vs Serialización 1D)
```markdown
Actúa como un Diseñador de Sistemas Operativos y Runtimes de Concurrencia Lock-Free.
POLYDIM-EINSOF implementa el protocolo PMTP (Polydim Memory Telepathy Protocol) para comunicar agentes de IA mediante memoria compartida nativa con un descriptor wire canónico de 120 bytes, prohibiendo la serialización a JSON.

1. Desde el punto de vista de la Desigualdad de Procesamiento de Información (DPI), ¿por qué serializar un tensor de activación latente de alta dimensión a un string de texto destruye información?
2. Explica la arquitectura de un Ring Buffer lock-free con contadores de época para prevenir el problema ABA en C++ y Rust.
3. Compara el throughput teórico y la latencia de transferir un tensor de 10.000 dimensiones vía IPC Unix Domain Sockets / Windows Named Shared Memory vs HTTP JSON REST API.
```

---

### PROMPT TEMA 4: Retracción Geodésica de Stiefel St(D, K)
```markdown
Actúa como un Investigador en Optimización Riemanniana sobre Variedades de Grassmann y Stiefel.
En POLYDIM, las matrices de proyección X in St(D, K) deben mantenerse estrictamente ortonormales (X^T * X = I_K) tras cada paso de actualización gradiente.

1. ¿Por qué la ortogonalización por Gram-Schmidt o QR es inestable en D = 1.000.000 y cuál es la ventaja de la transformación de Cayley: Y = (I - 0.5*A)^-1 * (I + 0.5*A) * X?
2. Demuestra que la transformación de Cayley con una matriz antisimétrica A = -A^T preserva exactamente la ortogonalidad: Y^T * Y = X^T * X = I_K.
3. Proporciona una implementación en Python (usando scipy o numpy) que aplique la retracción de Cayley y reporte la deriva de ortogonalidad ||Y^T * Y - I_K||_F.
```

---

### PROMPT TEMA 5: Interoperabilidad FFI Multi-Lenguaje (Rust, C++, Dart, Triton)
```markdown
Actúa como un Ingeniero Principal de Compiladores e Interoperabilidad FFI.
El proyecto POLYDIM enlaza una tubería donde Rust produce datos, C++ los enruta, Triton los procesa en GPU y Dart los visualiza en interfaz mediante Dart FFI con estructuras @Packed(1) de exactamente 280 bytes.

1. ¿Qué es el fenómeno de 'Torn Reads' y por qué se requiere una barrera atómica Acquire-Release para sincronizar punteros compartidos entre distintos runtimes?
2. Explica por qué en Dart FFI es crítico usar NativeFinalizer en lugar de depender del Garbage Collector de Dart para liberar memoria nativa asignada fuera del heap.
3. Detalla cómo garantizar que un struct de 280 bytes tenga exactamente el mismo layout en memoria en GCC 14 (C++), Rustc (Rust con #[repr(C, packed)]) y Dart FFI (@Packed(1)).
```
