# DICTAMEN DE EVALUACIÓN DOCTORAL SOTA — PERPLEXITY SONAR-PRO

**Fecha y Hora:** 2026-10-10 17:01:25 UTC
**Modelo Auditor:** `sonar-pro`
**Latencia de Auditoría:** 37.71 segundos
**Proyecto Evaluado:** POLYDIM-EINSOF (Kernel Series 1550 / Build V26155)
**Manuscrito Base:** `POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex`

---

## 1. DICTAMEN TÉCNICO Y EVALUACIÓN EXHAUSTIVA

The submission, as stated, does **not support its central claims**. Several numerical assertions are internally inconsistent, the information-theoretic argument confuses a particular tokenizer/channel with an unavoidable property of one-dimensional representation, the manifold retraction formula appears dimensionally or algebraically defective, and the systems evidence does not establish end-to-end superiority over existing tensor IPC or collective-communication mechanisms. The appropriate verdict is **Reject in its present form, with a plausible path to Major Revision only after substantial reconstruction**.

## 1. Executive assessment

The dissertation conflates four distinct propositions:

1. A particular finite-vocabulary, fixed-length token interface can lose information.
2. Native tensor transport can avoid that particular bottleneck.
3. A low-rank manifold update can be implemented efficiently and stably.
4. Such an interface constitutes a general systems and AGI paradigm shift.

The first proposition is usually true. The second can be true under explicit assumptions. The third requires a corrected derivation and rigorous numerical analysis. The fourth is not established by the supplied claims.

The central thesis should therefore be narrowed from:

> “One-dimensional tokenization is intrinsically defective.”

to:

> “For a specified finite-rate tokenizer and task distribution, direct structured tensor IPC can improve fidelity and latency by avoiding an explicitly modeled quantization, serialization, and decoding bottleneck.”

That revised statement is defensible. The present universal claim is not.

---

## 2. Information-theoretic audit

### 2.1 The DPI chain is formally valid but substantively misinterpreted

For a Markov chain

\[
X \rightarrow Z_T \rightarrow \hat X,
\]

the data-processing inequality gives

\[
I(X;\hat X)\le I(X;Z_T).
\]

Also,

\[
I(X;Z_T)\le H(Z_T)\le L\log_2 |V|
\]

provided that \(Z_T\) is exactly an ordered sequence of \(L\) symbols from an alphabet \(V\).

For \(L=256\) and \(|V|=2^{17}\),

\[
H(Z_T)\le 256\cdot 17 = 4352\text{ bits}.
\]

A \(4096\)-component FP16 vector occupies

\[
4096\cdot16 = 65\,536\text{ bits}.
\]

Thus the raw storage ratio is

\[
\frac{65\,536}{4\,352}\approx 15.06.
\]

Those arithmetic statements are correct. They do **not**, however, prove that “one-dimensional tokenization” itself causes an unrecoverable defect.

The bound applies to the specified channel: exactly \(256\) discrete symbols, each selected from a \(2^{17}\)-element vocabulary. It does not apply to:

- variable-length coding;
- arithmetic or entropy coding;
- continuous-valued sequences;
- lossless serialization of floating-point values;
- learned latent codes with a larger effective rate;
- multiple parallel token streams;
- tokens whose semantics are task-specific and do not require reconstructing \(X\);
- stochastic decoders evaluated only on a downstream task.

A \(4096\)-dimensional vector can be serialized into a one-dimensional byte stream without information loss. “One-dimensional” describes arrangement, not rate. The loss arises from **finite rate, quantization, restricted codebooks, and the reconstruction objective**, not from dimensionality reduction in the geometric sense.

### 2.2 “Entropy defect” is not a defined invariant

The phrase \(\Delta H=0\) requires a precise definition. Candidate quantities include:

\[
H(X)-H(Z_T),
\]

\[
H(X\mid Z_T),
\]

\[
I(X;X)-I(X;\hat X),
\]

or task loss relative to a baseline. These are not interchangeable.

