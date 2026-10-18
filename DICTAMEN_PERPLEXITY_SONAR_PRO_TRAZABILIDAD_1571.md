# DICTAMEN PERPLEXITY SONAR-PRO: TRAZABILIDAD TEOREMA-A-SILICIO (1.571 TEOREMAS)

> **Fecha y Hora:** 2026-10-10 14:00:07
> **Modelo:** `sonar-pro` (Perplexity AI)
> **Latencia:** 28.27 s | **Tokens:** 6700

The specification is **not presently defensible as a certified theorem-to-silicon traceability system**. It contains several plausible engineering components, but its strongest claims conflate theorem indexing with formal correspondence, exact accumulation with numerical exactness, zero-copy transport with information-theoretic invariance, and source-level pattern matching with proof of implementation correctness. The Cayley claim is substantially correct under explicit hypotheses; the Kulisch claim is materially overstated and internally inconsistent; the Hodge/Betti and cross-language claims are unsubstantiated without artifacts, invariants, proof obligations, and reproducible measurements.

## 1. Methodological audit

### 1.1 “Bijective mapping” is not established by AST and regex scanning

An AST/regex scanner can establish, at most, that:

- a syntactic pattern occurs in source code;
- an identifier resembles a theorem identifier;
- a function contains expressions resembling a mathematical formula;
- a source file is associated with a binary or build target.

It cannot establish that the compiled machine code computes the claimed mathematical function for all admissible inputs.

A genuine theorem-to-implementation correspondence requires a chain such as

\[
\text{formal theorem}
\;\Longrightarrow\;
\text{executable specification}
\;\Longrightarrow\;
\text{verified refinement}
\;\Longrightarrow\;
\text{compiled artifact}
\;\Longrightarrow\;
\text{deployed binary}
\;\Longrightarrow\;
\text{observed execution}.
\]

Each arrow requires a separately checkable relation. In particular:

- **Theorem identity:** immutable theorem hash, namespace, assumptions, conclusion, dependencies.
- **Executable specification:** typed preconditions, postconditions, representation invariants, error semantics, rounding model.
- **Refinement proof:** proof that implementation behavior satisfies the specification.
- **Compiler provenance:** source revision, compiler version, flags, target ISA, linker, dependencies, and reproducible build hash.
- **Binary validation:** disassembly, control-flow integrity, symbol provenance, and runtime artifact hash.
- **Execution evidence:** test vectors, coverage, hardware identification, microcode-relevant configuration, and failure logs.

A scanner does not prove any of these refinement relations. It also cannot prove noninterference, absence of undefined behavior, absence of data races, correct aliasing, or semantic equivalence after optimization.

The “zero-orphan invariant” is therefore a **catalogue invariant**, not a correctness invariant. It proves only that every theorem has been assigned a status. It does not prove that every assignment is true.

### 1.2 Pure analytical proofs are not interchangeable with executable correctness

A Lean theorem may formally prove a mathematical proposition, but this does not automatically establish that a C++, Rust, Triton, or Dart implementation realizes that proposition.

The missing bridge is a refinement theorem of the form

\[
\forall x \in \mathcal D,\qquad
\operatorname{decode}(\operatorname{run}(I,\operatorname{encode}(x)))
=
f(x),
\]

or, for approximate floating-point code,

\[
d\!\left(\operatorname{fl}(I(x)),f(x)\right)
\leq \varepsilon(x),
\]

with explicitly defined:

- domains;
- exceptional values;
- finite-precision semantics;
- memory model;
- concurrency model;
- permitted nondeterminism;
- error metric;
- observable side effects.

Labeling 548 results `PURE_ANALYTICAL_PROOF` is not a substitute for this refinement layer. The partition is valid only if the dissertation explicitly says that it classifies **proof obligations**, rather than claiming whole-system certification.

### 1.3 The theorem count is not a complexity or rigor metric

The number 1,571 has no evidentiary value without:

- definitions of “theorem”;
- proof dependency graphs;
- distinction between lemmas, corollaries, axioms, imported results, and generated obligations;
- proof-kernel replay;
- independent checking of the database against the source repository;
- handling of duplicated or parametrically instantiated propositions.

A database row marked “certified” is not equivalent to a kernel-checked proof. The dissertation must provide a machine-readable manifest and an independently replayable build.

## 2. Mathematical audit

## 2.1 Cayley transform claim

Let \(A^T=-A\), and define

\[
C(t)=\left(I-\frac t2A\right)^{-1}
      \left(I+\frac t2A\right).
\]

