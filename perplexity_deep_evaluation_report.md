# DICTAMEN DE AUDITORÍA SOTA — PERPLEXITY (SONAR-PRO)
## Evaluación de la Suite de Reproducibilidad y Fundamentos de POLYDIM EINSOF
**Fecha y Hora:** 2026-10-10 14:00:41

The suite contains several sound ideas, but the stated claims are not yet sufficient for a dissertation-level verification record. The strongest components are scaled norm computation, reorthogonalized MGS, and shared-memory transport. The principal technical corrections are:

- a norm defect of \(1.11\times10^{-16}\) does **not** establish a condition number of \(1\);
- two MGS passes do **not** guarantee machine-precision orthogonality independently of the input conditioning;
- the stated \(4{,}352\)-bit accumulator is not the canonical minimum for every exact binary64 dot-product model, and its bit indexing must be reconciled with signed range, product alignment, and accumulator headroom;
- “zero-copy” does not imply entropy preservation, and JSON does not necessarily violate the data-processing inequality.

## 1. Scope and audit assumptions

The empirical results cannot be independently certified without the actual source, hardware, Python version, compiler/runtime details, input distributions, and reproducibility logs. Therefore, the mathematical review below evaluates the algorithms and the claims as stated.

Let \(u\) denote unit roundoff for binary64:

\[
u=2^{-53}\approx 1.1102230246251565\times 10^{-16}.
\]

For a sequence of \(n\) floating-point operations, define

\[
\gamma_n=\frac{nu}{1-nu},
\]

provided \(nu<1\). Standard forward-error bounds use \(\gamma_n\), but these are worst-case bounds, not predictions of observed error.

---

# Component 1: Hyperspherical normalization

## 1.1 Scaled sum-of-squares algorithm

For \(x\in\mathbb{R}^D\), define

\[
s=\max_i |x_i|,
\qquad
q=\sum_{i=1}^{D}\left(\frac{x_i}{s}\right)^2,
\qquad
\|x\|_2=s\sqrt{q}.
\]

If \(0<s<\infty\), every scaled component lies in \([0,1]\). Consequently, squaring cannot overflow, and the sum of squares is at most \(D\), so the scaled accumulation is safe from overflow even when \(s\) is close to \(\mathrm{DBL}_{\max}\). This is the essential protection supplied by the Blue/LASSQ strategy.

However, the phrase “protects against underflow” requires qualification. If \(s\) is large and some \(x_i\) is tiny, the ratio \(x_i/s\) may underflow to zero even though \(x_i\) itself is representable. Such a term is then lost. The algorithm prevents catastrophic overflow and substantially reduces underflow risk, but it does not guarantee preservation of every nonzero contribution.

For a vector whose nonzero entries are all subnormal, choosing \(s\) as the largest magnitude still keeps the largest normalized term equal to one. Smaller terms may disappear, but their relative contribution may already be below the attainable precision of the norm.

The implementation must explicitly handle:

- \(x=0\), for which normalization is undefined;
- NaNs and infinities;
- \(s=\mathrm{DBL}_{\max}\);
- subnormal inputs and platforms using flush-to-zero;
- signed zero;
- vectors containing one infinite entry and finite entries.

## 1.2 Naive summation error

For nonnegative exact terms \(a_i\), sequential floating-point summation satisfies

\[
\operatorname{fl}\left(\sum_{i=1}^{D}a_i\right)
=
\left(\sum_{i=1}^{D}a_i\right)(1+\theta_{D-1}),
\qquad
|\theta_{D-1}|\le \gamma_{D-1}.
\]

For \(D=10^4\),

\[
\gamma_{9999}\approx 1.11\times 10^{-12}.
\]

For \(D=10^7\),

\[
\gamma_{9\,999\,999}\approx 1.11\times 10^{-9}.
\]

These are relative bounds under the usual model, assuming no overflow, underflow, subnormal anomalies, or exceptional values. They are not generally attainable worst cases, but they demonstrate why a measured \(10^{-16}\)-scale result cannot be interpreted as a universal bound for naive accumulation.

For a norm computed from the squared scaled values, additional errors arise from:

1. division by \(s\);
2. squaring;
3. accumulation;
4. square root;
5. final normalization.

Thus the full norm error is not described solely by the summation error.

## 1.3 Neumaier compensation

Neumaier summation maintains a running sum and a correction term. Under the standard floating-point model, its forward error is commonly bounded by a first-order expression of the form

\[
|\widehat{S}-S|
\lesssim
\left(2u+O(nu^2)\right)\sum_i |a_i|,
\]

assuming no exceptional behavior. More conservative analyses express the result as a small constant multiple of \(u\sum_i|a_i|\), rather than \(\gamma_n\sum_i|a_i|\).

For nonnegative terms, the distinction is particularly useful: Neumaier compensation largely removes the linear dependence on \(n\) that appears in the naive worst-case bound. It does not make the result exact, and it does not make the computation independent of evaluation order.

For \(D=10^4\) and \(D=10^7\), the practical interpretation is:

| Method | Typical first-order error scale |
|---|---:|
| Naive sequential sum | \(O(Du)\) |
| Pairwise/tree sum | \(O(u\log D)\) |
| Kahan/Neumaier compensation | \(O(u)\) times a modest constant |

The exact constant depends on the implementation, compiler transformations, treatment of subnormals, and whether intermediate arithmetic is performed in binary64 without contraction or excess precision.

In CPython, Python-level floating-point additions are generally individually rounded to binary64, but this should still be verified experimentally on the target interpreter and platform. Reproducibility requires specifying the summation order and forbidding replacement by a different reduction strategy.

## 1.4 Verification norm versus construction norm

A crucial methodological issue is whether the reported defect was measured using the same numerical pathway used to construct \(u\). If the vector is normalized with a compensated norm and verified with another compensated norm, the result is meaningful but not independent.

A stronger audit reports at least:

\[
\left|\operatorname{fl}_{\mathrm{naive}}(\|u\|_2)-1\right|,
\]

\[
\left|\operatorname{fl}_{\mathrm{pairwise}}(\|u\|_2)-1\right|,
\]

and, where feasible, a high-precision reference. Otherwise, the \(1.11\times10^{-16}\) value demonstrates consistency with binary64 rounding but does not prove that the true norm defect is exactly at that scale.

## 1.5 Condition number

The norm map \(f(x)=\|x\|_2\) has relative condition number one for nonzero \(x\):

\[
\kappa_f(x)
=
\frac{\|x\|_2}{\|x\|_2}=1
\]

under the usual relative perturbation model, because

\[
|\|x+\delta x\|_2-\|x\|_2|
\le \|\delta x\|_2.
\]

That is a condition number of the mathematical problem, not an observed property of one computation. It does not imply that normalization is numerically exact, nor does it account for componentwise perturbations, underflow, overflow, or errors in the input-generation procedure.

## 1.6 Recommendations

The harness should add:

- a reference implementation using arbitrary precision for test vectors;
- adversarial vectors with magnitudes spanning \(2^{-1074}\) through \(2^{1023}\);
- tests for one-large-plus-many-small components;
- explicit tests with \(D=10^4\), \(10^6\), and \(10^7\);
- independent verification using a different summation order;
- a statement that the reported defect is an observed result, not a worst-case guarantee.

---

# Component 2: Stiefel projection by MGS2

Let \(A\in\mathbb{R}^{D\times K}\), \(D\gg K\), and suppose the goal is a matrix \(Q\in\mathrm{St}(D,K)\) satisfying

\[
Q^\mathsf{T}Q=I_K.
\]

## 2.1 What MGS guarantees

Modified Gram–Schmidt is much more stable than classical Gram–Schmidt because each new vector is updated immediately after projection against each previously computed vector.

A standard qualitative bound has the form

\[
\|I-Q^\mathsf{T}Q\|
\lesssim
C\,u\,\kappa_2(A)
\]

for one-pass MGS under suitable assumptions, whereas classical Gram–Schmidt can exhibit behavior proportional to

\[
O(u\,\kappa_2(A)^2).
\]

The exact constants and norms depend on the theorem and implementation.

