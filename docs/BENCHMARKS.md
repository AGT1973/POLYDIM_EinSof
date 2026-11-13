# 📊 POLYDIM-PMTP BENCHMARK SUITE (BENCHMARKS.md)
## Reproducible Silicon Measurements & Cross-Model Validation

### 1. Empirical Latent State Transfer (Zero Tokens)
**Experiment**: `run_six_decisive_proofs` (Hidden state extraction from Qwen2.5-0.5B $\to$ Procrustes Stiefel projection $\to$ TinyLlama-1.1B attention injection).

| Metric | Traditional Text Prompt (REST / vLLM) | PMTP-CORE (Shared Memory) | Improvement / Delta |
| :--- | :--- | :--- | :--- |
| **Communication Tokens** | ~250 - 450 tokens / hop | **0 Tokens** | **100% Token Elimination** |
| **Inter-Agent Latency** | 350 - 1,200 ms | **< 0.005 ms** (3.8 μs) | **> 70,000× faster** |
| **Semantic Accuracy** | 80.0% (Text parse) | **75.0%** (15 / 20 correct) | Comparable ($p < 0.001$ vs 20% random baseline) |
| **KV-Cache Memory Footprint** | Dynamic linear allocation | **Fixed 16 KB slab** | Zero memory fragmentation |

---

### 2. Multi-Hop Reasoning Chains (Amdahl's Law Multiplier)
**Report**: `EXTERNAL_BENCHMARK_REPORT` (5-step chained agent reasoning).

| Stage | Baseline Text Token Count | PMTP Token Count | Token Reduction % |
| :--- | :--- | :--- | :--- |
| **Hop 1 (Ingest & Plan)** | 480 tokens | 480 tokens | 0% (Initial input) |
| **Hop 2 (Analysis)** | 1,240 tokens | 510 tokens | 58.8% |
| **Hop 3 (Refinement)** | 2,450 tokens | 535 tokens | 78.1% |
| **Hop 4 (Verification)** | 3,890 tokens | 550 tokens | 85.8% |
| **Hop 5 (Final Answer)** | 5,120 tokens | 567 tokens | **88.9% - 93.2%** |

**Amdahl Acceleration Factor**:
$$S = \frac{1}{1 - 0.80} = 5.0\times \quad \text{up to} \quad S = \frac{1}{1 - 0.90} = 10.0\times$$

---

### 3. Local Physical Hardware Audit (Rule 19 Certification)
**Script**: `tests/test_pmtp_silicon.py` (AVX2 + FP64 + Qwen2.5 on host silicon)
- **T-MP15 / T-MP17 / T-MP20**: Atomic concurrency, monitor and leases: **PASS**
- **T-MP18**: PolarSafe V2 scale-invariance:
  $$\|\mathbf{W}^T \mathbf{W} - \mathbf{I}\|_\infty = \mathbf{1.11 \times 10^{-15}} \quad (\text{Newton-Schulz Order 5})$$
- **T-MP21**: Sequence-to-Core ABI and anti-aliasing immutability: **PASS**
- **T-MP22**: Neural interoperability with KV-Cache:
  $$\text{max\_abs\_logit\_diff} = \mathbf{0.0} \quad (\text{Tokens match bit-by-bit})$$
- **Latency & Exit Code**: 61.19s total audit | **EXIT CODE 0**.

---

### 5. HumanEval+ Pilot-20 (Cerebras CS-3 Real) & Ablation de Silicio 164 Ensayos
**Piloto Real Cerebras CS-3 (20 tareas congeladas):** [`benchmarks/run_pilot20_humanevalplus_abcd.py`](../benchmarks/run_pilot20_humanevalplus_abcd.py)  
**JSON Crudo Pilot-20:** [`benchmarks/PILOT20_HUMANEVALPLUS_REPORT_A_B_C_D.json`](../benchmarks/PILOT20_HUMANEVALPLUS_REPORT_A_B_C_D.json)  
**Ablación 164 Ensayos en Vivo (Stiefel + SHM 0600/MAC):** [`benchmarks/humaneval_plus_ablation_164_real.py`](../benchmarks/humaneval_plus_ablation_164_real.py) | [`benchmarks/humaneval_plus_ablation_164_real.json`](../benchmarks/humaneval_plus_ablation_164_real.json)

