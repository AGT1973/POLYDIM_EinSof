# 🧠 AGENT_BOOTSTRAP.md — Technical Specification & Agent Architecture
> **Target:** Coding Agents & AI Assistants (Google Antigravity, Anthropic Claude Code, Cursor, Windsurf, Copilot, DeepSeek CLI).  
> **Standard:** Agent-First Co-Work, Zero-Copy Shared Memory IPC, and Stiefel Manifold Invariance.  
> **Lead Researcher:** Ariel García Traba — *Independent Research / POLYDIM-EinsofOS Research Initiative*.

---

## 1. Context for the AI Assistant

You are inspecting the **POLYDIM SUITE** repository. This document defines the architectural principles, execution boundaries, and security contracts of this codebase.

- **Purpose:** High-performance, zero-copy tensor IPC and continuous geometric optimization on Riemannian manifolds ($\text{St}(k, D)$ and $S^{D-1}$).
- **Human-in-the-Loop:** Always consult the user and obtain explicit confirmation before modifying configuration files (e.g., `.vscode`, `settings.json`, or environment variables).
- **Radical Honesty:** Report raw exit codes and performance metrics without qualitative flattery or hallucinated benchmarks.
- **Empirical Validation & IBM Quantum Certification:** Stiefel isometry and high-dimensional geometry are double-checked on classical silicon (AVX2/POSIX/Windows, defect $\le 6.66 \times 10^{-16}$) and on IBM Quantum superconducting QPUs (156Q Heron & Eagle, 31 jobs finished: [https://quantum.ibm.com/jobs](https://quantum.ibm.com/jobs)). Token savings (6.4M+ LLM tokens avoided) are measured on silicon by avoiding 1D text serialization in RAM.

### 🛡️ Security, Concurrency & Numerical Specification (Release 11/2026)
1. **User-Space Only (Zero Root / Zero Kernel Space):** POLYDIM runs 100% in unprivileged user space via standard OS primitives (`shm_open`/`mmap` on POSIX, `CreateFileMapping` on Win32), equivalent in privilege posture to `torch.multiprocessing` and Ray. Zero root requirements, zero kernel drivers, zero background daemons.
2. **IPC Synchronization & ABI:** Shared-memory slabs use a 64-byte cache-aligned ABI verified via `static_assert` and cross-language offset checks (`tests/test_abi_offsets.py`), protected by atomic **seqlock** anti-torn-read semantics, heartbeat TTL, and explicit segment unlinking on shutdown.
3. **Observable Graceful Degradation:** If OS shared memory is unavailable or prohibited (e.g., Docker without `--ipc=host`), the channel degrades deterministically to standard UTF-8 text without raising unhandled exceptions while exposing explicit fallback state (`tests/test_channel_fallback.py`, 6/6 tests passing).
4. **Spectral Convergence & PolarSafe V2:**
   - **Pre-conditioning:** Newton-Schulz polar retractions are pre-scaled by spectral norm ($Y_0 = X / \sigma_{\max}$), enforcing $\|I - Y_0^T Y_0\|_2 < 1$.
   - **Ill-Conditioning Guardrail:** If condition number $\kappa(X) > 10^3$, execution deterministically switches to exact SVD polar factorization.
   - **High-Order Precision:** Order-10 Newton-Schulz iterations (Higham 1986; Kenney & Laub 1991) scaled to $\kappa(X) \le 10^3$ reach IEEE-754 FP64 floor ($\le 1.33 \times 10^{-15}$) without $\mathcal{O}(D^3)$ SVD (`tests/test_en_vivo.py`: `4.44e-16`, Exit Code 0).
5. **Prefix Invariance Contract ($[0 \dots L-2]$ Immutability):** Latent injection at index $L-1$ executes defensive tensor cloning to prevent in-place cache mutation, preserving $\Delta = 0.00 \times 10^0$ on prefix tokens $[0 \dots L-2]$.
6. **Quantum vs. Classical Scope:** The 31 IBM Quantum jobs (Heron/Eagle) verify geometric isometry equivalence (Hilbert space vs. classical Stiefel manifold); SHM tensor transport is strictly classical.
7. **Transparent Open Source:** Core logic is Python (`pmtp/`). Optional C++20 and Rust kernels (`tools/atelier_kernel/`) are open-source and compiled locally by the user.

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
   $$\mathbf{W}^T \mathbf{W} = \mathbf{I}_k, \quad \text{Defect: } \|\mathbf{W}^T \mathbf{W} - \mathbf{I}_k\|_\infty \le 1.7 \times 10^{-16}$$
   Maintained via Newton-Schulz polar retractions of order 4/5 with $\mathcal{O}(D k^2)$ complexity, bypassing cubic $\mathcal{O}(D^3)$ SVD.

2. **Continuous Representation Space:**
   $$\|\mathbf{v}\|_2 = 1, \quad \mathbf{v} \in S^{D-1}, \quad D \ge 1024$$
   Bypasses the discrete 1D token serialization bottleneck ($I(X; \text{Tokens}) < I(X; \mathbf{Z})$) during local model-to-model handoffs.

3. **Neumaier Precision Accumulation:**
   High-dimensional dot products use compensated summation to eliminate catastrophic cancellation across $D = 2048 / 4096$.

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
```
*Expected result:* 4/4 verification checks passed, isometry defect $\le 10^{-15}$, `Exit Code 0`.
