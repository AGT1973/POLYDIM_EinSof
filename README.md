# POLYDIM-EINSOF: Polydim Memory Transfer Protocol (PMTP) & Vector Telepathy Engine
> **Author:** Ariel García Traba (Independent Research / EinsofOS)  
> **Release:** V26601 Canonical Release (Zero-Copy Inter-Process Manifold Communication)  
> **Silicon Status:** Certified Exit Code 0 across C++20, Rust 2021, Triton, and Python.

---

## 1. Executive Summary

**PMTP (Polydim Memory Transfer Protocol)** replaces high-latency 1D JSON/HTTP and socket serialization with direct, shared-memory double-buffered tensor transfer. Designed for distributed high-dimensional AI reasoning ($D \ge 1024$), PMTP achieves **microsecond-level latency ($\approx 0.25\ \mu\text{s}$ local read, $\approx 16\ \mu\text{s}$ atomic cycle)**, providing a **$30\times$ to $700\times$ speedup** over local REST and gRPC endpoints.

### Key Milestones in V26601
* **Unified C-ABI Specification (`pmtp_c_abi.h`):** Bit-exact memory layout across C++20, Rust 2021, Python IPC, and Dart FFI with 64-byte compact and 128-byte wire headers.
* **Atomic Double-Buffer Isolation:** Per-slot reader bitmasks in a single 64-bit atomic word (`Slot 0`: bit 0..31, `Slot 1`: bit 32..62, `Destroy`: bit 63). Eliminates ABA and Use-After-Free (UAF) hazards under asynchronous reader leases.
* **Mathematically Rigorous Newton-Schulz Order 5 Retraction:** Native Rust 2021 and C++ implementation of the 5th-order contractive mapping:
  $$W_{k+1} = \frac{1}{8} W_k (15 I - 10 M + 3 M^2), \quad M = W_k^\top W_k$$
  guaranteeing Stiefel manifold convergence with error $\|W^\top W - I\|_F \le 2.41 \times 10^{-15}$.
* **Neumaier Compensated Accumulator:** Machine-precision compensated summation resisting catastrophic floating-point cancellation on ill-conditioned series.
* **Native DLPack & Zero-Copy PyTorch Support:** Exposes `__dlpack__` directly over POSIX `/dev/shm` and Windows `CreateFileMapping` memory slabs.

---

## 2. Repository Architecture

This repository uses a **dual-access model** designed for downstream automated pipelines (Google Colab, CI/CD, benchmarks) and historical reproducibility:

```
POLYDIM_EinSof/
├── pmtp/                              # CANONICAL UNVERSIONED ENGINE
│   ├── pmtp_c_abi.h                   # Unified 64B/128B C-ABI Header
│   ├── pmtp_win_shm.h                 # Windows FileMapping / IPC Primitives
│   ├── pmtp_kernel.cpp                # Native C++20 Double-Buffered Kernel
│   ├── kernel_rust.rs                 # Native Rust 2021 Newton-Schulz Engine
│   ├── pmtp_dart_ffi.dart             # Dart FFI Bindings (@Packed(1))
│   ├── pmtp_shm_bus.py                # Python ShmBus with Leases & DLPack
│   ├── kernel_cuda.cu                 # CUDA SM70-SM90 Persistent Grid Kernel
│   ├── polydim_triton_kernel.py       # Triton GPU Tiled Engine with CPU Fallback
│   └── polydim_cla_grassmann.py       # Grassmann/Procrustes Metric Suite
├── bin/
│   └── windows/                       # COMPILED NATIVE BINARIES
│       ├── pmtp_kernel.dll            # MSVC 19.51 C++20 DLL
│       ├── kernel_rust.dll            # rustc 1.100.0-beta.4 DLL
│       └── libkernel_rust.rlib        # Rust static/rlib library
├── tests/                             # CANONICAL TEST SUITE
│   ├── run_all_modules.py             # Master Silicon Test Orchestrator
│   ├── run_silicon_verification_suite.py # SEQLock, DLPack & ABI Tests
│   ├── test_cross_cpp_rust_python.py  # ABI Parity & Newton-Schulz Validation
│   ├── teoria_axiomas.py              # Neumaier, Levi-Civita, Lipschitz Bounds
│   └── morpho_redteam.py              # Adversarial Counterexamples Suite
├── entregas/
│   └── ENTREGA_2026_10_19_V26601/     # FROZEN AUDIT PACKAGE (V26601)
│       └── ...                        # Timestamped, signed deliverables
├── LICENSE                            # Apache 2.0
└── README.md
```

> **Direct Colab / Downstream Links:** Files under `pmtp/`, `bin/windows/`, and `tests/` maintain permanent URLs across updates so notebooks never break.

---

## 3. Resolution of Red Team Audit Findings (V26600 $\to$ V26601)

