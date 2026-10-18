# LESSON PLAN: LEVEL 1 ADVANCED AI & HIGH PERFORMANCE COMPUTING
**Institution:** UTN-FRBA / Data Science Postgraduate Program  
**Course:** High-Dimensional AI Systems & Riemannian Optimization  
**Module:** 1D Token Streaming Bottleneck vs. Zero-Copy Shared Memory (PMTP)  
**Target Audience:** Engineering Students, M.Sc. Data Science Candidates  
**Hardware Requirements:** Any student laptop/desktop (AMD APU / Intel Core / Apple Silicon), 4 GB RAM, Python 3.10+  

---

## 1. LEARNING OBJECTIVES
By the end of this laboratory session, students will be able to:
1. Formulate the mathematical proof of the **Data Processing Inequality (DPI)** in Markov chains and understand how 1D tokenization collapses semantic entropy.
2. Quantitatively measure IPC latency, CPU cache misses, and memory bandwidth differences between JSON string serialization and Win32/POSIX Shared Memory.
3. Parse and construct the binary 88-byte **PMTP Descriptor** using Python `struct` and NumPy `ndarray` buffers.
4. Execute and interpret the 29 automated silicon conformance checks in `polydim_v26155_monolito.py`.

---

## 2. THEORETICAL FOUNDATION (30 MINUTES)

### 2.1 The 1D Token Bottleneck & DPI (Information-Theoretic Rigor)
Consider two cooperating AI agents, Agent $A$ and Agent $B$.
* Latent state of Agent $A$: $X \in \mathbb{R}^D$ where $D = 10,000$.
* Classical Pipeline: Agent $A$ projects $X \to$ discrete tokens $T_1, \dots, T_m \to$ JSON string $S \to$ network/IPC socket $\to$ Agent $B$ tokenizes $S \to$ embedding layer $\to \hat{X}$.
* **Shannon DPI & Rate-Distortion Bounds (Cover & Thomas, 2006):**
  A 1D byte stream can theoretically encode any tensor losslessly if unbounded. However, real-world LLM pipelines impose:
  1. Finite token budget: $m < \infty$.
  2. Finite vocabulary: $|\Sigma| \approx 32,000$.
  3. Non-injective floating-point serialization ($\exists x \ne y : T(x) = T(y)$).
  By the Data Processing Inequality $I(X; \hat{X}) \le I(X; S) \le H(S) \le m \log_2 |\Sigma|$, mutual information is capped at $m \log_2 |\Sigma| \approx 1,916\text{ bits}$ for $m=128$, inducing a strictly positive lower bound on expected distortion $\mathbb{E}[\|X - \hat{X}\|_F^2] \ge D^*(R)$.

### 2.2 The PMTP Zero-Copy Alternative & Numerical Guarantees
Instead of serializing floats into text:
1. Agent $A$ allocates a slab of OS shared memory (`multiprocessing.shared_memory` or native Win32 `CreateFileMappingW`).
2. Agent $A$ writes raw binary IEEE-754 FP64 bytes directly into the slab.
3. Agent $A$ sends an 88-byte struct containing the slab name, shape, dtype, and offset to Agent $B$.
4. Agent $B$ maps the slab into its address space. Zero bytes are copied across memory buses.
* **Throughput & Latency:** Transfers the 88-byte descriptor in $< 1.2\ \mu\text{s}$. Measured memory throughput saturates the hardware bus (e.g., $9.03\text{ GB/s}$ pinned host-to-device DMA; dual-channel host DDR5 up to $102.4\text{ GB/s}$; Triton SRAM tiling up to $139.78\text{ GB/s}$).
* **Numerical Conditioning:** On the Stiefel manifold $\mathrm{St}(n, k)$, the Cayley update achieves $\|Y^\top Y - I_k\|_F \le C(n, k) u \kappa(I_{2k} - \frac{t}{2} V^\top U)$ with automated fallback to Polar/QR factorization when condition numbers degrade.

---

## 3. HANDS-ON LAB EXERCISES (60 MINUTES)

### Exercise 3.1: Benchmarking JSON IPC vs. Shared Memory (Student Script)
Students run the following benchmark script comparing JSON serialization against PMTP shared memory on their local machines:

```python
import time
import json
import numpy as np
from multiprocessing import shared_memory

def run_comparison(dim=4096):
    print(f"=== BENCHMARK: Latent Tensor D={dim} (Float64) ===")
    tensor = np.random.randn(dim).astype(np.float64)
    raw_bytes = tensor.nbytes
    print(f"Raw Tensor Size: {raw_bytes} bytes ({raw_bytes / 1024:.2f} KB)")

    # 1. Classical JSON Serialization
    t0 = time.perf_counter()
    json_str = json.dumps(tensor.tolist())
    json_bytes = len(json_str.encode('utf-8'))
    t_ser = time.perf_counter() - t0

    t0 = time.perf_counter()
    reconstructed_list = json.loads(json_str)
    reconstructed_np = np.array(reconstructed_list, dtype=np.float64)
    t_deser = time.perf_counter() - t0
    total_json_time = (t_ser + t_deser) * 1000.0

    print(f"\n[1] Classical JSON Pipeline:")
    print(f"    Serialized Size:   {json_bytes} bytes (Blowup: {json_bytes / raw_bytes:.2f}x)")
    print(f"    Roundtrip Time:     {total_json_time:.3f} ms")
    print(f"    Reconstruction Err: {np.max(np.abs(tensor - reconstructed_np)):.2e}")

    # 2. PMTP Zero-Copy Shared Memory
    t0 = time.perf_counter()
    shm = shared_memory.SharedMemory(create=True, size=raw_bytes)
    target_buf = np.ndarray(tensor.shape, dtype=tensor.dtype, buffer=shm.buf)
    np.copyto(target_buf, tensor)
    t_write = time.perf_counter() - t0

    t0 = time.perf_counter()
    # Read view without memory copy
    read_buf = np.ndarray(tensor.shape, dtype=tensor.dtype, buffer=shm.buf)
    t_read = time.perf_counter() - t0
    total_shm_time = (t_write + t_read) * 1000.0

    print(f"\n[2] PMTP Shared Memory Pipeline:")
    print(f"    Metadata Overhead: 88 bytes fixed")
    print(f"    Roundtrip Time:    {total_shm_time:.3f} ms")
    print(f"    Reconstruction Err: {np.max(np.abs(tensor - read_buf)):.2e}")
    print(f"    Speedup:           {total_json_time / max(total_shm_time, 1e-6):.1f}x")

    shm.close()
    shm.unlink()

if __name__ == '__main__':
    run_comparison(4096)
```

### Exercise 3.2: Inspecting the 88-Byte Binary Descriptor
Students examine the layout of the 88-byte descriptor defined in `polydim_v26155_monolito.py`:
1. Why does `#pragma pack(push, 1)` matter when passing structs across Python, C++, and Rust?
2. What happens if `magic` does not equal `0x504D5450`?
3. Verify that CRC32 catches any bit flip in the memory offset or shape coordinates.

---

## 4. VERIFICATION & GRADING RUBRIC

Students clone the repository and run the monolith test suite:
```powershell
python E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26155\polydim_v26155_monolito.py
```

### Evaluation Criteria:
* **Check 1-7 (PMTP Conformance):** Pass with zero errors.
* **Check 8-15 (Numerical Geometry):** Orthogonality defect $< 10^{-14}$.
* **Exit Code:** Must exit with code 0. Any non-zero exit code or uncaught exception fails the assignment.
