# DICTAMEN DE ARBITRAJE FORMAL PERPLEXITY SONAR-PRO — ETAPA 18
Fecha: 2026-10-10 | Motor: Perplexity Sonar-Pro | Ámbito: Hardening Exhaustivo POLYDIM

## Subfase 1.4: Acumulador Kulisch Exacto W=4288b y Fuzzing IEEE 754 Subnormal (EVAL_SUBFASE_1_4)

1. **VERDICT — CLARIFIED / REFUTED**

- **CLARIFIED:** A 4,288-bit Kulisch-style accumulator is a recognized design point for exact binary64 dot products, but the quoted formula \(W(N)=4197+\lceil\log_2N\rceil\) does not by itself establish that 4,288 bits is sufficient for \(N=2^{64}\). The answer depends on whether the width includes sign, guard, carry, and endpoint conventions.
- **REFUTED:** The claimed bound is internally inconsistent with the stated conclusion. Substituting \(N=2^{64}\) gives
  \[
  W(2^{64})=4197+64=4261,
  \]
  not 4,288. That leaves 27 bits of apparent margin, but only if 4,197 is already a complete exact-product span and the accumulator’s signed representation has been defined correctly.
- **CLARIFIED:** The use of an integer product path is appropriate for exactness, but `_mm512_mul_epu32` does not multiply arbitrary 64-bit significands. It multiplies the low 32-bit halves of eight lanes, producing eight 64-bit products. A complete binary64 significand product therefore requires decomposition into 32-bit limbs and exact cross-term accumulation.
- **REFUTED:** “No intermediate carry explosion” does not follow merely from using 32-bit buckets. Without a proven per-bucket occupancy bound, 10 million deposits can overflow a 32-bit bucket.
- **REFUTED:** Cache-line alignment and slice-major layout do not, by themselves, eliminate 4K aliasing. They can reduce particular conflict patterns, but 4K aliasing is determined by page-offset congruence among simultaneously accessed addresses and by the actual access schedule.

2. **RIGOROUS MATHEMATICAL & ARCHITECTURAL ANALYSIS**

### Exact binary64 product range

A finite binary64 value has the form

\[
x=(-1)^s M2^e,
\]

where the significand \(M\) contains up to 53 significant bits, while subnormals use a fixed quantum of \(2^{-1074}\). The smallest positive binary64 value is \(2^{-1074}\), and the largest finite value is approximately \(2^{1024}(2-2^{-52})\).

Consequently, the smallest nonzero exact product is

\[
2^{-2148},
\]

while the largest product is less than

\[
2^{2048}.
\]

The exact product therefore spans approximately 4,196 binary exponent intervals. Literature describing Kulisch accumulators commonly identifies a 4,288-bit design for binary64 exact dot products, and one cited design-space analysis gives the binary64 product span as 4,196 bits while discussing 4,288 bits as a conservative accumulator width.[1][4][8]

That establishes that 4,288 bits is a plausible and historically recognized width—not that every implementation using 4,288 physical bits is automatically correct.

### The \(N\)-term growth bound

For a sum of \(N\) same-sign products,

\[
\left|\sum_{i=1}^{N}p_i\right|<N\,2^{2048}.
\]

For \(N=2^{64}\),

\[
\left|\sum_i p_i\right|<2^{2112}.
\]

Thus the high-end magnitude requires roughly 2,112 magnitude bits from the binary point, while the low-end product may reach \(2^{-2148}\). A fixed-point signed accumulator covering that entire interval needs approximately

\[
2112-(-2148)+1=4261
\]

bits before accounting for representation conventions. This matches the stated arithmetic evaluation \(4197+64=4261\), assuming 4,197 is the correct base span for one product plus the required endpoint bit.

Therefore:

- **4261 bits may be mathematically sufficient** for the stated magnitude bound under a particular signed fixed-point convention.
- **4,288 bits provides 27 bits of margin** under that convention.
- The proof must explicitly specify whether the sign bit, carry bit, zero representation, maximum finite operand, and negative endpoint are included.
- If the accumulator is a two’s-complement integer, the admissible positive and negative ranges are asymmetric; the proof must verify both signs, not only absolute magnitude.
- If NaNs, infinities, signed zeros, or exceptional IEEE behavior are accepted inputs, they require separate classification logic and are not represented by the finite fixed-point bound.

A robust proof should define an integer scale \(2^L\), prove

\[
p_i 2^L\in\mathbb Z,
\]

and then prove the exact integer bound

\[
-2^{B-1}\leq \sum_i p_i2^L\leq 2^{B-1}-1
\]

for the chosen \(B\). Without this inequality, “4,288 bits” remains an engineering assertion rather than a complete proof.

### 67 limbs versus 136 buckets

The proposed sizes are not equivalent:

- \(67\times64=4288\) bits.
- \(136\times32=4352\) bits.

The declaration

```cpp
alignas(64) struct SuperaccV {
    uint64_t w[137][8];
};
```

contains

\[
137\times8\times64=70016
\]

bits, or 8,752 bytes, before any implementation-specific padding. It is not a 4,288-bit accumulator. It is an array of 1,096 64-bit words, presumably representing lanes, slices, or independent partial accumulators. The mapping between those words and the logical accumulator must be specified.

If “136 buckets” means 136 independent 32-bit radix-\(2^{32}\) digits, the raw capacity is 4,352 bits. That offers 64 additional bits over 4,288, but capacity alone does not establish safety: signed-digit range, carry-save redundancy, bucket headroom, and normalization policy matter.

### Can 32-bit buckets absorb \(10^7\) products without normalization?

Not unconditionally.

If every product deposits at most one unit into a bucket, a 32-bit unsigned bucket can hold only

\[
2^{32}-1\approx4.29\times10^9
\]

deposits, so \(10^7\) such deposits fit. But a binary64 product is not generally one unit in one bucket. It may produce multiple nonzero limbs, and a vectorized decomposition can deposit several partial products into the same destination bucket.

For a limb holding \(k\) bits of product contribution, a coarse bound is

\[
C_{\max}\le N\,M_{\max},
\]

where \(M_{\max}\) is the maximum contribution per term to that bucket. A valid no-normalization claim requires

\[
N\,M_{\max}<2^{32}
\]

for every bucket, including sign handling and any duplicated cross terms.

For \(N=10^7\), this permits an average worst-case contribution below roughly 429 units per term. That may or may not hold, depending on the deposit representation. It cannot be inferred from the number of products alone.

Further complications include:

- Negative deposits cannot safely be represented by naïve unsigned accumulation.
- Carry-save or redundant signed digits may permit larger temporary populations, but the redundancy bound must be proved.
- Cross-term decomposition of 53-bit significands can cause multiple contributions to the same bucket.
- Vector lanes may accumulate independently and later merge; the per-lane bound differs from the global bound.
- Saturation, wraparound, and signed overflow are all unacceptable unless explicitly prevented.

A sound design should either normalize periodically or prove a bucket invariant such as

\[
|d_j|\leq D_j<2^{31}
\]

for every bucket \(j\), including the maximum batch size between normalization points.

### Exact integer multiplication path

Avoiding floating-point `TwoProduct` is defensible when the implementation must preserve subnormal products exactly. A product involving the minimum subnormal can lie at \(2^{-2148}\), below the minimum binary64 value, so a floating-point intermediate cannot represent the exact product as a normal binary64 result.

However, the proposed rationale is incomplete. `_mm512_mul_epu32` computes unsigned 32-by-32-bit products from selected 32-bit halves; it does not compute a full 64-by-64-bit product. For binary64, the implementation must:

1. Extract the 53-bit significands.
2. Split each into 32-bit limbs.
3. Compute all required cross products.
4. Place each cross product at the correct bit offset.
5. Add signs and exponents exactly.
6. Handle subnormal exponent alignment.
7. Prove that all intermediate products and additions remain within their lane widths.

For two 53-bit significands \(a=a_0+2^{32}a_1\) and \(b=b_0+2^{32}b_1\),

\[
ab=a_0b_0+2^{32}(a_0b_1+a_1b_0)+2^{64}a_1b_1.
\]

The middle term requires two products and a carry-safe addition. `_mm512_mul_epu32` can implement these pieces, but the instruction is only a primitive, not a complete exact multiplier.

### RNE correctness

A correct final RNE conversion requires more than floor division with negative-residue correction. The exact accumulator must be converted according to:

