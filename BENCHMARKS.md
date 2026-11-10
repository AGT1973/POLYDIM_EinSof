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

### 4. Interactive Reproduction Links (Google Colab / Kaggle)
All benchmarks can be executed with zero local setup via public Jupyter notebooks:
- [`polydim_two_models_transfer_colab.ipynb`](benchmarks/polydim_two_models_transfer_colab.ipynb)
- [`polydim_colab_suite_20_benchmarks.ipynb`](benchmarks/polydim_colab_suite_20_benchmarks.ipynb)
- [`polydim_colab_turing_t4_benchmark.ipynb`](benchmarks/polydim_colab_turing_t4_benchmark.ipynb)
- [`polydim_colab_benchmark_kit.ipynb`](benchmarks/polydim_colab_benchmark_kit.ipynb)
