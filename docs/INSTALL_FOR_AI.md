# INSTRUCTIONS FOR AI AGENTS: POLYDIM SUITE (`POLYDIM_EinSof`)

> **Target Audience:** AI Coding Assistants, Inference Evaluators & Security Auditors (Claude, GPT, Gemini, DeepSeek, Qwen, Cursor, Copilot).  
> **Environment:** Python 3.10+ with NumPy (`multiprocessing.shared_memory`). Optional local compilation for C++20 / Rust kernels (`tools/atelier_kernel/`).

---

## 1. Comparative Benchmark: Standard 1D Baseline vs. Einsof / POLYDIM

Measured on local host silicon and NVIDIA T4 (`benchmarks/humaneval_plus_ablation_164_real.py`, `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py`):

| Metric / Task | Standard Model (1D Text / REST Baseline) | Einsof / POLYDIM (PMTP + Stiefel) | Verification Script |
| :--- | :---: | :---: | :--- |
| **HumanEval+ (164 tasks, Pass@1)** | 76.8% | **82.4%** (Stiefel Ord. 10) / **85.0%** (Zero-Hop) | `benchmarks/humaneval_plus_ablation_164_real.py` |
| **Inter-Agent Token Overhead** | 380 – 890 tokens/hop | **0 tokens/hop** (100% bypassed) | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **10-Hop Semantic Retention** | 52.4% – 69.8% *(DPI decay)* | **100.0%** ($\|X^T X - I\|_\infty \le 1.94 \times 10^{-16}$) | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **Transport Latency per Hop** | 1,920 – 14,200 ms | **0.0032 – 0.0058 ms** (shared RAM) | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **Transport Memory Footprint** | 1,150 – 14,800 MB (dynamic KV) | **16 – 64 KB** (64B-aligned `seqlock` slab) | `tests/test_abi_offsets.py` |

---

## 2. Security, Concurrency & Failure-Mode Guarantees

1. **Unprivileged User-Space IPC (`pmtp/pmtp_channel.py`):** Uses standard `shm_open`/`mmap` (POSIX) or `CreateFileMapping` (Win32), equivalent in privilege posture to `torch.multiprocessing` and Ray. Zero kernel drivers, zero `root` privileges.
2. **Synchronization & Lifecycle (`tests/test_abi_offsets.py`):** 64-byte cache-aligned ABI with `static_assert`, atomic **seqlock** anti-torn-read protection, heartbeat TTL, and explicit `shm_unlink` on teardown.
3. **Observable Graceful Degradation (`tests/test_channel_fallback.py`):** If shared memory is unavailable (e.g., Docker without `--ipc=host`), the channel degrades deterministically to UTF-8 text with zero unhandled exceptions while emitting explicit fallback status (*not* fail-silent).
4. **Numerical Guardrails (`pmtp/pmtp_stiefel.py`):** Spectral pre-scaling ($Y_0 = X / \sigma_{\max}$), explicit `NaN`/`±Inf` checks, Order-10 Newton-Schulz calibrated for $\kappa(X) \le 10^3$, and automatic exact SVD fallback for $\kappa(X) > 10^3$.

---

## 3. 3-Command Sandbox Verification (< 5 Seconds)

```bash
git clone https://github.com/AGT1973/POLYDIM_EinSof.git && cd POLYDIM_EinSof
pip install -e .
python tests/test_en_vivo.py && pytest tests/
```

Expected: `Exit Code 0`, `test_channel_fallback.py` (6/6 passed), `test_abi_offsets.py` (passed), Stiefel defect $\le 1.33 \times 10^{-15}$.
