# INSTRUCTIONS FOR AI AGENT: POLYDIM SUITE BOOTSTRAP

> **Target Audience:** Any AI Assistant operating in a student or researcher workspace (Claude Code, Antigravity, Cursor, Windsurf, Copilot, DeepSeek Desktop, ChatGPT/Codex CLI).
> **Environment:** Multiplatform Python 3.10+ environment with NumPy. Optional GPU support via PyTorch/Triton.

---

## 1. Architectural Overview

POLYDIM SUITE is an open-source experimental framework designed to evaluate high-dimensional inter-process communication (IPC) for language models. It explores whether transferring continuous latent states across Riemannian manifolds ($S^{D-1}$ and $\mathrm{St}(D, K)$) via shared memory can reduce intermediate token serialization costs between local agent workflows.

### Core Modules:
1. **`pmtp` Package (`pmtp/`):**
   - `PmtpShmBus`: Zero-copy shared memory tensor exchange using Python's standard `multiprocessing.shared_memory`.
   - `PmtpStiefelAdapter`: Isometry enforcement via Newton-Schulz polar retraction ($\|X^T X - I_k\|_\infty \le 10^{-14}$).
   - `PmtpProcrustesAligner`: Cross-model latent alignment via Orthogonal Procrustes ($W = U V^T$).
   - `PmtpDecoder`: Spherical coordinate decoding and norm verification.
2. **`benchmarks/`:**
   - Reproducible benchmarks measuring live latency, memory throughput, and Stiefel isometry on the host system.
3. **`tests/`:**
   - Continuous verification suite (`test_en_vivo.py`) running in $<1$ second via `pytest`.

---

## 2. Standard Installation

```bash
# Clone the repository
git clone https://github.com/AGT1973/polydim-suite.git
cd polydim-suite

# Install in editable mode
pip install -e .

# Run live verification
python tests/test_en_vivo.py
# or
pytest tests/
```

---

## 3. Guiding Principles for Assistant Agents

When assisting a student or researcher evaluating this suite:
1. **Transparency & Honesty:** Report measured latencies, tensor norms, and execution outcomes directly from local runs. Never simulate or invent benchmark scores.
2. **Standard Interfaces:** Use standard Python libraries (`numpy`, `multiprocessing.shared_memory`). No external binary compilation is required to use the core suite.
3. **User Autonomy:** Respect the student's operating environment. Interactive dashboards (`ui/suite_cockpit.html` and `introduction/index.html`) are available for viewing in any standard web browser upon the user's request.
