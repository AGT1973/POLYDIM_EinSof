The failure is most likely **Kaggle session provisioning**, not a JAX/XLA defect. `libtpu.so` is supplied by the TPU-enabled runtime; a CPU-only container cannot initialize JAX’s TPU backend, so `jax.devices("tpu")` must fail there. Kaggle documents TPU v3-8 as a Notebook accelerator, while its CLI metadata documentation identifies `machine_shape` as the accelerator selector and lists `TpuV5E8` for TPU v5e-8.[1][2][3]

## 1. Why the CLI falls back to CPU

`enable_tpu: true` is a legacy boolean. Kaggle’s current API documentation marks `enable_tpu` and `enable_gpu` as deprecated in favor of `machine_shape`.[1] In practice, the following are distinct layers:

- **Metadata declaration**: requests an accelerator.
- **Kaggle scheduler allocation**: decides whether the job receives a TPU-backed session.
- **Container selection**: starts a TPU-compatible image.
- **JAX runtime discovery**: imports `libtpu.so` and exposes TPU devices.

If allocation fails or the request is normalized to a CPU session, Kaggle starts the ordinary Python image. That image does not contain the TPU runtime library, producing:

```text
Backend 'tpu' failed to initialize:
INTERNAL: Failed to open libtpu.so
Available backends are ['cpu']
```

Unused `tpuQuota` is not proof that a TPU VM was allocated. Quota is an account-side allowance; it does not guarantee scheduler capacity, eligibility for a particular accelerator, or that a CLI kernel submission is routed through the same provisioning path as a browser-created Notebook session.

`docker_image` also cannot manufacture TPU support. Selecting a generic CPU image while requesting a TPU is insufficient: the image must be one that Kaggle recognizes and launches with TPU runtime integration. Do not assume that `gcr.io/kaggle-images/python` contains `libtpu.so`.

## 2. Metadata and provisioning

The publicly documented metadata fields include the usual kernel fields plus `machine_shape`; the CLI metadata documentation gives this general structure and identifies `TpuV5E8` as a valid machine-shape example.[3]

A reasonable v5e request is:

```json
{
  "id": "OWNER/KERNEL_SLUG",
  "title": "TPU benchmark",
  "code_file": "benchmark.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_tpu": true,
  "enable_internet": true,
  "machine_shape": "TpuV5E8",
  "dataset_sources": [],
  "competition_sources": [],
  "kernel_sources": [],
  "model_sources": []
}
```

For the browser-visible TPU v3-8 option, use:

```json
"machine_shape": "TpuV3-8"
```

However, the exact capitalization and accepted enum names are controlled by Kaggle’s backend, not by JAX. The available documentation explicitly confirms `TpuV5E8`; it does **not** establish that every CLI deployment accepts `"TpuV3-8"` as a valid current enum. Therefore:

```bash
kaggle kernels push -p .
```

is the correct submission form once the metadata has been generated or validated locally, but there is no documented CLI flag that can force scheduler allocation if the backend rejects or ignores the TPU request.

Do not combine contradictory settings such as:

```json
"enable_gpu": true,
"enable_tpu": true
```

Use one accelerator class. Prefer `machine_shape` and retain `enable_tpu: true` only for compatibility with older Kaggle metadata handling.

For v3-8, the most reliable procedure is:

1. Create or open the Notebook in the Kaggle web UI.
2. Set **Settings → Accelerator → TPU v3-8**.
3. Save or execute a trivial cell.
4. Pull the resulting kernel metadata/notebook with the CLI.
5. Preserve the accelerator-related fields.
6. Push code changes without changing the accelerator selection.

Kaggle issue/discussion evidence indicates that browser-selected accelerator settings can be preserved by pulling the kernel and then using the CLI, whereas CLI-only submissions have historically failed to persist the requested accelerator configuration.[7] This makes the web-created Notebook session the practical “session lock”: the UI allocates the TPU-backed session, and the CLI is then used for source/version management rather than initial hardware selection.

Verification must occur before benchmarking:

