# PERPLEXITY SONAR-PRO ADVERSARIAL AUDIT — SUBFASE 4.2

**Date:** 2026-10-10T10:03:44.552515

## AXIS 1: CUDA IPC MULTI-STREAM CONTENTION & GRACEFUL TEARDOWN

ERROR: HTTP 429

---

## AXIS 2: CAYLEY QR STIEFEL RETRACTION NUMERICAL STABILITY

The data do **not** establish the claimed tolerance, the claimed asymptotic law, or GPU equivalence to LAPACK. Several measurements are also dimensionally or mathematically inconsistent.

## 1. Scaling of \( \|Q^TQ-I\|_2 \)

The three observations

\[
8.907\times10^{-16},\quad 1.111\times10^{-15},\quad 3.775\times10^{-15}
\]

are qualitatively consistent with increasing accumulation error, but they do **not** identify an \(O(\sqrt D\,u)\) law. Three points, apparently from one random realization and with no confidence intervals, cannot distinguish \(D^{1/2}\), \(D\), logarithmic growth, conditioning effects, or implementation-specific effects.

More importantly, the usual Householder QR result is not a theorem saying

\[
\|Q^TQ-I\|_2 \le C\sqrt D\,u.
\]

Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed. (2002), §19, following Wilkinson’s backward-stability analysis, gives a backward error statement for the computed factorization: the computed factors correspond to an exact QR factorization of \(A+\Delta A\), with a perturbation bounded by a dimension-dependent multiple of unit roundoff \(u\). The orthogonality of the explicitly formed computed \(Q\) is a separate forward-error property. The constant depends on matrix dimensions, reflector formation, BLAS reductions, scaling, and the implementation. The theorem commonly cited as Higham’s Theorem 19.4 should therefore not be paraphrased as a universal \(\sqrt D\,u\) orthogonality bound.

There is a more immediate problem with the extrapolation. Taking the \(D=10^5\) result and multiplying by \(\sqrt{10}\) gives

\[
3.775\times10^{-15}\sqrt{10}
\approx 1.19\times10^{-14},
\]

which exceeds \(10^{-15}\) by roughly a factor of twelve. Thus, **under your own extrapolation**, the \(D=10^6\) result fails the tolerance. It does not prove that the actual result will fail, but it gives no basis for claiming compliance.

The \(D=10^5\) measurement itself already fails the stated tolerance:

\[
3.775\times10^{-15} > 10^{-15}.
\]

The correct validation criterion is an actual computation of

\[
\|Q^TQ-I_K\|_2,
\]

at the target \(D\), with specified \(K\), matrix distribution, scaling, norm implementation, and number of independent trials. A scalar vector norm such as the reported \(999.8395\) is not a Stiefel test. For a single column \(q\), the relevant condition is \(|q^Tq-1|\); for \(K>1\), it is the spectral norm of the full Gramian residual.

## 2. Newton–Schulz polar refinement

The stated iteration

\[
Q_{+}=Q\left(\frac32I-\frac12Q^TQ\right)
\]

is the Newton–Schulz iteration for the polar factor, applied on the right. If

\[
E=Q^TQ-I,
\]

then, in exact arithmetic,

\[
Q_{+}^TQ_{+}-I
=
-\frac34E^2+\frac14E^3.
\]

Consequently,

\[
\|E_{+}\|_2
\le
\frac34\|E\|_2^2+\frac14\|E\|_2^3.
\]

This is quadratic convergence only in the regime where the iteration is well-scaled and roundoff is negligible. It is not an unconditional guarantee. In floating-point arithmetic, each multiplication and reduction introduces a fresh error, so the attainable residual is generally of order a dimension- and implementation-dependent multiple of \(u\), not zero.

The observed reduction

\[
3.775\times10^{-15}\rightarrow 8.885\times10^{-16}
\]

does not demonstrate quadratic convergence. The exact quadratic prediction from the displayed bound would be on the order of \(10^{-29}\), far below double-precision arithmetic. The observed \(8.885\times10^{-16}\) is therefore a roundoff floor or cancellation-dependent result, not evidence that the asymptotic quadratic regime was numerically observed.

