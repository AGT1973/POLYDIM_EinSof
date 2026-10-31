# ROUND 2 — FINAL ADVERSARIAL AUDIT

**Scope:** The supplied dossier and source excerpts only. No repository, PostgreSQL instance, build artifacts, execution logs, or Lean files were accessible. The Rust export and several C++ functions are truncated.

**Evidence rule:** A recorded defect is not a repaired defect. A redesign specification is not an implemented protocol. Reported exit code 0 is not independently reproduced execution.

## I. EXECUTIVE ADVERSARIAL VERDICT

| Required assessment | Verdict |
|---|---|
| **Overall System Readiness Score** | **0% certification readiness for the stated hostile-consumer production release.** This is a release-gate result, not an estimate of implementation completeness. |
| **Theoretical Coherence Score** | **Not quantitatively assessable.** The actual revised Theorem 1.2 and its proof were not supplied. |
| **Silicon Hardening & ABI Safety Score** | **Not quantitatively assessable.** Confirmed implementation/specification contradictions remain. |
| **Lean 4 Formal Proof Coverage** | **0 theorem bodies inspected; total proven theorems and unproven axioms unknown.** |
| **D16 closure** | **Partial rectification; closure denied.** The contraction claim is withdrawn correctly, but the replacement Morse–Bott convergence assertion needs additional hypotheses. |
| **V018 roadmap** | **Accepted as a structural redesign proposal, not accepted as a complete security/concurrency specification.** |
| **Advance to V018 implementation** | **YES**, after the specification corrections below. |
| **Advance to production tri-partite release** | **NO.** Existing SEV-1 debt remains open. |

### Top three release-blocking vulnerabilities

1. **D01 remains open:** The dossier acknowledges ordinary publisher writes racing atomic reader accesses. Neither a fence nor a post-copy generation check repairs that race.
2. **D04/D13 remain incompletely specified:** A 32-bit acquisition generation plus an 8-bit CRC/nonce does not deliver the advertised 64-bit monotonic, authenticated, replay-resistant lease protocol.
3. **D05/D06 remain incompletely specified:** Separate named objects do not themselves enforce hostile-process isolation; separately checked lifecycle state and in-flight count do not themselves establish atomic admission.

**Additional confirmed SEV-1:** `pmtp_tri_create` still performs unchecked size multiplication despite introducing an overflow-safe alignment helper.

---

## II. DEFECT REGISTER — SEV-1 TO SEV-3

Exact repository line numbers cannot be assigned from these excerpts. Locations below identify supplied functions or document sections.

### R2-01 — D16: Morse–Bott does not establish the stated convergence conclusion

```text
DEFECT ID: THEORETICAL DISCREPANCY
LOCATION: Section A summary, revised Theorem 1.2 — actual theorem/proof absent
COMPONENT: Theory
PRISM: Geometry
```

**Analysis**

The following correction is valid:

\[
\xi(X)=0 \implies F(X)=X,
\]

so a Lipschitz bound \(L=0<1\) on the vector field does **not** imply that its update map has a unique fixed point.

However, the replacement statement—

> convergence to isolated semantic subspaces requires a Morse–Bott potential

—is not established as either a necessary or sufficient condition.

- Morse–Bott critical sets may have positive dimension.
- A Morse–Bott potential can contain maxima and saddles.
- A vector field must actually be connected to that potential, for example \(\xi=-\operatorname{grad}V\).
- A discrete retraction update additionally needs a valid step-size/descent condition.
- Smoothness, metric, critical-set structure, initialization, and the intended notion of convergence must be specified.
- “Semantic” is not a mathematical property without an explicit definition.

**Counterexamples**

**Not necessary:** In a local coordinate \(\theta\) around a point of \(\mathrm{Gr}(1,2)\), let

\[
V(\theta)=\theta^4.
\]

The gradient flow

\[
\dot\theta=-4\theta^3
\]

converges locally to the isolated minimum \(\theta=0\), although its Hessian there vanishes, so this isolated critical point is not Morse–Bott.

