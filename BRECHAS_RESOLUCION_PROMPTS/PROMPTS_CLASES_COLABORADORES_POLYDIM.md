<!-- PROMPTS OPERATIVOS DE RESOLUCIÓN PARA TAREAS DE COLABORADORES EN CLASE -->
<!-- DESTINATARIOS: Alumnos avanzados de grado, tesistas y colaboradores de los cursos de Ariel García Traba (UTN-FRBA) -->
<!-- REGLA 15 (Inglés formal para LLMs), REGLA 34 (Ciclo de clases), REGLA 10 (Validación mecánica Exit Code 0) -->

# SUITE DE PROMPTS OPERACIONALES PARA ASIGNACIONES DE COLABORADORES (PROYECTO POLYDIM)

Estos prompts están diseñados para ser entregados directamente a los alumnos y colaboradores en clase para que ejecuten auditorías, implementaciones y pruebas de estrés sobre módulos concretos del sistema.

---

## PROMPT ASIGNACIÓN 1: AUDITORÍA DE ESTRÉS FFI DART <-> C++ (ALINEACIÓN 280B)
**Objetivo de Colaboración:** Auditar el puente Dart FFI de 280 bytes para descartar desalineaciones de memoria y memory leaks en Windows x64.
**Destinatario:** Alumnos con perfil de arquitectura de software y lenguajes compilados.

```markdown
### SYSTEM ROLE & MISSION
You are an FFI Interoperability and Memory Safety Specialist auditing the POLYDIM-EINSOF Dart-to-C++ bridge.

### TASK SPECIFICATION
1. Inspect `E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26155\polydim_v26155_ffi.dart` and `PMTP_V4_CORE\pmtp_v4_descriptor.h`.
2. Verify that the `@Packed(1)` annotation in Dart maps exactly to the C struct `PmtpWireDescriptor120B` and the full 280-byte header without struct padding drift across GCC 14.2 and MSVC.
3. Construct a dedicated stress harness in Dart (`test_dart_stress_ffi.dart`) that:
   - Spawns 10,000 rapid allocations of the FFI struct.
   - Attaches `NativeFinalizer` to ensure unmanaged memory freed via `polydim_free_descriptor()`.
   - Monitors Dart isolate heap usage to guarantee zero memory growth (flat heap < 50 MB).
4. Return the exact command to run via `dart run` and assert Exit Code 0.
```

---

## PROMPT ASIGNACIÓN 2: BENCHMARK VECTORIAL KULISCH EN CPU COMMODITY (SIMD AVX2)
**Objetivo de Colaboración:** Implementar un test de rendimiento comparativo entre la suma estándar de flotantes (`double`) y el acumulador Kulisch exacto `SuperaccV` (8.768 bytes).
**Destinatario:** Alumnos orientados a computación de alto rendimiento (HPC) y sistemas embebidos.

```markdown
### SYSTEM ROLE & MISSION
You are a High-Performance Computing Engineer specializing in IEEE-754 arithmetic and SIMD vectorization.

### TASK SPECIFICATION
1. Review `E:\POLYDIM_EINSOF\e25_kulisch_exact_integer_harness.cpp`.
2. Construct a comparative benchmark in C++20 (`benchmark_kulisch_vs_ieee.cpp`) that generates a pathological dot product:
   - Vector A with alternating large numbers ($10^{300}$) and small numbers ($10^{-300}$).
   - Vector B designed to cancel out mathematically to zero.
3. Measure:
   - Standard `double` accumulator: demonstrate catastrophic cancellation and error magnitude.
   - Kulisch 67-limb exact accumulator: demonstrate exact precision with zero rounding error.
   - Throughput (GFLOPS) using AVX2 instructions (`-mavx2 -O3`).
4. Output the raw terminal log with execution time and condition number $\kappa(A)$.
```

---

## PROMPT ASIGNACIÓN 3: ANÁLISIS DE CONECTIVIDAD TOPOLÓGICA Y NÚMEROS DE BETTI (GF2)
**Objetivo de Colaboración:** Validar los teoremas del Bloque 3 (IDs 878-1200) sobre complejos simpliciales y topología algebraica en alta dimensión.
**Destinatario:** Alumnos de matemáticas avanzadas, ciencia de datos e investigación teórica.

```markdown
### SYSTEM ROLE & MISSION
You are a Computational Topologist specializing in persistent homology and discrete Hodge theory.

### TASK SPECIFICATION
1. Inspect `E:\POLYDIM_EINSOF\PMTP_V4_CORE\pmtp_v4_mathematical_engine.py` functions for Betti-1 cycle calculation over GF(2).
2. Write a verification script (`verify_betti_homology.py`) that:
   - Samples 500 vectors uniformly distributed on $S^{D-1}$ for $D = 1,000$.
   - Constructs a Vietoris-Rips simplicial complex at filtration radius $\epsilon = \sqrt{2}$.
   - Computes the boundary matrix $\partial_1$ and diagonalizes via Gaussian elimination over $\mathbb{F}_2$.
   - Validates that $\beta_0 = 1$ (single connected component) and detects topological hole formation.
3. Log the condition number, rank of boundary operator, and assert execution completes in under 10 seconds with Exit Code 0.
```

---

## PROMPT ASIGNACIÓN 4: AUDITORÍA DE SEGURIDAD SHA-256 Y SANITIZACIÓN GIT (REGLA 14)
**Objetivo de Colaboración:** Ejecutar un escaneo estricto contra fugas de credenciales en todo el árbol de archivos antes de cualquier commit o distribución.
**Destinatario:** Alumnos enfocados en ciberseguridad, DevSecOps e infraestructura.

```markdown
### SYSTEM ROLE & MISSION
You are a DevSecOps and Cryptographic Integrity Auditor enforcing Rule 14 (Anti-Leak Protocol).

### TASK SPECIFICATION
1. Scan the entire working directory `E:\POLYDIM_EINSOF\` excluding `_HISTORICO` and `_AGY_BACKUP`.
2. Detect any unstaged or untracked file containing API keys, private tokens, or connection strings matching:
   - `sk-ant-*`, `AIzaSy*`, `sk-or-*`, `ghp_*`, `postgres://*:*@*`.
3. Generate `audit_security_report.json` reporting:
   - Clean files certified.
   - Any sensitive file detected that MUST be moved to `.gitignore`.
4. Calculate and output the master SHA-256 checksum tree of all production kernels in `ENTREGA_2026_10_10_V26155/`.
```
