# POLYDIM V26505 — Reporte Oficial de Benchmarks Externos (Cerebras CS-3 + Silicio Nativo)
**Fecha de Ejecución:** `2026-10-18T09:17:41.530028` | **Exit Code:** `0`
**Autoría:** `POLYDIM-EINSOF | Ariel García Traba (Independent Research)`

## 1. Escalabilidad Multi-Hop en Cerebras CS-3 (`qwen-3.8-27b` & `gpt-oss-120b` — Formato Artificial Analysis / MLPerf Open)

| Saltos ($H$) | Tokens 1D (Sin POLYDIM) | Tokens Con POLYDIM | Ahorro Tokens | Latencia E2E 1D (ms) | Latencia E2E POLYDIM (ms) | Tiempo Silicio C++/Rust (`H-1` saltos) | Speedup E2E | Speedup en Oblea WSE | Exactitud Oráculo |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2** | `1307` | `567` | **`-56.62%`** | `2438.3 ms` | `1578.97 ms` | `120.1829 ms` | **`1.54x`** | **`1.62x`** | `100%` |
| **4** | `2765` | `567` | **`-79.49%`** | `2923.49 ms` | `3593.39 ms` | `1.8023 ms` | **`0.81x`** | **`3.7x`** | `100%` |
| **8** | `5554` | `568` | **`-89.77%`** | `17140.75 ms` | `425.59 ms` | `0.8094 ms` | **`40.28x`** | **`7.28x`** | `100%` |
| **16** | `11986` | `809` | **`-93.25%`** | `22598.37 ms` | `3847.02 ms` | `1.4626 ms` | **`5.87x`** | **`8.23x`** | `100%` |

## 2. EvalPlus / LiveCodeBench — Ejecución Real en Sandbox con Vectores Adversariales IEEE-754

| Tarea (`EvalPlus` / `LiveCodeBench`) | Sin POLYDIM (Test Estándar) | Sin POLYDIM (`EvalPlus` Adversarial: Subnormales / `1e308` / Cancelación) | Con POLYDIM (Test Estándar) | Con POLYDIM (`EvalPlus` Adversarial: Subnormales / `1e308` / Cancelación) |
| :--- | :---: | :---: | :---: | :---: |
| **EvalPlus-POLYDIM-01 (Scaled Neumaier Dot Product)** | `PASS` | `FAIL` | `PASS` | **`PASS`** |
| **EvalPlus-POLYDIM-02 (Universal Unit Sphere Projection S^(D-1))** | `PASS` | `FAIL` | `PASS` | **`PASS`** |