- sign,
- leading significand position,
- retained significand bits,
- guard bit,
- sticky bit,
- tie detection,
- parity of the retained least-significant bit,
- normal versus subnormal result,
- overflow to infinity or maximum finite value,
- underflow and signed zero.

For a positive integer \(A\) divided by \(2^k\), let

\[
q=\left\lfloor A/2^k\right\rfloor,\qquad r=A-q2^k.
\]

RNE increments \(q\) when

\[
r>2^{k-1},
\]

or when

\[
r=2^{k-1}
\]

and \(q\) is odd. For negative values, the implementation must define whether it rounds the magnitude first and reapplies the sign, or uses a mathematically correct floor/remainder convention. In languages where division truncates toward zero, negative remainder correction is essential; but it is only one component of the proof.

“Across 4,352 bits” is also ambiguous. If the logical exact result occupies 4,261 required bits and the implementation stores 4,352 bits, the extra 91 bits are headroom—not a substitute for a verified extraction and rounding procedure. A carry from discarded low limbs must be reflected through guard/sticky logic or exact integer incrementing.

3. **SILICON FEASIBILITY & FAILURE MODES**

### Feasible components

The architecture is silicon-feasible in principle:

- Binary64 unpacking and integer significand multiplication are standard.
- AVX-512 can provide useful throughput for 32-bit limb products.
- A carry-save or redundant-digit accumulator can defer normalization.
- A 4,288-bit logical accumulator is large but practical as a software structure and possible as a specialized hardware datapath.
- Exact products avoid intermediate floating-point underflow.

The primary cost is not mathematical feasibility but bandwidth, shuffling, carry management, and reduction overhead. A full exact dot product is unlikely to approach ordinary FMA throughput without specialized hardware.

### Failure modes

**Incorrect `_mm512_mul_epu32` usage.** Treating it as a 64-bit product instruction silently drops high halves or cross terms.

**Accumulator aliasing.** If multiple vector lanes update shared buckets without atomics, privatization, or a proven conflict-free schedule, lost updates occur. Scatter operations do not make concurrent accumulation safe.

**32-bit overflow.** Deferred normalization is safe only under a formally bounded deposit count. A single worst-case input pattern can invalidate an average-case estimate.

**Signed arithmetic overflow.** C and C++ signed overflow is undefined behavior. Every temporary should use unsigned arithmetic or explicitly checked wider arithmetic.

**Carry-chain latency.** Final normalization of 136 radix-\(2^{32}\) digits can create a long serial dependency. Carry-save techniques reduce deposit cost but do not eliminate final carry propagation.

**Subnormal and exponent bugs.** Normal and subnormal operands use different significand and exponent interpretations. A one-unit exponent error produces systematic bit errors near the underflow boundary.

**Special values.** NaNs, infinities, and invalid operations require a separate IEEE classification path. An integer accumulator alone cannot encode the required exception semantics.

**Overflow conversion.** A mathematically finite exact sum can round to infinity; the conversion logic must implement the IEEE overflow threshold, not merely truncate the top bits.

**False confidence from padding.** `alignas(64)` aligns the object base; it does not guarantee that every logical slice has a desired cache-set mapping, nor does it make accesses conflict-free.

### 4K aliasing

4K aliasing generally refers to load/store addresses that share the same 12-bit page offset and therefore can be difficult for a cache or memory-disambiguation mechanism to distinguish before full address translation. A 64-byte alignment constrains the low six address bits, but leaves bits 6 through 11 unchanged. Consequently, many aligned addresses can still have identical 4K offsets.

The stride of a row in the shown declaration is

\[
8\times64=512\text{ bytes},
\]

not 8,768 bytes. The total object size is approximately 8,752 bytes, while the row stride is 512 bytes. If a different “odd stride padding” is intended, it is not represented by the declaration as written.

Even a stride such as 8,768 bytes does not automatically eliminate aliasing. Since

\[
8768\bmod4096=576,
\]

successive rows would change page offset by 576 bytes, which may reduce repeated congruence but does not guarantee that no simultaneously accessed rows share a 4K offset. The actual vector width, number of slices, alignment of each base, page placement, and access pattern must be modeled.

A layout can reduce 4K aliasing by selecting strides and offsets that avoid repeated page-offset collisions for the active working set, but this requires measurement or a formal address-set analysis. Cache-line alignment alone is insufficient.

4. **FORMAL RECOMMENDATIONS**

1. **Replace the informal width claim with a complete integer bound.** Define the fixed-point scale, sign representation, maximum operand class, special-value policy, and exact admissible range. Prove the two-sided inequality for \(N=2^{64}\).

2. **Distinguish logical width from physical storage.** Document separately:
   - exact product bit span,
   - accumulator width,
   - guard/headroom bits,
   - number of lanes,
   - number of slices,
   - physical padding.

3. **Audit the 4,288-bit conclusion.** State that \(4261\) bits follows from the supplied formula for \(N=2^{64}\), while 4,288 bits is a conservative implementation width only after representation overhead is specified.

4. **Publish a complete limb-level multiplication derivation.** Show the exact 32-by-32 decomposition, cross-term placement, carry bounds, and signed-product handling for `_mm512_mul_epu32`.

5. **Prove a per-bucket occupancy invariant.** For each bucket, derive the maximum number and magnitude of deposits between normalizations. Do not use “\(10^7\) products fit” unless the maximum contribution per product is included.

6. **Use periodic normalization or wider temporary digits.** If worst-case bucket bounds approach \(2^{32}\), use 64-bit temporary buckets, carry-save digits, or a statically verified normalization interval.

7. **Specify RNE as an executable algorithm.** Include sign, guard, round, sticky, ties-to-even, subnormal rounding, overflow, underflow, and signed zero. Test exact halfway cases exhaustively around normal/subnormal boundaries.

8. **Separate finite arithmetic from IEEE exception semantics.** Define behavior for NaNs, infinities, signaling NaNs, signed zeros, and invalid products.

9. **Correct the layout documentation.** The displayed structure has 512-byte row stride and approximately 8,752-byte total storage, not an 8,768-byte row stride. Use `static_assert` checks for `sizeof`, `alignof`, and row stride.

10. **Validate the cache claim empirically and analytically.** Record virtual and physical address mappings where possible, test multiple page placements, and benchmark conflict-sensitive access patterns. State the claim as “reduces observed aliasing under tested layouts,” unless a formal no-collision theorem is supplied.

11. **Build a differential test oracle.** Compare against arbitrary-precision integer arithmetic or a trusted exact-dot-product implementation for:
    - maximum finite operands,
    - minimum subnormals,
    - mixed normal/subnormal products,
    - alternating signs,
    - \(N=2^{64}\)-scaled stress patterns,
    - exact halfway RNE cases,
    - overflow and underflow boundaries.

12. **Do not claim bit-to-bit IEEE correctness until the full pipeline is proven.** The current claims support a plausible exact-accumulation architecture, but they do not yet establish correctness of the particular implementation, carry schedule, SIMD decomposition, or cache behavior.

---

## Subfase 4.2: PMTP-v4 CUDA IPC VRAM-to-VRAM Zero-Copy & Kernel Triton SRAM en Dual T4 (EVAL_SUBFASE_4_2)

1. **VERDICT — REFUTED / CLARIFIED**

- **REFUTED:** CUDA IPC does not itself create a transport path between GPUs. With PCIe peer access disabled—and no NVLink or other peer-capable fabric—`cudaIpcGetMemHandle()` and `cudaIpcOpenMemHandle()` only export/import a process-portable reference to device memory; they do not guarantee direct GPU-to-GPU DMA. NVIDIA describes IPC as a mechanism for sharing device allocations across processes, while actual peer access remains dependent on the topology and driver capabilities.[1][2]
- **REFUTED:** The claimed 9.03 GB/s VRAM-to-VRAM transfer that “completely bypasses host DRAM” is not established for dual PCIe T4s with P2P disabled. The defensible implementation is a staged transfer through host-pinned memory, or another explicitly supported transport. T4 is a PCIe Gen3 x16 device and has no NVLink in the stated configuration.[6][9]
- **CLARIFIED:** A 128-byte descriptor can be a valid serialization format, but its size does not establish cryptographic invariance, freshness, authenticity, or epoch fencing. Those properties depend on the actual fields, canonical encoding, authenticated binding, replay policy, and protocol state machine.
- **REFUTED:** A Triton `atomic_add` reduction cannot, by itself, guarantee bitwise deterministic FP64 results or an isometry defect of \(2.22\times10^{-16}\). Floating-point addition is non-associative, and atomic update order is generally schedule-dependent. A reported value near machine epsilon is an empirical observation, not a proof.

