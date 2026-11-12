#!/usr/bin/env python3
"""
test_atelier_silicon_kernels.py — Verificacion en Silicio de los Kernels Nativos de ATELIER
Regla 19: Comprobacion de ejecutables nativos C++20 y Rust (Exit Code 0, defecto <= 1e-15).
"""

import os
import subprocess
import pytest

KERNEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "atelier_kernel")

def test_atelier_cpp_kernel():
    exe_path = os.path.join(KERNEL_DIR, "atelier_stiefel_cpp.exe")
    assert os.path.exists(exe_path), f"Ejecutable C++20 no encontrado: {exe_path}"
    
    result = subprocess.run([exe_path, "1024", "16"], capture_output=True, text=True)
    assert result.returncode == 0, f"Kernel C++ fallo con Exit Code {result.returncode}: {result.stderr}"
    assert "TIER_STIEFEL_FLOOR_15" in result.stdout or "TIER_MACHINE_EPS_16" in result.stdout
    assert "Checks=4/4" in result.stdout

def test_atelier_rust_kernel():
    exe_path = os.path.join(KERNEL_DIR, "atelier_stiefel_rs.exe")
    assert os.path.exists(exe_path), f"Ejecutable Rust no encontrado: {exe_path}"
    
    result = subprocess.run([exe_path, "1024", "16"], capture_output=True, text=True)
    assert result.returncode == 0, f"Kernel Rust fallo con Exit Code {result.returncode}: {result.stderr}"
    assert "TIER_STIEFEL_FLOOR_15" in result.stdout or "TIER_MACHINE_EPS_16" in result.stdout
    assert "Checks=4/4" in result.stdout