For continuous \(X\), differential entropy \(h(X)\) is not directly comparable to the discrete entropy \(H(Z_T)\) without specifying quantization resolution, reference measure, and distortion criterion. A raw FP16 vector is discrete, but its entropy is generally **not** \(65\,536\) bits unless every bit pattern is uniformly distributed. The correct quantity is

\[
H(X) \le 65\,536,
\]

with equality only under a maximal-entropy distribution over all valid bit patterns.

Similarly,

\[
H(Z_T)\le 4352
\]

is only a cardinality bound, not the actual entropy.

A defensible statement would be:

\[
I(X;Z_T)\le 4352
\]

for the specified interface, and therefore any task requiring more than that mutual information cannot be losslessly supported under the assumed distribution. The dissertation must then provide:

- the distribution of \(X\);
- the exact encoder and decoder;
- the reconstruction or task distortion;
- a rate-distortion comparison;
- confidence intervals over held-out data.

### 2.3 PMTP cannot have \(\Delta I=0\) without specifying the reference

If PMTP transmits \(X\) exactly and \(\hat X=X\), then

\[
I(X;\hat X)=I(X;X)=H(X)
\]

for discrete \(X\). But this is not “bypassing DPI.” DPI still holds with equality because the channel is lossless:

\[
I(X;\hat X)=I(X;Z)=H(X)
\]

if \(Z\) is an injective representation of \(X\).

If PMTP transmits a floating-point tensor, equality is only with respect to the transmitted floating-point object. It does not imply preservation of:

- the original real-valued neural state;
- gradients;
- stochastic state;
- optimizer state;
- device-specific NaN payloads;
- flush-to-zero behavior;
- non-deterministic reduction order.

The correct claim is “PMTP can implement an injective transport for a specified finite representation,” not “native manifold IPC has zero information loss” in an unrestricted semantic sense.

---

## 3. Stiefel retraction and Cayley analysis

### 3.1 The stated formula is not adequately specified

The proposed update is

\[
R_X(\Xi)
=
X+
U
\left(I_{2K}-\frac12V^\top U\right)^{-1}
V^\top X,
\]

with

\[
U=[\Xi,-X],\qquad V=[X,\Xi].
\]

Here \(X,\Xi\in\mathbb R^{D\times K}\), so \(U,V\in\mathbb R^{D\times 2K}\), and the dimensions are compatible. But dimensional compatibility is not proof of correctness.

A standard Cayley-type Stiefel retraction is generally derived from a skew-symmetric matrix

\[
A=\Xi X^\top-X\Xi^\top
\]

or a closely related tangent-space construction, followed by an update such as

\[
Q(\Xi)=\left(I-\frac12 A\right)^{-1}
\left(I+\frac12 A\right),
\qquad
R_X(\Xi)=Q(\Xi)X.
\]

The dissertation must prove that its low-rank Woodbury/Sherman–Morrison–Morrison representation is algebraically identical to the intended full-space expression. In particular, it must establish:

1. \(A^\top=-A\);
2. \(A X\) has the required tangent-space relation;
3. the sign and ordering of \(U,V\) reproduce \(I+\frac12A\) and \(I-\frac12A\);
4. the small matrix is nonsingular for all admitted \(\Xi\);
5. the output satisfies \(R_X(\Xi)^\top R_X(\Xi)=I_K\).

The expression \(I_{2K}-\frac12V^\top U\) is not self-validating. A sign error in \(U,V\) changes the map completely.

### 3.2 The asymptotic limit is highly suspect

The claimed limit is

\[
\lim_{t\to\infty}R_X(tZ)
=
(2P_{\ker(A)}-I_D)X.
\]

For a standard Cayley transform,

\[
Q(t)=\left(I-\frac{t}{2}A\right)^{-1}
\left(I+\frac{t}{2}A\right),
\]

the spectral behavior must be analyzed on the orthogonal decomposition

\[
\mathbb R^D=\ker(A)\oplus\operatorname{range}(A).
\]

On \(\ker(A)\), \(Q(t)\) acts as \(+I\). On a nonzero \(2\times2\) skew-symmetric block with eigenvalues \(\pm i\lambda\), the scalar Cayley factor is

