**Verdict: conditionally acceptable, not yet a verification-grade remediation.** T-01 and T-04 have straightforward defects and sound basic fixes; T-02/T-03/T-05 require stronger oracle contracts and statistical acceptance criteria; T-06 contains a numerical error in the stated cluster calculation and an under-specified cryptographic proof obligation.

## T-01 — Runner Boolean trap

The proposed dispatch correctly prevents `False` from being interpreted as success:

```python
if ret is False:
    code = 1
elif ret is True or ret == 0 or ret is None:
    code = 0
else:
    code = int(ret)
```

Python booleans are subclasses of integers, with `False == 0` and `True == 1`[5]. However, the implementation is not fully fail-closed:

- `ret == 0` may invoke user-defined equality and return a non-Boolean object or raise an exception.
- `int(ret)` may accept unintended values, including floats, strings, or custom objects.
- `True` is explicitly treated as success, which is only correct if the suite’s conformance contract defines Boolean `True` as pass.
- `None` being success must likewise be an explicit contract, not an implicit convenience.

A stricter contract is:

```python
def normalize_result(ret):
    if type(ret) is bool:
        return 0 if ret else 1
    if ret is None:
        return 0
    if type(ret) is int:
        return ret
    raise TypeError(f"invalid theorem result type: {type(ret).__name__}")
```

Then enforce:

```python
try:
    code = normalize_result(test())
except BaseException:
    record_exception_with_traceback()
    code = 70              # internal execution failure, never PASS
```

Every nonzero code must be preserved in the result record and propagated to the process exit status, preferably with saturation only at the outermost OS boundary. Unexpected exceptions, segmentation faults, timeouts, signal termination, malformed result types, oracle mismatches, and missing artifacts must be distinct non-pass states. A theorem suite must never convert an infrastructure failure into theorem success.

## T-02/T-03/T-05 — Silicon-oracle architecture

The centralized dispatch is directionally correct because it replaces a constant-valued mock with independently executed native implementations. But **calling native code alone does not establish falsifiability**. Each oracle needs:

- Independent input generation, including adversarial and boundary cases.
- A separately implemented mathematical residual or invariant.
- Preconditions and postconditions recorded in the evidence log.
- Exact library version, compiler, flags, architecture, seed, and floating-point mode.
- Cross-language agreement checks between C++, Rust, and the Python harness.
- Failure injection proving that the test detects corrupted native output.
- No fallback path that returns a constant or “unknown means pass.”

Representative acceptance conditions should be explicit:

\[
\|X^\mathsf{T}X-I_K\|_F \le 10^{-12}
\]

for Stiefel outputs, with dimension-scaled tolerances justified by conditioning and machine precision. For retractions, additionally verify that the output lies on the manifold and that the local retraction contract holds, e.g.

\[
R_X(0)=X,\qquad
\|R_X(\eta)-X-\eta\|_F=O(\|\eta\|_F^2).
\]

For projection and compensated summation, denormal tests must verify both numerical result and floating-point environment: FTZ/DAZ state, rounding mode, underflow flags, and reproducibility. A single input such as \(10^{-305}\) is insufficient.

For Clifford rotors, “\(\|R\|^2=1\)” is not generally a complete unitarity test. Verify the appropriate reverse/conjugation relation:

\[
\widetilde R R = 1
\]

or the representation-level condition

\[
\rho(R)^\ast \rho(R)=I,
\]

with the signature \((p,q)\), basis convention, and normalization specified.

For Lanczos/Jackson, test recurrence residuals, tridiagonal projection consistency, spectral bounds, and monotonic damping of the intended kernel. For matrix martingales, the Freedman inequality must be tested as a statistical property over independent repetitions, not as a deterministic equality:

\[
\Pr\!\left(\|S_n\|\ge t,\;V_n\le v\right)
\le
2D\exp\!\left[-\frac{t^2}{2(v+Rt/3)}\right].
\]

The empirical violation rate must include a confidence interval and remain compatible with the bound; finite simulations cannot prove the theorem.

For Poincaré-to-Lorentz mapping, verify the correct hyperboloid constraint:

\[
\langle x,x\rangle_L
=
-x_0^2+\sum_{i=1}^{D-1}x_i^2
=
-1,\qquad x_0>0,
\]

plus distance preservation and numerical behavior near the ball boundary. This is a valid direct correction for the cited theorem only if the mapping, metric convention, and domain are explicitly fixed.

Thus the architecture is **empirically falsifiable only after fallback elimination, independent residual computation, mutation testing, and artifact-level provenance**. Otherwise it remains a more elaborate harness around potentially unverified native code.

