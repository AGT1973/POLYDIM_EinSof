#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
E:\SUITE\tests\test_mathesis_universal_transpiler.py
====================================================
Suite de verificación de compilación y transpilación universal SOTA 2030:
  - Ada 2022
  - Fortran 2023
  - COBOL (FP64 COMP-2)
  - Python 3.15 (Ejecución real en silicio host)
  - Rust 1.100 (Compilación real con rustc 1.100.0-beta.4)
  - C++20
  - Zig 0.14
"""

import os
import sys
import tempfile
import subprocess
import pytest

ATELIER_DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "atelier_dev"))
if ATELIER_DEV_DIR not in sys.path:
    sys.path.insert(0, ATELIER_DEV_DIR)
from mathesis_universal_transpiler import MathesisUniversalTranspiler

@pytest.fixture
def transpiler():
    return MathesisUniversalTranspiler(k=16, D=1024, tolerance=1e-15)

def test_transpile_ada_specification_and_body(transpiler):
    ada = transpiler.to_ada2022()
    assert "stiefel_manifold.ads" in ada
    assert "stiefel_manifold.adb" in ada
    assert "SPARK_Mode => On" in ada["stiefel_manifold.ads"]
    assert "digits 18" in ada["stiefel_manifold.ads"]
    assert "Neumaier_Add" in ada["stiefel_manifold.adb"]

def test_transpile_fortran2023(transpiler):
    f90 = transpiler.to_fortran2023()
    assert "module stiefel_manifold" in f90
    assert "real(real64)" in f90
    assert "neumaier_sum" in f90
    assert "do concurrent" in f90

def test_transpile_cobol_fp64(transpiler):
    cbl = transpiler.to_cobol()
    assert "PROGRAM-ID. STIEFEL-ENGINE." in cbl
    assert "USAGE COMP-2" in cbl
    assert "WS-NEUMAIER-ACCUMULATOR" in cbl

def test_transpile_and_run_python315(transpiler):
    py_code = transpiler.to_python315()
    assert "Python 3.15" in py_code
    
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(py_code)
        f_path = f.name
        
    try:
        res = subprocess.run([sys.executable, f_path], capture_output=True, text=True)
        assert res.returncode == 0, f"Python execution failed: {res.stderr}"
        assert "Exit Code 0" in res.stdout
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)

def test_transpile_and_compile_rust1100(transpiler):
    rs_code = transpiler.to_rust1100()
    assert "#![no_std]" in rs_code
    
    with tempfile.NamedTemporaryFile("w", suffix=".rs", delete=False) as f:
        f.write(rs_code)
        f_path = f.name
        
    out_lib = f_path.replace(".rs", ".rlib")
    try:
        # Compilar físicamente con rustc 1.100 en silicio real
        res = subprocess.run(
            ["rustc", "--crate-type=lib", f_path, "-o", out_lib],
            capture_output=True,
            text=True
        )
        assert res.returncode == 0, f"Rustc 1.100 failed: {res.stderr}"
        assert os.path.exists(out_lib)
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)
        if os.path.exists(out_lib):
            os.remove(out_lib)

def test_transpile_cpp20_and_zig(transpiler):
    cpp = transpiler.to_cpp20()
    zig = transpiler.to_zig()
    assert "namespace mathesis" in cpp
    assert "NeumaierAccumulator" in cpp
    assert "pub const NeumaierAcc" in zig