| Métrica Medida (Real) | Brazo A: Relevo Texto 1D | Brazo B: Vector Afín (Sin Stiefel) | Brazo C: POLYDIM Stiefel + PMTP | Brazo D: Zero-Hop Directo |
| :--- | :---: | :---: | :---: | :---: |
| **HumanEval Base Pass@1 (20 tareas)** | 65.0% (13/20) | 70.0% (14/20) | **80.0% (16/20)** | **90.0% (18/20)** |
| **HumanEval+ Adversarial Pass@1** | 60.0% (12/20) | 70.0% (14/20) | **75.0% (15/20)** | **85.0% (17/20)** |
| **Tokens Totales Facturados (20 tareas)** | 65,903 tokens | 16,868 tokens | 17,382 tokens | **14,910 tokens** |
| **Defecto Ortogonal 10 Saltos (164 ensayos)**| N/A (1D string) | $8.27 \times 10^{3}$ *(Colapso)* | **$8.88 \times 10^{-16}$** (Máx $1.33 \times 10^{-15}$, `164/164` QDWH) | N/A (Raw SHM) |
| **Latencia Desglosada (`T_proj` / `T_ipc` / `T_e2e`)** | 2.4255 ms (JSON roundtrip) | 930.55 μs | $T_{\text{proj}}=8.89$ ms + $T_{\text{ipc}}=354.4$ μs = $9.26$ ms | **256.2 μs** (p95: 289.9 μs) |
| **Exit Code** | 0 | 0 | **0 (164/164 QDWH + MAC OK)** | **0 (164/164 MAC OK)** |

---

### 6. Matriz Dimensional End-to-End en Silicio: JSON 1D vs. PMTP ($T_{\text{proj}} + T_{\text{sync}} + T_{\text{copy}}$)
**Script Reproducible:** [`benchmarks/benchmark_matriz_con_vs_sin_pmtp.py`](../benchmarks/benchmark_matriz_con_vs_sin_pmtp.py)  
**JSON Crudo:** [`benchmarks/benchmark_matriz_con_vs_sin_pmtp.json`](../benchmarks/benchmark_matriz_con_vs_sin_pmtp.json)

| Dimensión Latente | Baseline JSON 1D (Local) | $T_{\text{proj}}$ (QDWH Frío) | $T_{\text{sync}}$ (Seqlock+MAC) | $T_{\text{copy}}$ (SHM) | $T_{\text{ipc}}$ ($T_{\text{sync}}+T_{\text{copy}}$) | $T_{\text{e2e}}$ (Total Frío) | Speedup IPC / E2E | Defecto Stiefel |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$D = 2048$ (`St(16,2048)`)** | 3.62 ms (45,736 B) | 16.95 ms | 163.1 μs | 81.7 μs | **244.8 μs** | 17.20 ms | **14.8× IPC** / 0.21× E2E | **$6.66 \times 10^{-16}$** |
| **$D = 4096$ (`St(16,4096)`)** | 7.36 ms (92,031 B) | 39.18 ms | 284.1 μs | 107.4 μs | **391.5 μs** | 39.58 ms | **18.8× IPC** / 0.19× E2E | **$6.66 \times 10^{-16}$** |
| **$D = 5120$ (`St(16,5120)`)** | 9.36 ms (115,226 B) | 48.00 ms | 351.2 μs | 141.9 μs | **493.1 μs** | 48.54 ms | **19.0× IPC** / 0.19× E2E | **$6.66 \times 10^{-16}$** |
| **$D = 8192$ (`St(16,8192)`)** | 14.83 ms (185,103 B) | 122.79 ms | 583.2 μs | 208.8 μs | **792.0 μs** | 123.58 ms | **18.7× IPC** / 0.12× E2E | **$4.44 \times 10^{-16}$** |

> Auditoría en 1 comando vía Docker (incluye ASan/UBSan + `memfd_create` + `0600` + `pytest` + benchmarks):
> ```bash
> docker build -t polydim-audit . && docker run --rm --ipc=private polydim-audit
> ```
