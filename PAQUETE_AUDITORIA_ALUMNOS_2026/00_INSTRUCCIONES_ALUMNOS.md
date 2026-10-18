# 🎓 GUÍA DE AUDITORÍA ADVERSARIAL EXTERNA (CURSO 2026)
**Profesor:** Ariel García Traba  
**Proyecto:** POLYDIM EINSOF — Motor de Espacios Nativos de Alta Dimensión ($S^{D-1}, St(D,K)$) y Telepatía de Tensores en Memoria Compartida (PMTP).

---

## 🎯 OBJETIVO DE LA ACTIVIDAD
Cada alumno o grupo tomará el código fuente del paquete y lo someterá a su propia IA frontera (ChatGPT Plus, Claude 3.5 Sonnet / Opus, Gemini Advanced, DeepSeek V3/R1, Kimi Moonshot, Qwen 2.5, etc.) utilizando el **Prompt Maestro Red Team**.

El objetivo no es pedir explicaciones amables ni resúmenes, sino **encontrar errores reales, brechas numéricas, cuellos de botella de memoria, fallas en frontera FFI y singularidades algebraicas**.

---

## 📁 ESTRUCTURA DUAL DE ARCHIVOS (ADAPTADA A CADA IA)

### 📌 Opción A: Archivo Único Consolidado (Para DeepSeek, Kimi, Qwen y modelos de contexto largo)
* **`02_CODIGO_FUENTE_CONSOLIDADO_UNIVERSAL.txt`** (50.4 KB):
  Contiene los **5 códigos fuente unificados** en un solo archivo con separadores de sección claros:
  1. Monolito Universal Python con test suite (`polydim_v26150_monolito.py`)
  2. Kernel C++20 AVX-512 / OpenMP (`kernel_cpp_v26150.cpp.txt`)
  3. Kernel Rust Safe SIMD & Neumaier (`kernel_rust_v26150.rs.txt`)
  4. Kernel NVIDIA CUDA C++20 cuBLAS/cuSOLVER (`kernel_cuda_v26150.cu.txt`)
  5. Kernel GPU Triton SRAM Tiling (`polydim_triton_kernel_v26150.py`)

---

### 📌 Opción B: Archivos Individuales Modulares (Para Gemini, Claude, ChatGPT)
Si tu IA permite adjuntar múltiples archivos por separado o vas a auditar un kernel específico:
1. `polydim_v26150_monolito.py` — Monolito universal Python (Orquestador, PMTP, retractor y tests).
2. `kernel_cpp_v26150.cpp.txt` — Kernel C++20.
3. `kernel_rust_v26150.rs.txt` — Kernel Rust.
4. `kernel_cuda_v26150.cu.txt` — Kernel CUDA C++20 nativo.
5. `polydim_triton_kernel_v26150.py` — Kernel Triton GPU.

---

## 🛠️ PASO A PASO PARA EL ALUMNO

### Paso 1: Seleccionar tu IA
- **DeepSeek / Kimi / Qwen:** Usa el archivo único `02_CODIGO_FUENTE_CONSOLIDADO_UNIVERSAL.txt`.
- **Gemini / Claude / ChatGPT:** Sube los archivos individuales correspondientes.

### Paso 2: Cargar el Código y Enviar el Prompt
1. Abre tu IA.
2. Adjunta el archivo o los archivos de código.
3. Copia y pega el contenido completo de `01_PROMPT_RED_TEAM_MAESTRO.txt`.

### Paso 3: Analizar la Respuesta Crítica
Presta especial atención a si tu IA detecta:
1. **Comportamiento IEEE-754:** Manejo de NaNs, subnormales (`1e-318`), desbordamiento en $\tau \to \infty$.
2. **Álgebra de Manifolds:** Derivación del sistema de Woodbury $M W = RHS$ y solvers de Lyapunov $G C + C G = S + S^T$.
3. **Ancho de Banda DRAM & Triton/CUDA:** Fusión GEMM $XZ^T XZ$ y coalescencia de memoria en GPU.
4. **Seguridad de Memoria IPC:** Manejo de descriptores binarios de 88 bytes, alignment y shared memory `mmap`.

### Paso 4: Completar la Plantilla y Entregar
Completa el archivo `06_PLANTILLA_REPORTE_ALUMNO.md` con:
- Nombre del alumno y modelo de IA utilizado.
- Veredictos concretos (CRITICAL / HIGH / MEDIUM / LOW / ALUCINACIÓN).
- Propuesta de código de corrección si la IA sugiere un parche superior.
- Pegar la respuesta cruda de la IA al final.