\[
\frac{1+i t\lambda/2}{1-i t\lambda/2}
\longrightarrow -1
\]

as \(t\to\infty\). Therefore, under standard assumptions,

\[
Q(t)\longrightarrow P_{\ker(A)}-P_{\operatorname{range}(A)}
=
2P_{\ker(A)}-I_D.
\]

That limit can be correct for \(Q(t)\), but the dissertation must prove that its proposed \(R_X(tZ)\) is exactly \(Q(t)X\). The formula is not automatically valid if:

- \(A\) is singular;
- \(Z\) is not a valid tangent vector;
- the low-rank factorization changes with \(t\);
- the inverse is formed in finite precision;
- the implementation uses a stabilized or truncated solve.

The phrase “asymptotic limit” also conceals a numerical problem: \(t\to\infty\) is not a useful computational regime. The condition number of the small system, cancellation in \(I\pm tA/2\), and loss of tangent information must be quantified.

### 3.3 The machine-isometry claim is implausible as a universal guarantee

The assertion

\[
\|R_X(\Xi)^\top R_X(\Xi)-I_K\|_2\le 10^{-15}
\]

cannot be accepted without specifying:

- hardware;
- compiler;
- arithmetic format;
- matrix dimensions;
- condition numbers;
- reduction order;
- whether FMA is used;
- whether the bound is measured or proved;
- whether denormals are enabled;
- whether the inverse is FP64, FP32, or mixed precision.

A universal \(10^{-15}\) spectral-norm bound is especially implausible for large \(D\) under ordinary FP64 arithmetic. Even stable orthogonal transformations accumulate errors proportional to machine epsilon, matrix dimension, and conditioning. A realistic theorem would have a form such as

\[
\|\widehat R^\top\widehat R-I\|_2
\le
C(D,K,\kappa)\,u + O(u^2),
\]

where \(u\) is unit roundoff and \(C\) depends on the algorithm and conditioning.

The dissertation must distinguish:

- exact mathematical orthogonality;
- backward stability;
- forward error;
- empirical residuals on selected test cases.

---

## 4. Kulisch accumulator audit

### 4.1 The width arithmetic is inconsistent

The submission states

\[
W(N)=4196+\lceil\log_2N\rceil
\]

and then says that for \(N=2^{64}\) the instantiated width is \(4261\) bits. But

\[
4196+\lceil\log_2 2^{64}\rceil
=
4196+64
=
4260,
\]

not \(4261\).

An additional guard or sign bit could justify \(4261\), but it must be stated explicitly. The derivation needs to specify:

- the exact significand range;
- signed versus unsigned products;
- exponent alignment;
- cancellation requirements;
- carry propagation;
- guard, round, and sticky bits;
- overflow and underflow handling;
- whether \(N\) denotes terms, products, or partial sums.

The subsequent hardware capacity is also inconsistent:

- \(136\times32=4352\) bits;
- \(67\times64=4288\) bits.

These are different capacities. A structure declared as `int64_t b[136][8]` contains

\[
136\cdot 8\cdot 64=69\,632\text{ bits}
\]

or \(8\,704\) bytes, but this is a two-dimensional array of 64-bit elements, not a 136-limb, 32-bit-radix representation unless only half of each element is semantically used. The layout must be clarified.

### 4.2 The five-row deposit bound is not established

For a \(53\times53\)-bit product,

\[
53+53=106
\]

bits, and

\[
\left\lceil \frac{106}{64}\right\rceil=2.
\]

A bound of five contiguous 64-bit rows may be safe under particular alignment and carry conventions, but it does not follow from

\[
\left\lceil106/64\right\rceil+1=5.
\]

That expression evaluates to

\[
2+1=3,
\]

not \(5\).

To prove a five-row deposit bound, the dissertation must define the deposit operation precisely:

- Is the product shifted by an arbitrary exponent?
- Are limbs aligned to 32-bit or 64-bit boundaries?
- Is there a carry-in from the preceding limb?
- Is there a carry-out into the following limb?
- Are rows logical limbs or physical cache rows?
- Are partial products accumulated independently or atomically?

For arbitrary bit alignment, a 106-bit product can touch at most three 64-bit limbs before carry propagation. Additional rows may be required for accumulated carries, but that depends on the maximum number of overlapping deposits and their bounds. It is not a direct consequence of product width alone.

### 4.3 Exact reduction to IEEE RNE requires a complete specification

An exact integer accumulator can produce correctly rounded IEEE-754 results, but only if the reduction explicitly handles:

- sign determination after cancellation;
- leading-zero detection;
- normal/subnormal distinction;
- guard, round, and sticky bits;
- ties-to-even;
- underflow tininess policy;
- overflow to infinity versus maximum finite;
- signed zero;
- NaNs and signaling NaNs if applicable.

“Floor-form integer reduction” is insufficient as a theorem statement. The dissertation must give a bit-level algorithm and prove equivalence to IEEE-754 round-to-nearest-even for every exponent range and sign combination.

---

## 5. Cache and microarchitectural feasibility

The 8,704-byte object is below a 32 KiB L1D capacity. Zen 4 cores have a 32 KiB L1 data cache and 64-byte cache lines.[3] That does **not** imply that the object will remain resident or that it occupies only \(26.6\%\) of practically available L1 capacity.

The actual occupancy includes:

- stack or heap metadata;
- input and output arrays;
- loop state;
- register spills;
- instruction-side effects;
- other active working sets;
- set conflicts;
- hardware prefetch traffic;
- write-allocate lines;
- coherence states.

If the array has 136 rows of \(8\times8\) bytes, each row is exactly 64 bytes, which is cache-line aligned only if the base is aligned and the compiler does not introduce unexpected padding. `alignas(64)` on the array object helps alignment but does not guarantee favorable cache-set placement. A 136-line footprint can conflict with other hot lines depending on associativity and address mapping.

The key performance question is not “does it fit?” but:

\[
\text{cycles per deposit}
=
\text{load/store traffic}
+
\text{carry propagation}
+
\text{dependency-chain latency}
+
\text{reduction overhead}.
\]

A superaccumulator is often limited by serial carry chains rather than nominal cache bandwidth. The dissertation needs hardware-counter evidence:

- L1D load and store misses;
- L2 misses;
- cache-line writebacks;
- cycles stalled on memory;
- integer multiply throughput;
- carry-chain dependency latency;
- branch mispredictions;
- vector-unit utilization;
- frequency under sustained load.

### 5.1 “229.885 GB/s RAM throughput” is not self-explanatory

A single socket or core reporting 229.885 GB/s requires a precise benchmark definition. It may mean:

- aggregate socket DRAM bandwidth;
- read-plus-write traffic;
- cache bandwidth;
- non-temporal streaming bandwidth;
- modeled bytes rather than physically transferred bytes;
- throughput of a synthetic benchmark unrelated to the accumulator.

If the accumulator fits in L1, calling the result “RAM throughput” is misleading. If the benchmark uses reused cache-resident data, the number is not DRAM bandwidth. If the result is derived from operation count divided by time, it is an effective bandwidth, not a memory-subsystem measurement.

The dissertation must report raw counters and a roofline model, separating:

\[
B_{\text{effective}}
\neq
B_{\text{L1}}
\neq
B_{\text{L2}}
\neq
B_{\text{DRAM}}.
\]

---

## 6. Control-plane versus data-plane SLA

The decomposition is conceptually valid. A control-plane operation can complete in tens of microseconds while a 1.28 GB payload takes milliseconds. At 48 GB/s,

\[
\frac{1.28\ \text{GB}}{48\ \text{GB/s}}
\approx 26.7\ \text{ms}.
\]

Therefore, a \(34.8\,\mu\text{s}\) SLA cannot describe end-to-end movement of that payload.

The issue is not whether the decomposition is mathematically possible; it is whether the advertised SLA is being presented without qualification. A complete latency equation should be:

\[
T_{\text{e2e}}
=
T_{\text{validation}}
+
T_{\text{mapping}}
+
T_{\text{fence}}
+
T_{\text{queue}}
+
T_{\text{transfer}}
+
T_{\text{kernel}}
+
T_{\text{completion}}.
\]

If the data is already resident and only a descriptor is exchanged, \(T_{\text{control}}\) is relevant. If the consumer needs the bytes transferred, \(T_{\text{transfer}}\) dominates. If producer and consumer overlap, the effective critical path may be

\[
T_{\text{e2e}}
=
T_{\text{control}}
+
\max(T_{\text{transfer}},T_{\text{compute}})
\]

rather than a sum, but this must be demonstrated with a timeline.

The dissertation should report p50, p95, p99, and worst-case latency under:

- cold and warm caches;
- NUMA-local and NUMA-remote allocation;
- page faults;
- concurrent producers;
- IOMMU enabled;
- memory pressure;
- PCIe contention;
- GPU context interference;
- queue saturation.

“Exit Code 0” proves successful execution, not correctness, throughput, or reproducibility.

---

## 7. T4, UVA, and interprocess communication

The T4 is a PCIe Gen3 x16 device with 16 GB of GDDR6 memory.[10] Unified Virtual Addressing is an address-space abstraction, not a guarantee of peer-to-peer physical data movement or coherent shared memory.

A staged UVA path may involve:

1. GPU-to-host copy;
2. host synchronization;
3. host-to-peer-GPU copy;
4. kernel launch and stream synchronization.

That is materially different from direct P2P transport. The relevant comparison is:

\[
T_{\text{staged}}
=
T_{g_0\to h}
+
T_{\text{host synchronization}}
+
T_{h\to g_1}
+
T_{\text{launch}},
\]

versus

\[
T_{\text{P2P}}
=
T_{g_0\to g_1}
+
T_{\text{launch}}.
\]

The staged path can be appropriate when:

- peer access is unavailable;
- GPUs are in separate PCIe root complexes;
- topology prevents direct P2P;
- driver policy disables peer mapping;
- host staging enables better overlap.

But it consumes host memory bandwidth, PCIe bandwidth in both directions, and synchronization overhead. “139.78 GB/s sustained VRAM/SRAM tile reduction” must not be interpreted as 139.78 GB/s end-to-end IPC unless the benchmark includes all transfers and synchronization. A reduction kernel’s internal global-memory throughput is a different metric from interprocess communication throughput.

The evaluation must include:

- device topology;
- `cudaDeviceCanAccessPeer` results;
- P2P enabled/disabled cases;
- pinned versus pageable host memory;
- payload sizes;
- copy-engine overlap;
- PCIe transaction efficiency;
- kernel duration;
- end-to-end latency;
- comparison with NCCL and CUDA IPC.

---

## 8. TPU and XLA claims

TPUs execute through XLA compilation; Cloud TPU documentation states that XLA produces the device executable.[4][5] That creates a fundamentally different execution model from a general-purpose CPU process with dynamic pointer-based IPC.

The claimed bfloat16 contract also needs correction. TPU matrix multiplication commonly uses bfloat16 operands with float32 accumulation, and conversion behavior includes round-to-nearest-even, overflow to infinity, and flushing subnormals to zero.[1] Consequently, a bfloat16-versus-binary64 comparison is not merely a type substitution. It changes:

- representable significand precision;
- subnormal behavior;
- accumulation semantics;
- contraction and reassociation;
- compiler fusion;
- reduction order;
- stochastic or deterministic rounding assumptions.

Binary64 emulation on TPU is not equivalent to native FP64 unless the implementation proves exact emulation of all relevant operations and exceptional cases. A “contract” must specify whether it guarantees:

- numerical equivalence;
- bounded forward error;
- correctly rounded elementary operations;
- reproducibility across compiler versions;
- deterministic reductions;
- matching NaN and signed-zero behavior.

The dissertation should use explicit error bounds, for example:

\[
\frac{\|\widehat y-y\|}{\|y\|}
\le
\gamma_n^{(\mathrm{bf16/fp32})}\kappa(A)
+
\epsilon_{\mathrm{conversion}},
\]

with separate treatment for cancellation, ill-conditioning, and underflow. Theorems numbered “837” and “1182” are not meaningful evidence without statements, hypotheses, proof terms, and publicly reproducible artifacts.

---

## 9. Lean verification

Mechanization is valuable but theorem names alone establish nothing. The four claimed LeaseGuard theorems require inspection of:

- exact definitions;
- imported axioms;
- admitted proofs;
- noncomputable constructions;
- correspondence between the Lean model and generated Rust/C++/GPU code;
- memory model assumptions;
- floating-point formalization;
- compiler transformations;
- FFI boundaries.

In particular:

- Memory disjointness in Lean may prove separation in an abstract heap, not absence of C++ data races under the C++ memory model.
- ABA immunity requires a bounded-wraparound argument. A 64-bit epoch is practically robust, not mathematically immune if epochs can wrap.
- Neumaier stability is not a proof of correct rounding or subnormal preservation.
- DPI invariance requires precise probabilistic semantics and cannot be established by a type-level serialization theorem alone.

A serious systems verification claim needs a refinement theorem:

\[
\operatorname{Trace}_{\text{implementation}}
\subseteq
\operatorname{Trace}_{\text{specification}},
\]

including the relevant memory ordering, device synchronization, and numerical behavior.

---

## 10. Comparison with existing systems

The proposed architecture must be compared against the right baselines.

### Apache Arrow

Arrow provides a columnar, language-interoperable memory representation with zero-copy opportunities. It is not primarily a high-dimensional manifold transport protocol, but it already addresses schema, layout, and cross-language exchange. PMTP must demonstrate benefits beyond Arrow’s fixed-width tensor buffers and device-memory extensions.

### Ray Plasma

Plasma-style object stores provide immutable shared objects, ownership, lifecycle management, and process-level exchange. PMTP may improve latency by avoiding object-store copies, but it must compare:

- object creation;
- sealing;
- metadata exchange;
- ownership transfer;
- fault recovery;
- eviction;
- backpressure;
- multi-node behavior.

### NCCL

NCCL is optimized for GPU collectives and topology-aware transport. A single tensor handoff is not automatically a collective advantage. PMTP needs comparisons with NCCL point-to-point or collective paths under equivalent topology, synchronization, and payload conditions.

### TensorRT

TensorRT is an inference compiler/runtime, not a general IPC system. A comparison is meaningful only for end-to-end inference pipelines where tokenization, tensor handoff, kernel scheduling, and engine execution are all measured.

The strongest novelty claim is therefore not “a new universal IPC paradigm,” but potentially:

> a verified, typed, zero-copy tensor exchange protocol with explicit numerical and lifetime contracts for heterogeneous CPU/GPU processes.

That could be publishable if demonstrated rigorously.

---

## 11. Does this eliminate the “1D worm collapse”?

No. It may eliminate a **specific serialized discrete bottleneck** in a particular multi-agent pipeline. It does not establish that one-dimensional representations are intrinsically inferior.

Neural systems routinely use one-dimensional buffers, packed tensors, sequences, and byte streams while preserving arbitrary information. The relevant distinction is:

\[
\text{representation dimensionality}
\quad\neq\quad
\text{information rate}
\quad\neq\quad
\text{semantic sufficiency}.
\]

A direct high-dimensional tensor interface can reduce:

- quantization error;
- encode/decode latency;
- memory copies;
- vocabulary lookup;
- autoregressive serialization overhead.

But it may increase:

- bandwidth;
- synchronization complexity;
- memory footprint;
- security attack surface;
- coupling between model versions;
- failure-domain size;
- numerical portability problems.

The work would represent a systems optimization and interface redesign, not a demonstrated AGI phase transition, unless it shows broad gains across tasks, models, hardware, and competing representations.

---

## 12. Required revisions before a defense

At minimum, the committee should require:

1. **A corrected information-theoretic theorem**
   - Define \(X\), \(Z_T\), \(\hat X\), and the task.
   - Distinguish entropy bounds from actual entropy.
   - Replace “one-dimensional defect” with a finite-rate channel statement.
   - Include a rate-distortion or task-distortion analysis.

2. **A complete Cayley derivation**
   - State the exact full-space transform.
   - Derive the low-rank form using Woodbury.
   - Prove nonsingularity.
   - Prove the asymptotic limit.
   - Give finite-precision error bounds.

3. **A corrected accumulator specification**
   - Resolve 4260 versus 4261 bits.
   - Resolve 4288 versus 4352-bit representations.
   - Correct the five-row derivation.
   - Prove IEEE-754 RNE equivalence, including subnormals and cancellation.

4. **End-to-end benchmarks**
   - Measure payload movement, not merely kernel bandwidth.
   - Compare staged UVA, P2P, CUDA IPC, NCCL, Arrow, and a conventional serialization baseline.
   - Report confidence intervals and tail latency.
   - Publish benchmark code and topology.

5. **Hardware-counter evidence**
   - Separate L1, L2, DRAM, PCIe, VRAM, and effective bandwidth.
   - Include NUMA and contention experiments.
   - Explain all compiler flags and clock states.

6. **Formal verification artifacts**
   - Make Lean source, theorem statements, assumptions, and proof status available.
   - State exactly what is verified and what remains outside the model.
   - Provide a refinement argument from specification to implementation.

7. **A narrowed scientific conclusion**
   - Remove universal AGI claims.
   - State the workload and hardware conditions under which PMTP wins.
   - Quantify the tradeoff between bandwidth, fidelity, latency, and coupling.

---

## Final doctoral verdict

**Recommendation: Reject in present form; invite resubmission after major reconstruction.**

The submission contains potentially valuable components:

- a legitimate observation that finite-rate token interfaces have information-capacity limits;
- a potentially useful low-rank orthogonal update;
- an interesting exact-accumulation implementation direction;
- a sensible distinction between control-plane and data-plane latency.

However, the current manuscript does not meet doctoral standards because its headline conclusions exceed what the mathematics and measurements establish. The most serious defects are:

- treating a finite-vocabulary rate bound as a theorem about one-dimensionality;
- asserting \(\Delta H=0\) and \(\Delta I=0\) without operational definitions;
- presenting inconsistent accumulator-width arithmetic;
- providing an unsupported five-row deposit proof;
- asserting near-machine-precision isometry without a numerical error theorem;
- conflating kernel throughput, memory bandwidth, and end-to-end IPC;
- treating UVA as evidence of direct peer transport;
- comparing TPU numerical modes without a complete precision contract;
- using mechanized theorem titles as a substitute for inspectable formal correspondence.

A revised dissertation could become a strong systems-and-numerics contribution if it abandons the universal “dimension is all you need” thesis and instead proves a narrower result: **under specified rate, fidelity, topology, and numerical-contract assumptions, verified tensor-native IPC can outperform discrete serialization for selected heterogeneous inference workloads.**

---

## 2. FUENTES Y CITAS BIBLIOGRÁFICAS PERPLEXITY

1. https://docs.cloud.google.com/tpu/docs/bfloat16
2. https://www.amd.com/content/dam/amd/en/documents/products/embedded/ryzen/amd-ryzen-embedded-8000-product-brief.pdf
3. https://docs.amd.com/api/khub/documents/7HYBEP83IGNYJKH5mRVl5A/content
4. https://docs.cloud.google.com/tpu/docs/intro-to-tpu
5. https://docs.cloud.google.com/tpu/docs/performance-guide
6. https://cloud.google.com/blog/products/ai-machine-learning/train-ml-models-with-pytorch-lightning-on-tpus
7. https://developers.google.com/edge/api/tflite/c/struct/tf-lite-b-float16
8. https://docs.cloud.google.com/tpu/docs
9. https://cloud.google.com/tpu
10. https://www.nvidia.com/en-us/data-center/tesla-t4/
