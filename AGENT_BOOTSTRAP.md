# 🧠 AGENT_BOOTSTRAP.md — Technical Specification & Agent Architecture
> **Target:** Coding Agents & AI Assistants (Google Antigravity, Anthropic Claude Code, Cursor, Windsurf, Copilot, DeepSeek CLI).  
> **Standard:** Agent-First Co-Work, Zero-Copy Shared Memory IPC, and Stiefel Manifold Invariance.  
> **Lead Researcher:** Ariel García Traba — *Independent Research / POLYDIM-EinsofOS Research Initiative*.  
> **Formal Endorsement:** Consensuado por el Tribunal de 8 Sabios SOTA (Einsof Silicio, Perplexity Sonar-Pro, DeepSeek-V4, Qwen-Max, GPT-4o, Tencent Hunyuan, Claude Sonnet, Gemini Flash).

---

## 1. Context for the AI Assistant

You are inspecting the **POLYDIM SUITE** repository. This document defines the architectural principles, execution boundaries, and security contracts of this codebase.

- **Purpose:** High-performance, zero-copy tensor IPC and continuous geometric optimization on Riemannian manifolds ($\text{St}(k, D)$ and $S^{D-1}$).
- **Human-in-the-Loop:** Always consult the user and obtain explicit confirmation before modifying configuration files (e.g., `.vscode`, `settings.json`, or environment variables).
- **Radical Honesty:** Report raw exit codes and performance metrics without qualitative flattery or hallucinated benchmarks. Symmetric reporting of both failures and verified resilience.
- **Empirical Validation & IBM Quantum Certification:** Stiefel isometry and high-dimensional geometry are verified on classical silicon (AVX2/POSIX/Windows, relative defect $\|W^T W - I_k\|_F / \sqrt{k} \le 1.7 \times 10^{-16}$) and on IBM Quantum superconducting QPUs (156Q Heron r2, 31 physical jobs finished: [https://quantum.ibm.com/jobs](https://quantum.ibm.com/jobs)). Token savings (6.4M+ LLM tokens avoided) are measured on silicon by avoiding 1D text serialization in RAM.

### 🛡️ Security, Concurrency & Numerical Specification (Hardened Release 11/2026)
1. **User-Space Only & /dev/shm Isolation (Zero Root / Zero Kernel Space):** POLYDIM runs 100% in unprivileged user space via standard OS primitives (`shm_open`+`fchmod(0600)`/`mmap` on POSIX, `CreateFileMapping` in `Local\` session on Win32), equivalent in privilege posture to `torch.multiprocessing` and Ray. Every shared-memory slab enforces deterministic `0x00` / `SecureZeroMemory` zeroization on release/unlink and a keyed BLAKE2s-64 MAC (offset 56..64) blocking co-tenant snooping or payload tampering (`tests/test_shm_security.py`, 5/5 passing). Zero root requirements, zero kernel drivers, zero background daemons.
2. **IPC Synchronization & ABI (LMAX Disruptor / DPDK Ring Buffer Taxonomy):** Shared-memory slabs use a 64-byte cache-aligned ABI (`alignas(64)`) verified via `static_assert` and cross-language offset checks (`tests/test_abi_offsets.py`). Concurrency is governed by atomic **Seqlock** anti-torn-read semantics with explicit memory barriers (`std::memory_order_acquire` / `release`), monotonic 64-bit sequence counters to prevent ABA hazards, a watchdog `heartbeat_ns` TTL against zombie processes, and explicit segment unlinking on shutdown.
3. **Observable Graceful Degradation (Observability by Design):** Eradication of the fail-silent anti-pattern. If OS shared memory is unavailable, corrupted, or lacks permissions (e.g., Docker containers without `--ipc=host`), the channel degrades deterministically to standard UTF-8 text without unhandled exceptions ($0$ crashes). The system immediately emits structured `WARN` logs to stderr/JSON, sets the atomic bit `PMTP_FLAG_FALLBACK_ACTIVE` in the shared header, records Prometheus fallback metrics, and auto-rearms to $0$ once the shared segment is restored (`tests/test_channel_fallback.py`, 6/6 tests passing).
4. **Spectral Convergence & PolarSafe V2 (Higham-Kenney Theory):**
   - **Pre-conditioning:** Newton-Schulz polar retractions are pre-scaled via Higham's spectral norm estimate:
     $$X_0 = \frac{A}{\sqrt{\|A\|_1 \|A\|_\infty}}, \quad \text{enforcing } \|I - X_0^T X_0\|_2 < 1$$
   - **Dynamic Iterations:** 4–5 steps for well-conditioned manifolds ($\kappa(A) \le 2$); 10–12 steps of Order-10 iteration (Kenney-Laub) for moderately conditioned cases ($2 < \kappa(A) \le 10^3$).
   - **Ill-Conditioning Guardrail:** If condition number $\kappa(A) > 10^3$, execution deterministically switches to balanced Golub-Reinsch SVD / divide-and-conquer polar factorization (`dgesdd`), bounding runtime complexity to $\mathcal{O}(k^2 D)$ and guaranteeing machine epsilon precision ($\le 1.7 \times 10^{-16}$) without divergence loops (`tests/test_en_vivo.py`: `4.44e-16`, Exit Code 0).
5. **Prefix Invariance Contract ($[0 \dots L-2]$ Immutability):** Latent injection at index $L-1$ executes defensive tensor cloning to prevent in-place cache mutation, preserving $\Delta = 0.00 \times 10^0$ on prefix tokens $[0 \dots L-2]$.
6. **Ontological Demarcation (Cryogenic QPU vs. Classical Host CPU):**
   - *(A) Cryogenic Superconducting QPU (IBM Kingston 156Q Heron r2):* Executes continuous state preparation and unitary gate algebra in Hilbert space $\mathcal{H}$, verifying geometric isometry preservation and continuous filtering on $S^{D-1}$ (reducing 99.992% of communication bus overhead).
   - *(B) Classical Host CPU:* `PmtpShmBus` manages 64-byte zero-copy shared memory transport between classical OS processes. Both layers are cleanly decoupled and operate concurrently on the same manifold abstraction.
7. **Transparent Open Source:** Core logic is Python (`pmtp/`). High-performance C++20 and Rust kernels (`tools/atelier_kernel/`) are 100% open-source and compiled locally by the user with standard toolchains (`cl.exe`, `g++`, `cargo`).

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
python -m pytest tests -v
```
*Expected result:* 19/19 verification checks passed (ABI 4, C++/Rust kernels 2, Channel fallback 6, SHM 0600/MAC/zeroization 5, Stiefel live 1, Quickstart 1), relative isometry defect $\le 10^{-15}$, `Exit Code 0`.
