# POLYDIM REPRODUCIBILITY GUIDE: STUDENT HARDWARE BENCHMARKING

## 1. PURPOSE & GUARANTEE OF RIGOR
Under **Rule 10 (Empirical Veto)** and **Rule 34 (Daily Pedagogical Rigor)**, no benchmark or performance metric is published without a concrete reproducibility script and verifiable terminal output (Exit Code 0).

This guide provides step-by-step instructions for running the complete POLYDIM V26155 Conformance Suite on baseline consumer hardware:
* Dual-core / Quad-core AMD APU (e.g., AMD A4, Ryzen 3/5)
* Intel Core i3 / i5 / i7 / i9 (8th Gen+)
* Apple Silicon (M1/M2/M3) via Rosetta 2 or native arm64
* Standard student laptops with 4 GB to 16 GB of DDR3/DDR4/DDR5 RAM.

---

## 2. PREREQUISITES & ENVIRONMENT SETUP

### 2.1 Dependencies
POLYDIM V26155 requires only Python 3.10+ and standard numerical scientific libraries:
```bash
pip install numpy scipy
```
Optional (for native acceleration, auto-fallback to NumPy reference if absent):
* WinLibs GCC 14.2 / Clang 18 (C++20)
* Rust toolchain (cargo, rustc 1.80+)

### 2.2 Deterministic Seeds, Tolerances & Numerical Policies
To guarantee exact reproducibility across heterogeneous environments:
* **Deterministic Seed:** All random orthogonal initializations use a fixed seed (`seed = 42` or deterministic Householder QR).
* **Orthogonality Tolerance Threshold:** Correctness requires $\|X^\top X - I_k\|_F \le \tau_{\mathrm{orth}} = 10^{-14}$ for standard condition numbers ($\kappa \approx 1$).
* **Separation of Correctness vs. Performance:** Silicon conformance (Exit Code 0) strictly enforces the 29 mathematical invariants (aliasing protection, NaN/subnormal immunity, dimension checks, orthogonality). Timing and latency metrics are reported for diagnostic profiling and do not invalidate correctness on legacy student CPUs.

---

## 3. EXECUTING THE CONFORMANCE SUITE

Run the test suite directly from the command line:

```bash
python E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26155\polydim_v26155_monolito.py
```

### 3.1 Expected Output & Reference Metrics
When executed on standard CPU host hardware, the suite performs 29 deterministic checks. The expected terminal log must match the following output:

```text
========================================================================================
POLYDIM V26155 UNIVERSAL SILICON ORCHESTRATOR & PMTP BUS CONFORMANCE
========================================================================================
Hardware Profile: Vendor=generic, Target=cpu_numa, MemoryClass=3
Active Backend:   rust_native (or reference)
Device Name:      CPU Generic Host (x2)
Available:        reference, cpp, rust, rust_native, cpp_native
----------------------------------------------------------------------------------------
  [PASS] PMTP descriptor fixed width (88B) — size=88 bytes
  [PASS] PMTP descriptor roundtrip — exact binary reconstruction
  [PASS] PMTP zero-copy shared memory mapping — val=42.26155
  [PASS] PMTP AnchoredArray lifetime anchor (Theorem 691) — slab owner correctly referenced in ndarray view
  [PASS] PMTP path traversal rejection — regex validation passed
  [PASS] PMTP negative offset rejection — offset >= 0 enforced
  [PASS] PMTP object dtype rejection — POD types enforced
  [PASS] Differential Cayley Oracle DxD verification — diff_vs_oracle=3.261e-16, displacement=5.295e-01
  [PASS] Stiefel Cayley small solve — ortho_defect=1.110e-15
  [PASS] Stiefel orthogonality machine precision — max_defect=1.110e-15
  [PASS] Gram drift preservation — drift=5.551e-16
  [PASS] Vertical tangent component solve — defect=7.772e-16
  [PASS] Asymptotic scale D=10,000, K=8 solve — time=13.30 ms
  [PASS] Scale Invariance (Z*1e154, t*1e-154) — diff=5.551e-17
  [PASS] Scale Invariance (Z*1e-200, t*1e200) — diff=8.327e-17
  [PASS] Strict dtype contract (float64 only) — rejected bool/int32/float32/complex128
  [PASS] Strict 2D shape contract — rejected 1D array
  [PASS] Read-only output buffer rejection — rejected non-writeable out
  [PASS] Non-tangent input rejection — rc=NOT_TANGENT
  [PASS] Non-orthonormal X rejection — rc=NOT_UNIT
  [PASS] Non-finite step rejection — rc=INVALID_ARGUMENT
  [PASS] Dimension mismatch rejection — rc=DIMENSION_MISMATCH
  [PASS] Zero step identity preservation — diff=0.000e+00
  [PASS] Negative step retraction — ortho_defect=1.332e-15
  [PASS] IEEE-754 binary64 subnormal preservation — val=1.000e-318
  [PASS] Ultra-extreme step t=1e200 adaptive stability — ortho_defect=6.661e-16
  [PASS] Polar QR fallback execution verification — fallback_engaged=True, defect=6.661e-16
  [PASS] Input aliasing protection (X shares memory with Z) — rc=ALIAS_VIOLATION
  [PASS] Output buffer aliasing protection (out aliases X) — rc=ALIAS_VIOLATION
----------------------------------------------------------------------------------------
Summary: 29 / 29 checks PASSED.
CONFORMANCE RESULT: SUCCESS (Exit Code 0)
```

---

## 4. TROUBLESHOOTING & EDGE CASES

| Error / Warning | Root Cause | Solution |
| :--- | :--- | :--- |
| `ALIAS_VIOLATION` | Arrays pass overlapping memory views | Monolith strictly rejects aliased pointers; allocate distinct arrays. |
| `NOT_UNIT` | Matrix $X$ violates $X^\top X = I_k$ | Re-orthonormalize using `scipy.linalg.qr(X, mode='economic')[0]`. |
| `NOT_TANGENT` | Tangent vector violates $X^\top Z + Z^\top X = 0$ | Project $Z \to T_X \mathrm{St}(n, k)$ via $Z - X \mathrm{sym}(X^\top Z)$. |
| High Latency ($> 100\text{ ms}$) | CPU thermal throttling or energy saver mode | Connect laptop to AC power; set power profile to High Performance. |