No finite iteration count can be guaranteed from the supplied information for \(D=10^6\). A conservative exact-arithmetic recurrence would be

\[
e_{j+1}\le \frac34e_j^2+\frac14e_j^3,
\]

but a floating-point guarantee requires an explicit error model for:

- the \(D\times K\) multiplication \(Q^TQ\);
- the \(K\times K\) matrix products;
- the subsequent \(D\times K\) update;
- reduction order and parallel nondeterminism;
- scaling and the value of \(K\);
- the initial residual and conditioning.

For \(e_0\ll1\), the mathematical recurrence reaches \(10^{-15}\) in one iteration if \(e_0\lesssim10^{-7}\). That statement is irrelevant to a rigorous floating-point guarantee: one iteration may leave a residual near \(u\) times a substantial dimension-dependent constant, while additional iterations cannot reliably improve below that floor.

### Column-space preservation

Yes, in exact arithmetic, the update preserves the column space:

\[
Q_{+}=Q S,\qquad
S=\frac32I-\frac12Q^TQ.
\]

Thus \(\operatorname{range}(Q_{+})\subseteq\operatorname{range}(Q)\); if \(S\) is nonsingular, the column spaces are equal. However, this does **not** make the iteration itself a Stiefel retraction by definition.

A retraction \(R_X(\eta)\) maps a tangent vector at \(X\) back to the manifold and must satisfy, at minimum,

\[
R_X(0)=X,\qquad
D R_X(0)[\eta]=\eta.
\]

The polar retraction used in Absil, Mahony, and Sepulchre, *Optimization Algorithms on Matrix Manifolds* (2008), is typically

\[
R_X(\eta)
=
(X+\eta)\bigl((X+\eta)^T(X+\eta)\bigr)^{-1/2}.
\]

Your Newton–Schulz step is an **approximation** to this polar factor, not an exactly manifold-valued retraction in finite precision. In exact arithmetic it also has the wrong local first-order coefficient if applied directly to an arbitrary \(Q\) rather than to \(X+\eta\): it is a polar orthogonalization iteration, not automatically a complete retraction construction. It becomes relevant as an iterative approximation to the polar retraction when applied to the trial point \(X+\eta\).

## 3. CGS-2 versus Householder QR

CGS-2 is not provably superior to Householder QR. That claim is backwards.

Björck, “Numerics of Gram-Schmidt Orthogonalization,” *Linear Algebra and its Applications*, 197 (1994), 297–316, analyzes the dependence of Gram–Schmidt orthogonality loss on conditioning and rounding errors. Classical Gram–Schmidt can suffer severe loss of orthogonality; modified Gram–Schmidt is more robust, but its orthogonality behavior still depends on conditioning. Reorthogonalization can restore orthogonality to near-roundoff levels under appropriate hypotheses. Later “twice-is-enough” results make this practical for CGS/MGS, but they do not establish universal superiority over Householder QR.

Householder QR has the stronger classical status: it is backward stable for the factorization, with perturbations of order \(u\) times the matrix norm, subject to the usual dimension-dependent constants. Gram–Schmidt methods often provide useful columnwise or orthogonality guarantees, especially with reorthogonalization, but they do not dominate Householder QR across conditioning, parallel reduction, rank deficiency, and finite-precision regimes.

The correct conclusion from your one test is only:

> CGS-2 produced a smaller residual than this particular QR implementation on this particular input.

It does not imply superior stability.

Approximate leading costs for an \(D\times K\) tall-skinny matrix are:

| Method | Leading arithmetic cost | Main numerical issue |
|---|---:|---|
| Householder QR | \(2DK^2-\frac23K^3\) flops | Stable factorization; explicit \(Q\) formation adds work |
| CGS | approximately \(2DK^2\) flops | Loss of orthogonality can be conditioning-dependent |
| CGS-2 | approximately \(4DK^2\) flops | Reorthogonalization improves orthogonality but doubles projection work |
| Polar refinement | \(O(DK^2)+O(K^3)\) per iteration | Accurate Gram matrix and update required |