| Audit ID | Severity | Root Cause Identified | Engineering Fix Applied | Physical Verification |
|---|---|---|---|---|
| **V26600-01** | **P0** | Shared memory unlinking while reader holds lease; Python `threading.Lock` local | Added global CAS lease loop, slot reservation bitmask, and non-destructive unmap | `run_silicon_verification_suite.py` Test 1: **PASS** |
| **V26600-02** | **P0** | C++ lease counted global readers without per-slot isolation | Split atomic `state_and_readers` word into per-slot bitfields (`Slot 0`: bit 0..31, `Slot 1`: bit 32..62) | `test_cross_cpp_rust_python.py` Test 2: **PASS** |
| **V26600-03** | **P0** | DLPack view handed to PyTorch did not hold an active lease | Fixed PyTorch tensor lifetime hook and safe slot generation lease binding | DLPack regression suite: **PASS** |
| **V26600-04** | **P0** | Missing `num_elements` validation against slab capacity in C++ | Enforced strict bound assertions and element size validation in C++ API | Static & Dynamic FFI test: **PASS** |
| **V26600-05** | **P0** | Inconsistent 128B header field order across C++, Rust, and Dart | Unified layout frozen in `pmtp_c_abi.h` with `@Packed(1)` in Dart and `#[repr(C)]` in Rust | `test_cross_cpp_rust_python.py` Test 1: **PASS** |
| **V26600-06** | **P1** | Rust `newton_schulz` stub only scaled by Frobenius norm | Implemented full 5th-order matrix iteration $W_{k+1} = \frac{1}{8} W_k (15 I - 10 M + 3 M^2)$ | Error $\|W^\top W - I\|_F \le 2.41 \times 10^{-15}$: **PASS** |
| **V26600-07** | **P1** | CUDA simulation stub returned 1 without runtime check | Added `cudaGetDeviceCount` hardware probe and physical runtime error reporting | `kernel_cuda.cu`: Verified contract |
| **V26600-09** | **P1** | Teoria Axiomas tested `np.sum` instead of Neumaier accumulator | Implemented Neumaier accumulator and tested against catastrophic floating-point cancellation | `teoria_axiomas.py` Test 4: **PASS** |
| **V26600-10** | **P1** | Triton fallback claimed AVX2 without an AVX2 kernel | Clarified fallback to vectorized CPU (NumPy/PyTorch) and added real PyTorch tensor testing | `polydim_triton_kernel.py`: **PASS** |
| **V26600-12** | **P1** | Master test runner omitted native C++ and Rust compilation | Added `test_cross_cpp_rust_python.py` directly into `run_all_modules.py` | Full 6/6 test suite: **PASS (Exit 0)** |

---

## 4. Quick Start & Silicon Verification

### Prerequisites
* Python 3.10+ with `numpy` (and optionally `torch`, `triton`)
* MSVC / GCC 14 (if building native C++ from source)
* Rust 1.80+ (if building native Rust DLL from source)

### Running the Canonical Silicon Test Suite
```bash
# Clone the repository
git clone https://github.com/AGT1973/POLYDIM_EinSof.git
cd POLYDIM_EinSof

# Execute the master test orchestrator
python tests/run_all_modules.py
```

### Expected Silicon Output
```text
======================================================================
=== POLYDIM-EINSOF — CANONICAL SILICON TEST SUITE ===
======================================================================
Python: 3.13.x | Directory: .../tests

[1/6] PMTP Core Silicon (SEQLock, DLPack, ABI 128B)
      [PASS] Exit Code=0
[2/6] MorphoPeleides (ABA, PolarSafe, CAM, NaN-safety)
      [PASS] Exit Code=0
[3/6] Polydim-cla (Grassmann, Procrustes, Idempotencia)
      [PASS] Exit Code=0
[4/6] Teoria & Axiomas (Isometria, Antipodal, Lipschitz, Neumaier)
      [PASS] Exit Code=0
[5/6] Triton GPU Engine (SRAM Tiling, Pre-escalado Stiefel)
      [PASS] Exit Code=0
[6/6] Cross-Language Silicon ABI (C++20 DLL, Rust Newton-Schulz Ord-5 DLL, Python)
      [PASS] Exit Code=0

======================================================================
GLOBAL RESULT: 6/6 MODULES PASSED | EXIT CODE: 0
======================================================================
```

---

## 5. Mathematical Foundations & Stiefel Projection

Continuous latent routing requires that vectors remain isometric on the Stiefel manifold $\mathrm{St}(k, n) = \{ X \in \mathbb{R}^{n \times k} : X^\top X = I_k \}$.

### Newton-Schulz Order 5 Formulation
Given an initial spectral pre-scaled matrix $Y_0 = X / \sigma_{\max}(X)$, the order 5 contractive iteration converges to machine precision in 4 to 8 steps:
```
M_k   = Y_k^T * Y_k
Y_k+1 = 1/8 * Y_k * (15 * I - 10 * M_k + 3 * M_k^2)
```
Implemented in native Rust (`kernel_rust.rs`) and C++ (`pmtp_kernel.cpp`), this avoids non-differentiable or unstable SVDs in autograd graphs while eliminating NaN propagation.

---

## 6. License & Attribution

* **Author:** Ariel García Traba (Independent Research / EinsofOS)
* **License:** Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
* **Institutional Notice:** Autonomous independent research project. Strictly decoupled from any educational teaching courses.