2. **RIGOROUS MATHEMATICAL & ARCHITECTURAL ANALYSIS**

### CUDA IPC and transport semantics

`cudaIpcGetMemHandle()` produces a shareable handle for an allocation owned by one process. `cudaIpcOpenMemHandle()` maps that allocation into another process’s CUDA address space.[1][2] The handle exchange is normally performed through host operating-system IPC; the descriptor path therefore necessarily uses host-visible control communication, even if the payload transfer could later use a peer link.

The critical distinction is:

\[
\text{IPC capability} \neq \text{GPU peer-transport capability}.
\]

Direct remote-memory access requires a supported peer path, typically exposed through CUDA peer access and validated with mechanisms such as device topology queries and `cudaDeviceCanAccessPeer`. If peer access is unavailable or disabled, importing the handle does not turn an ordinary PCIe root-complex topology into a GPU-to-GPU DMA fabric.

For two independent PCIe GPUs, possible paths include:

\[
G_0 \rightarrow \text{host pinned memory} \rightarrow G_1,
\]

or, where supported,

\[
G_0 \rightarrow \text{PCIe peer transaction} \rightarrow G_1.
\]

The first path is a host-memory bounce path. “Pinned” means page-locked and DMA-friendly; it does not mean that host DRAM is bypassed. The second path requires platform, firmware, IOMMU, driver, GPU, and topology support. P2P being disabled rules it out for the stated deployment.

Thus, `cudaIpcOpenMemHandle(..., cudaIpcMemLazyEnablePeerAccess)` is not evidence that peer access succeeded. The flag requests or permits peer enabling where possible; it does not override an unsupported topology or a policy-disabled path.

### Throughput and latency claim

A measured 9.03 GB/s may be plausible as an aggregate or staged-transfer number, but it cannot be attributed to direct VRAM-to-VRAM DMA without instrumentation proving the route. The claim needs at least:

- `cudaDeviceCanAccessPeer` results in both directions.
- `cudaDeviceGetP2PAttribute` results, including access support and performance rank.
- PCIe topology, root-complex, ACS, IOMMU, and BAR configuration.
- Nsight Systems or equivalent traces showing the transfer engine and absence of host staging.
- Separate measurements for device-to-host, host-to-device, and end-to-end GPU-to-GPU latency.
- Transfer size, batching, stream configuration, synchronization method, and whether the reported throughput is one-way or bidirectional.

An IPC handle is metadata, not a data-plane measurement. The asserted 0.825 ms latency is also undefined unless the timing boundary is specified: kernel launch to completion, source synchronization to destination visibility, or application-level request-to-acknowledgment.

### Descriptor invariance and LeaseGuard

The proposed decomposition is arithmetically consistent:

\[
88\ \mathrm{B}+64\ \mathrm{B}=152\ \mathrm{B},
\]

not 128 bytes. Therefore, unless the “88B core metadata” overlaps, is compressed, or the handle is not actually 64 bytes in the target ABI, the stated descriptor size is internally inconsistent.

Even if the intended descriptor is 128 bytes, fixed length does not imply canonicality. A canonical descriptor requires, at minimum:

- Fixed endianness and integer widths.
- Explicit padding rules.
- No uninitialized or nondeterministic bytes.
- Defined encoding for optional fields.
- Stable field ordering.
- Version and schema identifiers.
- Explicit representation of GPU identity, allocation identity, size, permissions, and epoch.

Cryptographic invariance requires an authenticated digest or MAC over the exact canonical byte sequence. A raw CUDA IPC handle is an opaque implementation object, not a cryptographic commitment. Its equality across processes, restarts, driver versions, or allocations must not be assumed unless documented and tested.

Epoch fencing also requires a formal acceptance predicate. For example, a receiver might accept a message only if

\[
\operatorname{MAC}_K(D\parallel e\parallel \text{context}) \text{ verifies}
\]

and

\[
e_{\text{message}}=e_{\text{current}},
\]

with monotonic epoch advancement and replay rejection. A descriptor that merely contains an epoch field is not epoch fencing. The protocol must define crash recovery, concurrent renewal, delayed packets, duplicate delivery, revocation, and wraparound behavior.

### Stiefel constraint and numerical claim

For \(Y\in\mathbb{R}^{n\times k}\), the Stiefel constraint is

\[
Y^{T}Y=I_k.
\]

An isometry defect

\[
\|Y^{T}Y-I_k\|_2\le 2.22\times10^{-16}
\]

is approximately one binary64 unit roundoff. Such a bound is not generally credible for a large reduction unless the computation is specially structured, the conditioning is favorable, and the result is measured with a rigorously specified norm and reference procedure.

For a reduction of \(D=10{,}000{,}000\) FP64 values, the result depends on the summation tree. A serial or pairwise reduction, compensated summation, reproducible superaccumulator, or exact-style algorithm can provide different guarantees. An unordered atomic reduction does not.

For floating-point addition,

\[
\operatorname{fl}(a+b)
\]

is not associative:

\[
\operatorname{fl}(\operatorname{fl}(a+b)+c)
\neq
\operatorname{fl}(a+\operatorname{fl}(b+c)).
\]

Atomic operations serialize updates in an order determined by execution timing, contention, and scheduling. The operation can be atomic with respect to memory visibility while remaining numerically non-deterministic. Therefore, repeated launches can produce different low-order bits even when the input is unchanged.

The assertion can only be supported if the implementation uses a deterministic reduction tree or a mathematically justified compensated/exact accumulator, and if the reported defect is computed independently in sufficiently high precision. “Machine zero” is not a proof term.

The bandwidth claim also needs definition. Calling 139.78 GB/s “SRAM reduction bandwidth” is potentially misleading:

- GPU shared memory is not the same as on-chip register storage.
- A reduction necessarily reads input data and performs arithmetic; effective bandwidth must state the byte-count convention.
- For FP64, arithmetic throughput and memory traffic must be separated.
- Sustained bandwidth must specify problem shape, occupancy, warm-up, repetitions, synchronization, clock state, and whether compilation overhead is excluded.

3. **SILICON FEASIBILITY & FAILURE MODES**

### GPU and PCIe failures

- **Host bounce:** The driver stages data through pinned host memory when peer access is unavailable, violating the no-host-DRAM claim.
- **Topology asymmetry:** GPU 0 may reach GPU 1 differently from GPU 1 reaching GPU 0.
- **ACS/IOMMU blocking:** PCIe access-control services or IOMMU settings can prevent peer transactions even when the physical topology appears favorable.
- **BAR and address-window limitations:** Mapping remote memory may fail or incur constrained addressing behavior.
- **Driver-dependent IPC behavior:** Handle import may succeed while the intended access mode remains unavailable or falls back.
- **Context and lifetime errors:** Freeing the exporting allocation, terminating the exporting process, or closing handles prematurely can invalidate access.
- **Visibility errors:** IPC mapping does not replace stream synchronization, event synchronization, or a defined producer-consumer memory-order protocol.
- **False benchmark attribution:** A benchmark may measure host-staged copies, overlapping transfers, cached data, or launch-to-launch timing rather than payload movement.

### Descriptor and distributed-systems failures

- **ABI mismatch:** `cudaIpcMemHandle_t` size and representation must be compiled and validated for the exact CUDA ABI; hard-coding 64 bytes is unsafe without a compile-time assertion.
- **Padding leakage:** Uninitialized padding can change hashes and invalidate supposedly identical descriptors.
- **Replay:** A valid old descriptor may be accepted after lease expiration unless epochs are authenticated and checked.
- **Split-brain leases:** Two coordinators can issue valid-looking descriptors for different epochs without a single-writer or quorum rule.
- **ABA reuse:** An allocation can be freed and reallocated at the same address, defeating address-only identity.
- **Partial failure:** One GPU or process can disappear after the descriptor is committed but before the consumer maps it.
- **Confused deputy:** An imported handle may be used by an unauthorized process if authentication is not bound to identity, allocation, and intended operation.
- **Crash ambiguity:** Lease renewal and revocation need durable state or a clearly defined failure detector.

### Reduction and silicon-level numerical failures