Reorthogonalization can improve the result substantially. A second MGS pass often gives

\[
\|I-Q^\mathsf{T}Q\|
\lesssim C\,u
\]

when the reorthogonalization criterion is satisfied and the input is not so ill-conditioned that numerical rank has already been destroyed.

But the absolute claim that “two passes are sufficient regardless of the initial condition number” is false.

## 2.2 Why condition-independent machine precision is impossible

Suppose two columns of \(A\) are mathematically distinct but differ by less than the working precision relative to their scale. In binary64, the difference can be unrepresentable. For example, if

\[
a_2=a_1+\delta,
\qquad
\|\delta\|_2\ll u\|a_1\|_2,
\]

then the stored columns may be identical. No orthogonalization algorithm operating only on the stored binary64 data can recover the lost direction.

More generally, if

\[
\sigma_{\min}(A)\lesssim u\,\sigma_{\max}(A),
\]

the numerical rank is ambiguous. A theorem cannot promise a well-conditioned \(K\)-dimensional orthonormal basis from data whose independent directions are absent at working precision.

Thus MGS2 can produce near-machine-precision orthogonality for numerically full-rank data, but it cannot do so “regardless of \(\kappa(A)\).” A rigorous implementation must either:

- detect loss of numerical rank;
- use a rank-revealing factorization;
- specify a threshold such as \(\sigma_{\min}/\sigma_{\max}>\tau\);
- or permit arbitrary replacement vectors when the requested dimension is numerically unattainable.

## 2.3 Role of compensated inner products

For

\[
r_{ij}=q_i^\mathsf{T}a_j,
\]

the dot product itself may be the dominant source of error. Neumaier compensation improves the scalar reduction, particularly when terms have mixed signs or severe cancellation. It does not eliminate:

- rounding in the vector update;
- rounding in normalization;
- errors from storing and rereading \(q_i\);
- errors in repeated projections;
- errors caused by nearly dependent columns.

The reported value

\[
\|Q^\mathsf{T}Q-I\|_\infty=4.441\times 10^{-16}
\]

is plausible for \(K=4\) and well-scaled random inputs, but it is not evidence of a universal MGS2 theorem. The audit should report distributions over adversarial and random matrices, including prescribed condition numbers.

## 2.4 Complexity and bandwidth

For \(D\gg K\):

- MGS requires approximately \(O(DK^2)\) arithmetic;
- MGS2 requires approximately \(O(2DK^2)\);
- storage is \(O(DK)\);
- the dominant traffic is streaming through the \(D\)-length columns.

For fixed \(K=4\), the operation count is effectively linear in \(D\). A rough MGS2 structure consists of:

- \(K\) column norms;
- approximately \(K(K-1)/2\) projections per pass;
- \(K\) vector updates per pass;
- a second pass with comparable cost.

The algorithm is frequently memory-bandwidth-bound in low-level implementations. Pure Python loops are instead dominated by interpreter overhead and object access, so the 559 ms timing is not a hardware bandwidth measurement. It is a Python execution benchmark.

A direct thin SVD costs approximately

\[
O(DK^2+K^3)
\]

for a tall-skinny matrix using a specialized algorithm, but with a much larger constant and more workspace. SVD provides singular values and rank information, making it preferable when conditioning or rank deficiency matters.

The polar factor

\[
Q=A(A^\mathsf{T}A)^{-1/2}
\]

has the same broad \(O(DK^2+K^3)\) structure but requires forming and factoring the \(K\times K\) Gram matrix. It can be attractive when the closest orthonormal matrix in Frobenius norm is specifically required. It is less attractive when \(A^\mathsf{T}A\) is ill-conditioned, because forming the Gram matrix squares the condition number.

A Cayley transform is structurally different. Given a skew-symmetric generator \(\Omega\), one may use

\[
Q=(I-\tfrac12\Omega)^{-1}(I+\tfrac12\Omega),
\]

but this requires solving a system and generally represents an update from an already orthogonal point rather than a projection of arbitrary \(A\). For dense tall-skinny data, it is not a direct replacement for QR-like orthogonalization.

## 2.5 Recommendations