For real skew-symmetric \(A\), the eigenvalues over \(\mathbb C\) are \(i\lambda_j\), where \(\lambda_j\in\mathbb R\), together with possible zero eigenvalues. On an eigenvector associated with \(i\lambda\),

\[
c_\lambda(t)
=
\frac{1+i t\lambda/2}{1-i t\lambda/2}
=
\exp\!\left(2i\arctan(t\lambda/2)\right).
\]

Thus the spectral formula is correct. The matrix \(I-\frac t2 A\) is nonsingular for every real \(t\), because the eigenvalues of \(\frac t2A\) are purely imaginary.

For \(\lambda>0\),

\[
\theta_\lambda(t)=2\arctan(t\lambda/2)
\]

is strictly increasing, with

\[
\theta_\lambda'(t)
=
\frac{\lambda}{1+(t\lambda/2)^2}>0,
\qquad
\lim_{t\to+\infty}\theta_\lambda(t)=\pi.
\]

For \(\lambda<0\), the phase decreases toward \(-\pi\). Consequently,

\[
c_\lambda(t)\to -1
\quad \text{for every }\lambda\neq 0,
\]

while \(c_0(t)=1\). Therefore,

\[
\lim_{t\to+\infty}C(t)
=
P_{\ker A}-P_{(\ker A)^\perp}
=
2P_{\ker A}-I.
\]

This limit is an orthogonal involution:

\[
R^T R=I,
\qquad
R^2=I,
\qquad
R|_{\ker A}=I,
\qquad
R|_{(\ker A)^\perp}=-I.
\]

The claim is therefore mathematically sound **provided that**:

- \(A\) is real and skew-symmetric;
- the limit is taken in finite-dimensional operator norm or an equivalent matrix topology;
- “monotonic convergence” refers to the scalar phase \(\theta_\lambda(t)\), not to matrix entries, eigenvectors, or a global matrix order;
- the zero-eigenvalue subspace is handled explicitly;
- numerical implementation does not attempt to evaluate the \(t\to\infty\) limit by forming an ill-conditioned inverse.

The phrase “generalized Householder reflector” requires qualification. A conventional Householder reflector has the form

\[
H=I-2uu^T
\]

and changes sign on a one-dimensional subspace. Here,

\[
2P_{\ker A}-I
\]

changes sign on the entire orthogonal complement of the kernel. It is an orthogonal involution, but not generally a rank-one Householder reflector. It is better described as a generalized orthogonal reflection or a subspace reflection.

A further systems issue is that the Cayley map omits orthogonal matrices having eigenvalue \(-1\). The limiting reflector is obtained only as \(t\to\infty\); it is not necessarily the finite-\(t\) image of a regular Cayley transform. The claimed “retraction” terminology is also potentially wrong: a retraction normally maps a tangent-space neighborhood to a manifold and satisfies first-order agreement with the exponential map at the origin. A global asymptotic limit is not itself a retraction.

## 2.2 Kulisch-width claim

The specification contains three distinct quantities that must not be conflated:

1. the exponent span needed to represent a single exact product;
2. the width needed to represent a sum of \(N\) such products;
3. the width needed under a particular signed encoding and overflow convention.

A binary64 significand has 53 bits of precision. The exact product of two finite binary64 values has up to 106 significand bits. A full Kulisch accumulator is commonly described as a fixed-point accumulator covering the complete binary64 product range; published design literature frequently uses 4,288 bits, corresponding to \(67\times64\) bits.[1][2][3]

However, the assertion

\[
W_{\min}=4261
\]

followed by

\[
4288-4261=27
\]

is not established by the supplied reasoning.

If the maximum product magnitude is bounded by \(2^{2048}\), then summing \(N\leq2^{64}\) terms gives

\[
\left|\sum_{k=1}^{N}p_k\right|
\leq N\,2^{2048}
\leq 2^{2112},
\]

not \(2^{4260}\). The \(2^{4260}\) expression appears to combine exponent ranges in a way that requires a precise definition of the accumulator coordinate system. It cannot be accepted as a bound merely because the operands span a large exponent interval.

Moreover:

- “minimum positive” is ambiguous: binary64’s minimum positive subnormal is \(2^{-1074}\), while the minimum product of two nonzero subnormals is \(2^{-2148}\);
- the largest finite binary64 number is slightly below \(2^{1024}\), so the maximum finite product is slightly below \(2^{2048}\), not exactly \(2^{2048}\);
- the exact signed width depends on whether the representation is sign-magnitude, two’s complement, redundant carry-save, or a nonnegative magnitude plus sign;
- adding \(N\) products requires an explicit \(N\)-dependent carry bound;
- NaNs, infinities, signed zero, underflow policy, and overflow policy must be excluded or specified.

The published 4,288-bit figure supports the engineering plausibility of a complete binary64 Kulisch accumulator, not the claimed proof that 4,261 bits is the exact minimum for the stated workload.[1][2][3] The specification must provide a bit-index derivation identifying:

\[
\text{LSB weight},\qquad
\text{MSB weight},\qquad
\text{carry headroom},\qquad
\text{signed encoding},
\]

and then prove minimality by constructing an attainable input whose exact sum requires the proposed top bit.

The statement

> “machine precision \(\epsilon_{\mathrm{mach}}=0\)”

is false as written. Exact accumulation can make the accumulator operation associative and eliminate rounding **during accumulation**, but conversion back to binary64 can round, overflow, underflow, or lose information. The correct claim is something like:

\[
S_{\mathrm{acc}}=\sum_{k=1}^{N}x_k y_k
\]

is represented exactly in the accumulator, subject to representability and finite-width hypotheses. The final returned floating-point value is exact only if \(S_{\mathrm{acc}}\) is binary64-representable or a correctly rounded conversion is performed.

The use of `VPMULUDQ` also requires scrutiny. A 53-bit significand product is mathematically exact in a sufficiently wide integer representation, but the instruction’s operand width, lane layout, upper-bit handling, carry propagation, and signedness must be proven against the implementation. “53-bit exact integer multiplication” is not by itself a proof of a 106-bit product pipeline.

## 2.3 Discrete Hodge Laplacian and Betti-1 filtration

The Hodge-theoretic claims are too underspecified to audit.

For a finite simplicial complex \(K\), with oriented boundary matrices \(B_k\), the combinatorial Hodge Laplacian is

\[
\Delta_k
=
B_{k+1}B_{k+1}^{T}
+
B_k^{T}B_k.
\]

The harmonic \(k\)-cochains satisfy

\[
\mathcal H^k(K)=\ker \Delta_k
=
\ker B_k \cap \ker B_{k+1}^{T},
\]

and, over a field of characteristic zero,

\[
\dim \mathcal H^k(K)=\beta_k(K).
\]

But the specification mixes:

- real or rational Hodge theory;
- GF(2) homology;
- Vietoris–Rips complexes;
- a 1-skeleton;
- a geometric sphere \(S^{D-1}\);
- a “filtration.”

These are not interchangeable.

A graph’s 1-skeleton alone has no 2-simplices, so its graph cycle space is not the same as simplicial \(H_1\). For a graph \(G\),

\[
\dim Z_1(G;\mathbb F_2)=|E|-|V|+\beta_0(G),
\]

but simplicial homology is

\[
H_1(K;\mathbb F_2)
=
\ker \partial_1/\operatorname{im}\partial_2.
\]

The triangle boundaries supplied by \(\partial_2\) can eliminate graph cycles. Any claim about Betti-1 must state whether it computes:

- cycle-space dimension of the graph;
- \(H_1\) of the full Vietoris–Rips complex;
- persistent \(H_1\) over a filtration;
- harmonic representatives over \(\mathbb R\);
- homology over \(\mathbb F_2\).

A real Hodge Laplacian does not directly produce GF(2) homology. Mod-2 boundary algebra requires arithmetic over \(\mathbb F_2\), whereas Hodge decomposition generally uses an inner product over \(\mathbb R\), \(\mathbb Q\), or another characteristic-zero field. A valid bridge requires an explicit comparison theorem; absent that, the system is combining related but distinct computations.

The phrase “on \(S^{D-1}\)” also requires a sampling model. A finite point cloud on a sphere does not automatically inherit the sphere’s homology. The result depends on:

- sampling density;
- metric;
- duplicate and antipodal points;
- radius;
- floating-point distance comparisons;
- filtration thresholds;
- open versus closed simplex conventions;
- coefficient field;
- numerical rank tolerance.

At finite sample size, the complex can have spurious cycles and missing cycles. This is a statistical and topological inference problem, not merely an implementation detail.

## 3. Systems architecture and verification

### 3.1 Cross-language ABI

The C++/Rust/Triton/Dart bridge requires a single authoritative ABI specification. For every shared structure, document:

- size and alignment;
- field offsets;
- endianness;
- integer widths;
- enum representation;
- pointer ownership;
- lifetime;
- mutability;
- atomicity;
- padding initialization;
- versioning;
- error and status encoding.

`@Packed(1)` is especially dangerous. It removes natural alignment and can induce unaligned accesses, inefficient code generation, hardware faults on some targets, or non-atomic accesses to fields that would otherwise be naturally aligned. A packed wire representation should generally be copied into a naturally aligned internal representation before use. Packed layout is not a concurrency protocol.

The claim of “strict 8-byte alignment” is incompatible with indiscriminate packed structures unless the specification distinguishes wire layout from in-memory layout. A 280-byte or 88-byte object may have a stable size but still contain fields at offsets unsuitable for atomic operations or SIMD loads.

### 3.2 Memory ordering and lock-free correctness

A ring buffer or QSBR implementation is not validated by the label “lock-free.” The proof must specify:

- producer and consumer counts;
- single-producer/single-consumer versus multiple-producer/multiple-consumer;
- reservation protocol;
- sequence counters;
- ABA prevention;
- wraparound behavior;
- linearization points;
- acquire/release or stronger memory orders;
- cache-line ownership;
- publication and reclamation ordering;
- behavior under thread preemption.

For QSBR, reclamation is safe only if every reader that could hold a pointer has passed through a quiescent state after publication of the retirement epoch. The proof must account for:

- thread registration and deregistration;
- stalled readers;
- thread suspension;
- signal handlers;
- foreign runtimes;
- GPU consumers;
- process crashes;
- epoch counter wraparound;
- memory visibility across processes.

C++ atomics do not automatically provide a portable interprocess memory model for arbitrary shared-memory mappings. Process-shared correctness must be established for the target operating systems and architectures, including cache coherence and mapping attributes.

### 3.3 NUMA and cache coherence

Zero-copy does not imply low latency. A shared-memory descriptor may incur:

- remote NUMA access;
- cache-line migration;
- false sharing;
- write amplification;
- TLB misses;
- page faults;
- IOMMU translation;
- PCIe or GPU interconnect latency.

The architecture needs measurements partitioned by:

- local versus remote NUMA placement;
- core pinning;
- producer/consumer topology;
- cache-hot versus cache-cold operation;
- payload size;
- queue depth;
- contention;
- CPU frequency state;
- page size;
- GPU transfer path.

A ring index and descriptor should be placed on separate cache lines when ownership differs. Memory fences do not eliminate cache-coherence traffic.

### 3.4 Subnormal handling

“Subnormal float injection fuzzing” is not sufficient. x86 execution can be affected by MXCSR settings, including flush-to-zero and denormals-are-zero behavior. GPU and ARM behavior can differ. The implementation must record and validate:

- rounding mode;
- exception masks;
- FTZ/DAZ state;
- FMA contraction;
- reassociation;
- SIMD instruction selection;
- compiler fast-math flags;
- GPU flush behavior;
- treatment of signed zero;
- NaN payload and signaling behavior.

If the theorem assumes IEEE 754 gradual underflow but the machine executes with FTZ/DAZ, the implementation is not a realization of that theorem. Conversely, if FTZ/DAZ is part of the intended model, it must appear in the formal specification.

### 3.5 Anti-aliasing

“Zero partial aliasing” is not a meaningful certification phrase unless translated into a formal memory property. The relevant questions are:

- Are pointers `restrict`-like?
- Does Rust’s aliasing model remain valid across FFI?
- Are Dart finalizers concurrent with native access?
- Can the GPU access memory after the host believes it has been reclaimed?
- Are descriptor fields mutated while readers hold them?
- Are lifetime tokens represented in the type system?
- Are all externally visible writes atomic or protected by publication ordering?

Rust’s safety guarantees stop at unsafe FFI boundaries. A `NativeFinalizer` does not prove that no outstanding native or GPU reference exists.

## 4. Red-team challenges

An adversarial committee member should demand answers to the following.

### Mathematical counterexamples and ambiguities

- What exactly does “monotonic” mean for a complex eigenvalue or matrix?
- Is the Cayley limit a retraction, a reflector, or merely an asymptotic orthogonal limit?
- Does the theorem handle \(A=0\), repeated eigenvalues, rank deficiency, and arbitrary basis choices?
- Is the claimed Kulisch width derived from attainable bounds or loose exponent arithmetic?
- What happens with \(0\), subnormals, infinities, NaNs, cancellation, and signed zero?
- Is the accumulator result exact before or after final rounding?
- Are Hodge harmonic spaces computed over \(\mathbb R\) while Betti numbers are computed over \(\mathbb F_2\)?
- Does “Betti-1” refer to graph cycles or homology after filling 2-simplices?
- What theorem connects the sampled Vietoris–Rips complex to \(S^{D-1}\)?