- **Atomic ordering variance:** Different warp and block schedules yield different sums.
- **Cancellation:** Mixed-sign data can amplify relative error dramatically.
- **Overflow/underflow:** Norm or Gram-matrix calculations can overflow or lose subnormal contributions.
- **Flush-to-zero behavior:** Kernel compilation and hardware modes can affect subnormal handling.
- **FMA and contraction differences:** Compiler choices can alter last-bit results.
- **Register spills and occupancy changes:** Tuning changes can alter reduction order and timing.
- **Contention collapse:** Atomic throughput can degrade sharply as many lanes target the same accumulator.
- **Invalid validation norm:** Computing a spectral norm with an unstable or low-precision method can manufacture an apparently tiny defect.
- **Data-layout ambiguity:** “D elements” does not specify matrix dimensions, number of columns, or whether \(Y^TY\) is formed exactly as claimed.

4. **FORMAL RECOMMENDATIONS**

1. Replace the direct-DMA claim with a conditional statement: CUDA IPC exports allocation handles; direct VRAM-to-VRAM transfer occurs only when validated peer access exists. For the stated dual-T4, P2P-disabled configuration, document host-pinned staging as the expected path.

2. Add a mandatory runtime capability matrix:
   \[
   (\text{device pair},\ \text{peer access},\ \text{P2P attributes},\ \text{topology},\ \text{driver},\ \text{IOMMU/ACS}).
   \]
   Refuse the zero-copy mode unless every required capability check passes.

3. Publish a reproducible benchmark protocol with payload sizes, directionality, synchronization boundaries, warm-up policy, repetitions, PCIe topology, clock settings, and independent tracing of host traffic.

4. Correct the descriptor-size arithmetic and define the ABI explicitly. Use:
   - fixed-width fields;
   - explicit endianness;
   - zeroed padding;
   - schema/version identifiers;
   - compile-time size assertions;
   - authenticated hashes or MACs over canonical bytes.

5. Define LeaseGuard as a state machine with authenticated epochs, monotonicity, expiration, renewal, revocation, replay rejection, crash recovery, and allocation-generation identifiers. Include formal safety and liveness invariants.

6. Separate control-plane IPC from data-plane transport in the architecture. The descriptor may be exchanged through host IPC while the payload uses either staged copies or validated P2P; these must not be conflated.

7. Replace atomic floating-point reductions with a deterministic hierarchical reduction when reproducibility is required. Use fixed block partitions, fixed reduction trees, and deterministic final aggregation. For stronger guarantees, use compensated summation, binned accumulators, or a reproducible summation library.

8. State the numerical guarantee honestly:
   - empirical tolerance under a specified test distribution;
   - deterministic bitwise reproducibility;
   - forward-error bound;
   - or formal worst-case bound.
   
   These are distinct claims and must not be presented interchangeably.

9. Validate the Stiefel defect independently using high-precision arithmetic or a trusted reference implementation, and report:
   \[
   \|Y^TY-I\|_2,\quad
   \|Y^TY-I\|_F,\quad
   \|Y^TY-I\|_{\max},
   \]
   together with dimensions, conditioning, input generation, reduction order, and repeated-run variance.

10. Treat \(2.22\times10^{-16}\) as an extraordinary result requiring proof or a tightly bounded experimental protocol—not as a consequence of Triton, FP64, or atomicity alone.

---

## Subfase 5.1: Erradicación del 1D Worm y Cota DPI de Preservación Entrópica (EVAL_SUBFASE_5_1)

1. VERDICT (CLARIFIED / REFUTED)

**CLARIFIED:** The Data Processing Inequality (DPI) is mathematically applicable to continuous, discrete, and mixed random variables when the relevant probability distributions and Markov chain are well-defined. It does not require both representations to inhabit the same type of space. Mutual information is defined through relative entropy and remains well-defined for continuous variables, unlike differential entropy itself, which is coordinate- and units-dependent.[8]

**REFUTED:** The stated theorem does not establish that conventional foundation models necessarily incur a strictly positive, irrecoverable information loss merely because they serialize representations into tokens. The expression

\[
I(T;Z_T)=I(T;Z_L)-I(T;Z_L\mid Z_T)
\]

is valid only under the Markov relation \(T \rightarrow Z_L \rightarrow Z_T\), or an equivalent conditional-independence assumption. Even then, \(\Delta I=I(T;Z_L\mid Z_T)>0\) is not automatic. Strict positivity requires a distribution-specific proof that \(Z_T\) omits information relevant to \(T\).

**REFUTED:** “\(\Delta H=0.0\)” does not follow from preserving tensors on \(S^{D-1}\), using shared-memory pointers, or avoiding text serialization. Zero-copy transport can avoid an additional copy and quantization step, but it does not prove zero information loss, zero numerical error, or semantic sufficiency.

The reported figures—34.8 microseconds, 229.8 GB/s, and a 4,023-fold latency advantage—are not independently established by the supplied claims. They require a reproducible benchmark definition, hardware specification, payload size, concurrency model, memory topology, and a matched baseline.

2. RIGOROUS MATHEMATICAL & ARCHITECTURAL ANALYSIS

### DPI and mixed continuous/discrete representations

Let \(T\) denote the task-relevant source variable, \(Z_L\) a continuous latent tensor, and \(Z_T\) a discrete token sequence. If tokenization is a stochastic or deterministic channel applied only to \(Z_L\), then

\[
T \rightarrow Z_L \rightarrow Z_T
\]

is a Markov chain. DPI gives

\[
I(T;Z_T)\le I(T;Z_L).
\]

This remains true when \(Z_L\) is continuous and \(Z_T\) is discrete. The proper definition is

\[
I(T;Z)=D_{\mathrm{KL}}\!\left(P_{T,Z}\,\middle\|\,P_TP_Z\right),
\]

not a naive subtraction of incompatible “continuous entropy” and discrete entropy terms. Differential entropy \(h(Z_L)\) cannot be compared directly with Shannon entropy \(H(Z_T)\): their numerical values depend differently on coordinate systems, units, and quantization resolution. Mutual information, by contrast, is invariant under suitable invertible reparameterizations and is the appropriate cross-domain quantity.[6][8]

For deterministic tokenization,

\[
Z_T=f(Z_L),
\]

the conditional mutual information identity is

\[
I(T;Z_L)-I(T;Z_T)=I(T;Z_L\mid Z_T),
\]

provided the Markov condition holds. Therefore,

\[
\Delta I=I(T;Z_L\mid Z_T)\ge 0.
\]

However, the strict inequality

\[
I(T;Z_T)<I(T;Z_L)
\]

requires

\[
I(T;Z_L\mid Z_T)>0.
\]

That is an empirical or model-specific fact, not a consequence of discreteness alone.

### Why strict loss is not automatic

A discrete representation can preserve all task-relevant information. If \(T\) itself is finite and \(Z_T\) is an injective code for \(T\), then

\[
I(T;Z_T)=I(T;Z_L)=H(T),
\]

even if \(Z_L\) is continuous. More generally, if \(Z_T\) is a sufficient statistic of \(Z_L\) for \(T\), then

\[
T\perp Z_L\mid Z_T
\]

and the loss is exactly zero for that task.

Conversely, a continuous tensor may contain little or no information about \(T\). The dimensionality of \(Z_L\), its manifold structure, and its membership in \(S^{D-1}\) do not imply high task-relevant mutual information. A high-dimensional continuous vector can be noisy, redundant, or unrelated to the target.

The correct conclusion is therefore:

- Tokenization can be lossy.
- Continuous transport can preserve more of the originating tensor.
- Neither representation type alone proves task-relevant information preservation or loss.
- Strict loss depends on the source distribution, tokenizer, decoder, task variable, quantization, truncation, and context.

### Serialization is not equivalent to tokenization

The phrase “serialize continuous representations into 1D discrete tokens” conflates several operations:

- **Serialization:** changing layout or ordering, potentially invertible.
- **Memory transport:** copying or sharing bytes, potentially lossless.
- **Quantization:** mapping values to finite precision, generally lossy.
- **Tokenization:** mapping text or symbols to a vocabulary sequence, potentially lossy with respect to the original signal.
- **Autoregressive decoding:** generating a sequence through a probabilistic model, introducing approximation and latency.

A tensor flattened from \(D\) dimensions into a one-dimensional array is not necessarily an information bottleneck. If shape, ordering, dtype, and all values are retained, flattening is an invertible reindexing. The “1D worm” thesis is therefore false if “1D” means only linear memory order.