**Not sufficient for convergence to a desired minimum:** A Morse potential is also Morse–Bott. Start its gradient flow exactly at a maximum: the trajectory remains at that maximum.

**Required replacement**

Use a qualified statement, not a universal implication:

> A Morse–Bott potential is one possible sufficient structural hypothesis for suitable gradient-flow convergence results. Attraction to a designated isolated minimum requires further assumptions concerning the dynamics, basin of attraction, and—under discrete retraction updates—step size and numerical error. Morse–Bott structure is not necessary for isolated-minimum convergence.

Define vector-field Lipschitz continuity through parallel transport within a specified geodesic neighborhood, or use a covariant-derivative bound. A bound \(L<1\) alone is not a complete step-size stability theorem.

**D16 status: PARTIALLY RESOLVED, NOT CLOSED.**

---

### R2-02 — D01: the two redesign alternatives require different correctness proofs

```text
DEFECT ID: SEV-1 — OPEN IMPLEMENTATION DEBT / INCOMPLETE SPECIFICATION
LOCATION: Section B, D01; pmtp_kernel_cpp.cpp publisher functions
COMPONENT: C++ / Protocol
PRISM: Concurrency
```

**Analysis**

The supplied publisher still executes:

```cpp
std::memmove(dst, data, copy_bytes);
```

The dossier states that an unleased reader uses `atomic_ref<uint64_t>` on overlapping payload storage. That mixture remains invalid when accesses overlap concurrently.

The raw publisher’s added `seq_cst` fence does not change ordinary payload writes into atomic accesses or prevent conflicting accesses.

**Required architectural correction**

**Protocol A:** Writer reservation and reader pinning must arbitrate through the **same atomic slot state**:

```text
Writer:
  CAS (READABLE, readers=0) -> WRITING
  write payload and slot-local metadata
  release-publish slot
  release-publish descriptor

Reader:
  acquire-load descriptor
  CAS-pin its referenced READABLE slot
  revalidate descriptor
  access payload only after successful validation
  release exactly its own pin
```

A preliminary `active_readers == 0` check is not the reservation.

**Protocol B:** Symmetric atomic words can eliminate word-level data races, but they do **not** by themselves provide a coherent multiword snapshot. Specify:

- Valid typed storage and object lifetime.
- Word and tail representation.
- Writer serialization.
- Snapshot/version validation.
- Wrap policy.
- Atomic-only access by every participant.

Ordinary reads through borrowed payload pointers are incompatible with concurrent atomic-word rewriting.

**Drop-in patch:** None can be certified from this excerpt. This is a versioned protocol replacement.

---

### R2-03 — D04: advertised 64-bit generation becomes 32 bits; CRC is not authentication

```text
DEFECT ID: SEV-1 — REPLAY / OWNERSHIP SPECIFICATION GAP
LOCATION: Section B, D04, pmtp_lease_cookie_t
COMPONENT: C++ / Control protocol
PRISM: Concurrency / Security
```

**Analysis**

The issue matrix requires a **64-bit monotonic generation**. The proposed structure contains:

```cpp
uint32_t acquisition_generation;
uint8_t  crc8_nonce;
```

These are not equivalent.

At \(10^7\) acquisitions per second, a 32-bit counter exhausts its range in approximately

\[
\frac{2^{32}}{10^7}=429.50\ \text{seconds}.
\]

An 8-bit CRC is a checksum, not an anti-forgery primitive. An 8-bit random nonce also provides only 256 possibilities.

The proposed check:

```cpp
ctx->active_cookie != 0
```

is not a non-reentrant concurrent admission mechanism unless synchronized atomically or under a mutex.

Also, transitioning directly to `PINNED` before publishing its slot and generation risks exposing an incompletely initialized record.

**Required replacement**

Use a server-owned record and an opaque handle:

```text
FREE -> ACQUIRING -> PINNED -> RELEASING -> FREE
```

