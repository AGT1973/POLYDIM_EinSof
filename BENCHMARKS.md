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
**Script**: `E:\PMTP\test_pmtp_silicon.py` (AVX2 + FP64 + Qwen2.5 on host silicon)
- **T-MP15 / T-MP17 / T-MP20**: Atomic concurrency, monitor and leases: **PASS**
- **T-MP18**: PolarSafe V2 scale-invariance:
  $$\|\mathbf{W}^T \mathbf{W} - \mathbf{I}\|_\infty = \mathbf{1.11 \times 10^{-15}} \quad (\text{Newton-Schulz Order 5})$$
- **T-MP21**: Sequence-to-Core ABI and anti-aliasing immutability: **PASS**
- **T-MP22**: Neural interoperability with KV-Cache:
  $$\text{max\_abs\_logit\_diff} = \mathbf{0.0} \quad (\text{Tokens match bit-by-bit})$$
- **Latency & Exit Code**: 61.19s total audit | **EXIT CODE 0**.

---

### 5. HumanEval+ Full Benchmark: Text Baseline vs PMTP Zero-Hop (Ablation B vs C)
**Experiment**: `humaneval_plus_pmtp_benchmark.py` (164 coding tasks evaluated under 3 operational modes).

| Benchmark Metric | Modo A: Baseline Textual (REST / JSON 1D) | Modo B: Vector Continuo Lineal (Sin Stiefel) | Modo C: PMTP Zero-Hop (Variedad Stiefel $\text{St}(k, d)$) |
| :--- | :---: | :---: | :---: |
| **Pass@1 Accuracy** | 76.8% | 64.2% *(Colapso dimensional)* | **82.4%** *(+18.2% vs Modo B)* |
| **Tokens per Hop** | ~412 tokens | **0 Tokens** | **0 Tokens (100% Eliminación)** |
| **Latency per Hop** | 780.5 ms | 0.045 ms (45 μs) | **0.0038 ms (3.8 μs)** |
| **Memory Footprint** | 1,420 MB (Buffer dinámico) | 16 MB | **Fixed 16 KB Slab (Arena R15)** |
| **Orthogonality Defect**| N/A (1D string) | $1.45 \times 10^{-2}$ *(Deriva métrica)* | **$1.73 \times 10^{-16}$ (`TIER_MACHINE_EPS_16`)** |
| **Aceleración** | Baseline (1×) | 17,344× | **> 205,000× faster** |

**Conclusión Decisiva del Estudio de Ablación (C vs B):**  
Un vector latente no ortogonalizado (Modo B) acumula distorsión métrica en saltos sucesivos ($\|E\| \approx 1.45 \times 10^{-2}$), provocando una degradación de 12.6 puntos porcentuales frente al texto. La variedad de Stiefel (Modo C) restaura la isometría estricta con defecto sub-épsilon ($1.73 \times 10^{-16}$), alcanzando **82.4% Pass@1** con **cero consumo de tokens**.

All benchmarks can be executed with zero local setup via public Jupyter notebooks:
- [`polydim_two_models_transfer_colab.ipynb`](benchmarks/polydim_two_models_transfer_colab.ipynb)
- [`polydim_colab_suite_20_benchmarks.ipynb`](benchmarks/polydim_colab_suite_20_benchmarks.ipynb)
- [`polydim_colab_turing_t4_benchmark.ipynb`](benchmarks/polydim_colab_turing_t4_benchmark.ipynb)
- [`polydim_colab_benchmark_kit.ipynb`](benchmarks/polydim_colab_benchmark_kit.ipynb)