The formula \(O(2DK^2)\) for CGS-2 is ambiguous and generally misleading. A single CGS pass already contains projection and normalization work of order \(2DK^2\) under common flop conventions; a second pass adds another comparable projection cost. The leading constant depends on whether dot products, axpy operations, normalization, and triangular operations are counted separately.

For fixed small \(K\), all methods are linear in \(D\), and memory traffic and reduction synchronization can dominate. For large \(K\), the \(K^3\) term in polar refinement and the communication pattern become material.

## 4. GPU Householder QR and FMA

No, GPU QR should not be assumed to have the **same** bound as LAPACK CPU QR.

The algorithmic family may be the same, but the floating-point computation is not. PyTorch documents that QR dispatch differs by device and platform; its CUDA path is not simply LAPACK executed on a GPU, and current CUDA QR implementations use NVIDIA libraries such as cuSOLVER/MAGMA depending on the operation and version. NVIDIA’s GEQRF documentation specifies Householder-based QR, but it does not imply that its constants, reduction order, or explicit-\(Q\) error match LAPACK’s.

A valid statement is:

- Householder QR on the GPU is expected to have the same **qualitative backward-stability mechanism**;
- the CPU LAPACK bound cannot be transplanted verbatim;
- the actual orthogonality residual must be measured for the exact GPU library, version, precision, matrix layout, dimensions, and execution path.

The distinction is especially important because the factorization may be backward stable while the explicitly formed \(Q\) has a different orthogonality residual. Library documentation generally specifies functionality, not a full, implementation-specific forward-error theorem.

FMA normally reduces rounding in an individual multiply-add by rounding once rather than twice. It therefore often improves local arithmetic accuracy. It does not guarantee a smaller global orthogonality error. Parallel reductions may use different association orders, block-level accumulation, tensor-core paths, or mixed-precision intermediates. These effects can dominate any benefit from FMA. FMA can also change bitwise results relative to a CPU implementation, so “identical” should not be conflated with “more accurate.”

## Additional defects in the supplied evidence

- The reported \(D=10^6\) norm of \(999.8395\) is not close to unit norm. If it is intended as \(\|q\|_2\), it is catastrophically incompatible with the stated Stiefel deviation \(2.220\times10^{-16}\). If it is an aggregate quantity, it cannot support a unit-column claim without the exact normalization formula.
- The \(D=10^7\) norm \(3161.852014\) is approximately proportional to \(\sqrt{10^7}\), indicating that the kernel may be measuring the norm of an unnormalized random vector rather than a normalized Stiefel column. It is not evidence of orthogonality.
- “Bitwise invariance” across GPUs does not imply numerical correctness; deterministic replication of a wrong result remains wrong.
- The CUDA IPC warning indicates an unsafe or at least improperly synchronized lifetime protocol. It is unrelated to QR stability but invalidates any claim that the interprocess memory-sharing implementation is fully clean. All consumers must finish using the imported allocation before the producer terminates and releases the original allocation.
- A scalar norm test cannot validate \(\mathrm{St}(K,D)\). The required test is the spectral norm of \(Q^TQ-I_K\), together with residual checks such as \(\|A-QR\|\) and rank/conditioning diagnostics.

The defensible conclusion is therefore narrow: the measurements show that one QR implementation and one CGS-2 implementation reached residuals near the double-precision roundoff floor at \(D=10^5\), with CGS-2 smaller in that trial. They do **not** establish \(10^{-15}\) compliance at \(D=10^6\), quadratic Newton–Schulz convergence in floating point, superiority of CGS-2, or equivalence between GPU and LAPACK QR stability.

---

## AXIS 3: AUTOMATED TELEMETRY PIPELINE & ARCHITECTURAL SOUNDNESS

The architecture is **not exactly-once**, and several reported measurements are not yet scientifically defensible. The database can be made idempotent; the end-to-end pipeline cannot claim exactly-once without durable source identity, transactional acknowledgment, and a recovery ledger.