The implementation should:

- distinguish “orthogonalization” from “projection onto the Stiefel manifold”;
- report numerical rank;
- include a reorthogonalization stopping test;
- benchmark MGS2, Householder QR, TSQR, SVD, and polar retraction;
- report arithmetic intensity, bytes transferred, and achieved bandwidth;
- test matrices with controlled \(\kappa(A)\);
- avoid claiming condition-independent \(O(u)\) orthogonality.

For production-grade tall-skinny orthogonalization, Householder QR or TSQR is generally the stronger reference method. MGS2 remains pedagogically valuable and can be effective for small \(K\) when rank is known to be safe.

---

# Component 3: Kulisch superaccumulation

## 3.1 Mathematical foundation

Every finite binary64 number can be written as

\[
x=(-1)^s M_x 2^{e_x},
\]

where \(M_x\) is an integer significand after choosing a common fixed-point representation. Therefore, for two finite inputs,

\[
xy=(-1)^{s_x+s_y}M_xM_y2^{e_x+e_y}.
\]

All exact products can be shifted to a common least-significant binary position and accumulated as signed integers. The result is exact until the fixed-point accumulator itself overflows. Final conversion to binary64 then performs one correctly rounded conversion, rather than rounding every product and every addition separately.

This is the basis of the exact-dot-product theorem associated with Kulisch and later reproducible-reduction work: the accumulator must contain enough bits to represent every possible product alignment and enough additional range to absorb the intended number of accumulated terms.

The cited IEEE material gives a commonly referenced binary64 exact-dot-product accumulator size of 4,288 bits under a specified model, with additional headroom for a prescribed number of accumulations[2]. Other literature describes 4,288-bit or approximately 4,352-bit designs depending on indexing conventions, sign handling, guard bits, and accumulation headroom[5][10].

## 3.2 Bit-range calculation

The minimum positive binary64 subnormal is

\[
2^{-1074}.
\]

Therefore the smallest positive product is

\[
2^{-1074}2^{-1074}=2^{-2148}.
\]

The largest finite binary64 number is slightly less than \(2^{1024}\), so the largest product is strictly less than

\[
2^{2048}.
\]

A fixed-point grid with unit weight \(2^{-2148}\) therefore needs to represent product exponents extending from approximately \(-2148\) through \(+2048\). The raw span is

\[
2048-(-2148)=4196
\]

binary exponent intervals, with further bits required for endpoint inclusion, sign, carry, and accumulation headroom.

This is why a value around 4,288 bits appears in canonical exact-dot-product designs. A 4,352-bit implementation can be entirely reasonable, but “necessary and sufficient” is incomplete unless the suite precisely defines:

- whether the accumulator represents a signed magnitude or two’s-complement integer;
- the position of the binary point;
- whether products may be accumulated indefinitely or only for a bounded \(n\);
- the number of guard/carry bits;
- whether infinities, NaNs, and signed zeros are supported;
- the maximum dot-product length;
- overflow signaling semantics.

The stated mapping

- bit \(0\) at \(2^{-2148}\);
- bit \(2148\) at \(1\);
- bit \(4351\) at \(2^{2203}\)

is arithmetically inconsistent if “bit \(2148\) corresponds to \(1.0\)” is interpreted literally, because bit \(2148\) has weight \(2^0\), while bit \(4351\) has weight \(2^{2203}\). It does cover the product range with substantial positive headroom, but the documentation should explicitly state the binary-point convention and correct any contradictory endpoint wording.

## 3.3 Subnormal products

For

\[
10^{-315}\cdot10^{-315}\approx10^{-630},
\]

the exact binary exponent lies far below the binary64 subnormal range, so binary64 multiplication rounds the result to zero. The exact product is not a binary64 number, but it can be represented in a sufficiently fine fixed-point accumulator if the operands are first decoded exactly into integer significands and exponents.

The statement that “56 bits of mantissa information” are destroyed requires qualification. Each binary64 operand has at most 53 significant bits, and the product of two significands can carry up to 106 exact significand bits before alignment. The exact information retained by the superaccumulator is therefore not simply “56 bits”; it is the exact integer product and its exponent alignment. The active-bit count in a particular test must be reported from the decoded operands, not inferred from decimal literals.