```python
import json
import os
import platform
import jax
import jaxlib

report = {
    "platform": jax.default_backend(),
    "devices": [str(d) for d in jax.devices()],
    "tpu_devices": [str(d) for d in jax.devices("tpu")],
    "jax_version": jax.__version__,
    "jaxlib_version": jaxlib.__version__,
    "hostname": platform.node(),
    "env": {
        k: v for k, v in os.environ.items()
        if k.startswith(("TPU", "JAX", "XLA", "LIBTPU"))
    },
}

print(json.dumps(report, sort_keys=True))
assert report["platform"] == "tpu"
assert len(report["tpu_devices"]) == 8
```

If this assertion fails, stop. Installing `libtpu` inside the running CPU job does not convert that job into a TPU VM.

## 3. Headless execution when CLI allocation fails

There is no supported mechanism whereby a CPU-only Kaggle CLI kernel can dynamically attach a TPU VM after startup. The reliable headless pattern is:

1. Use the web UI once to create and save a TPU v3-8 Notebook session.
2. Put the benchmark and a JSON-producing launcher in the Notebook.
3. Execute the Notebook through Kaggle’s existing Notebook/session mechanism or trigger execution of that already TPU-bound kernel.
4. Pull the resulting output artifact or Notebook version.
5. Validate the JSON report locally.

A launcher should write both a machine-readable file and an unmistakable failure record:

```python
from pathlib import Path
import json
import traceback
import time

out = Path("/kaggle/working/tpu_result.json")

try:
    import jax

    record = {
        "timestamp": time.time(),
        "backend": jax.default_backend(),
        "devices": [str(x) for x in jax.devices()],
        "tpu_devices": [str(x) for x in jax.devices("tpu")],
    }

    if record["backend"] != "tpu" or len(record["tpu_devices"]) != 8:
        raise RuntimeError(f"Not a TPU v3-8 session: {record}")

    # Execute the benchmark here.
    record["status"] = "verified_tpu"

except Exception as exc:
    record = {
        "status": "failed",
        "error": repr(exc),
        "traceback": traceback.format_exc(),
    }

out.write_text(json.dumps(record, indent=2, sort_keys=True))
print(out.read_text())

if record["status"] != "verified_tpu":
    raise SystemExit(2)
```

For truly unattended TPU VM jobs, use Google Cloud TPU rather than Kaggle: create a TPU VM with the Cloud TPU API or `gcloud`, install JAX/libtpu using Google’s TPU instructions, run the process over SSH or startup scripts, and upload JSON to Cloud Storage. Google’s TPU documentation describes the JAX/XLA stack and TPU execution model, while the performance guide documents compilation and execution behavior.[2][6] Kaggle quota cannot be transferred to a Google Cloud project.

## 4. JAX/XLA structure for zero-host execution

“Zero-host latency” should mean **no host involvement inside the timed steady-state loop**, not zero host work during compilation or initial dispatch. Compile once, execute repeatedly on device, and synchronize only outside the measured region.

### Static-shape Cayley/Sherman–Morrison–Woodbury pattern

For a Cayley transform

\[
Q=(I-A)^{-1}(I+A),
\]

where \(A\) is represented as a low-rank update, avoid constructing a dense \(D \times D\) matrix. With

\[
A=U V^\top,
\]

Woodbury gives

\[
(I-U V^\top)^{-1}
=
I+U(I-V^\top U)^{-1}V^\top.
\]

A JAX pattern is:

```python
import jax
import jax.numpy as jnp
from functools import partial

D = 1_000_000
K = 16

@partial(jax.jit, static_argnames=("D", "K"))
def cayley_apply(x, U, V, D, K):
    # x: [D], U/V: [D, K]
    # Small KxK system only.
    eye_k = jnp.eye(K, dtype=x.dtype)
    small = eye_k - V.T @ U

    # y = (I - U V^T)^(-1) x
    rhs = V.T @ x
    correction = U @ jnp.linalg.solve(small, rhs)
    y = x + correction

    # (I + U V^T)y
    return y + U @ (V.T @ y)
```

For a rank-\(K\) Stiefel update, keep all dimensions fixed, use fixed-size arrays, and pass dimensions as static arguments only when they affect tracing. Prefer `jnp.linalg.solve` on the \(K \times K\) system; do not form an inverse explicitly.

If the update is skew-symmetric and represented by factors, preserve that structure in the factorization rather than materializing \(A\). Also verify the algebraic ordering: left versus right Cayley application changes whether the solve is applied before or after the low-rank multiplication.

### Clifford rotor application