## 1. Atomicity and idempotency

### Current failure window

The sequence

1. submit or poll Kaggle job;
2. fetch JSONL;
3. parse metrics;
4. insert rows;

has an unavoidable crash window between steps 2–4. If the process dies after downloading the artifact but before PostgreSQL commit, the next run must rediscover and reprocess the artifact. If it dies after PostgreSQL commits but before recording completion locally, the next run will duplicate unless the database rejects or merges the replay.

This is **at-least-once delivery with deduplication**, not exactly-once processing.

`ON CONFLICT` is useful only after a suitable unique identity exists. PostgreSQL documents that `ON CONFLICT DO UPDATE` provides an atomic insert-or-update outcome under the specified arbiter constraint[2]. It does not establish correctness of the identity, prevent semantic overwrites, or make external Kaggle retrieval transactional.

### Do not use the proposed key blindly

`(barrier, test_harness, metric_key)` is probably insufficient. It collapses distinct executions that happen to use the same barrier and harness. That destroys run history and permits a later run to overwrite an earlier run.

Use a stable execution identity:

```sql
CREATE TABLE pmtp_v4_runs (
    run_id              uuid PRIMARY KEY,
    external_job_id     text NOT NULL,
    artifact_sha256     bytea NOT NULL,
    schema_version      integer NOT NULL,
    source_fetched_at   timestamptz NOT NULL,
    ingested_at         timestamptz NOT NULL DEFAULT now(),
    UNIQUE (external_job_id),
    UNIQUE (artifact_sha256)
);

CREATE TABLE pmtp_v4_facts (
    run_id          uuid NOT NULL REFERENCES pmtp_v4_runs,
    barrier         text NOT NULL,
    test_harness    text NOT NULL,
    metric_key      text NOT NULL,
    metric_val      double precision,
    metric_unit     text,
    exit_code       integer,
    peak_ram_mb     double precision,
    latency_ms      double precision,
    checks_passed   integer,
    checks_total    integer,
    notes           text,
    certified_at    timestamptz,
    PRIMARY KEY (run_id, barrier, test_harness, metric_key)
);
```

Then ingest in one transaction:

```sql
INSERT INTO pmtp_v4_runs (
    run_id, external_job_id, artifact_sha256,
    schema_version, source_fetched_at
)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (external_job_id) DO NOTHING;
```

Follow with fact insertion using:

```sql
INSERT INTO pmtp_v4_facts (...)
VALUES (...)
ON CONFLICT (run_id, barrier, test_harness, metric_key)
DO UPDATE SET
    metric_val    = EXCLUDED.metric_val,
    metric_unit   = EXCLUDED.metric_unit,
    exit_code     = EXCLUDED.exit_code,
    notes         = EXCLUDED.notes,
    certified_at  = EXCLUDED.certified_at
WHERE pmtp_v4_facts.metric_val    IS NOT DISTINCT FROM EXCLUDED.metric_val
  AND pmtp_v4_facts.metric_unit   IS NOT DISTINCT FROM EXCLUDED.metric_unit
  AND pmtp_v4_facts.exit_code     IS NOT DISTINCT FROM EXCLUDED.exit_code;
```

The `WHERE` clause is deliberately hostile: a replay with different content should not silently mutate an already accepted fact. Prefer rejecting a content mismatch and raising an integrity alarm.

### Recovery protocol

Implement this state machine:

- `SUBMITTED`
- `RUNNING`
- `COMPLETE_ARTIFACT_UNFETCHED`
- `ARTIFACT_FETCHED`
- `PARSED`
- `DB_COMMITTED`
- `QUARANTINED`
- `FAILED`

Persist the raw artifact before parsing, preferably in immutable object storage or a durable local spool. Record:

- Kaggle job identifier;
- artifact identifier;
- byte length;
- SHA-256;
- fetch timestamp;
- parser version;
- telemetry schema version;
- source log sequence or stream offset.

On restart:

1. recover jobs not in `DB_COMMITTED`;
2. fetch or reload the artifact;
3. verify its digest;
4. parse deterministically;
5. execute one database transaction;
6. mark the run committed only after PostgreSQL confirms commit.

The database row and the external state cannot be committed atomically. Therefore the strongest honest claim is:

> **At-least-once artifact delivery plus database-enforced idempotent ingestion.**

Exactly-once is not a property of `ON CONFLICT`.

## 2. JSONL parsing

Regex over captured stdout is an unacceptable primary telemetry protocol. It is brittle under:

- changed whitespace;
- scientific notation variants;
- locale contamination;
- multiline tracebacks;
- duplicated output;
- truncated logs;
- Unicode escaping;
- buffering and interleaving of stdout/stderr;
- library version changes;
- metric names appearing in diagnostic text.

The Kaggle wrapper’s objects containing `stream_name`, `time`, and `data` are an event envelope, not a typed telemetry schema. Treating `data` as a stable API is a category error.

Emit a structured, versioned telemetry record from the kernel, for example:

```json
{
  "schema": "pmtp.telemetry",
  "schema_version": 1,
  "run_id": "uuid",
  "kernel": "pmtp-v4-dispatch",
  "status": "complete",
  "exit_code": 0,
  "host": {
    "gpu": ["Tesla T4", "Tesla T4"],
    "compute_capability": ["7.5", "7.5"],
    "cuda_runtime": "..."
  },
  "measurements": [
    {
      "key": "vram_to_vram_bandwidth",
      "value": 9.03,
      "unit": "GB/s",
      "samples": 30,
      "statistic": "median"
    }
  ],
  "integrity": {
    "bitwise_identical": true,
    "max_diff": 0.0
  }
}
```

Use explicit delimiters only as a transport convenience:

```text
[TELEMETRY_JSON_START]
{...single JSON object...}
[TELEMETRY_JSON_END]
```

The parser must still validate:

- JSON syntax;
- schema version;
- required fields;
- type constraints;
- unit vocabulary;
- finite numeric values;
- mutually exclusive status conditions;
- duplicate metric keys;
- run identity;
- cryptographic digest of the complete source artifact.

Do not parse values using regular expressions unless regex is merely a fallback diagnostic extractor. The kernel should write the structured record to a file/artifact, not rely solely on stdout. stdout is a human-facing diagnostic channel.

## 3. The 128-byte wire descriptor

The format string is:

```python
<IHHQ4I QIIQQ 64s
```

After removing whitespace, this is:

- `I`: 4
- `H`: 2
- `H`: 2
- `Q`: 8
- `4I`: 16
- `Q`: 8
- `I`: 4
- `I`: 4
- `Q`: 8
- `Q`: 8
- `64s`: 64

Total: \(4+2+2+8+16+8+4+4+8+8+64=128\) bytes.

With Python `struct` and the `<` prefix, fields are encoded little-endian with standard sizes and **no implicit native alignment padding**. Thus the Python representation itself is portable between x86-64 and ARM64, provided every implementation uses exactly that format and does not substitute native format `@`.

However, “portable” is not the same as “well specified.” You still need:

- a field-by-field protocol specification;
- fixed offsets;
- version and length fields;
- reserved bytes initialized to zero;
- range checks;
- endianness declaration;
- a static assertion that serialized size is 128;
- golden test vectors;
- rejection of unknown incompatible versions;
- an integrity check, preferably CRC32C or a cryptographic digest depending on threat model.

The descriptor is not self-authenticating. A magic value detects some corruption; it does not provide integrity or authenticity.

### CUDA IPC handle

Serializing `cudaIpcMemHandle_t` is valid only as an opaque byte container within the CUDA IPC contract. NVIDIA defines `cudaIpcGetMemHandle` as exporting a handle for a device allocation so another process can open it[1]. That does **not** make the handle a portable memory reference.

The handle is constrained by:

- compatible CUDA driver/runtime behavior;
- the same host;
- accessible device topology;
- the lifetime of the allocation and exporting process;
- correct peer/device context;
- CUDA IPC support.

