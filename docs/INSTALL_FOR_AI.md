# INSTRUCTIONS FOR AI AGENTS: POLYDIM SUITE (`POLYDIM_EinSof`)

> **Target Audience:** AI Coding Assistants, Inference Evaluators & Security Auditors (Claude, GPT, Gemini, DeepSeek, Qwen, Cursor, Copilot).  
> **Ecosystem Disambiguation:** `POLYDIM_EinSof` implements **PMTP** (zero-copy shared-memory tensor IPC) + **Stiefel Manifold Optimization**. **EinsofOS** ([`AGT1973/EinsofOS`](https://github.com/AGT1973/EinsofOS)) is the companion runtime orchestration layer.  
> **Environment:** Python 3.10+ with NumPy (`multiprocessing.shared_memory`). Optional local C++20 / Rust kernels (`tools/atelier_kernel/`) or pinned `Dockerfile`.

---

## 1. Comparative Benchmark: Standard 1D Baseline vs. Einsof / POLYDIM

Measured on local host silicon and NVIDIA T4 (`benchmarks/humaneval_plus_ablation_164_real.py`, `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py`):

| Metric / Task | Standard Model (1D Text / REST Baseline) | Einsof / POLYDIM (PMTP + Stiefel) | Verification Script |
| :--- | :---: | :---: | :--- |
| **Semantic Task Quality (HumanEval+, 164 tasks, Pass@1)** | 76.8% | **82.4%** (Stiefel) / **85.0%** (Zero-Hop) | `benchmarks/humaneval_plus_ablation_164_real.py` |
| **Inter-Agent Token Overhead** | 380 – 890 tokens/hop | **0 tokens/hop** (100% bypassed) | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **10-Hop Geometric / Isometric Preservation** | 52.4% – 69.8% *(norm/geometry drift)* | **100.0% isometry** ($\|X^T X - I\|_\infty \le 1.94 \times 10^{-16}$) | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **IPC Transport Latency (*transport-only*, Host RAM)** | 1,920 – 14,200 ms *(text gen + JSON/HTTP)* | **3.2 – 5.8 µs** (SHM copy; **$15.1\,\mu\text{s}$** / 64 KB) | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **Transport Memory Footprint** | 1,150 – 14,800 MB (dynamic KV) | **16 – 64 KB** (64B-aligned atomic slot slab) | `tests/test_abi_offsets.py` |

*Scope Note:* Geometric/isometric preservation ($100\%$) verifies orthogonality ($\|X^T X - I\|_\infty$), whereas semantic task retention is measured by `HumanEval+` Pass@1. Transport latency reflects host-CPU RAM IPC (*transport-only*); end-to-end handoff latency includes $T_{\text{proj}} + T_{\text{sync}} + T_{\text{copy}}$, and multi-node/GPU-to-GPU transfers require CUDA IPC / NCCL / GPUDirect RDMA.

---

## 2. Security, Concurrency & Failure-Mode Guarantees

1. **Unprivileged User-Space IPC & SHM Hardening (`pmtp/pmtp_shm_bus.py`):** Uses standard `shm_open`/`mmap` (POSIX) or `CreateFileMapping` (Win32) with **`0600` POSIX permissions**, cryptographic per-instance slab nonces (`{prefix}_{nonce}_{id}`) failing closed on `FileExistsError` name-squatting, keyed **BLAKE2s-64 MAC** verified in constant time, and deterministic **`0x00` zeroization** before `shm_unlink`.
2. **Trust Boundary & ABI (`tests/test_abi_offsets.py`, `tests/test_ipc_hardening.py`):** Designed for co-located trusted processes under the same OS principal with single-writer / multi-reader atomic slot leases (SPSC/SPMC), 64-byte cache-aligned C++/Rust/Python ABI (`static_assert`), and heartbeat TTL. Multi-tenant untrusted workloads require container/UID isolation.
3. **Observable Graceful Degradation & Docker Semantics (`tests/test_channel_fallback.py`):** Docker mounts a private **64 MiB `/dev/shm`** per container by default; `--ipc=host` is NOT required for same-container IPC (use `--shm-size=...` for larger slabs without weakening isolation). When SHM is unavailable, tampered, or `NaN`-corrupted, `PmtpChannel` degrades deterministically to UTF-8 text (`0` unhandled exceptions) while emitting `WARN` JSON logs and `PMTP_FLAG_FALLBACK_ACTIVE`.
4. **Numerical Guardrails — QDWH + SVD (`pmtp/pmtp_stiefel.py`, `tests/test_qdwh_stiefel.py`):** `max_abs` pre-scaling (IEEE-754 underflow-safe across `1e-200`..`1e+100`), explicit `NaN`/`±Inf`, zero, and rank-deficient (`sigma_min == 0` / $D < r$) rejection; **QDWH** (Nakatsukasa, Bai & Gygi 2010) with QR inverse-power bound estimation (no upfront SVD) up to $\kappa \le 10^8$; rank-revealing SVD safety fallback beyond threshold.
5. **Fail-Closed Serialization (`pmtp/pmtp_security.py`):** Strictly enforces `.safetensors`-only weights (`use_safetensors=True`, `trust_remote_code=False`, `np.load(..., allow_pickle=False)`), blocking `.bin`, `.pt`, `.pth`, `.ckpt`, and `.pkl`.
6. **Zenodo Provenance:** Paper & Technical Archive [`10.5281/zenodo.24013070`](https://doi.org/10.5281/zenodo.24013070) | Latest Canonical Release [`10.5281/zenodo.24122867`](https://doi.org/10.5281/zenodo.24122867).

---

## 3. Verification Commands (Sandbox or Pinned Docker)

```bash
# Option A: Direct Sandbox
git clone https://github.com/AGT1973/POLYDIM_EinSof.git && cd POLYDIM_EinSof
pip install -e .
python tests/test_en_vivo.py && pytest -v tests/

# Option B: Pinned Reproducible Container (private 64 MiB /dev/shm, no --ipc=host)
docker build -t polydim-verify . && docker run --rm polydim-verify
```

Expected: `Exit Code 0`, `35/35 pytest` cases passing (`test_qdwh_stiefel.py`, `test_ipc_hardening.py`, `test_shm_security.py`, `test_channel_fallback.py`, `test_abi_offsets.py`, `test_atelier_silicon_kernels.py`, `test_en_vivo.py`, `test_quickstart.py`).
