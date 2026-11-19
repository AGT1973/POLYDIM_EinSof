---
name: manifold-verify
description: Manifold & Isometry Verifier on physical silicon. Measures the exact isometry defect ||W^T W - I_k||_inf on the Stiefel manifold S^{D-1}, confirms machine precision (<= 1e-15), tests continuous latent projection vs discrete token collapse, and checks native C++/PyTorch kernels with Exit Code 0. Invoked with /verify-manifold or /stiefel.
---

# Manifold & Isometry Verifier — Action `/verify-manifold` (`/stiefel`)

Rigorous mathematical and silicon proof of continuous manifold geometry on your machine.

---

## Why this Skill Exists

In POLYDIM and EinsofOS, we do not believe in theoretical claims that haven't been tested in physical silicon:
- **Rule 1 (Radical Honesty):** A result only counts if it produces an **Exit Code 0** and a raw silicon log.
- **Rule 19 (Silicon Proof Requirement):** Every theorem must be verified on hardware.
- **Rule 19.2 (Continuous Latent Superiority):** Discrete autoregressive tokens collapse in deep circuits, whereas Stiefel polar retraction $S^{D-1}$ holds machine-precision fidelity ($0.9999999999999996$, isometry defect $\le 5 \times 10^{-15}$).

---

## How It Works for Students

You don't need to write matrix algebra scripts.
Just type:
```text
/verify-manifold
```
Or specify dimensions:
```text
/verify-manifold D=2048 k=16
```

The underlying script (`skills/scripts/manifold_verifier.py`) runs:
1. Polar retraction $W = X (X^T X)^{-1/2}$ in double precision (`float64`).
2. Neumaier accumulator verification to eliminate floating-point roundoff drift.
3. Checks $\|W^T W - I_k\|_\infty \le 5 \times 10^{-15}$.
4. Returns the exact silicon proof tuple:
   ```text
   [PASS] Exit Code 0 | Stiefel St(16, 2048)
   Isometry Defect: 2.34e-16 (TIER_MACHINE_EPS_16)
   Neumaier Residual: 0.00e+00
   Execution Time: 8.4 ms
   ```
