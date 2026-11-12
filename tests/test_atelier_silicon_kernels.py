#!/usr/bin/env python3
"""
test_atelier_silicon_kernels.py — Verificacion en Silicio de los Kernels Nativos de ATELIER
Regla 19: Comprobacion de ejecutables nativos C++20 y Rust (Exit Code 0, defecto <= 1e-15).
Nota: Los kernels son binarios Windows (.exe) compilados con MSVC/Rust. En Linux/Mac
se saltan con pytest.skip() para mantener CI/CD verde en todas las plataformas.
"""

import os
import sys
import subprocess
import pytest

KERNEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "atelier_kernel")

_SKIP_REASON = (
    "Kernels nativos de ATELIER son binarios Windows (.exe) compilados con MSVC C++20 y Rust. "
    "Saltar en plataformas no-Windows. Ejecutar localmente en el nodo de silicio Windows."
)

def _require_windows_kernel(exe_name):
    """Retorna la ruta al ejecutable o salta el test si no es Windows o no existe."""
    if sys.platform != "win32":
        pytest.skip(_SKIP_REASON)
    exe_path = os.path.join(KERNEL_DIR, exe_name)
    if not os.path.exists(exe_path):
        pytest.skip(f"Ejecutable no encontrado en este entorno: {exe_path}")
    return exe_path

def test_atelier_cpp_kernel():
    exe_path = _require_windows_kernel("atelier_stiefel_cpp.exe")
    
    result = subprocess.run([exe_path, "1024", "16"], capture_output=True, text=True)
    assert result.returncode == 0, f"Kernel C++ fallo con Exit Code {result.returncode}: {result.stderr}"
    assert "TIER_STIEFEL_FLOOR_15" in result.stdout or "TIER_MACHINE_EPS_16" in result.stdout
    assert "Checks=4/4" in result.stdout

def test_atelier_rust_kernel():
    exe_path = _require_windows_kernel("atelier_stiefel_rs.exe")
    
    result = subprocess.run([exe_path, "1024", "16"], capture_output=True, text=True)
    assert result.returncode == 0, f"Kernel Rust fallo con Exit Code {result.returncode}: {result.stderr}"
    assert "TIER_STIEFEL_FLOOR_15" in result.stdout or "TIER_MACHINE_EPS_16" in result.stdout
    assert "Checks=4/4" in result.stdout
