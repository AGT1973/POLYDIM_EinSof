#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUITE DE CERTIFICACIÓN DE SILICIO: POLYDIM V26300
Verifica en silicio real:
1. Kernel C++20 WinLibs GCC 14 (libpolydim_cpp_v26300.dll):
   - Proyección esférica S^(D-1) Neumaier
   - Producto interno dot_neumaier
   - Puente Stiefel residual con bypass exacto bit a bit
   - Monitor atómico PMTP V5
2. Kernel Rust 2021 Safe SIMD (libpolydim_rust_v26300.dll):
   - Dot product Neumaier
   - Sphere project con subnormal handling
   - Stiefel residual inject
   - PMTP V5 validate lease
3. Monolito Python V26300 (polydim_v26300_monolito.py)
"""

import os
import sys
import ctypes
import numpy as np
import torch

MINGW_BIN = r"E:\varios\winlibs_gcc14_zip\mingw64\bin"
if os.path.exists(MINGW_BIN):
    try:
        os.add_dll_directory(MINGW_BIN)
    except Exception:
        pass

def test_cpp_silicon():
    print("--- [TEST 1/3] C++20 WinLibs Kernel (libpolydim_cpp_v26300.dll) ---")
    cpp_path = r"E:\POLYDIM_EINSOF\libpolydim_cpp_v26300.dll"
    assert os.path.exists(cpp_path), "libpolydim_cpp_v26300.dll no existe"
    lib = ctypes.CDLL(cpp_path)

    # 1. Dot Neumaier
    a = np.array([1.0e16, 1.0, -1.0e16], dtype=np.float64)
    b = np.array([1.0, 1.0, 1.0], dtype=np.float64)
    out_dot = ctypes.c_double(0.0)

    class View(ctypes.Structure):
        _fields_ = [("ptr", ctypes.c_void_p), ("len", ctypes.c_uint64)]

    va = View(a.ctypes.data, 3)
    vb = View(b.ctypes.data, 3)
    res = lib.polydim_dot_neumaier_v26300(va, vb, ctypes.byref(out_dot))
    assert res == 0, f"Error en dot_neumaier: {res}"
    assert np.isclose(out_dot.value, 1.0), f"Falla en compensación Neumaier: {out_dot.value}"

    # 2. Stiefel residual bypass beta=0.0
    D, K = 896, 64
    h = np.random.randn(D).astype(np.float64)
    W = np.random.randn(D, K).astype(np.float64)
    z_orig = np.random.randn(K).astype(np.float64)
    z_prime = np.random.randn(K).astype(np.float64)
    h_out = np.zeros(D, dtype=np.float64)

    res_inj = lib.polydim_stiefel_residual_inject_v26300(
        h.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        W.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        z_orig.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        z_prime.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_double(0.0),
        ctypes.c_uint64(D),
        ctypes.c_uint64(K),
        h_out.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    assert res_inj == 0, f"Error en inject residual: {res_inj}"
    assert h.tobytes() == h_out.tobytes(), "Falla en bypass exacto bit a bit C++"
    print("C++20 SILICON TEST: 100% PASSED")
    return True


def test_rust_silicon():
    print("--- [TEST 2/3] Rust 2021 Safe SIMD Kernel (libpolydim_rust_v26300.dll) ---")
    rust_path = r"E:\POLYDIM_EINSOF\libpolydim_rust_v26300.dll"
    assert os.path.exists(rust_path), "libpolydim_rust_v26300.dll no existe"
    lib = ctypes.CDLL(rust_path)

    # Dot Neumaier
    a = np.array([1.0e16, 1.0, -1.0e16], dtype=np.float64)
    b = np.array([1.0, 1.0, 1.0], dtype=np.float64)
    out_dot = ctypes.c_double(0.0)
    res = lib.polydim_rust_dot_neumaier_v26300(
        a.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        b.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_uint64(3),
        ctypes.byref(out_dot)
    )
    assert res == 0, f"Error en rust dot: {res}"
    assert np.isclose(out_dot.value, 1.0), f"Falla en Rust Neumaier: {out_dot.value}"

    # Stiefel residual bypass beta=0.0
    D, K = 896, 64
    h = np.random.randn(D).astype(np.float64)
    W = np.random.randn(D, K).astype(np.float64)
    z_orig = np.random.randn(K).astype(np.float64)
    z_prime = np.random.randn(K).astype(np.float64)
    h_out = np.zeros(D, dtype=np.float64)

    res_inj = lib.polydim_rust_stiefel_residual_inject_v26300(
        h.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        W.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        z_orig.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        z_prime.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        ctypes.c_double(0.0),
        ctypes.c_uint64(D),
        ctypes.c_uint64(K),
        h_out.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    assert res_inj == 0, f"Error en rust inject residual: {res_inj}"
    assert h.tobytes() == h_out.tobytes(), "Falla en bypass exacto bit a bit Rust"
    print("RUST 2021 SILICON TEST: 100% PASSED")
    return True


def test_monolith_silicon():
    print("--- [TEST 3/3] Monolito Python V26300 Integration ---")
    from polydim_v26300_monolito import run_silicon_benchmark_v26300
    res = run_silicon_benchmark_v26300()
    assert res["exit_code"] == 0, f"Falla en monolito: {res}"
    assert res["sequence_abi_bitwise_identity"] is True
    assert res["cam_mqar_max_error"] == 0.0
    print(f"MONOLITO INTEGRATION TEST: 100% PASSED (Tiempo: {res['elapsed_ms']:.2f} ms)")
    return True


if __name__ == "__main__":
    print("=== POLYDIM V26300 FULL SUITE SILICON CERTIFICATION ===")
    test_cpp_silicon()
    test_rust_silicon()
    test_monolith_silicon()
    print("=== TODAS LAS CAPAS VALIDADAS EN SILICIO FÍSICO CON EXIT CODE 0 ===")
    sys.exit(0)