The bottleneck arises when the representation is mapped to a restricted alphabet, finite sequence length, reduced precision, lossy codec, or learned semantic summary. It is not caused by one-dimensional indexing itself.

### Natural-language serialization

Intermediate natural-language serialization can incur information loss relative to a continuous latent tensor, but no universal theorem establishes a positive loss for every model and task.

For a specific pipeline

\[
Z_L \rightarrow X_{\text{text}} \rightarrow \widehat{Z}_L,
\]

DPI gives

\[
I(T;X_{\text{text}})\le I(T;Z_L)
\]

when \(X_{\text{text}}\) is generated solely from \(Z_L\). A measurable loss can be demonstrated by estimating or bounding

\[
I(T;Z_L\mid X_{\text{text}}).
\]

Possible mechanisms include:

- bounded vocabulary and sequence length;
- lossy semantic abstraction;
- ambiguity and paraphrase;
- omitted numerical or geometric detail;
- decoder errors;
- finite context windows;
- stochastic generation;
- exposure bias and approximation error.

But a text representation may be sufficient for a narrowly defined task. For example, if \(T\) is only a coarse label and the text deterministically encodes that label, then the relevant loss can be zero even though substantial information about \(Z_L\) is discarded.

The scientifically defensible claim is task-relative:

\[
\Delta I_T
=
I(T;Z_L)-I(T;X_{\text{text}})
\ge 0,
\]

with strict positivity requiring measurement or proof for the stated \(P(T,Z_L)\) and serialization channel.

### Sphere normalization

Mapping a nonzero vector \(x\in\mathbb{R}^{D}\) to

\[
u=\frac{x}{\|x\|}\in S^{D-1}
\]

removes radial information. It is therefore not generally information-preserving. If magnitude carries information relevant to \(T\), then

\[
I(T;u)<I(T;x)
\]

may occur. A sphere representation preserves direction, not norm. It can be appropriate when the intended geometry is angular similarity, but it is not a proof of zero entropy or mutual-information loss.

Even direction-only representations remain subject to:

- finite-precision storage;
- normalization error;
- quantization;
- memory corruption;
- synchronization failures;
- distribution shift;
- downstream approximation.

### Zero-copy shared memory

A pointer is metadata, not a representation of the data. Shared-memory transport can avoid copying, but only if producer and consumer agree on:

- virtual or physical addressability;
- tensor shape and strides;
- dtype and alignment;
- ownership and lifetime;
- cache coherence;
- synchronization and memory ordering;
- device placement;
- protection boundaries;
- versioning and reclamation.

If the consumer reads the same bytes with a compatible interpretation, transport can be lossless relative to the stored tensor. That supports a conditional statement such as

\[
Z_{\text{consumer}}=Z_{\text{producer}}
\]

at the logical value level. It does not imply

\[
H(Z_{\text{consumer}}\mid Z_{\text{producer}})=0
\]

for the complete system unless metadata, synchronization, numerical representation, and failure behavior are included in the random variables.

3. SILICON FEASIBILITY & FAILURE MODES

The throughput and latency claims are arithmetically plausible only under a specified payload. A bandwidth of \(229.8\ \mathrm{GB/s}\) with \(34.8\ \mu\mathrm{s}\) implies an effective transferred payload of approximately

\[
229.8\times 10^9 \times 34.8\times 10^{-6}
\approx 8.0\ \mathrm{MB}.
\]

That may represent a local memory operation or mapped-buffer access, but it does not by itself characterize end-to-end inference or inter-device communication.

Major failure modes include:

- **Benchmark boundary inflation:** measuring pointer handoff rather than tensor readiness, synchronization, cache misses, or downstream consumption.
- **Warm-cache bias:** excluding first-touch page faults, TLB misses, NUMA placement, and cache-coherence costs.
- **Bandwidth/latency conflation:** peak streaming bandwidth does not imply low tail latency or sustained application throughput.
- **PCIe or interconnect limits:** device-to-device movement may be constrained by PCIe, CXL, NVLink, fabric contention, or IOMMU translation.
- **NUMA penalties:** shared memory across sockets can incur materially different latency from same-node access.
- **Synchronization overhead:** fences, atomics, queues, and reclamation can dominate a nominal zero-copy path.
- **False sharing and cache invalidation:** concurrent metadata or tensor writes can cause coherence traffic and stale reads.
- **Lifetime races:** a producer may recycle or mutate a buffer while a consumer still reads it.
- **ABI and layout mismatch:** strides, padding, endian assumptions, dtype interpretation, and alignment can silently corrupt computation.
- **Memory protection:** arbitrary shared pointers weaken isolation and complicate fault containment.
- **Security exposure:** a compromised process may inspect or modify tensors, including sensitive activations.
- **Numerical degradation:** normalization and low-precision storage can alter angular distances and downstream logits.
- **Backpressure:** eliminating copies does not eliminate queueing when consumers are slower than producers.
- **Thermal and power limits:** sustained bandwidth may throttle under realistic workloads.
- **Fault recovery:** a pointer-based protocol needs detection, timeout, replay, and recovery semantics.

The 4,023-fold comparison is especially vulnerable to an invalid baseline. Comparing a raw tensor pointer handoff with full autoregressive text generation compares different computational tasks. A valid comparison should distinguish:

1. tensor-to-tensor transfer;
2. tensor-to-text conversion;
3. text tokenization;
4. text transport;
5. text-to-tensor reconstruction;
6. downstream model execution;
7. end-to-end task accuracy and tail latency.

Without matched semantics and equal output requirements, the ratio is a systems metric for two different paths, not evidence that one representation universally dominates the other.

4. FORMAL RECOMMENDATIONS

1. Replace the universal theorem with a conditional proposition:

   \[
   T\rightarrow Z_L\rightarrow Z_T
   \quad\Longrightarrow\quad
   I(T;Z_T)\le I(T;Z_L),
   \]

   and state that strict inequality requires a demonstrated non-sufficiency condition.

2. Define every random variable precisely, including whether \(T\) is the raw input, task label, downstream output, or future computation.

3. Separate serialization, tokenization, quantization, compression, transport, and decoding into distinct channels.

4. Do not compare \(H(Z_T)\) with differential entropy \(h(Z_L)\). Use mutual information, conditional mutual information, rate-distortion functions, task loss, or sufficient-statistic criteria.

5. Prove or estimate

   \[
   I(T;Z_L\mid Z_T)
   \]

   for a fixed dataset distribution, tokenizer, sequence budget, precision, and task. Use confidence intervals and estimator-bias analysis.

6. Test whether text is task-sufficient rather than asking whether it preserves all latent information. Report task-specific degradation across reconstruction, classification, retrieval, generation, calibration, and robustness.

7. Treat \(S^{D-1}\) as a modeling choice, not an information-preservation guarantee. Quantify the information in the discarded radial coordinate.

8. Define “\(\Delta H=0\)” operationally. Specify the variables, entropy measure, precision, metadata, and failure model. A defensible claim would be “bit-exact logical tensor values under stated conditions,” not universal zero entropy loss.

9. Publish complete benchmark details: hardware, firmware, compiler, tensor size, dtype, strides, cache state, NUMA topology, synchronization, repetitions, percentile latency, power state, and whether setup costs are included.

10. Compare against matched baselines with identical payload semantics and accuracy targets. Report end-to-end latency and tail percentiles, not only pointer-transfer latency.

11. Add formal ownership and synchronization protocols—such as versioned ring buffers, acquire/release ordering, reference counting or epochs, timeout handling, and integrity checks.

12. Report security and isolation properties for shared memory, including access control, process compromise, confidential-computing assumptions, and fault containment.

13. Recast the strongest defensible conclusion as follows: POLYDIM may reduce representational and systems overhead when downstream components can directly consume compatible tensors, while natural-language mediation may discard task-relevant information and add latency. Neither DPI nor zero-copy transport alone proves universal information preservation, strict loss for all token pipelines, or the stated performance multiplier.

---

## Subfase 5.2: Retracción Stiefel Cayley-SMW y Convergencia Asintótica en Lean 4 (EVAL_SUBFASE_5_2)

## 1. VERDICT

**CLARIFIED / PARTIALLY REFUTED.**

