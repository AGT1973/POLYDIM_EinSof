# 🎓 GUÍA DE AUDITORÍA ADVERSARIAL EXTERNA V26250
**Profesor / Investigador Principal:** Ariel García Traba  
**Proyecto:** POLYDIM EINSOF — Álgebra Geométrica de Clifford, Variedades de Stiefel $St(D,K)$ y Telepatía de Tensores en Memoria Compartida (PMTP).  
**Destinatarios:** Alumnos del Curso de Grado/Posgrado y Colegas / Investigadores de Red Team.

---

## 🎯 OBJETIVO DE LA ACTIVIDAD
Someter el código y la arquitectura de POLYDIM EINSOF V26250 al escrutinio adversarial más riguroso posible utilizando las IAs frontera de última generación (Claude 3.7 / Opus, ChatGPT o3 / 4.5, DeepSeek R1 / V3, Kimi Moonshot k3, Qwen 2.5 72B, Gemini 2.5 / Pro).

El objetivo **NO** es generar resúmenes amables ni felicitaciones sintácticas, sino **identificar brechas numéricas reales, derivas de ortogonalidad, fallos en frontera FFI, desbordamientos de memoria compartida o fallas de condicionamiento asintótico ($D \ge 10^4$)**.

---

## 📁 ESTRUCTURA DUAL DE ARCHIVOS (AMBOS CONJUNTOS DISPONIBLES)

Para facilitar la auditoría tanto en interfaces con límite de archivos como en modelos con ventana de contexto extendida, se proporcionan **ambos conjuntos de archivos**:

### 📌 CONJUNTO 1: Archivo Único Consolidado (Para modelos de contexto masivo)
* **`02_CODIGO_FUENTE_CONSOLIDADO_UNIVERSAL_V26250.txt`**:
  Contiene los 5 códigos fuente unificados en un único archivo de texto con delimitadores claros:
  1. Monolito Universal Python (`polydim_v26250_monolito.py`)
  2. Kernel C++20 AVX-512 / OpenMP (`kernel_cpp_v26250.cpp.txt`)
  3. Kernel Rust Safe SIMD + Neumaier (`kernel_rust_v26250.rs.txt`)
  4. Kernel NVIDIA CUDA C++20 cuBLAS/cuSOLVER (`kernel_cuda_v26250.cu.txt`)
  5. Kernel GPU Triton SRAM Tiling (`polydim_triton_kernel_v26250.py`)
  *Ideal para:* DeepSeek R1, Kimi k3, Google Gemini Pro, Qwen 2.5.

---

### 📌 CONJUNTO 2: Archivos Modulares Independientes (Para Claude, ChatGPT y auditoría selectiva)
Disponibles directamente en el directorio raíz de la entrega y en la subcarpeta `archivos_modulares/`:
1. `polydim_v26250_monolito.py`: Orquestador universal de silicio y bus PMTP.
2. `kernel_cpp_v26250.cpp.txt`: Implementación C++20 con intrinsics AVX-512 y OpenMP.
3. `kernel_rust_v26250.rs.txt`: Implementación Rust Safe SIMD con acumuladores Neumaier.
4. `kernel_cuda_v26250.cu.txt`: Kernel nativo CUDA C++20 para aceleración SM70+.
5. `polydim_triton_kernel_v26250.py`: Kernel Triton para GPUs modernas sin vendor-lock.

---

## 📐 EVALUACIÓN DE TEOREMAS MATEMÁTICOS Y PRUEBAS EN SILICIO

Para que los alumnos y el colega evalúen si los teoremas matemáticos están **bien aplicados y certificados**:

1. **Tabla Maestra de Teoremas:**
   * `TABLA_MAESTRA_TEOREMAS_V26250.md` y `TABLA_MAESTRA_TEOREMAS_V26250.csv`:
     Contiene los **1.571 teoremas SOTA** con ID, Ciclo, Tópico, Enunciado Matemático formal, Estado (`SOTA_CERTIFIED`) y Código de Salida (Exit Code 0).
2. **Suite Maestra de Prueba Consolidada (Un único archivo con funciones y docstrings):**
   * **`suite_consolidada_1571_teoremas.py`**:
     Un único archivo ejecutable donde **cada uno de los 1.571 teoremas** está implementado como una función (`test_teorema_1()`, ..., `test_teorema_1666()`) con docstrings detallados que explican:
     - El teorema que prueban.
     - La ratio matemática de **por qué se prueba** (ortogonalidad Stiefel, preservación isométrica, acumuladores Neumaier IEEE-754, unitaridad de rotores Clifford, o invariantes FFI).
   * Comandos de ejecución:
     ```bash
     python suite_consolidada_1571_teoremas.py --smoke      # Ejecuta muestra representativa de 20 teoremas
     python suite_consolidada_1571_teoremas.py --id 1       # Ejecuta el test del teorema 1
     python suite_consolidada_1571_teoremas.py --range 1 50 # Ejecuta rango de teoremas
     python suite_consolidada_1571_teoremas.py --all        # Ejecuta la totalidad de los 1.571 teoremas
     ```
3. **Scripts y Logs Individuales:**
   * Carpeta `scripts_teoremas/`: Contiene los 1.571 scripts individuales (`verify_th_*.py`).
   * Carpeta `logs_teoremas/`: Contiene los 1.559 logs crudos de ejecución física en silicio (`verify_th_*.log`) acreditando Exit Code 0 y latencia.

---

## 🛠️ PASO A PASO PARA LA AUDITORÍA

### Paso 1: Elegir el entorno de tu IA
* Si tu IA soporta documentos grandes (DeepSeek / Gemini / Kimi): adjunta `02_CODIGO_FUENTE_CONSOLIDADO_UNIVERSAL_V26250.txt`.
* Si auditas un subsistema o usas Claude / ChatGPT: adjunta el archivo modular correspondiente (ej. `kernel_cpp_v26250.cpp.txt` o `polydim_v26250_monolito.py`).

### Paso 2: Cargar el Prompt Maestro
* Copia y pega el contenido íntegro de **`01_PROMPT_RED_TEAM_MAESTRO_V26250.txt`**.

### Paso 3: Evaluar las respuestas de la IA
Analiza si las observaciones de la IA son **errores reales** o **alucinaciones**:
* ¿El reclamo tiene fundamento matemático formal?
* ¿Se reproduce en silicio ejecutando la prueba con `python suite_consolidada_1571_teoremas.py --id <N>`?
* ¿Se preserva la ortogonalidad en $St(D,K)$ ($\|X^T X - I\| < 10^{-12}$)?

### Paso 4: Completar la Plantilla de Reporte
Completa el formulario en **`06_PLANTILLA_REPORTE_AUDITORIA.md`** y entrégalo para consolidación.