A general Clifford rotor should not be represented as a dense \(D \times D\) operator. For a rotor generated by a bivector,

\[
R=\exp\left(\frac{1}{2}\theta\,B\right),
\]

the action on a vector can often be reduced to a small number of inner products and fused elementwise operations when the bivector has low-rank or plane-pair structure.

For a two-plane rotation with orthonormal \(u,v\), let

\[
a=u^\top x,\qquad b=v^\top x.
\]

Then

\[
x' = x
+u\left((\cos\theta-1)a-\sin\theta\,b\right)
+v\left(\sin\theta\,a+(\cos\theta-1)b\right).
\]

```python
@jax.jit
def rotor_plane(x, u, v, theta):
    c = jnp.cos(theta)
    s = jnp.sin(theta)

    a = jnp.vdot(u, x)
    b = jnp.vdot(v, x)

    du = (c - 1.0) * a - s * b
    dv = s * a + (c - 1.0) * b
    return x + u * du + v * dv
```

For multiple independent planes, store `u` and `v` as `[D, R]` and fuse the contractions:

```python
@jax.jit
def rotor_planes(x, u, v, theta):
    # u, v: [D, R]; theta: [R]
    c = jnp.cos(theta)
    s = jnp.sin(theta)

    a = u.T @ x
    b = v.T @ x

    cu = (c - 1.0) * a - s * b
    cv = s * a + (c - 1.0) * b

    return x + u @ cu + v @ cv
```

This is still \(O(DR)\), but avoids \(O(D^2)\) storage and computation. For \(D=10^7\), memory traffic—not merely FLOP count—will dominate, and TPU v3-8 sharding is essential.

### Compile once, then run device-resident steps

```python
import jax
import jax.numpy as jnp

def step(x, U, V, u, v, theta):
    x = cayley_apply(x, U, V, D=D, K=K)
    x = rotor_planes(x, u, v, theta)
    return x

compiled = jax.jit(step).lower(x0, U, V, u, v, theta).compile()

x = x0
x = compiled(x, U, V, u, v, theta).block_until_ready()  # warm-up

for _ in range(100):
    x = compiled(x, U, V, u, v, theta)

x.block_until_ready()
```

For a static loop, use `lax.scan` or `lax.fori_loop` so the loop is part of one compiled executable:

```python
from jax import lax

@jax.jit
def repeated(x, U, V, u, v, theta, n):
    def body(_, state):
        return step(state, U, V, u, v, theta)
    return lax.fori_loop(0, n, body, x)
```

If `n` is static and modest, an unrolled or scan-based computation can reduce dispatch overhead. If it is dynamic, XLA may generate a loop while preserving device execution, but shape polymorphism and dynamic control flow can reduce optimization quality.

### FP64 caveat on TPU v3

Use explicit `jnp.float64` and enable X64:

```python
jax.config.update("jax_enable_x64", True)

dtype = jnp.float64
x = jnp.asarray(x, dtype=dtype)
```

Then verify the lowered IR and runtime behavior rather than assuming that a requested dtype implies fast native FP64. TPU generations have substantially different numeric capabilities and performance characteristics; FP64 may be emulated, decomposed, or much slower than BF16/FP32. For a benchmark claiming FP64 performance, report:

- requested JAX dtype;
- lowered StableHLO/HLO dtype;
- TPU generation;
- compile time;
- steady-state device time;
- numerical error against a trusted reference;
- host-to-device transfers;
- whether collective operations occur.

Useful inspection hooks include:

```python
lowered = jax.jit(step).lower(x0, U, V, u, v, theta)
print(lowered.as_text())
```

and, where supported by the installed JAX version:

```python
compiled = lowered.compile()
print(compiled.runtime_executable())
```

The key arbitration conclusion is:

- `libtpu.so` missing means the process is not running in a TPU-enabled runtime.
- Quota alone does not establish TPU allocation.
- `machine_shape` is the relevant modern metadata selector; `enable_tpu` is legacy.
- A browser-created TPU v3-8 Notebook, pulled and then driven through the CLI, is the practical Kaggle workaround when headless push does not provision hardware.
- No JAX code can repair a CPU-only Kaggle session.
- For the benchmark itself, compile fixed-shape low-rank formulas once, keep the iteration loop on device, and validate the backend and eight-device topology before collecting performance data.