- The displayed low-rank formula is algebraically valid for the standard Stiefel Cayley transform **provided the sign conventions and tangent-space construction are specified correctly**.
- The claimed universal asymptotic formula  
  \[
  \lim_{t\to\infty}R_X(tZ)=(2P_{\ker(A)}-I)X
  \]
  is **not generally correct as stated**. It requires a particular skew-symmetric generator \(A\), a well-defined spectral decomposition, and exclusion or separate treatment of zero modes.
- Finite-\(\tau\) singularities are possible in the reduced \(2K\times 2K\) system in a generic low-rank representation, although they cannot occur for the canonical real skew-symmetric Cayley generator under the usual sign convention.
- The assertion \(\kappa(X)=1.0\pm10^{-15}\) is not a mathematical consequence of the retraction. Exact orthogonality may hold in exact arithmetic; the numerical condition number depends on floating-point arithmetic, scaling, implementation, and conditioning of the reduced solve.
- A Lean 4 mechanization “eliminating `sorry`” cannot be accepted as evidence without the repository, theorem statements, dependency versions, kernel-checkable build, and proof audit. The quoted chordal metric is valid on projector representatives, but quotient well-definedness and metric properties must be demonstrated explicitly.

## 2. RIGOROUS MATHEMATICAL & ARCHITECTURAL ANALYSIS

Let \(X\in\mathbb R^{D\times K}\) satisfy \(X^{T}X=I_K\), and let \(Z\in T_X\mathrm{St}(K,D)\). A standard Cayley construction uses a skew-symmetric ambient matrix \(A\), commonly

\[
A=ZX^{T}-XZ^{T},
\qquad A^{T}=-A,
\]

for which \(AX=Z\) when \(X^TZ+Z^TX=0\). The Cayley curve is

\[
R_X(\tau Z)
=
\left(I-\frac{\tau}{2}A\right)^{-1}
\left(I+\frac{\tau}{2}A\right)X.
\]

Because \(A\) is skew-symmetric,

\[
\det\!\left(I-\frac{\tau}{2}A\right)>0
\]

for every real finite \(\tau\): the eigenvalues of \(A\) are \(0\) and \(\pm i\lambda_j\), so the corresponding factors are \(1\) and \(1+\tau^2\lambda_j^2/4\). Thus the **full ambient Cayley inverse is nonsingular for every finite real step**.

### Low-rank formula

If

\[
A=UV^{T},
\]

then

\[
\left(I-\frac{\tau}{2}UV^{T}\right)^{-1}
=
I+\frac{\tau}{2}
U\left(I-\frac{\tau}{2}V^{T}U\right)^{-1}V^{T},
\]

by Sherman–Morrison–Woodbury. Consequently,

\[
R_X(\tau Z)
=
X+\tau U
\left(I_{2K}-\frac{\tau}{2}V^{T}U\right)^{-1}
V^{T}X.
\]

This confirms the supplied formula **if and only if** the chosen \(U,V\) satisfy \(A=UV^T\) with the same sign convention.

For the stated choice

\[
U=[G,-X],\qquad V=[X,G],
\]

one obtains

\[
UV^{T}=GX^{T}-XG^{T}.
\]

Therefore this represents the skew generator

\[
A=GX^{T}-XG^{T}
\]

only when \(G\) is the actual tangent direction or an explicitly defined scaled variant. If \(G\) denotes a gradient rather than a tangent vector, the formula generally does not have the claimed first-order retraction property until the tangent projection and sign are specified.

The reduced matrix is

\[
M(\tau)=I_{2K}-\frac{\tau}{2}V^{T}U.
\]

The determinant identity gives

\[
\det\!\left(I-\frac{\tau}{2}UV^{T}\right)
=
\det M(\tau).
\]

Hence, for an exact factorization of a real skew-symmetric \(A\), \(M(\tau)\) must be nonsingular whenever the ambient inverse is nonsingular. A finite singularity in \(M(\tau)\) therefore indicates one of the following:

- \(UV^T\) is not actually the intended skew-symmetric generator.
- The factors contain inconsistent signs or transposes.
- \(G\) is not tangent or has been preconditioned asymmetrically.
- The reduced matrix is numerically singular even though the exact matrix is nonsingular.
- The implementation uses a different Cayley convention from the proof.

The distinction between **mathematical singularity** and **numerical ill-conditioning** is essential. For a valid real skew-symmetric generator, exact finite singularity does not occur, but the reduced system may still be poorly scaled or lose accuracy in finite precision.

### Asymptotic limit

Let \(A\) be real skew-symmetric and define

\[
C(\tau)=
\left(I-\frac{\tau}{2}A\right)^{-1}
\left(I+\frac{\tau}{2}A\right).
\]

On \(\ker(A)\), \(C(\tau)\) acts as \(+I\). On every nonzero invariant two-dimensional eigenspace associated with eigenvalues \(\pm i\lambda\), the scalar Cayley factor is

\[
\frac{1+i\tau\lambda/2}{1-i\tau\lambda/2}
\longrightarrow -1
\qquad (\tau\to+\infty).
\]

Therefore

\[
\lim_{\tau\to+\infty}C(\tau)
=
P_{\ker(A)}-P_{\ker(A)^\perp}
=
2P_{\ker(A)}-I.
\]

Thus the stated limiting operator is correct **for the full Cayley transform of a fixed real skew-symmetric \(A\)** and for a one-sided real limit \(\tau\to+\infty\). Consequently,

\[
\lim_{\tau\to+\infty}R_X(\tau Z)
=
(2P_{\ker(A)}-I)X.
\]

However, several qualifications invalidate the claim as a universal POLYDIM theorem:

- \(A\) must be explicitly defined and skew-symmetric.
- The limit is not obtained by casually substituting \(\tau=\infty\) into the Woodbury expression.
- If \(A\) depends on \(\tau\), the result need not hold.
- If the implementation uses a nonskew or approximate generator, the limit may fail to exist or may diverge.
- The limit is generally an involution, not necessarily a geometrically desirable endpoint.
- The statement does not imply avoidance of numerical singularities for arbitrary finite-step reduced matrices.
- For \(\tau\to-\infty\), the same limit occurs for real skew-symmetric \(A\), but the path orientation differs.

The formula also does not establish a condition-number claim. Exact orthogonality follows from

\[
C(\tau)^TC(\tau)=I,
\]

so \(R_X(\tau Z)^TR_X(\tau Z)=I_K\) in exact arithmetic. But \(\kappa_2(X)\) is exactly \(1\) for every full-rank orthonormal \(X\), independent of the asymptotic limit. In floating point,

\[
\kappa_2(\widehat X)
\]

can deviate from one due to rounding and loss of orthogonality. A bound of \(10^{-15}\) requires an explicit backward-error theorem involving machine precision, \(D,K\), matrix norms, solver residuals, and conditioning. It cannot be asserted from the retraction identity alone.

### Grassmann quotient and chordal distance

For \(X,Y\in\mathrm{St}(K,D)\), the quantity

\[
d_c([X],[Y])
=
\frac{1}{\sqrt 2}
\left\|XX^T-YY^T\right\|_F
\]

is independent of the choice of orthonormal bases \(XQ\) and \(YR\), because

\[
(XQ)(XQ)^T=XX^T.
\]

It is therefore a well-defined projector-based distance on the Grassmann quotient. For equal-rank orthogonal projectors, it is related to principal angles \(\theta_i\) by

\[
d_c^2([X],[Y])
=
\sum_{i=1}^{K}\sin^2\theta_i.
\]

A formal proof must still establish:

- quotient invariance;
- nonnegativity and symmetry;
- identity of indiscernibles on equivalence classes;
- triangle inequality;
- equivalence between quotient equality and projector equality;
- preservation of \(X^TX=I\);
- continuity and differentiability claims used by the optimization pipeline.

“Lean 4 Core” is not itself a mathematical result. A credible mechanization claim requires a public, reproducible artifact and theorem-level coverage. In particular, absence of `sorry` must be verified by the compiler and inspected for axioms such as `Classical.choice`, imported unproved assumptions, or admitted external theorems. Use of classical axioms is not equivalent to use of `sorry`, but it should be disclosed.

## 3. SILICON FEASIBILITY & FAILURE MODES

The reduced \(2K\times2K\) solve is attractive only when \(K\ll D\). The dominant costs are:

- forming \(V^TU\), approximately \(O(DK^2)\);
- forming \(V^TX\), approximately \(O(DK^2)\);
- factoring the reduced matrix, approximately \(O(K^3)\);
- applying the update, approximately \(O(DK^2)\).

