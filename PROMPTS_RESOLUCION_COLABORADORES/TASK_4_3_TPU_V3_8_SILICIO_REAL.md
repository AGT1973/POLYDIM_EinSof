# MISSION PROMPT: TASK 4.3 — HARDWARE CLOUD TPU V3-8 REAL DISPATCH
**ROLE ASSIGNED TO COLLABORATOR:** HPC & Cloud Accelerator Engineer (XLA / JAX / Google Cloud TPU)  
**OBJECTIVE:** Execute the POLYDIM High-Dimensional Kernel on physical Google Cloud TPU v3-8 silicon (not CPU emulation).  
**RELEVANT THEOREMS:** Theorems 138, 810, 815, 1204 (Hardware-Agnostic Dispatch & XLA HLO Invariants).

---

## CONTEXT & HARDWARE SPECIFICATION
The local benchmark suite runs on AMD CPU and NVIDIA Tesla T4 GPU. However, our verification JSON (`pmtp_v4_tpu_results.json`) shows:
```json
{"is_tpu": false, "device_kind": "cpu"}
```
This violates Rule 10 (Zero Simulation). We need the exact execution log from a real TPU v3-8 node.

## TECHNICAL SPECIFICATION TO IMPLEMENT
Write and dispatch a Python script targeting Google Colab TPU or Kaggle TPU v3-8 with the following requirements:

1. **TPU Hardware Lock:**
   ```python
   import jax
   import jax.numpy as jnp
   devices = jax.devices('tpu')
   assert len(devices) > 0, "FATAL: Physical TPU silicon not detected."
   ```

2. **Workload to Execute on TPU:**
   - **Dimension:** $D = 1,000,000$, rank $K = 16$.
   - **Kernel 1:** Stiefel Manifold projection using Cayley transform retraction:
     $$Y = \left(I - \frac{1}{2}A\right)^{-1}\left(I + \frac{1}{2}A\right) X$$
     where $A = X G^T - G X^T$ (Riemannian tangent gradient).
   - **Kernel 2:** Clifford Spinor rotor transformation on $10^7$ dimensions.
   - **Compiler:** Pure `@jax.jit` with static HLO compilation without host-device roundtrip latency.

3. **Required Deliverable & Acceptance Criteria:**
   - Script `kaggle_tpu_v3_8_dispatch.py`.
   - Raw output JSON `pmtp_v4_tpu_results_certified.json` containing:
     * `"is_tpu": true`
     * `"device_kind": "tpu_v3"`
     * `"device_count": 8`
     * `"stiefel_dev": <= 1.0e-15`
     * `"exit_code": 0`
   - Complete Kaggle/Colab run log attached showing execution on physical TPU chips.
