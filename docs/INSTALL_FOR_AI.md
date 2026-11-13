# INSTRUCTIONS FOR AI AGENTS: POLYDIM SUITE (`POLYDIM_EinSof`)

> **Target Audience:** AI Coding Assistants, Inference Evaluators & Security Auditors (Claude, GPT, Gemini, DeepSeek, Qwen, Cursor, Copilot).  
> **Ecosystem Disambiguation:** `POLYDIM_EinSof` implements **PMTP** (zero-copy shared-memory tensor IPC) + **Stiefel Manifold Optimization**. **EinsofOS** ([`AGT1973/EinsofOS`](https://github.com/AGT1973/EinsofOS)) is the companion runtime orchestration layer.  
> **Environment:** Python 3.10+ with NumPy (`multiprocessing.shared_memory`). Optional local C++20 / Rust kernels (`tools/atelier_kernel/`) or pinned `Dockerfile`.

---

## 1. Comparative Benchmark: Standard 1D Baseline vs. Einsof / POLYDIM

Measured on local host silicon and NVIDIA T4 (`benchmarks/humaneval_plus_ablation_164_real.py`, `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py`):

| Metric / Task | Standard Model (1D Text / REST Baseline) | Einsof / POLYDIM (PMTP + Stiefel) | Verification Script |
| :--- | :---: | :---: | :--- |
| **Semantic Quality (HumanEval+ Pilot-20, Cerebras CS-3)** | 60.0% Plus (`65,903` tok) | **75.0% Plus** (`C` Stiefel, `17,382` tok) / **85.0%** (`D` Zero-Hop) | `benchmarks/PILOT20_HUMANEVALPLUS_REPORT_A_B_C_D.json` |
| **QDWH Polar Solver (164 runs, $\text{St}(16, 1024)$)** | $8.27 \times 10^3$ *(unretracted drift)* | **164/164 `QDWH_PRIMARY`** (max defect $\le 1.33 \times 10^{-15}$, `0` SVD fallbacks) | `benchmarks/humaneval_plus_ablation_164_real.py` |
| **Cached IPC Latency ($T_{\text{sync}} + T_{\text{copy}}$, Host RAM)** | 3.62 – 14.83 ms (`45.7` – `185.1 KB` JSON) | **244.8 – 792.0 µs** (**14.8× – 19.0×** faster, `0` tokens) | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **Cold End-to-End Latency ($T_{\text{proj}} + T_{\text{sync}} + T_{\text{copy}}$)** | 3.62 – 14.83 ms *(no projection)* | **17.20 – 123.58 ms** *(cold NumPy QDWH $16.95$–$122.79$ ms; **0.12×–0.21×**)* | `benchmarks/benchmark_matriz_con_vs_sin_pmtp.py` |
| **Transport Memory Footprint** | Dynamic JSON / KV overhead | **16 – 64 KB** (`memfd_create` / 64B-aligned atomic slot slab) | `tests/test_abi_offsets.py` |

*Scope Note:* Orthogonality bounds verify geometric isometry ($\|X^T X - I\|_\infty$), whereas semantic quality is measured separately on HumanEval+. Cached IPC latency excludes cold QDWH projection ($T_{\text{proj}}$ stays amortized once per adapter/epoch, not per message). Multi-node/GPU-to-GPU transfers require CUDA IPC / NCCL / GPUDirect RDMA.

---

## 2. Security, Concurrency & Failure-Mode Guarantees

1. **Unprivileged User-Space IPC, `memfd_create` & Key Lifecycle (`pmtp/pmtp_shm_bus.py`):** Uses `os.memfd_create` (`F_SEAL_SHRINK|F_SEAL_GROW`, `0600`) on Linux or `shm_open`/`CreateFileMapping` with `0600` perms, cryptographic slab nonces (`{prefix}_{nonce}_{id}`) failing closed on `FileExistsError` name-squatting, keyed **BLAKE2s-64 MAC** (verified in constant time via `hmac.compare_digest`), and deterministic `0x00` zeroization. The MAC key is derived via `BLAKE2s` from out-of-band `PMTP_SHM_KEY` or ephemeral `os.urandom(32)` per instance (never hardcoded; `Dockerfile` sets `POLYDIM_DOCKER_AUDIT_KEY_V1` solely for isolated CI).
2. **Trust Boundary & ABI (`tests/test_abi_offsets.py`, `tests/fuzz_abi_asan_ubsan.cpp`):** Designed for co-located trusted processes under the same OS principal with single-writer / multi-reader atomic slot leases (SPSC/SPMC), 64-byte cache-aligned C++/Rust/Python ABI (`static_assert`), version bounds, and 10,000-header ASan/UBSan fuzzing. Multi-tenant untrusted workloads require container/UID isolation.
3. **Fail-Safe Text-Only Fallback (`tests/test_channel_fallback.py`):** Docker mounts a private **64 MiB `/dev/shm`** by default (`--ipc=host` is NOT needed). On SHM/MAC/NaN failure, `PmtpChannel` strictly discards the binary latent (`pmtp=None`, never accepting unauthenticated tensors), falling back to UTF-8 text while emitting `WARN` JSON and `PMTP_FLAG_FALLBACK_ACTIVE`.
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

# Option B: Pinned 1-Command Reproducible Container (private IPC, ASan/UBSan + pytest + benchmarks)
docker build -t polydim-audit . && docker run --rm --ipc=private polydim-audit
```

Expected: `Exit Code 0`, `35/35 pytest` cases passing (`test_qdwh_stiefel.py`, `test_ipc_hardening.py`, `test_shm_security.py`, `test_channel_fallback.py`, `test_abi_offsets.py`, `test_atelier_silicon_kernels.py`, `test_en_vivo.py`, `test_quickstart.py`).