The method is not automatically “low cost” when \(K\) is large, when \(D\) is moderate, or when repeated retractions require high-throughput factorization.

Critical failure modes include:

- **Loss of skew symmetry:** independently rounded or approximated factors can produce \(A+A^T\neq0\), destroying exact orthogonality guarantees.
- **Reduced-system instability:** \(M(\tau)\) may have a large condition number even when the exact Cayley transform exists.
- **Cancellation at large \(\tau\):** the expression \(X+\tau U M(\tau)^{-1}V^TX\) can subtract large terms to produce a bounded result.
- **Overflow or dynamic-range stress:** intermediate quantities scale with \(\tau\), even though the final Cayley transform remains bounded.
- **Rank inflation:** numerical rank deficiency or redundant columns in \(U,V\) can make the reduced representation unnecessarily ill-conditioned.
- **Non-tangent input:** using an unprojected gradient can produce a generator that is not the intended Stiefel tangent lift.
- **Mixed precision:** tensor cores or reduced-precision accumulation can violate the claimed \(10^{-15}\) orthogonality tolerance.
- **Solver misuse:** explicit matrix inversion is inferior to QR, LU with pivoting, or a stable skew-aware solve.
- **Hardware faults:** silent data corruption in \(V^TU\) or factorization can yield a plausible but non-orthogonal output; residual checks are required.
- **Distributed reduction error:** \(V^TU\) and \(V^TX\) often require global reductions whose reproducibility and error bounds must be specified.

The recommended implementation should never form an inverse explicitly. It should solve

\[
M(\tau)W=V^TX
\]

using a numerically stable factorization, then compute

\[
Y=X+\tau UW.
\]

Afterward, evaluate both

\[
\|Y^TY-I\|
\]

and the linear residual

\[
\left\|
\left(I-\frac{\tau}{2}A\right)Y
-
\left(I+\frac{\tau}{2}A\right)X
\right\|.
\]

These diagnostics should be tied to a fallback path, such as QR or polar retraction.

### Adaptive step-size policy

A sound adaptive policy should monitor the reduced solve rather than rely only on \(\|\tau Z\|\). At minimum:

1. Construct a tangent-consistent, explicitly skew-symmetric \(A\).
2. Compute or estimate the condition number of \(M(\tau)\), preferably using a factorization-based reciprocal condition estimate.
3. Reject or reduce \(\tau\) if the solve residual, orthogonality defect, or estimated condition number violates prescribed tolerances.
4. Use backtracking, for example \(\tau\leftarrow\beta\tau\) with \(0<\beta<1\), until all tests pass.
5. Fall back to QR/polar retraction if repeated reductions fail.
6. Include an optimization acceptance test based on objective decrease or a Riemannian line-search condition.
7. Impose a finite precision ceiling on \(\tau\) to prevent cancellation and overflow.

For a truly skew-symmetric \(A\), singularity avoidance does not require a theoretical finite-\(\tau\) exclusion beyond real \(\tau\); it requires numerical stability control. If the implementation observes exact or near singularity in the reduced matrix, that is evidence of a construction, sign, scaling, or arithmetic problem—not a normal property of the canonical real Cayley transform.

## 4. FORMAL RECOMMENDATIONS

- State the exact definitions of \(G\), \(Z\), \(A\), \(U\), and \(V\), including all dimensions and sign conventions.
- Prove explicitly that \(A=UV^T\) and \(A^T=-A\).
- Prove \(AX=Z\) or state the actual tangent vector generated by the construction.
- Separate three claims: exact existence, asymptotic behavior, and finite-precision stability.
- Replace the universal condition-number claim with a backward-error theorem containing explicit dependence on \(u,D,K,\|A\|,\tau\), and solver residual.
- State the asymptotic theorem only for fixed real skew-symmetric \(A\), and prove it through the spectral decomposition or invariant-subspace decomposition.
- Add a theorem showing that \(I-(\tau/2)A\) is nonsingular for every finite real \(\tau\).
- Add a determinant-lemma theorem connecting ambient and reduced nonsingularity.
- Treat near-singular reduced solves as numerical conditioning failures, not as mathematical Cayley singularities.
- Use stable solves rather than explicit inversion.
- Add runtime checks for skew residual, orthogonality residual, solve residual, and projector-distance consistency.
- Formalize the Grassmann quotient through an explicit equivalence relation \(X\sim Y\iff Y=XQ\) for \(Q\in O(K)\), then prove projector invariance and metric properties.
- Provide the complete Lean source, exact toolchain, imported axioms, build logs, and theorem inventory before accepting the mechanization claim.
- Include adversarial tests: \(Z=0\), rank-deficient \(G\), \(K=1\), \(K=D\), repeated singular values, very large \(\tau\), very small \(\tau\), non-tangent gradients, redundant low-rank factors, and mixed-precision execution.
- Revise the central claim to: **the canonical skew-symmetric Cayley retraction has no exact finite real singularity, while its low-rank implementation can be numerically ill-conditioned and must be governed by residual-based adaptive stepping.**

---

## Subfase 5.3: Modelo Económico de Tokens LATAM y Protocolo de Transferencia Pedagógica (EVAL_SUBFASE_5_3)

## 1. VERDICT

**CLARIFIED, with material parts REFUTED.**

- The economic intuition is valid: repeated inter-agent text routed through paid frontier APIs can become expensive, especially when messages contain duplicated context, verbose reasoning, or high output-token volumes. Published API prices vary substantially by model and provider, with output generally costing more than input.[1][8]
- The statement that local/shared-memory communication has a marginal transfer cost of **$0.000000 per hop** is only true as an accounting abstraction. It does not mean zero economic cost. CPU/GPU time, DRAM bandwidth, electricity, hardware depreciation, engineering labor, orchestration, synchronization, and failure recovery remain real costs.
- “Zero-token inter-agent communication” is feasible **inside a single process or suitably coordinated host** when agents exchange binary objects, tensor handles, pointers, queues, or structured records rather than serialized natural-language prompts. It is not generally feasible across arbitrary heterogeneous machines, devices, trust domains, or model providers without serialization, copying, protocol metadata, or network transport.
- A strict local-first testing rule is operationally defensible, but freezing a kernel version and requiring two to four daily classes is not itself evidence of correctness, performance, safety, or economic superiority. It can also create regression, reproducibility, and opportunity-cost risks.

## 2. RIGOROUS MATHEMATICAL & ARCHITECTURAL ANALYSIS

### Cost model

Let an inter-agent exchange have:

- \(n_i\): input tokens transmitted to a paid model,
- \(n_o\): output tokens generated,
- \(p_i,p_o\): prices per token,
- \(C_{\mathrm{fixed}}\): request, platform, and operational overhead,
- \(C_{\mathrm{local}}\): local compute, memory, power, and depreciation cost.

Then the API cost is approximately

\[
C_{\mathrm{API}}=n_i p_i+n_o p_o+C_{\mathrm{fixed}}.
\]

The equivalent local cost is better modeled as

\[
C_{\mathrm{local}}
=
E_{\mathrm{local}}P_{\mathrm{electricity}}
+
C_{\mathrm{hardware}}
+
C_{\mathrm{memory}}
+
C_{\mathrm{maintenance}}
+
C_{\mathrm{engineering}}
+
C_{\mathrm{failure}}.
\]

The correct decision rule is not “API tokens versus zero tokens,” but

\[
C_{\mathrm{local}}+C_{\mathrm{latency}}+C_{\mathrm{risk}}
<
C_{\mathrm{API}}+C_{\mathrm{egress}}+C_{\mathrm{vendor}}.
\]

API prices can range from fractions of a dollar to many dollars per million input tokens, with output prices often several times higher.[1][8] Therefore, the claim of unsustainable continuous API billing is plausible for high-volume workloads, but it is not universally true. A small number of concise calls to a low-cost model may be cheaper than purchasing, operating, and maintaining local accelerators.

### What “zero-token” can and cannot mean

A token is a representation unit used by a language model. A memory transfer need not be tokenized. Thus, the following can avoid language-token billing:

- Shared memory containing tensors.
- Memory-mapped files.
- In-process object references.
- Device buffers and GPU IPC handles.
- Binary RPC or columnar records.
- Local queues carrying IDs, logits, embeddings, or structured state.