Likewise, “100% information lost” is rhetorically understandable but mathematically imprecise. The rounded binary64 result is zero, whereas the exact real product is nonzero. The relative error is indeed one, but information loss should be described as complete loss of the nonzero product under the binary64 output format.

## 3.4 Cancellation example

For

\[
10^8+10^{-8}-10^8,
\]

a left-to-right binary64 evaluation typically yields zero because \(10^8+10^{-8}\) rounds to \(10^8\), after which subtraction gives zero. The exact result is \(10^{-8}\), so the relative error is \(100\%\), not universally \(49.01\%\).

A reported 49.01% error may arise from a different normalization, ordering, or test construction, but it is not the canonical relative error of this three-term expression. The harness must disclose:

- exact decimal or binary inputs;
- operation order;
- definition of relative error;
- reference value;
- whether the “standard FPU” path uses fused operations;
- whether the superaccumulator rounds only at the end.

For long sums, exact accumulation prevents intermediate cancellation loss, but the final conversion to binary64 can still round the exact result. If the exact result is below the binary64 subnormal range, the final binary64 output may again be zero even though the accumulator retained the information internally.

## 3.5 Impact on optimization

Exact dot products can improve:

- determinism across reduction trees;
- reproducibility across thread counts;
- stability of near-canceling inner products;
- consistency of line searches and stopping criteria;
- reproducibility of gradient norms and orthogonality tests.

They do not automatically improve neural-network convergence. Training is a nonlinear dynamical system involving:

- approximate matrix multiplications;
- nonlinear activations;
- stochastic minibatches;
- normalization layers;
- non-associative reductions;
- optimizer state updates;
- hardware-specific kernels.

An exact dot product may reduce numerical drift in selected reductions, but it cannot compensate for poor scaling, exploding gradients, biased stochastic estimates, or ill-conditioned parameterizations. Its largest value is usually deterministic reproducibility and reliable diagnostics, not universal accuracy improvement.

A realistic evaluation should compare:

- loss trajectories;
- gradient cosine similarity;
- parameter divergence;
- seed-to-seed variance;
- final validation metrics;
- convergence failures;
- cost per training step.

The superaccumulator also has a substantial cost. A 4,352-bit addition involves 136 32-bit limbs, and a naïve Python implementation is many orders of magnitude slower than hardware floating-point reduction. It should therefore be used selectively: reference mode, audit mode, critical reductions, or offline validation.

---

# Component 4: PMTP zero-copy IPC

## 4.1 Entropy and the data-processing inequality

Let \(X\) denote the original vector and \(Y\) its serialized representation. If serialization is deterministic and lossless, then \(X\) is recoverable from \(Y\), so

\[
H(X\mid Y)=0
\]

and

\[
I(X;Y)=H(X).
\]

A binary shared-memory representation can preserve the payload exactly, provided that:

- all bits are copied or mapped without alteration;
- dtype, shape, byte order, and strides are correctly specified;
- the consumer interprets the same memory region;
- lifetime and synchronization are correct.

JSON is not inherently lossy for finite decimal values if sufficient digits and metadata are emitted, but typical JSON serializers may:

- round binary64 values to a decimal string;
- lose NaN payloads and signed zero;
- omit dtype and byte-order metadata;
- convert arrays into textual decimal tokens;
- impose parsing and allocation costs.

Thus JSON can reduce recoverable information in practical implementations, but this is not a consequence of the data-processing inequality. The inequality says that a processing chain cannot increase mutual information:

\[
I(X;Z)\le I(X;Y).
\]

It does not say that every serialization reduces information, nor that a slower representation has lower entropy. A lossless JSON encoding can preserve all payload information while being computationally inefficient.

The strongest claim for PMTP is therefore not “entropy preservation versus JSON,” but:

- exact bit preservation;
- explicit metadata;
- lower CPU overhead;
- lower allocation pressure;
- lower latency;
- predictable ABI behavior.

## 4.2 88-byte descriptor assessment