- Synchronize handle admission.
- Reserve the slot before exposing the pointer.
- Initialize all identity fields before release-publishing `PINNED`.
- Validate the exact outstanding acquisition.
- Atomically consume that acquisition on release.
- Fail closed before generation exhaustion.
- Bind the handle to a session/instance identity.

A 64-bit opaque handle can reference a trusted record; it need not pack every identity field. If unpredictability/authentication is required, specify an appropriately sized capability independently.

---

### R2-04 — D05: separate objects are not automatically separately authorized

```text
DEFECT ID: SEV-1 UNDER THE HOSTILE-CONSUMER THREAT MODEL
LOCATION: Section B, D05; pmtp_tri_posix_create; pmtp_tri_win_create
COMPONENT: POSIX / Win32 / Protocol
PRISM: SHM Security
```

**Analysis**

The claim—

> B lacks A’s descriptor, therefore corruption is physically impossible

—omits authorization.

On POSIX, predictable named objects with mode `0600` do not separate consumers running under the same UID. A consumer can potentially reopen another consumer’s object by name.

On Windows, individual objects require individual security descriptors tied to the actual process security identities. Separate object names alone supply no isolation.

The implementation still contains one `lease_shm` and indexed entries in a monolithic lease mapping. Per-reader isolation is not implemented in the supplied source.

**Required replacement**

- Broker-created objects.
- Authenticated descriptor/handle distribution.
- No hostile-consumer access to another reader’s writable lease state.
- Distinct security identities or a sandbox policy that actually blocks reopening and handle theft.
- Explicit handling of same-UID/same-token consumers.
- Trusted validation of consumer-supplied lease transitions.

**Important boundary:** Even an isolated hostile consumer can corrupt its own writable record. The publisher must not interpret arbitrary client-written state as trusted evidence of safe reclamation.

---

### R2-05 — D06: separate state check and increment reproduce the admission race

```text
DEFECT ID: SEV-1 — LIFECYCLE SPECIFICATION GAP
LOCATION: Section B, D06
COMPONENT: C++ lifecycle protocol
PRISM: Concurrency
```

**Stress interleaving**

```text
Operation: observes ACTIVE
Operation: descheduled before incrementing in_flight_ops
Close:     changes ACTIVE -> DRAINING
Close:     observes in_flight_ops == 0
Close:     unmaps or destroys context
Operation: resumes and increments/accesses destroyed storage
```

RAII ensures eventual decrement only after successful admission. It does not make admission atomic.

**Required replacement**

Couple lifecycle and operation count in one CAS-managed gate, or use a mutex-protected equivalent.

Additionally:

- `release` must remain permitted during `DRAINING`.
- Outstanding borrowed pointers require lease accounting beyond API-call duration.
- Concurrent closers require serialization.
- Timeout must preserve mappings and define a retryable state.
- `timeout=0` should perform a nonblocking drain check, not unconditional destruction.
- Context lifetime needs an external ownership contract: an internal gate cannot safely dereference an already freed context.

**Drop-in patch:** None without the complete context and ownership API.

---

### R2-06 — D12: proposed “identical 32-bit masks” collide with DESTROYING

```text
DEFECT ID: SEV-2 — ABI CONTRADICTION
LOCATION: Section B, D12 versus Sections C/D
COMPONENT: C++ / Rust / ABI
PRISM: Silicon ABI
```

**Confirmed contradictions**

The proposed mask is:

```cpp
PMTP_SLOT1_READER_MASK = 0xFFFFFFFF00000000ULL;
```

But bit 63 is already:

```cpp
PMTP_DESTROYING_BIT = 1ULL << 63;
```

Therefore:

```cpp
PMTP_SLOT1_READER_MASK & PMTP_DESTROYING_BIT
```

is nonzero.

The delivered header correctly uses **32 bits for slot 0 and 31 bits for slot 1**. It cannot simultaneously preserve that destroying bit and provide two full 32-bit counters in the same 64-bit word.

Rust still initializes:

```rust
generation: AtomicU32::new(1),
```

and still applies `0x7FFFFFFF` to both slots.