## T-04 — Routing collision

Replacing substring containment with token or exact-keyword routing is required. `r"\brust\b"` avoids matching words such as “incrustación,” but boundary matching alone can still mishandle punctuation, Unicode normalization, or compound identifiers.

Prefer normalized tokenization with an allowlisted vocabulary:

```python
tokens = set(re.findall(r"[a-z0-9_]+", topic.casefold()))
if "rust" in tokens:
    route = RUST_FFI
```

Routing must be mutually exclusive or explicitly prioritized. Every dispatch should log the matched token, selected family, and rejected alternatives. Add negative tests for Spanish morphology, substrings, punctuation, mixed case, and Unicode text.

## T-06 — Theorem 1664

The design-effect calculation is correct:

\[
\mathrm{DEFF}
=
1+(m-1)\rho
=
1+(60-1)(0.3)
=
18.7.
\]

This is the standard equal-cluster-size inflation factor[1][2]. The individual-level requirement is stated as

\[
n_{\text{individual}}
=
\left\lceil
\frac{\sigma_d^2}{\Delta_{\mathrm{NI}}^2}
(z_{\alpha/2}+z_\beta)^2
\right\rceil
=
238.
\]

The cluster requirement is **not** \(75\) clusters per arm under the stated formula:

\[
\frac{238\times18.7}{60}
=
74.1533\ldots,
\]

so

\[
n_{\text{clusters}}=\lceil74.1533\ldots\rceil=75
\]

clusters per arm. The arithmetic is valid, but the interpretation must be precise: \(75\) clusters per arm gives \(75\times60=4500\) individuals per arm, while the inflated individual requirement is

\[
238\times18.7=4450.6,
\]

hence \(4500\) is the smallest whole-cluster allocation at \(m=60\).

Verification must recompute all quantities from the declared \(\sigma_d\), noninferiority margin, \(\alpha\), power, and endpoint covariance—not merely assert the final constants. For co-endpoints, the Intersection–Union Principle requires rejecting the global null only when **every required endpoint** satisfies its prespecified noninferiority criterion. Multiplicity adjustment must not be introduced unless the protocol requires a different global decision rule.

Also test sensitivity to unequal cluster sizes, attrition, ICC uncertainty, and analysis method; the simple \(1+(m-1)\rho\) formula assumes equal cluster sizes, while variable sizes require an adjusted design effect[2][4].

## T-06 — Theorem 1665

A dictionary lookup verifies neither authenticated hashing nor crash consistency. The operational test must:

1. Construct a genuine 21-level BLAKE3 chunk tree over data exceeding one chunk.
2. Recompute the root independently, including chunk counters, parent-node flags, and output-length handling.
3. Verify that any bit, chunk order, counter, or tree-node mutation changes the root.
4. Maintain a monotonic journal sequence \(G_n\) and reject:
   \[
   G_n\le G_{\mathrm{last}}.
   \]
5. Persist data, metadata, and commit marker using a defined ordering and `fsync`/directory durability protocol.
6. Kill the process at every write/flush boundary, restart, replay, and verify no committed record is lost or applied twice.
7. Test torn writes, duplicated records, truncation, reordered records, stale manifests, and counter rollback.

The claimed replay bound

\[
\Pr[\mathrm{replay}]
\le
2^{-128}+\frac{q^2}{2^{128}}
\]

is a birthday-style bound and is meaningful only after defining \(q\), the number of authenticated comparisons or forgery opportunities, the adversary model, domain separation, nonce/counter uniqueness, and the exact BLAKE3 construction. It cannot be established by ordinary functional tests. The implementation should use explicit domain separation for chunk, parent, journal-record, and root contexts, and the journal counter must be authenticated as part of the record.

## Final disposition

- **T-01:** Accept after strict type validation and exception-to-failure propagation.
- **T-04:** Accept after tokenized routing plus negative collision tests.
- **T-02/T-03/T-05:** Reject as complete until independent residuals, mutation tests, provenance, and statistical acceptance criteria are implemented.
- **T-06/1664:** Formula is correct; \(75\) clusters per arm follows by ceiling, but the theorem must verify all inputs and the co-endpoint IUR rule.
- **T-06/1665:** Current dictionary test is invalid; replace it with tree reconstruction, authenticated monotonic journaling, crash-replay testing, and a formally scoped security claim.

The remediation becomes verification-grade only when **no execution path can produce PASS without a real computation, an independently checked invariant, and durable evidence of the exact inputs and implementation used**.