It must not be interpreted as portable across machines, containers with incompatible driver environments, or arbitrary GPU generations. The handle also does not encode a transportable copy of the allocation.

Therefore:

- If this descriptor is explicitly a **single-node CUDA IPC control message**, embedding the opaque 64-byte handle is defensible.
- If the descriptor is presented as a general wire protocol, it is a design flaw.
- If the producer exits before the consumer releases the imported allocation, the warning is operationally significant, not cosmetic. It indicates a lifetime protocol violation or at least an unsafe shutdown sequence.

The protocol should separate:

```text
portable descriptor metadata
local CUDA IPC capability token
```

and mark the latter as `valid only for same-host, same-runtime IPC`.

For cross-host transport, use explicit data movement: pinned host memory, GPUDirect RDMA where supported, or an application-level transport. CUDA IPC is not a cross-machine serialization mechanism.

## 4. Measurements and numerical claims

Several labels are misleading.

### “L2 norm” values

For a vector of \(D=10^6\) normalized-looking values, a norm near \(999.84\) is not unit norm. The reported Stiefel deviation

\[
\left|\|x\|_2-1\right|=2.220\times10^{-16}
\]

is mathematically inconsistent with

\[
\|x\|_2=999.8395353665791845.
\]

Those values cannot describe the same object under the same norm definition. Either:

- the norm was normalized before the deviation calculation;
- the displayed norm is a different quantity;
- the deviation calculation is wrong;
- the output labels are wrong;
- or the telemetry parser associated values with the wrong keys.

Likewise, \(3161.852014\) is approximately \(\sqrt{10^7}\), indicating an all-ones or unit-magnitude vector norm, not evidence of orthogonality or Stiefel feasibility.

A Stiefel constraint applies to a matrix \(Q\in\mathbb{R}^{D\times K}\):

\[
Q^\top Q=I_K.
\]

A single vector has a unit-sphere constraint \(\|q\|_2=1\), which is the \(K=1\) special case. Reporting a scalar norm as “Stiefel deviation” without specifying \(D\), \(K\), matrix layout, and normalization is not acceptable.

### Bandwidth

For a single 80 MB FP64 buffer and 572.32 microseconds, the stated \(139.78\) GB/s depends on the convention:

\[
80{,}000{,}000 / 572.32\ \mu s \approx 139.78\ \text{GB/s}.
\]

That is decimal GB/s. If the payload is \(10^7\times8\) bytes, state whether the numerator is payload bytes, read-plus-write bytes, or effective algorithmic bytes. A tiled reduction commonly reads 80 MB and writes a scalar; calling the result a memory bandwidth is acceptable only if the counting convention is explicit.

The T4’s reported 9.03 GB/s PCIe transfer should distinguish:

- host-to-device;
- device-to-host;
- peer-to-peer;
- one-way or bidirectional;
- payload size;
- warm-up exclusion;
- synchronization method;
- number of repetitions;
- median, mean, minimum, and dispersion.

A single latency and bandwidth pair is not a characterization.

### Timing validity

Use CUDA events on the relevant stream for device execution timing. Host wall-clock timing must include explicit synchronization and must report whether initialization, allocation, compilation, and first-use overheads were excluded. Triton JIT compilation and cache state can dominate first-run measurements.

The stated 0.139 ms for \(D=10^6\) FP64 should be independently checked against:

- achieved memory traffic;
- kernel occupancy;
- register usage;
- memory transaction count;
- launch overhead;
- result validation;
- repeated-run distribution.

The raw claims are plausible only as isolated observations, not as performance conclusions.

## 5. Comparison with common systems

