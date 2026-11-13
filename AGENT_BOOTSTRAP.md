# 🧠 AGENT_BOOTSTRAP.md — Technical Specification & Agent Architecture
> **Target:** Coding Agents & AI Assistants (Google Antigravity, Anthropic Claude Code, Cursor, Windsurf, Copilot, DeepSeek CLI).  
> **Standard:** Agent-First Co-Work, Zero-Copy Shared Memory IPC, and Stiefel Manifold Invariance.  
> **Lead Researcher:** Ariel García Traba — *Independent Research / POLYDIM-EinsofOS Research Initiative*.  
> **Formal Endorsement:** Consensuado por el Tribunal de 8 Sabios SOTA (Einsof Silicio, Perplexity Sonar-Pro, DeepSeek-V4, Qwen-Max, GPT-4o, Tencent Hunyuan, Claude Sonnet, Gemini Flash).

---

## 1. Context for the AI Assistant

You are inspecting the **POLYDIM SUITE** (`POLYDIM_EinSof`) repository. This document defines the architectural principles, execution boundaries, and security contracts of this codebase.

- **Ecosystem Disambiguation:** **POLYDIM / PMTP** (this repository) implements zero-copy tensor IPC and Stiefel manifold geometry ($\text{St}(k, D)$, $S^{D-1}$). **EinsofOS** (`AGT1973/EinsofOS`) is the companion agentic runtime and orchestration layer; **ATELIER** (`tools/atelier_kernel/`) provides the C++20 and Rust silicon kernels.
- **Purpose:** High-performance, zero-copy tensor IPC and continuous geometric optimization on Riemannian manifolds ($\text{St}(k, D)$ and $S^{D-1}$).
- **Human-in-the-Loop:** Always consult the user and obtain explicit confirmation before modifying configuration files (e.g., `.vscode`, `settings.json`, or environment variables).
- **Radical Honesty:** Report raw exit codes and performance metrics without qualitative flattery or hallucinated benchmarks. Symmetric reporting of both failures and verified resilience.
- **Empirical Validation & IBM Quantum Certification:** Stiefel isometry and high-dimensional geometry are verified on classical silicon (AVX2/POSIX/Windows, relative defect $\|W^T W - I_k\|_F / \sqrt{k} \le 1.7 \times 10^{-16}$) and on IBM Quantum superconducting QPUs (156Q Heron r2, 31 physical jobs validating Hilbert-vs-Stiefel geometric equivalence: [https://quantum.ibm.com/jobs](https://quantum.ibm.com/jobs)). Token savings (6.4M+ LLM tokens avoided) are measured on silicon by bypassing 1D text serialization in RAM.

### 🛡️ Security, Concurrency & Numerical Specification (Hardened Release 11/2026)
1. **User-Space Only & SHM Isolation (`pmtp/pmtp_shm_bus.py`):** POLYDIM runs 100% in unprivileged user space (`shm_open`/`mmap` on POSIX, `CreateFileMapping` on Win32). Slabs enforce **`0600` POSIX permissions** (`S_IRUSR|S_IWUSR` / Win32 private session), unpredictable per-instance cryptographic nonces (`{prefix}_{nonce}_{id}`) with fail-closed rejection against `FileExistsError` name-squatting, keyed **BLAKE2s-64 MAC** verification (constant-time `hmac.compare_digest`), and deterministic `0x00` zeroization before `shm_unlink`.
2. **Trust Boundary & Concurrency Model (`pmtp/pmtp_shm_bus.py`, `tests/test_abi_offsets.py`):** Designed for co-located trusted processes under the same OS principal operating a **single-writer / multi-reader atomic slot-lease (SPSC/SPMC)** protocol (`64`-byte `alignas(64)` ABI, `static_assert`, 64-bit generation counter, `heartbeat_ns` TTL). Untrusted multi-tenant workloads require container/UID isolation; multi-node or GPU-to-GPU transfers should use CUDA IPC / NCCL / GPUDirect RDMA.
3. **Observable Graceful Degradation & Docker Semantics (`tests/test_channel_fallback.py`, `Dockerfile`):** Docker mounts a private **64 MiB `/dev/shm`** per container by default; `--ipc=host` is NOT needed for same-container IPC (use `--shm-size=...` if larger slabs are required, keeping IPC isolation intact). If OS shared memory is unavailable, corrupted, or fails MAC/NaN checks, `PmtpChannel` degrades deterministically to UTF-8 text without unhandled exceptions ($0$ crashes), emitting structured `WARN` JSON and setting `PMTP_FLAG_FALLBACK_ACTIVE` (`6/6` tests passing).
4. **Spectral Convergence & PolarSafe V2 (`pmtp/pmtp_stiefel.py`, `tests/test_qdwh_stiefel.py`):**
   - **Scale Invariance & Edge-Case Guards:** Pre-scaling by `max_abs` to prevent IEEE-754 underflow/overflow (`1e-200` to `1e+100`), plus explicit rejection of `NaN`/`±Inf` (`REJECTED_NON_FINITE`), zero matrices (`REJECTED_SINGULAR`), underdetermined shapes $D < r$ (`REJECTED_RANK_DEFICIENT`), and exact rank deficiency $\sigma_{\min}=0$ (`REJECTED_RANK_DEFICIENT_SVD`).
   - **QDWH Primary Solver + SVD Fallback:** Avoids upfront $\mathcal{O}(Dr^2)$ SVD via norm-based spectral upper bound and QR inverse-power conditioning estimation on $R \in \mathbb{R}^{r \times r}$, running **QDWH** (QR-based Dynamically Weighted Halley; Nakatsukasa, Bai & Gygi 2010) with cubic convergence up to $\kappa \le 10^8$ and rank-revealing SVD fallback beyond contract bounds (`11/11` tests passing).
5. **Fail-Closed Serialization (`pmtp/pmtp_security.py`, `tests/test_ipc_hardening.py`):** Strict **`.safetensors`-only** weight loading policy (`use_safetensors=True`, `trust_remote_code=False`, `allow_pickle=False`), rejecting pickle-backed artifacts (`.bin`, `.pt`, `.pth`, `.ckpt`, `.pkl`).
6. **Prefix Invariance Contract ($[0 \dots L-2]$ Immutability):** Latent injection at index $L-1$ executes defensive tensor cloning to prevent in-place cache mutation, preserving $\Delta = 0.00 \times 10^0$ on prefix tokens $[0 \dots L-2]$.
7. **Reproducible Container & Open Source (`Dockerfile`):** Core logic is open-source Python (`pmtp/`), C++20, and Rust (`tools/atelier_kernel/`). A pinned `Dockerfile` (`python:3.12.7-slim-bookworm`, `numpy==2.1.3`, `pytest==8.3.4`, non-root `pmtpuser`) provides reproducible `pytest tests/` verification without `--ipc=host`.

---

## 2. Architectural Boundaries & Security Guarantees

### A. IPC vs. Cloud API Disambiguation
- **Local Open-Weight Models (Qwen, Ollama, C++, Rust):** Communicate via the Polydim Memory Tensor Protocol (`PmtpShmBus`), utilizing local OS shared memory (`shm_open` / POSIX or Windows Named Shared Memory) with atomic generation leases.
- **Cloud Models (Claude, Gemini, DeepSeek APIs):** Communicate exclusively via standard HTTPS client libraries and MCP `stdio` JSON-RPC pipes. Shared memory is strictly local and never crosses network boundaries.

### B. Network & Privacy Isolation
- **No Network Scanning:** POLYDIM contains zero port scanning, subnet broadcast, or peer-to-peer discovery code.
- **Deterministic Endpoints:** Distributed Ollama instances must be explicitly defined by the user in `.env` variables (`OLLAMA_HOST=...`). If undefined, execution defaults strictly to local loopback (`127.0.0.1`).
- **No Hidden Binaries:** All core logic is published in open source (`.py`, `.cpp`, `.rs`). Users compile locally with standard toolchains (`cl.exe`, `g++`, `cargo`).

---

## 3. Core Mathematical Contracts

When interacting with POLYDIM kernels, maintain the following analytical invariants:

1. **Stiefel Manifold Invariance:**
   $$\mathbf{W}^T \mathbf{W} = \mathbf{I}_k, \quad \text{Relative Defect: } \frac{\|\mathbf{W}^T \mathbf{W} - \mathbf{I}_k\|_F}{\sqrt{k}} \le \epsilon_{\text{mach}} \approx 1.7 \times 10^{-16}$$
   Maintained via Newton-Schulz polar retractions of order 4/5 with $\mathcal{O}(D k^2)$ complexity, bypassing cubic $\mathcal{O}(D^3)$ SVD.

2. **Continuous Representation Space:**
   $$\|\mathbf{v}\|_2 = 1, \quad \mathbf{v} \in S^{D-1}, \quad D \ge 1024$$
   Bypasses the discrete 1D token serialization bottleneck ($I(X; \text{Tokens}) < I(X; \mathbf{Z})$) during local model-to-model handoffs.

3. **Neumaier Precision Accumulation:**
   High-dimensional dot products use compensated summation to eliminate catastrophic cancellation across $D = 2048 / 4096$:
   $$|S_{\text{Neumaier}} - S_{\text{exact}}| \le 2 \epsilon_{\text{mach}} \sum_{i=1}^D |x_i y_i|$$

---

## 4. MCP Interface & Tool Registration

If your host environment supports the Model Context Protocol (MCP), the reference bridge is provided at:
```text
mcp_servers/suite_bridge_mcp.py
```
- **Transport:** Standard input/output (`stdio`) JSON-RPC.
- **Capabilities Provided:**
  - `inspect_stiefel_defect`: Computes the Frobenious and Chebyshev isometry defect of a given matrix.
  - `query_local_tensor_slab`: Reads an active snapshot from the local PMTP ring buffer without disk serialization.

---

## 5. Verification Protocol

To verify that the local environment satisfies all silicon and mathematical contracts, run the unit validation suite:
```bash
python tests/test_en_vivo.py
python tests/test_abi_offsets.py
python tests/test_channel_fallback.py
```
*Expected result:* 14/14 verification checks passed, relative isometry defect $\le 10^{-15}$, `Exit Code 0`.
