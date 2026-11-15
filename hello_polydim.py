#!/usr/bin/env python3
"""
hello_polydim.py — The 30-Line "Hello World" of POLYDIM
======================================================
What this library actually does (in plain systems & math terms):
  1. Orthogonal Subspace Math (`PmtpStiefelAdapter`):
     Computes an orthonormal matrix W (W.T @ W = I_k) using QR + QDWH polar retraction
     so vectors projected between collaborating AI agents do not suffer floating-point drift.
  2. Local Shared-Memory Clipboard (`PmtpShmBus` + `PmtpChannel`):
     Passes NumPy/DLPack arrays between local user-space processes via standard OS shared memory
     (`multiprocessing.shared_memory` / `memfd_create`), authenticated with a 64-bit SipHash-2-4 MAC.
  3. Safe Text Fallback:
     If shared memory is disabled or unsupported, `PmtpChannel` returns the normal UTF-8 text string.
     Zero model weights are modified. Zero root privileges. Zero network calls.
"""

import numpy as np
from pmtp import PmtpShmBus, PmtpChannel, PmtpStiefelAdapter


def main() -> None:
    # 1. Orthonormal basis on Stiefel manifold St(16, 1024): W.T @ W = I_16
    rng = np.random.default_rng(42)
    raw_matrix = rng.standard_normal((1024, 16))
    W, kappa, _, status = PmtpStiefelAdapter.polar_safe_v2(raw_matrix)
    ortho_error = float(np.max(np.abs(W.T @ W - np.eye(16))))

    # 2. Cooperative local shared-memory transfer (with automatic UTF-8 fallback)
    bus = PmtpShmBus(prefix="hello", max_slabs=4, max_dim=1024)
    channel = PmtpChannel(bus)
    try:
        vec_a = W[:, 0]  # Unit vector in R^1024
        envelope = channel.send("Hello from Agent A (standard UTF-8 text)", vec_a)

        # Agent B receives both the UTF-8 text and the exact float64 vector from RAM
        text_b, vec_b = channel.receive(envelope, supports_pmtp=True)
        assert text_b == "Hello from Agent A (standard UTF-8 text)"
        assert np.allclose(vec_a, vec_b, atol=1e-15)

        # Zero-copy DLPack view (points to the exact same physical RAM address)
        slab_id = int(envelope["pmtp"]["slab_id"])
        with bus.get_zero_copy_dlpack_tensor(slab_id) as leased:
            dl_view = np.from_dlpack(leased)
            assert np.allclose(dl_view, vec_a, atol=1e-15)

        print(f"[OK] hello_polydim.py passed | Solver={status} | ||W^T W - I||={ortho_error:.2e} | DLPack=ZeroCopy")
    finally:
        bus.cleanup()


if __name__ == "__main__":
    main()
