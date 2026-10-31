# POLYDIM / EINSOF — PUBLICACIÓN CANÓNICA SOBERANA
> **Rama Canónica:** `polydim.einsof`  
> **Arquitectura:** Variedades de Stiefel $St(D, K)$, Álgebras de Lie y Memoria Compartida Nativa PMTP  
> **Investigador Principal:** Ariel García Traba (Independent Research / EinsofOS)  
> **Fecha:** 2026-10-31  

---

## ESTRUCTURA TRIPARTITA CANÓNICA (REGLA 13)

Esta rama aísla de forma 100% limpia y autocontenida la especificación consolidada de POLYDIM fuera de las ramas de desarrollo intermedio (`V900`, `v8_main`).

### 1. `teoria/` (Manuscritos Maestros y Especificaciones Axiomáticas)
- `DIMENSION_IS_ALL_YOU_NEED_PAPER_V1550_HARDENED.md`: Paper científico canónico y comparativa SOTA.
- `POLYDIM_FORMAL_AXIOMATIC_THEORY_SOTA.md`: Especificación axiomática SOTA en 10 dimensiones con Teorema 1.2 rectificado formalmente (cota Lipschitz en variedad riemanniana cociente).
- `POLYDIM_EINSOFOS_ENTERPRISE_WHITEBOOK_V1550.md`: Libro blanco de arquitectura de silicio y despliegue empresarial.
- `POLYDIM_V018_TECHNICAL_DEBT_ISSUE_TRACKER.md`: Registro formal y especificaciones de rediseño arquitectónico para V018 (D01, D04, D05, D06, D12, D13, R2-08).
- `DICTAMEN_GPT6_EXTERNAL_REDTEAM_R2.md`: Dictamen adversarial externo de cierre emitido por `openai/gpt-6.1-sol-pro`.

### 2. `tests/` (Suites de Reproducibilidad y Certificación)
- `polydim_colab_benchmark_kit.ipynb`: Notebook interactivo para verificación en entornos acelerados.
- `polydim_advanced_8_tests_suite.ipynb`: Batería analítica de 8 pruebas de estrés tensorial.
- `test_cross_cpp_rust.py`: Suite de validación cruzada y paridad C++20 / Rust 2021 en silicio (max_diff = 0.0, Exit Code 0).

### 3. `benchmarks/` (Kits de Evidencia Empírica de Silicio)
- `run_six_decisive_proofs_v26505.py`: Kit ejecutable de las 6 pruebas analíticas decisivas.
- `run_aladin_external_repro_v26505.py`: Script de reproducción de telepatía vectorial sobre nodo Aladín (Debian 13).
- `EXTERNAL_BENCHMARK_REPORT_V26505.json`: Telemetría cruda y resultados de evaluación.
- `PILOT20_HUMANEVALPLUS_REPORT_A_B_C_D.json`: Benchmarking de modelos en tareas de razonamiento algebraico.
- `prompts_100.json`: Corpus de prompts matemáticos de estrés.

---

## COMPROBACIÓN DE SILICIO Y SEGURIDAD
- **Escudo Anti-Fugas (Regla 14):** 0 archivos `.env`, 0 claves de API ni credenciales embebidas.
- **Desacople Institucional (Regla 40):** Investigación independiente EinsofOS.
