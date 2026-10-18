<!-- PROMPT BRECHA 4: CLOUD TPU V3-8 PHYSICAL DISPATCH & PROOF OF SILICON -->
<!-- PROTOCOLO: Regla 15 (Inglés formal), Regla 10 (Zero Simulation), Regla 27 (Hardware Agnosticism: XLA/JAX HLO) -->
<!-- TARGET API: Perplexity Sonar-Pro / Claude 3.7 Sonnet / Moonshot Kimi k3 -->

# MISSION CONTEXT: GOOGLE CLOUD TPU V3-8 VERIFICATION VIA KAGGLE/XLA
You are a High-Performance Computing (HPC) Specialist with deep expertise in Google Cloud TPUs, XLA Compiler internals, and JAX graph optimization.

## THE PROBLEM
POLYDIM's multi-silicon benchmark table currently contains:
- CPU Local (AMD A4-6300): Verified Exit Code 0, 9/9 tests passed.
- GPU Cloud (NVIDIA Tesla T4 x2 on Kaggle): Verified Triton SRAM 139.78 GB/s, Stiefel dev 2.22e-16.
- Cloud TPU: The repository contains `pmtp_v4_tpu_results.json`, but inspection reveals `is_tpu: false` and `device_kind: "cpu"`. This violates Rule 10 (Empirical Veto). The thesis requires physical proof on Google Cloud TPU hardware (TPU v3-8).

## YOUR MANDATE
Construct the complete dispatch bundle for Kaggle TPU execution:

### 1. `kaggle_tpu_worker.py`
A stand-alone, zero-host-latency JAX script targeting Kaggle's TPU v3-8 environment:
- Forces TPU backend initialization: `jax.devices('tpu')`. Fails immediately if `len(devices) == 0`.
- Compiles a static HLO graph for:
  1. High-dimensional Stiefel retraction via Cayley transform: $Y = (I - \frac{1}{2}A)^{-1}(I + \frac{1}{2}A)X$ for $D = 1,000,000$ and $K = 16$.
  2. Orthogonality drift calculation: $\|Y^T Y - I_K\|_F$.
  3. Clifford spinor rotor transformation over $10^7$ dimensions.
- Captures raw execution metrics: Device Kind, Device Count, HLO Operation Count, Execution Latency (ms), and Max Memory Bandwidth.
- Generates `pmtp_v4_tpu_results_certified.json` containing `is_tpu: true` and the raw hardware timestamp.

### 2. `kaggle_push_tpu.py`
Automated runner using the official Kaggle CLI to:
- Push `kaggle_tpu_worker.py` to Kaggle Kernel `tradingnewtech/polydim-tpu-v3-8-bench`.
- Enable TPU v3-8 accelerator via `kernel-metadata.json` (`"enable_tpu": true`).
- Poll until status is `COMPLETE` and download the verified execution log with Exit Code 0.