However, every cross-boundary exchange still requires some representation. Across processes, the system needs synchronization and ownership rules. Across hosts, it needs a network protocol. Across incompatible devices, it may need format conversion, staging buffers, or copies. Across separate model APIs, it must eventually serialize content into an accepted request format.

Consequently, the defensible claim is:

> Local tensor or structured-state communication can eliminate *language-token billing for internal transfers*; it cannot eliminate physical data movement, synchronization, serialization in the general case, or the cost of producing the exchanged representation.

### Shared memory is not universal zero-copy

“Shared memory” has several distinct meanings:

- Two CPU processes mapping the same pages.
- CPU-to-GPU pinned memory.
- GPU-to-GPU peer access.
- Unified virtual addressing.
- Distributed shared memory.
- A network fabric exposing remote memory semantics.

Only the first few may provide genuine local zero-copy behavior, and even there, cache coherence, NUMA placement, page faults, synchronization, and ownership transfer impose costs. A tensor handle may avoid copying payload bytes, but metadata, reference counting, barriers, and lifecycle management remain necessary.

A useful transfer model is

\[
T_{\mathrm{transfer}}
=
T_{\mathrm{setup}}
+
\frac{S}{B_{\mathrm{effective}}}
+
T_{\mathrm{sync}}
+
T_{\mathrm{format}}
+
T_{\mathrm{contention}},
\]

where \(S\) is payload size and \(B_{\mathrm{effective}}\) is the achieved—not advertised—bandwidth. For small messages, setup and synchronization dominate. For large tensors, bandwidth, memory pressure, and device staging dominate.

### Architectural boundary conditions

The POLYDIM/E EinsofOS architecture should explicitly distinguish:

- **Intra-process communication:** potentially near-zero-copy and low latency.
- **Same-host inter-process communication:** often efficient, but dependent on OS, allocator, NUMA, and device support.
- **Same-cluster communication:** no token billing if using binary protocols, but network bandwidth and serialization remain material.
- **Cross-cloud or cross-provider communication:** egress, encryption, authentication, retries, and schema compatibility become major costs.
- **Human-readable agent dialogue:** tokenization may be justified for interpretability, but it is not cost-optimal for machine-to-machine state transfer.

Natural-language messages should therefore be reserved for semantic negotiation, exceptions, audit records, and human-facing explanations. Routine control flow should use typed schemas, tensors, IDs, and bounded state machines.

### Kernel freezing and testing cadence

Freezing kernel V26155 can improve reproducibility, but only if accompanied by:

- A cryptographic build identifier.
- Locked compiler, driver, runtime, model, and firmware versions.
- Reproducible datasets and seeds where applicable.
- Compatibility tests across supported hardware.
- A rollback mechanism.
- Explicit change-control criteria.

A cadence of two to four classes per day, every day, may increase defect discovery, but cadence alone is not a validation metric. Better metrics include:

- Failure rate per 1,000 runs.
- Tail latency.
- Recovery time.
- Memory peak and fragmentation.
- Numerical drift.
- Cost per successful task.
- Accuracy and calibration.
- Reproducibility across devices.
- Security and isolation violations.

Mandatory local or free-tier execution before paid calls is a sensible budget guardrail only if it does not conceal the cost of local resources or degrade evaluation fidelity. A local model that differs materially from the frontier model may produce misleading “preflight” results.

## 3. SILICON FEASIBILITY & FAILURE MODES

### Feasible cases

Zero-token internal exchange is practical when:

- Agents run on one host or tightly integrated cluster.
- They share compatible tensor layouts and numeric formats.
- A common runtime owns allocation and synchronization.
- The workload is batch-oriented or latency-tolerant.
- Model state and intermediate activations remain local.
- The system uses explicit typed schemas instead of prose.

Examples include passing embeddings, attention states, logits, masks, feature maps, task IDs, and structured tool results between local workers.

### Major failure modes

- **Memory exhaustion:** Tensor intermediates can be vastly larger than text messages. Avoiding tokenization may increase memory traffic and peak allocation.
- **Bandwidth bottlenecks:** DRAM or PCIe bandwidth can become the limiting resource even when compute units are underutilized.
- **NUMA penalties:** A tensor allocated on one CPU socket may incur substantial latency when consumed by another.
- **GPU synchronization stalls:** Events, streams, fences, and device ownership transfers can destroy the apparent benefit of zero-copy exchange.
- **Format incompatibility:** FP16, BF16, FP8, quantized formats, layouts, strides, and endian conventions may differ.
- **Allocator fragmentation:** Long-lived shared buffers and variable tensor sizes can cause unusable holes and unpredictable latency.
- **Backpressure failure:** Fast producers can exhaust queues or overwrite buffers when consumers stall.
- **Deadlock and livelock:** Lock ordering, cyclic dependencies, and failed workers require formal timeout and recovery policies.
- **Fault containment:** A process with shared writable memory may corrupt another agent’s state; isolation is weaker than message passing.
- **Security leakage:** Shared buffers can expose data across users, tasks, or tenants unless access control and zeroization are enforced.
- **Silent numerical corruption:** Race conditions may produce plausible but incorrect tensors, making debugging difficult.
- **Heterogeneous deployment collapse:** Unsupported instructions, driver differences, thermal throttling, and memory capacity variance can turn a nominally portable pipeline into a hardware-specific system.
- **Model-boundary incompatibility:** A local tensor cannot be sent directly to a remote closed model API without conversion into the provider’s input representation.
- **Economic mismeasurement:** “Free tier” usage may shift cost to electricity, lab hardware, staff time, quota limits, and slower throughput.

The central silicon trade-off is that text is compact, inspectable, and portable, whereas tensors are semantically richer but often enormous. A 1D textual message may cost tokens but consume little local memory; an activation tensor can avoid token billing while imposing substantial DRAM, cache, interconnect, and synchronization pressure.

## 4. FORMAL RECOMMENDATIONS

1. Replace the absolute claim “zero-token communication costs $0.000000” with:  
   **“Internal binary/tensor communication incurs no per-token API charge, but retains measurable compute, memory, energy, synchronization, transport, and engineering costs.”**

2. Define a complete cost function including:
   \[
   C_{\mathrm{total}}
   =
   C_{\mathrm{API}}
   +
   C_{\mathrm{egress}}
   +
   C_{\mathrm{local}}
   +
   C_{\mathrm{operations}}
   +
   C_{\mathrm{failure}}
   +
   C_{\mathrm{latency}}.
   \]

3. Establish a communication taxonomy:
   - In-process object passing.
   - Same-host shared memory.
   - Same-host GPU IPC.
   - Cluster binary RPC.
   - Cross-region transport.
   - External LLM API invocation.

4. Require every interface to specify:
   - Schema and version.
   - Tensor shape, dtype, layout, and device.
   - Ownership and lifetime.
   - Synchronization protocol.
   - Backpressure behavior.
   - Authentication and authorization.
   - Failure and retry semantics.
   - Observability fields.

5. Use a **hybrid routing policy**:
   - Local models for preprocessing, retrieval, classification, summarization, and routine control.
   - Shared tensors for high-volume internal state.
   - Frontier APIs only for tasks whose measured quality gain exceeds their fully loaded cost.
   - Human-readable text only where interpretability or semantic flexibility is necessary.

6. Benchmark against realistic baselines:
   - Cost per successful task, not cost per transfer.
   - P50/P95/P99 latency.
   - Throughput under contention.
   - Peak resident memory.
   - Energy per task.
   - Accuracy and error severity.
   - Recovery behavior under worker, driver, and network failure.

7. Treat V26155 as a reproducibility anchor, not a permanent truth. Maintain frozen release artifacts plus a separately governed experimental branch.

8. Modify Rule 34 into a risk-based gate:
   - Local/free-tier execution first for low-risk and regression tests.
   - Paid frontier execution for statistically justified samples, adversarial cases, and quality-sensitive evaluations.
   - Automatic budget ceilings, anomaly detection, and approval for unusually expensive runs.

9. For heterogeneous deployments, provide a portable fallback:
   - Serialize tensors when zero-copy is unavailable.
   - Quantize or compress only after measuring quality loss.
   - Fall back from shared memory to typed binary messaging, then to text/API calls.

10. Do not claim economic superiority until POLYDIM publishes an end-to-end study covering hardware amortization, electricity, staff time, memory capacity, model quality, API prices, data egress, failure recovery, and utilization. The strongest defensible conclusion is that **local structured communication can reduce marginal API billing and latency, but it does not make communication economically free or universally portable**.

---

