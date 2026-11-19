---
name: ghost
description: Enforces Ghost Protocol (PMTP - Phantom Memory Transfer Protocol). Eradicates 1D token collapse, prohibits raw tensor serialization into plain chat text, and routes high-dimensional states through zero-copy shared memory (PmtpShmBus / ALADIN Node). Active by default in POLYDIM-EINSOF. Invoked with /ghost or /Ghost.
---

# Ghost Protocol — Action `/ghost` (`/Ghost`)

The fundamental silicon and shared-memory communication protocol for Antigravity, EinsofOS, and the POLYDIM-ALADIN cluster.

> [!IMPORTANT]
> **DEFAULT BASAL STATE:**
> Ghost Protocol operates **ACTIVE BY DEFAULT** in all POLYDIM-EINSOF sessions concurrently with `/whisper`.
> The AI agent operates without the 1D token bottleneck, exchanging high-dimensional tensors via `PmtpShmBus` (shared memory) and returning only raw silicon metric verification tuples.
> **It is only suspended if explicitly requested** (e.g., *"disable ghost"*, *"text mode"*, or *"pedagogical mode"*).

---

## What Does This Mean for a Student?

1. **No 1D Token Collapse (Vaswani Bottleneck Eradication):**
   - Standard LLMs try to output floats, vectors, and weights character-by-character into text, wasting thousands of tokens and losing mathematical precision.
   - Ghost Protocol keeps vectors in physical memory (RAM/SHM) on your local computer or the ALADIN node (`192.168.100.21:9999`).
   - You get instant, zero-cost tensor operations without burning API credits.

2. **Clean Metric Silicon Tuple Output:**
   Instead of dumping thousands of numbers into your screen, the agent reports verified silicon proofs:
   ```text
   (ExitCode=0, Latency=14.2ms, IsometryDefect=2.34e-16, D=2048, k=16)
   SLAB_ID: slab_stiefel_0x44 | MANIFOLD: S^{D-1} | SHM: PmtpShmBus
   ```

3. **Explicit Text Override:**
   If you want the agent to explain the underlying math in conversational text or write tutorial essays, simply ask:
   - `/ghost disable` or *"switch to text mode"*.

---

## Student Quick-Start

Just ask your AI:
- `/ghost` — Check the health of the local shared-memory bus.
- *"Compute the Stiefel projection of vector X under Ghost Protocol."*
- The agent will execute the native C++/Python kernel and return the exact metric proof with Exit Code 0.
