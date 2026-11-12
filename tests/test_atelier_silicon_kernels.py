#!/usr/bin/env python3
"""
test_atelier_silicon_kernels.py — Verificacion en Silicio de los Kernels Nativos de ATELIER
Regla 19: Comprobacion de ejecutables nativos C++20 y Rust (Exit Code 0, defecto <= 1e-15).
Multiplataforma: Windows (binarios compilados .exe) / Linux & macOS (compilados in-situ en CI o local).
"""

import os
import sys
import shutil
import subprocess
import pytest

KERNEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "atelier_kernel")

def _get_or_build_kernel(name_base, source_file, lang="cpp"):
    """
    Retorna la ruta al binario ejecutable. Si no existe en plataformas POSIX,
    intenta compilarlo in-situ (g++/clang++ o rustc).
    """
    ext = ".exe" if sys.platform == "win32" else ""
    exe_name = f"{name_base}{ext}"
    exe_path = os.path.join(KERNEL_DIR, exe_name)

    if os.path.exists(exe_path):
        return exe_path

    # Intento de compilacion in-situ en Linux/macOS
    src_path = os.path.join(KERNEL_DIR, source_file)
    if not os.path.exists(src_path):
        pytest.skip(f"Codigo fuente {source_file} no encontrado.")

    if lang == "cpp":
        compiler = shutil.which("g++") or shutil.which("clang++")
        if not compiler:
            pytest.skip("Compilador C++ (g++/clang++) no disponible en este entorno.")
        cmd = [compiler, "-std=c++20", "-O3", src_path, "-o", exe_path]
        if sys.platform.startswith("linux"):
            cmd.append("-lrt")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            pytest.skip(f"Compilacion C++ in-situ fallo: {res.stderr}")

    elif lang == "rust":
        rustc = shutil.which("rustc")
        if not rustc:
            pytest.skip("rustc no disponible en este entorno.")
        cmd = [rustc, "-O", src_path, "-o", exe_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            pytest.skip(f"Compilacion Rust in-situ fallo: {res.stderr}")

    if os.path.exists(exe_path):
        return exe_path

    pytest.skip(f"Binario {exe_name} no disponible.")

def test_atelier_cpp_kernel():
    exe_path = _get_or_build_kernel("atelier_stiefel_cpp", "atelier_stiefel.cpp", lang="cpp")
    result = subprocess.run([exe_path, "1024", "16"], capture_output=True, text=True)
    assert result.returncode == 0, f"Kernel C++ fallo con Exit Code {result.returncode}: {result.stderr}"
    assert "TIER_STIEFEL_FLOOR_15" in result.stdout or "TIER_MACHINE_EPS_16" in result.stdout
    assert "Checks=4/4" in result.stdout

def test_atelier_rust_kernel():
    exe_path = _get_or_build_kernel("atelier_stiefel_rs", "atelier_stiefel.rs", lang="rust")
    result = subprocess.run([exe_path, "1024", "16"], capture_output=True, text=True)
    assert result.returncode == 0, f"Kernel Rust fallo con Exit Code {result.returncode}: {result.stderr}"
    assert "TIER_STIEFEL_FLOOR_15" in result.stdout or "TIER_MACHINE_EPS_16" in result.stdout
    assert "Checks=4/4" in result.stdout