**Minimal local correction**

```rust
generation: AtomicU32::new(0),
```

In both Rust acquisition and release:

```rust
let mask = if slot == 0 { 0xFFFF_FFFFu64 } else { 0x7FFF_FFFFu64 };
let count = (prev >> bit_shift) & mask;
```

Use `mask` as the saturation limit during acquisition.

These patches fix the shown EMPTY/mask discrepancies only. They do not certify the lease protocol.

**Architectural decision required:** Preserve the existing 32/31 partition, or version the ABI and move lifecycle state elsewhere.

---

### R2-07 — D13: valid MACs can still be replayed

```text
DEFECT ID: SEV-2 — AUTHENTICATION WITHOUT SINGLE-USE ENFORCEMENT
LOCATION: Section B, D13
COMPONENT: Control plane
PRISM: SHM Security
```

**Analysis**

A keyed BLAKE2s MAC authenticates its encoded message. It does not make release single-use.

```text
Acquire token T
Release with T: valid MAC, decrement
Replay T:      valid MAC again
```

Constant-time comparison does not prevent this replay.

**Required replacement**

- Trusted outstanding-lease table.
- Atomic transition `OUTSTANDING -> RELEASED`.
- Exactly one successful release per acquisition.
- Token binding to session/instance, acquisition ID, slot and reader identity.
- Canonical field encoding and domain separation.
- Session key inaccessible to hostile consumers.
- Removal or effective production disabling of all bypass release APIs.

Authentication cannot protect counters that the attacker can directly overwrite through RW mappings.

---

### R2-08 — unchecked multiplication survives the overflow “fix”

```text
DEFECT ID: SEV-1 — ALLOCATION SIZE OVERFLOW
LOCATION: pmtp_tri_segment.cpp, pmtp_tri_create
COMPONENT: C++
PRISM: Silicon / Domain Engineering
```

**Confirmed vulnerable calculations**

```cpp
const size_t slot_bytes_raw =
    static_cast<size_t>(num_elements) * itemsize;

data_descriptor_size + num_slots * slot_bytes
```

The alignment helper checks only its own addition. It cannot recover a multiplication that already wrapped.

**Concrete arithmetic trigger on a 64-bit target**

```cpp
num_elements = UINT64_C(1) << 61;
dtype_id = PMTP_DTYPE_FP64;  // itemsize = 8
```

Then `slot_bytes_raw` wraps to zero. Creation can allocate a small segment while retaining an enormous advertised element count.

**Required replacement pattern**

```cpp
if (num_elements > SIZE_MAX / itemsize) return nullptr;
const size_t raw = static_cast<size_t>(num_elements) * itemsize;

uint64_t aligned64;
if (!pmtp_tri_align_up_checked(raw, 64, aligned64) ||
    aligned64 > SIZE_MAX)
    return nullptr;
const size_t slot_bytes = static_cast<size_t>(aligned64);

if (slot_bytes > (SIZE_MAX - data_descriptor_size) / num_slots)
    return nullptr;
const size_t unaligned_data =
    data_descriptor_size + num_slots * slot_bytes;
```

Also validate the final aligned size and its representability in `off_t` before `ftruncate`.

The helper is locally correct; the calling allocation pipeline remains incorrect.

---

### R2-09 — sealing fallback is permissive, not fail-closed

```text
DEFECT ID: SEV-2; POTENTIALLY SEV-1 UNDER HOSTILE RESIZE
LOCATION: pmtp_tri_posix_create / pmtp_tri_posix_open
COMPONENT: POSIX
PRISM: SHM Security
```

**Analysis**

The supplied implementation:

- Continues after failed sealing on `shm_open`.
- Makes `F_SEAL_FUTURE_WRITE` optional.
- Accepts absent or insufficient seals on open.
- Contains empty “leave trace” branches that perform no logging or rejection.
- Accepts larger-than-requested objects.
- Reopens `/proc/<pid>/fd/<fd>` without an inspected identity-binding protocol.