An 88-byte descriptor can be effective if it contains, at minimum:

- magic/version;
- total descriptor size;
- producer and consumer ABI/version;
- shared-memory identifier;
- byte offset;
- byte length;
- dtype code;
- rank;
- shape;
- stride or contiguity flags;
- byte order;
- alignment;
- checksum or generation counter;
- ownership/lifetime information.

Offsets and lengths must be validated against the mapped segment before creating a view. Integer overflow, negative values, stale handles, and malicious or accidental out-of-range descriptors must be rejected.

“Zero-copy” should be defined precisely. Mapping shared memory creates a virtual-memory mapping but does not necessarily eliminate all physical page movement, cache traffic, or kernel involvement. It means that the payload is not copied into an intermediate serialized byte string or a second user-space array.

## 4.3 CPython buffer lifecycle

The lifecycle problem is real. A shared-memory object cannot be safely closed while exported buffers or live `memoryview` objects still reference its storage. On some platforms, particularly Windows, closing the mapping while views remain exported can raise `BufferError` or lead to invalid-resource behavior.

The correct ownership pattern is:

1. create or open the shared-memory segment;
2. construct the memoryview;
3. construct any typed view over it;
4. use the view;
5. explicitly release derived views;
6. delete references;
7. close the shared-memory object;
8. unlink only when ownership policy permits.

A robust Python pattern is:

```python
shm = shared_memory.SharedMemory(name=name)
view = None
typed = None
try:
    view = memoryview(shm.buf)
    typed = view.cast("B")
    # Consume data.
finally:
    if typed is not None:
        typed.release()
    if view is not None:
        view.release()
    shm.close()
```

In real code, additional objects may retain exports indirectly. Slices, casts, `array`, `ctypes`, and third-party wrappers can all extend the lifetime of the underlying buffer. The C buffer protocol requires every successful buffer acquisition to be paired with a release[3]. A Python-level `memoryview.release()` is the corresponding explicit operation[4].

The producer and consumer need a clear protocol for:

- who creates the segment;
- who closes it;
- who unlinks it;
- how in-flight readers are counted;
- how descriptor reuse is prevented;
- how crashes are recovered;
- how version mismatches are rejected.

A generation counter or lease protocol is preferable to relying solely on object destruction and reference counting.

## 4.4 Benchmark interpretation

The reported reduction from 54.02 ms to 0.94 ms is plausible for a large Python JSON path versus a shared-memory view, but it must be decomposed into:

- serialization;
- allocation;
- parsing;
- mapping/opening;
- descriptor validation;
- synchronization;
- first-touch page faults;
- actual consumer computation.

The benchmark should report median, percentile tails, warm and cold runs, payload size, CPU affinity, process topology, operating system, and whether the JSON path uses compact separators and a high-performance parser. A single latency number is insufficient for an IPC claim.

---

# Component 5: Pedagogical and reproducibility assessment

## 5.1 Strengths

A zero-dependency, pure-Python reference implementation has major educational value:

- every algorithmic step is inspectable;
- installation failures are minimized;
- the reference path is portable;
- students can compare mathematical formulas with executable behavior;
- external optimized libraries are not silently masking algorithmic errors.

Automatic hardware probing is useful for contextualizing timing and detecting unsupported features. A strict memory budget encourages streaming algorithms and exposes hidden allocations.

The suite is particularly strong as a **reference and teaching artifact**, not necessarily as a high-performance implementation.

## 5.2 Necessary reproducibility metadata

The harness should record:

- Python implementation and exact version;
- operating system and architecture;
- CPU model;
- operating-system floating-point mode;
- flush-to-zero and denormals-are-zero status where observable;
- process affinity;
- timer source and resolution;
- input-generation seed;
- byte order;
- descriptor schema version;
- source revision or cryptographic hash;
- test vector hash;
- expected outputs and tolerances.

Timing results must be separated from correctness results. Correctness tests should use deterministic vectors and exact or high-precision references. Performance tests should use repeated trials and report distributions.

## 5.3 Memory accounting

A “less than 80 MB” claim needs a defined metric:

- resident set size;
- Python allocator high-water mark;
- process virtual size;
- peak allocation from `tracemalloc`;
- total shared-memory mapping;
- child processes included or excluded.

Python’s allocator and operating system page behavior mean that these metrics can differ substantially. The harness should report at least RSS and Python-tracked allocations, with methodology.

## 5.4 Documentation quality

The guide should distinguish clearly among:

- mathematical guarantees;
- floating-point error bounds;
- empirical observations;
- platform-dependent behavior;
- implementation limits;
- pedagogical simplifications.

The following claims should be revised:

- “machine precision floor” → “observed defect at approximately one unit roundoff”;
- “condition number \(=1\)” → “the Euclidean norm has relative condition number one under the normwise model”;
- “two passes guarantee \(O(u)\) regardless of conditioning” → “two passes commonly yield \(O(u)\) orthogonality for numerically full-rank inputs”;
- “entropy degradation from JSON” → “possible information loss or metadata loss in practical decimal serialization”;
- “zero-copy” → “no user-space payload copy after shared-memory mapping.”

## 5.5 Recommended validation matrix

A dissertation-quality artifact should include a machine-readable test matrix:

| Component | Normal tests | Adversarial tests | Reference |
|---|---|---|---|
| Norm | random \(D=10^4\) | mixed exponents, subnormals, max finite | high precision |
| MGS2 | random tall-skinny matrices | controlled \(\kappa\), rank deficiency | Householder/SVD |
| Superaccumulator | random products | extreme exponents, cancellation | integer exact arithmetic |
| PMTP | contiguous vectors | malformed descriptors, stale segments | round-trip bit comparison |
| Reproducibility | repeated runs | different process counts/orderings | hashes and exact logs |

For every tolerance, document whether it is:

- a theorem-derived upper bound;
- a heuristic acceptance threshold;
- an observed percentile;
- or a platform-specific regression threshold.

---

# Overall verdict

The suite is technically promising and pedagogically valuable, but several headline statements currently overreach the mathematics.

**Strongly defensible:**

- scaled sum-of-squares is the correct basic strategy for robust norm computation;
- compensated summation materially reduces accumulation error;
- MGS with reorthogonalization is effective for well-scaled, numerically full-rank tall-skinny matrices;
- exact fixed-point accumulation provides deterministic, lossless accumulation before final rounding;
- shared-memory descriptors can eliminate serialization copies and greatly reduce latency;
- explicit buffer release is essential for portable IPC cleanup.

**Require correction or qualification:**

- Neumaier summation is not exact and remains order-dependent;
- LASSQ does not preserve every tiny term against underflow;
- MGS2 cannot guarantee machine precision for arbitrarily ill-conditioned input;
- 4,352 bits must be justified by an explicit bit-layout and accumulation-range derivation;
- the \(10^8+10^{-8}-10^8\) example does not intrinsically imply 49.01% relative error;
- JSON does not automatically violate information-theoretic preservation;
- pure-Python timings should not be interpreted as DRAM-bandwidth results.

With those corrections, adversarial tests, independent references, complete metadata, and explicit lifecycle protocols, the project could serve as an excellent reproducible numerical-computing teaching suite and a credible dissertation artifact. At present, it should be presented as a carefully engineered reference implementation with strong empirical evidence—not yet as a universally verified implementation of the strongest mathematical claims.

## Referencias y Citaciones SOTA
1. https://davis.lbl.gov/Manuals/PYTHON/c-api/buffer.html
2. https://grouper.ieee.org/groups/1788/email/pdf7OYfgSd9H4.pdf
3. https://docs.python.org/3/c-api/buffer.html
4. https://docs.python.org/3/c-api/memoryview.html
5. https://hal-lirmm.ccsd.cnrs.fr/lirmm-01206348v1/document
6. https://wiki.python.org/jython/BufferProtocol.html
7. https://docs.python.org/ko/3.15/c-api/buffer.html
8. https://hal.science/hal-01488916v2/document
9. https://runebook.dev/en/docs/python/c-api/buffer
10. https://hal.science/hal-00949355v1/preview/superaccumulator.pdf