### Hardware and compiler challenges

- What happens on AVX2, AVX-512, ARMv8, and heterogeneous machines?
- Are binaries compiled with `-ffast-math`, FMA contraction, or reassociation?
- Are MXCSR and GPU floating-point modes captured in the trace?
- Does the same binary produce the same result under different microarchitectures?
- Are atomics lock-free according to the target implementation, or merely syntactically atomic?
- Is shared memory mapped with compatible cache attributes in every process?
- Can a stalled consumer prevent reclamation indefinitely?
- What happens when a process dies while owning a ring slot?
- Can epoch counters wrap?
- Are packed fields read atomically?
- Is the GPU stream synchronized before reclamation?
- Can Dart garbage collection invoke finalization while native work remains in flight?

### Evidence challenges

The committee should require:

- a public theorem manifest;
- Lean proof replay from a clean environment;
- formal definitions of all 1,571 propositions;
- source-to-binary reproducibility;
- signed artifact hashes;
- disassembly and compiler provenance;
- ABI layout tests generated independently in each language;
- litmus tests for the memory protocol;
- model checking of queue and reclamation algorithms;
- differential tests across CPU architectures;
- exact reference implementations for numerical kernels;
- adversarial tests for NaNs, subnormals, overflow, underflow, aliasing, and cancellation;
- performance experiments with confidence intervals and raw traces;
- independent replication by a party not involved in implementation.

The claimed 14,120× speedup is especially vulnerable. It needs a complete baseline definition, equal semantic workload, identical data source, warm-up policy, allocation accounting, serialization format, thread count, NUMA placement, GPU synchronization policy, and statistical uncertainty. A zero-copy descriptor cannot be compared fairly with a full \(O(D)\) serialization pipeline unless both systems perform equivalent work.

The claim \(\Delta H=0\) is also undefined. Entropy of what random variable? Payload bytes, descriptor states, application-level information, or observer uncertainty? A representation change can preserve information while changing entropy under a specified distribution, and synchronization metadata can leak information. “Zero-copy” is a transport property, not an entropy theorem.

## 5. Required corrective program

Before defense, the project should be reduced to explicit, testable claims:

1. Replace “bijective mapping” with **traceability relation** unless a formal bijection between theorem objects and implementation obligations is proved.
2. Separate theorem identity, proof status, executable specification, refinement status, and deployment status.
3. Publish exact Lean definitions and replayable proof builds.
4. Derive the Kulisch width from bit indices and encoding assumptions; remove the phrase \(\epsilon_{\mathrm{mach}}=0\).
5. State all floating-point modes and exceptional-value policies.
6. Formalize the ring buffer and QSBR linearization and reclamation proofs.
7. Replace packed shared structs with versioned wire layouts plus aligned internal layouts.
8. Define Hodge and GF(2) computations separately and specify whether 2-simplices are included.
9. Replace \(\Delta H=0\) with a precisely defined information-preservation theorem, if one exists.
10. Reproduce performance results under controlled and independently audited conditions.

## Final verdict

The work contains the outline of a potentially valuable systems-and-mathematics research platform, and the finite-dimensional Cayley-limit result is defensible after careful qualification. The existence and usefulness of 4,288-bit Kulisch accumulators are also supported by established exact-accumulation literature,[1][2][3] but that does not validate the asserted 4,261-bit minimality, the 27-bit margin, or the claim of zero machine precision.

In its current form, the system **does not meet the highest standards for a doctoral dissertation defense claiming certified theorem-to-silicon correspondence**. The central deficiency is not implementation ambition; it is evidentiary structure. A theorem database, lexical mapper, Lean proof partition, and collection of optimized kernels do not constitute a verified refinement chain.

The appropriate recommendation is **major revision and conditional resubmission**, not acceptance. Acceptance would become plausible only after the project narrows its claims, supplies formal refinement proofs and ABI/concurrency models, corrects the Kulisch and entropy assertions, separates real Hodge theory from GF(2) homology, and provides independently reproducible artifact-level evidence.

---
*Dictamen certificado bajo Regla 15 y Regla 35 de POLYDIM-EINSOF.*
