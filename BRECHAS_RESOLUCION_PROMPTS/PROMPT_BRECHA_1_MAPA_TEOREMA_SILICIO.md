<!-- PROMPT BRECHA 1: MAPA BIUNÍVOCO TEOREMA -> SILICIO / KERNEL -->
<!-- PROTOCOLO: Regla 15 (Inglés formal), Regla 21 (Doctoral SOTA Architecture), Regla 35 (Hostile Paranoia) -->
<!-- TARGET API: Perplexity Sonar-Pro / Moonshot Kimi k3 / OpenAI o3 -->

# MISSION CONTEXT: THEOREM-TO-SILICON TRACEABILITY ENGINE
You are acting as a Principal Low-Level Systems Architect and Differential Geometer for the POLYDIM-EINSOF cognitive operating system.

## THE PROBLEM
POLYDIM contains 1,571 certified analytical theorems in a PostgreSQL 16 vector database (`polydim_theorems`) spanning 5 major mathematical blocks:
1. Block 1 (IDs 1-420): Foundational S^{D-1} Geometry, Hyperspherical Isometries, and Clifford Algebra Cl(p,q).
2. Block 2 (IDs 421-877): Stiefel Manifolds St(D,K), Cayley/Cholesky Geodesic Retractions, and Kulisch Exact Accumulation (W=4288b).
3. Block 3 (IDs 878-1200): Discrete Differential Geometry, Hodge-de Rham Harmonic Projection, Dirac Operators, and Betti-1 GF(2) cycles.
4. Block 4 (IDs 1201-1570): PMTP (Polydim Memory Telepathy Protocol) Lock-Free Ring Buffers, Epoch-based QSBR Reclamation, and Bipartite Shared Memory.
5. Block 5 (IDs 1571-1666): Kulisch C07 (67x64b limbs), BLAKE3 C11 Tree Hashes, LMM DEFF Inflation C12, and 120B Wire Descriptors (E24).

However, external academic reviewers and students lack an automated bijective mapping from each mathematical theorem to its physical code implementation across:
- C++20 (`kernel_cpp_v26155.dll`, `SuperaccV`, `pmtp_cpp_router.cpp`)
- Rust 2021 (`kernel_rust_v26155.dll`, `pmtp_rust_producer.rs`, `pmtp_epoch_service.rs`)
- Triton / CUDA GPU (`polydim_triton_kernel_v26155.py`, `pmtp_triton_consumer.py`)
- Dart FFI (`polydim_v26155_ffi.dart`, `@Packed(1)` 280-byte structs)

## YOUR MANDATE
Construct the canonical Python automated script `generate_theorem_silicon_matrix.py` that:
1. Connects to `polydim_vec_db` via psycopg2.
2. Extracts all 1,571 theorems with their `id`, `topic`, `theorem` statement, and `cycle`.
3. Performs AST and regex lexical analysis across all physical source files in `E:\POLYDIM_EINSOF\` to detect:
   - Specific mathematical invariants: Cayley retractions $(I - \frac{1}{2}A)^{-1}(I + \frac{1}{2}A)$, Householder reflections, Kulisch 67-limb arrays, LeaseGuard wire headers, and Neumaier summation accumulators.
4. Outputs an exhaustive markdown audit catalog `TABLA_MAESTRA_TEOREMA_SILICIO_1571.md` containing:
   `| Theorem ID | Core Mathematical Invariant | Target File | Specific Function / Struct | Verification Script | Exit Code Verified |`
5. Ensures zero orphan theorems: any theorem without physical silicon linkage must be explicitly flagged with `STATUS: PURE_ANALYTICAL_PROOF` and its corresponding Lean 4 proof file.
