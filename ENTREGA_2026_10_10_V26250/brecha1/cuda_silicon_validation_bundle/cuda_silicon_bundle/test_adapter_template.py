"""Template only: adapt this file to the real API of the project sources.

Do not return fabricated values. Replace TODOs with actual allocations, CUDA
entry-point calls, Triton kernel launches, synchronizations, correctness checks,
and CUDA-event timing. The harness rejects missing/false metrics.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def run_silicon_tests(*, library_path: str, cuda_source: str, triton_source: str,
                      output_dir: str, orthogonality_tolerance: float,
                      log: Callable[[str], None]) -> dict[str, Any]:
    """Run the real project kernels, then return measurements.

    Required return fields:
      cuda_passed: bool
      triton_passed: bool
      orthogonality_error: float  # measured ||Y.T @ Y - I|| in the declared norm
      gpu_time_ms: float          # CUDA-event elapsed time, not host wall time
      bitwise_deterministic: bool # compare repeated output bit patterns on same GPU
      synchronized_after_kernel: bool

    Before returning success, this adapter should at minimum:
      1. Load library_path with ctypes and configure exact argtypes/restype from
         the real exported C ABI (do not guess signatures).
      2. Construct valid Stiefel input data and invoke the actual CUDA retraction.
      3. Check CUDA launch status AND synchronize the device/stream; check errors.
      4. Import/load the actual Triton module, launch the actual kernel on GPU,
         synchronize, validate masked non-multiple dimensions (e.g. D=100_000),
         and compare repeated output bit patterns if determinism is claimed.
      5. Measure the project operation with torch.cuda.Event or native CUDA events.
      6. Compute ||Y.T @ Y - I|| in float64 if that is the agreed numerical contract.

    The project CUDA/Triton source files were not included with this template, so
    there is intentionally no speculative implementation of their unknown API.
    """
    log(f"[ADAPTER TEMPLATE] library={library_path}")
    log(f"[ADAPTER TEMPLATE] CUDA source={cuda_source}")
    log(f"[ADAPTER TEMPLATE] Triton source={triton_source}")
    log(f"[ADAPTER TEMPLATE] requested orthogonality tolerance < {orthogonality_tolerance:g}")
    raise NotImplementedError(
        "Wire this adapter to the real source project's exported CUDA ABI and Triton entry points; "
        "the harness intentionally refuses to invent pass metrics."
    )
