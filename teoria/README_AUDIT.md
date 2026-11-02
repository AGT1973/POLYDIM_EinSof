# README_AUDIT.md — POLYDIM EinsofOS
**Versión del corpus:** V26506 | **Entrega canónica:** ENTREGA_2026_10_31_V_turing_019  
**Autor:** Ariel García Traba (Independent Research / EinsofOS)  
**Fecha de auditoría:** 2026-10-31  
**Lean:** 4.34.1 | **GCC:** 14.2.0 (Aladin Debian 13) | **MSVC:** 19.44 (Windows Host)

---

## 1. Mapa Afirmación → Evidencia

| # | Afirmación del paper | Clasificación | Evidencia física | Archivo |
|---|---------------------|---------------|-----------------|---------|
| A1 | Ortonormalidad del slab: X^T X = I_K | TEOREMA | `theorem6a_cayley_orthogonality_preservation` compila EC=0 | `pmtp_v4_axioms.lean` L89 |
| A2 | Estabilidad aritmética Neumaier para subnormales | TEOREMA + IMPLEMENTACIÓN | `theorem2_neumaier_subnormal_stability` + ASAN Exit Code 0 | `pmtp_v4_axioms.lean` L34 · `test_cross_cpp_rust.py` |
| A3 | Inmunidad ABA por epochs monótonos | TEOREMA | `theorem3_monotonic_epoch_aba_immunity` compila EC=0 | `pmtp_v4_axioms.lean` L52 |
| A4 | Disjointness de slabs en dominios distintos | TEOREMA | `theorem1_memory_disjointness_anti_aliasing` compila EC=0 | `pmtp_v4_axioms.lean` L18 |
| A5 | Serialización canónica biyectiva conserva entropía | TEOREMA | `theorem4_dpi_entropy_invariance` compila EC=0 | `pmtp_v4_axioms.lean` L67 |
| A6 | Métrica cordal en Grassmann bien definida | TEOREMA | `theorem5_grassmann_chordal_metric` compila EC=0 | `pmtp_v4_axioms.lean` L78 |
| A7 | Convergencia asintótica retracción Cayley | TEOREMA | `theorem683_cayley_asymptotic_reflector_convergence` | `pmtp_v4_axioms.lean` L112 |
| A8 | Cota acumulador Kulisch | TEOREMA | `theorem7_definitive_kulisch_accumulator_bound` | `pmtp_v4_axioms.lean` L134 |
| A9 | Invarianza de grado y norma en Clifford | TEOREMA | `clifford_blade_grade_and_norm_invariance` EC=0 | `polydim/Core.lean` L23 |
| A10 | Isometría de espinores | TEOREMA | `clifford_spinor_isometry` EC=0 | `polydim/Core.lean` L87 |
| A11 | Preservación de hiperesfera bajo rotores | TEOREMA | `clifford_hypersphere_preservation` EC=0 | `polydim/Core.lean` L103 |
| A12 | Reducción de tokens 56–94% en multi-hop | MEDICIÓN | `EXTERNAL_BENCHMARK_REPORT_V26505.json` — datos reales Cerebras CS3 | `benchmark_p99_aladin.json` |
| A13 | Latencia hand-off descriptor P50=37µs P99=64µs | MEDICIÓN | `benchmark_p99_aladin.json` — N=200, Aladin i3-8100 | `benchmark_p99_aladin.json` |
| A14 | Canal continuo supera canal discreto (capacidad Shannon) | AXIOMA | `continuous_channel_superiority` — referencia Shannon (1948) T.17 | `PolydimFormalVerification.lean` |
| A15 | Dominancia de información en protocolo PMTP | TEOREMA | `pmtp_strict_information_dominance` EC=0 | `polydim/Core.lean` L118 |
| A16 | **Linearización Seqlock y Cero Torn Reads (Teorema 9.5)** | **TEOREMA + MEDICIÓN** | **`stress_shm_concurrent_v019.py` (0 torn reads en 190k lecturas Aladin / 32k Windows)** | `tests/stress_shm_concurrent_v019.py` · `stress_report.json` |

---

## 2. Comandos de Verificación Reproducibles

```bash
# 1. Lean 4 — verificar teoremas formales (0 sorry, Exit Code 0)
lean polydim/Core.lean
lean PolydimFormalVerification.lean
lean polydim/pmtp_v4_axioms.lean

# 2. C++20 vs Rust 2021 FFI Oracle Parity Test (Exit Code 0)
python test_cross_cpp_rust.py

# 3. Canonical Seqlock Tri-Bus Concurrent Stress Test (Exit Code 0)
python stress_shm_concurrent_v019.py 2

# 4. Dart FFI Static Analysis (Exit Code 0)
dart analyze pmtp_dart_ffi.dart
```