The preliminary `ftruncate(fd, 1)` is not an anti-aliasing proof.

**Required correction**

If the hostile-consumer mode requires sealed objects, reject unavailable or insufficient sealing. Pass validated descriptors through authenticated `SCM_RIGHTS` rather than treating a PID/fd pathname as object identity.

Existing writable mappings are intentionally compatible with `F_SEAL_FUTURE_WRITE`; that seal is not a statement that all writers have disappeared.

---

### R2-10 — Rust workspace dimensions are not bound to the operation

```text
DEFECT ID: SEV-2 — PANIC / CONTRACT GAP
LOCATION: kernel_rust.rs, RetractWorkspace and retract_with_workspace
COMPONENT: Rust
PRISM: Domain Engineering
```

**Analysis**

A workspace constructed for one shape can be supplied to an operation for another shape. Its fields are public, and the operation does not verify every workspace slice length before use.

**Minimal trigger**

```rust
let mut storage = [0.0; 5];
let mut ws = RetractWorkspace::from_slice(&mut storage, 1, 1).unwrap();
let mut w = [0.0; 4];

let _ = newton_schulz_ord5_retract_with_workspace(
    &mut w, 2, 2, 1, 1e-6, &mut ws
);
```

This reaches a length-mismatched `copy_from_slice` and panics rather than returning a workspace error.

**Required correction**

Store dimensions privately and validate all required slice lengths at entry. Whether the exported C ABI catches this panic cannot be determined: its implementation is truncated.

---

## III. MATHEMATICAL FIDELITY MATRIX

| Formal claim | Lean symbol | Physical implementation | Parity status | Evidence / bound |
|---|---|---|---|---|
| Vector-field \(L<1\) implies unique update fixed point | Not supplied | None inspected | **Invalid claim withdrawn** | Zero-field identity counterexample is decisive. |
| Revised geodesic perturbation stability | Not supplied | Not supplied | **UNVERIFIED** | Requires actual inequality, transport convention and step-size assumptions. |
| Morse–Bott guarantees/requires isolated semantic convergence | Not supplied | None inspected | **DRIFT** | Neither universal necessity nor universal sufficiency holds as summarized. |
| Exact polar retraction | Not supplied | Rust polynomial iteration | **DRIFT** | Finite iterations are an approximation, not exact inverse square root. |
| Ord5 local convergence | Not supplied | Rust/CUDA polynomial matches displayed coefficients | **PARTIAL MATCH** | Basin, rank and floating-point conditions remain distinct obligations. |
| Cross-language EMPTY semantics | Not supplied | C++ 0, Rust 1 | **DRIFT** | Directly visible constructor mismatch. |
| Full 32/32 reader partition plus destroying bit | Not supplied | 64-bit packed field | **IMPOSSIBLE AS SPECIFIED** | Requires 65 bits of independent state. |
| Authenticated release ownership | Not supplied | Raw slot-based release remains exported | **UNIMPLEMENTED** | Header warning expressly has no enforcement effect. |
| Neumaier correctness at subnormal scales | Not supplied | Scaled norm and compensated sum shown | **UNVERIFIED GUARANTEE** | Product underflow, rounding environment and guard invocation still matter. |
| Dart/Rust/C wire parity | Not supplied | C/Rust declarations shown | **PARTIAL MATCH** | Dart absent; no build/runtime layout evidence supplied. |

### Additional numerical boundaries

- The Rust Gram calculation still rounds each product before Neumaier addition. Compensated summation does not reconstruct product information lost to underflow.
- Clearing DAZ/FTZ does not prevent mathematically tiny products from rounding to zero.
- The CUDA acceptance threshold is actually `1e-14`; its comment says `1e-9`.
- The CUDA claim that `X == Y` necessarily makes the final copy overlap is incorrect here: that copy is from private buffer `a` to `Y`, not from `X` to `Y`. Concurrent external access remains a separate hazard.
- `std::launder` does not create an object or initialize its lifetime. Its appearance cannot independently close an SHM object-lifetime defect.

