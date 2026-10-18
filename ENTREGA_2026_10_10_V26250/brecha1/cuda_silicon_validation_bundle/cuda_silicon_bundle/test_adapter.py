"""
POLYDIM EINSOF — PRODUCTION CUDA/TRITON SILICON TEST ADAPTER V26250
Target: Real NVIDIA Silicon (Tesla T4 sm_75 / A100 sm_80) in Kaggle/Colab.
Binds to:
  1. kernel_cuda_v26250.cu -> polydim_stiefel_retract_cuda_v26250
  2. polydim_triton_kernel_v26250.py -> dot_triton, sphere_project_triton, sphere_transport_triton
"""
from __future__ import annotations

import ctypes
import importlib.util
import math
import sys
from pathlib import Path
from typing import Any, Callable

c_size_t = ctypes.c_size_t
c_void_p = ctypes.c_void_p
c_int32 = ctypes.c_int32
c_int64 = ctypes.c_int64
c_double = ctypes.c_double


def run_silicon_tests(
    *,
    library_path: str,
    cuda_source: str,
    triton_source: str,
    output_dir: str,
    orthogonality_tolerance: float,
    log: Callable[[str], None]
) -> dict[str, Any]:
    log(f"[ADAPTER V26250] Initializing silicon validation suite...")
    log(f"[ADAPTER V26250] Shared library : {library_path}")
    log(f"[ADAPTER V26250] CUDA source    : {cuda_source}")
    log(f"[ADAPTER V26250] Triton source  : {triton_source}")
    log(f"[ADAPTER V26250] Target tol     : < {orthogonality_tolerance:g}")

    import torch
    assert torch.cuda.is_available(), "Physical NVIDIA GPU required for silicon tests"
    device = torch.device("cuda:0")

    # 1. Cargar librerías y configurar FFI
    log("[ADAPTER V26250] Binding cuBLAS, cuSOLVER, and libpolydim_cuda...")
    cudart = ctypes.CDLL("libcudart.so")
    cublas = ctypes.CDLL("libcublas.so")
    cusolver = ctypes.CDLL("libcusolver.so")
    polydim = ctypes.CDLL(library_path)

    blas_handle = c_void_p()
    solver_handle = c_void_p()
    st_b = cublas.cublasCreate_v2(ctypes.byref(blas_handle))
    st_s = cusolver.cusolverDnCreate(ctypes.byref(solver_handle))
    assert st_b == 0, f"cublasCreate_v2 failed with status {st_b}"
    assert st_s == 0, f"cusolverDnCreate failed with status {st_s}"

    fn_retract = polydim.polydim_stiefel_retract_cuda_v26250
    fn_retract.argtypes = [
        c_void_p, c_void_p, c_void_p, c_void_p, c_void_p,
        c_int64, c_int64, c_double,
        c_void_p, c_size_t, c_void_p
    ]
    fn_retract.restype = c_int32

    # 2. Ejecutar Stiefel Retraction en GPU con Monolithic Workspace
    D = 10_000
    K = 8
    step = 0.1

    def alloc_colmajor(rows: int, cols: int) -> torch.Tensor:
        """Aloca tensor 2D en memoria Column-Major (Fortran-order, stride (1, rows))."""
        return torch.empty(cols, rows, dtype=torch.float64, device=device).t()

    log(f"[ADAPTER V26250] Allocating Stiefel Manifold test tensors D={D}, K={K} (FP64, Column-Major)...")
    torch.manual_seed(42)
    G_raw = torch.randn(D, K, dtype=torch.float64, device=device)
    # Generar punto X sobre Stiefel St(D, K) vía factorización QR
    Q, _ = torch.linalg.qr(G_raw)
    X = alloc_colmajor(D, K)
    X.copy_(Q)

    # Generar vector tangente Z en T_X St(D, K): Z = W - X @ sym(X.T @ W)
    W = torch.randn(D, K, dtype=torch.float64, device=device)
    XtW = X.T @ W
    sym_XtW = 0.5 * (XtW + XtW.T)
    Z_raw = W - X @ sym_XtW
    Z = alloc_colmajor(D, K)
    Z.copy_(Z_raw)

    # Calcular tamaño de Monolithic Workspace:
    # U: 2*D*K*8, V: 2*D*K*8, G: 4*K*K*8, B: 2*K*K*8, piv: 2*K*4, info: 1*4, work: 64KB
    ws_bytes = (2 * D * 2 * K * 8) + (4 * K * K * 8) + (2 * K * K * 8) + (2 * K * 4) + 4 + 65536
    ws_tensor = torch.empty(ws_bytes, dtype=torch.uint8, device=device)
    d_out1 = alloc_colmajor(D, K)
    d_out2 = alloc_colmajor(D, K)

    log("[ADAPTER V26250] Launching polydim_stiefel_retract_cuda_v26250 (Pass 1)...")
    ev_start = torch.cuda.Event(enable_timing=True)
    ev_end = torch.cuda.Event(enable_timing=True)

    ev_start.record()
    rc1 = fn_retract(
        blas_handle, solver_handle,
        c_void_p(X.data_ptr()),
        c_void_p(Z.data_ptr()),
        c_void_p(d_out1.data_ptr()),
        D, K, step,
        c_void_p(ws_tensor.data_ptr()),
        ws_bytes,
        None
    )
    ev_end.record()
    torch.cuda.synchronize()
    gpu_time_ms = float(ev_start.elapsed_time(ev_end))

    assert rc1 == 0, f"CUDA retraction returned error code: {rc1}"
    log(f"[ADAPTER V26250] Pass 1 complete in {gpu_time_ms:.4f} ms (CUDA Events).")

    # Medir error de ortogonalidad ||Y^T Y - I_K||
    I_K = torch.eye(K, dtype=torch.float64, device=device)
    Gram = d_out1.T @ d_out1
    orth_err = float(torch.max(torch.abs(Gram - I_K)).item())
    log(f"[ADAPTER V26250] Max orthogonality deviation: ||Y^T Y - I||_max = {orth_err:.3e}")
    assert orth_err < orthogonality_tolerance, f"Orthogonality violated: {orth_err} >= {orthogonality_tolerance}"

    # Pass 2: Verificación estricta de determinismo bit a bit
    log("[ADAPTER V26250] Launching Pass 2 for bitwise determinism check...")
    rc2 = fn_retract(
        blas_handle, solver_handle,
        c_void_p(X.data_ptr()),
        c_void_p(Z.data_ptr()),
        c_void_p(d_out2.data_ptr()),
        D, K, step,
        c_void_p(ws_tensor.data_ptr()),
        ws_bytes,
        None
    )
    torch.cuda.synchronize()
    assert rc2 == 0, f"CUDA retraction pass 2 returned error code: {rc2}"

    bitwise_match = torch.equal(d_out1, d_out2)
    log(f"[ADAPTER V26250] Bitwise determinism across runs: {bitwise_match}")
    assert bitwise_match, "Non-deterministic GPU execution detected!"

    # 3. Casos de Borde (Boundary Tests): D no múltiplo de 128
    log("[ADAPTER V26250] Running boundary dimension tests (D=100003, D=129)...")
    for D_b in (100_003, 129):
        X_b_raw = torch.randn(D_b, K, dtype=torch.float64, device=device)
        Q_b, _ = torch.linalg.qr(X_b_raw)
        X_b = alloc_colmajor(D_b, K)
        X_b.copy_(Q_b)
        W_b = torch.randn(D_b, K, dtype=torch.float64, device=device)
        Z_b_raw = W_b - X_b @ (0.5 * (X_b.T @ W_b + (X_b.T @ W_b).T))
        Z_b = alloc_colmajor(D_b, K)
        Z_b.copy_(Z_b_raw)
        ws_b_bytes = (2 * D_b * 2 * K * 8) + (4 * K * K * 8) + (2 * K * K * 8) + (2 * K * 4) + 4 + 65536
        ws_b = torch.empty(ws_b_bytes, dtype=torch.uint8, device=device)
        out_b = alloc_colmajor(D_b, K)

        rc_b = fn_retract(
            blas_handle, solver_handle,
            c_void_p(X_b.data_ptr()),
            c_void_p(Z_b.data_ptr()),
            c_void_p(out_b.data_ptr()),
            D_b, K, step,
            c_void_p(ws_b.data_ptr()),
            ws_b_bytes,
            None
        )
        torch.cuda.synchronize()
        assert rc_b == 0, f"Boundary test D={D_b} failed with code {rc_b}"
        err_b = float(torch.max(torch.abs(out_b.T @ out_b - I_K)).item())
        log(f"  Boundary D={D_b}: PASS (orth_err={err_b:.3e})")
        assert err_b < orthogonality_tolerance

    # 4. Validación de Kernel Triton
    log("[ADAPTER V26250] Importing and testing Triton kernel module...")
    spec = importlib.util.spec_from_file_location("polydim_triton", triton_source)
    assert spec is not None and spec.loader is not None, "Failed to load Triton module spec"
    triton_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(triton_mod)

    # Validar dot_triton en D=100_003
    t_x = torch.randn(100_003, dtype=torch.float64, device=device)
    t_y = torch.randn(100_003, dtype=torch.float64, device=device)
    dot_val = triton_mod.dot_triton(t_x, t_y)
    torch_dot = float(torch.dot(t_x, t_y).item())
    dot_diff = abs(dot_val - torch_dot)
    log(f"[ADAPTER V26250] Triton dot_triton vs torch.dot diff: {dot_diff:.3e}")
    assert dot_diff < 1e-9, f"Triton dot precision loss: {dot_diff}"

    # Validar sphere_project_triton
    rc_p, proj_out, meta_p = triton_mod.sphere_project_triton(t_x)
    assert rc_p == 0, f"sphere_project_triton returned code {rc_p}"
    norm_proj = float(torch.norm(proj_out, p=2).item())
    norm_err = abs(norm_proj - 1.0)
    log(f"[ADAPTER V26250] Triton sphere_project norm error: {norm_err:.3e}")
    assert norm_err < 1e-12, f"Sphere projection norm error: {norm_err}"

    # Validar sphere_transport_triton
    v_tan = torch.randn(100_003, dtype=torch.float64, device=device)
    # Asegurar que v_tan es tangente a proj_out: v = v - (proj_out . v) * proj_out
    v_tan = v_tan - torch.dot(proj_out, v_tan) * proj_out
    y_target = torch.randn(100_003, dtype=torch.float64, device=device)
    _, y_proj, _ = triton_mod.sphere_project_triton(y_target)
    rc_t, trans_out, meta_t = triton_mod.sphere_transport_triton(proj_out, y_proj, v_tan)
    assert rc_t == 0, f"sphere_transport_triton returned code {rc_t}"
    log("[ADAPTER V26250] Triton transport: PASS")

    # Limpieza de Handles
    cublas.cublasDestroy_v2(blas_handle)
    cusolver.cusolverDnDestroy(solver_handle)

    log("[ADAPTER V26250] All CUDA C++20 and Triton silicon obligations PASSED.")

    return {
        "cuda_passed": True,
        "triton_passed": True,
        "orthogonality_error": orth_err,
        "gpu_time_ms": gpu_time_ms,
        "bitwise_deterministic": True,
        "synchronized_after_kernel": True,
        "D": D,
        "K": K,
        "device_name": torch.cuda.get_device_name(0),
    }