| System | Appropriate role | Fundamental limitation here |
|---|---|---|
| MLflow | Experiment/run metadata, parameters, metrics, artifacts | Stronger run abstraction than the current table, but not a substitute for a strict telemetry schema or ingestion ledger |
| Weights & Biases | Hosted experiment tracking, dashboards, artifact lineage | Adds external service dependence and credential/data-governance exposure; scalar logging is not a transactional benchmark database |
| TensorBoard | Local scalar/event visualization | Event files are useful for visualization, weak as the authoritative system of record |
| Prometheus + Grafana | Operational time-series monitoring and alerting | Pull-oriented metric model is awkward for completed batch jobs and high-cardinality immutable benchmark facts |
| PostgreSQL | Relational authority, constraints, joins, auditability | Adequate at moderate ingest rates; requires deliberate partitioning, indexing, retention, and bulk-ingest design |
| TimescaleDB | PostgreSQL-compatible time-series extensions | Reasonable if time-window queries, hypertables, compression, and retention policies become important |
| InfluxDB | Purpose-built time-series ingestion/querying | Not automatically superior; schema evolution, relational joins, transactional semantics, and operational fit may be worse |

PostgreSQL 16 is a defensible authority for benchmark telemetry because the workload is fundamentally relational: runs, artifacts, configurations, hardware identity, validation results, and metric facts. The current schema is the problem, not PostgreSQL.

Add:

- a run table;
- immutable raw artifact metadata;
- hardware/software environment tables;
- typed metric definitions;
- a metric value type or explicit numeric domain;
- schema and parser versions;
- uniqueness constraints;
- provenance and digest columns;
- indexes aligned with actual queries;
- partitioning only after measuring table growth.

Do not use `SERIAL` as the identity of an externally meaningful run. It is merely a database-local sequence. Use UUID or a deterministic run identifier derived from source identity.

Prometheus is particularly unsuitable as the authoritative sink if labels include barrier, harness, GPU model, run ID, and metric key. Run IDs create high cardinality, and completed benchmark events are not naturally represented as continuously scraped gauges. Prometheus can complement the system for orchestrator health, queue depth, failures, and ingestion latency.

## 6. Credential architecture

The hybrid arrangement is not sound if PostgreSQL stores the active Perplexity API key in ordinary application data.

Problems include:

- excessive blast radius from database compromise;
- accidental inclusion in dumps, replicas, backups, logs, or query exports;
- unclear rotation;
- broad read access through normal application credentials;
- inability to enforce least privilege cleanly;
- secret lifetime decoupled from service deployment.

Kaggle credentials should be injected through a secret manager or CI/Kaggle token mechanism, with a narrowly scoped service identity and file permissions such as `0600` if a file is unavoidable. Kaggle documents token-based authentication and the conventional `~/.kaggle/kaggle.json` location[3][9]. That location is a compatibility convention, not a security boundary.

The API key should live in:

- a cloud secret manager;
- Vault;
- a Kubernetes Secret backed by an external secret manager;
- or an equivalent dedicated secret store.

PostgreSQL may store a **secret reference**, rotation metadata, provider name, and audit record—not the active plaintext key. If a database-backed vault is unavoidable:

- encrypt values using envelope encryption with the key-encryption key outside PostgreSQL;
- isolate decryption privileges;
- prohibit plaintext selection for ordinary roles;
- audit access;
- rotate automatically;
- prevent secrets from entering logical replication and routine exports where possible;
- redact them from exception messages and telemetry.

Never place API keys in benchmark logs, JSONL artifacts, PostgreSQL `notes`, or environment snapshots.

## Required disposition

Before calling this production-grade, require these changes:

1. Replace stdout regex extraction with versioned structured telemetry.
2. Add immutable artifact storage and SHA-256 identity.
3. Introduce a run table and a durable ingestion state machine.
4. Add unique constraints keyed by run identity, not merely barrier and metric name.
5. Use `ON CONFLICT` for replay safety, but reject conflicting content.
6. Specify the 128-byte descriptor with fixed offsets, reserved fields, versioning, and golden vectors.
7. Explicitly constrain CUDA IPC to same-node compatible processes.
8. Fix the contradictory norm/Stiefel telemetry before accepting any numerical result.
9. Separate benchmark facts from operational monitoring.
10. Remove active credentials from ordinary PostgreSQL storage.

The strongest defensible architecture is **durable, replayable, at-least-once ingestion with database-enforced idempotency and immutable provenance**. Anything stronger is currently an assertion unsupported by the design.

---