**Epoch arithmetic correction:**

\[
T_{48}(10^7/\mathrm{s})\approx 0.892\text{ years},
\qquad
T_{48}(10^5/\mathrm{s})\approx 89.2\text{ years}.
\]

Neither supports “over 800 years.” Lease bounds can support a conditional modular-order argument; they do not change the wrap interval.

---

## IV. CONCURRENCY & SHM DRF AUDIT TABLE

| Shared state / descriptor | Access pattern | Memory order | Risk | ABA / replay mitigation | Verdict |
|---|---|---|---|---|---|
| Compact payload, D01 | Ordinary publisher copy versus reported atomic reader access | Fence added to raw publisher | Conflicting accesses remain | Generation recheck cannot undo UB | **OPEN SEV-1** |
| Compact `active_slot` / `generation` | Separate atomic publication | Release/acquire | Split descriptor; Rust ignores writer flag | C++ refuses generation wrap | **Cross-language mismatch** |
| Packed reader counters | CAS increments/decrements | Acquire/release variants | Rust slot-0 mask wrong | No acquisition identity in raw release | **OPEN** |
| Tri-segment lease table | Publisher scans client-writable entries | Atomic field loads | Monolithic hostile-writable state; no shown slot reservation CAS | Existing cookies acknowledged replayable | **OPEN SEV-1** |
| Tri payload | Atomic word/tail stores | Relaxed | Ordinary borrowed reads require proven exclusion | No inspected complete pin/reclaim proof | **NOT CERTIFIED** |
| Proposed lifecycle/count | Separate state and count in prose | Not fully specified | Admission/destruction race | None relevant | **SPECIFICATION INCOMPLETE** |
| Proposed capability token | MAC validation | Not specified | Authenticated replay | Single-use transition absent | **SPECIFICATION INCOMPLETE** |
| POSIX object seals | Strict memfd branch, permissive fallback/open | OS operations | Resize/write restrictions not consistently enforced | Descriptor identity incomplete | **NOT HOSTILE-SAFE** |
| Per-consumer objects | Proposed, not implemented | OS authorization | Names/permissions insufficient alone | Per-session identity unspecified | **UNIMPLEMENTED** |

---

## V. FINAL RED TEAM CERTIFICATION DECREE

# **REJECTED (REQUIRES HARDENING)**

### Closure decisions

- **D16:** Reject complete closure. Accept withdrawal of the Banach/unique-fixed-point claim. Require the actual revised theorem and removal or qualification of the Morse–Bott necessity/sufficiency assertion.
- **V018 debt register:** Accept its classification as structural architectural debt. Reject the assertion that its current specifications fully resolve every root vulnerability.
- **V018 implementation:** Authorized as a development milestone after specification correction.
- **Tri-partite production release:** Blocked.

### Required release gates

1. Correct the cookie width, replay model, counter partition and admission protocol.
2. Implement common atomic slot arbitration—or a fully specified symmetric atomic snapshot protocol.
3. Establish enforceable hostile-consumer permissions and trusted lease ownership.
4. Fix all allocation-size arithmetic.
5. Make required sealing and descriptor identity checks fail closed.
6. Remove or enforceably disable unauthorized raw release paths.
7. Supply complete source, exact compiler versions, flags, source hashes, artifact hashes and execution logs. “Rust 2021” identifies an edition, not a compiler version.
8. Test stale-token replay, concurrent acquisition, reader suspension, close/admission interleavings, hostile cross-reader writes, size overflow, generation exhaustion, NaNs, subnormals and failure rollback.
9. Model-check slot and lifecycle protocols; run same-process race instrumentation and separate IPC fault tests.
10. Supply Lean theorem bodies and axiom dependencies, explicitly separating real-number proofs from floating-point and platform contracts.

The reported **5/5, `max_diff=0`, exit code 0** tuple does not exercise these release blockers. The Windows cross-build limitation is a tooling constraint, not evidence that the Windows artifact passed equivalent tests. No “aerospace/financial-grade certainty” follows from the current dossier.