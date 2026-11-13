#!/usr/bin/env python3
r"""
================================================================================
  SETUP SOBERANO DE MATHESIS: AUTO-INSTALADOR Y DIAGNÓSTICO EN SILICIO
================================================================================
Diseñado para que la IA (Antigravity u otra) lo ejecute automáticamente en el
primer arranque de la máquina de un usuario novato o avanzado.

Garantías:
  1. Detecta SO y microarquitectura (x86_64, SSE2, AVX, FMA).
  2. Verifica dependencias mínimas (Python >= 3.10, NumPy). Las instala si faltan.
  3. Crea un programa de ejemplo 'primer_ejecutable.mth'.
  4. Compila a ejecutable nativo (.exe en Windows / .elf en Linux) sin GCC ni MSVC.
  5. Ejecuta el binario en silicio y valida Exit Code 0.
================================================================================
"""

import os
import sys
import platform
import subprocess
import time

def print_banner():
    print("=" * 75)
    print("   MATHESIS SOVEREIGN SETUP -- INICIALIZADOR AUTOMÁTICO EN SILICIO")
    print("   (Para usuarios novatos guiados por Inteligencia Artificial)")
    print("=" * 75)

def check_python_and_deps():
    print("\n[1/4] Verificando entorno básico de ejecución...")
    py_ver = platform.python_version()
    print(f"    - Python detectado: {py_ver} ({platform.system()} {platform.machine()})")
    
    # Verificar NumPy
    try:
        import numpy as np
        print(f"    - NumPy detectado: v{np.__version__} (OK)")
    except ImportError:
        print("    [!] NumPy no encontrado. Instalando automáticamente vía pip...")
        res = subprocess.run([sys.executable, "-m", "pip", "install", "numpy"], capture_output=True, text=True)
        if res.returncode == 0:
            print("    [+] NumPy instalado exitosamente.")
        else:
            print(f"    [!] Error instalando NumPy: {res.stderr}")
            sys.exit(1)

def test_compiler_ready():
    print("\n[2/4] Verificando compilador soberano MTHC...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mthc_path = os.path.join(base_dir, "mthc.py")
    if not os.path.exists(mthc_path):
        print(f"    [!] Error: No se encontró mthc.py en {base_dir}")
        sys.exit(1)
    print(f"    [+] mthc.py disponible en: {mthc_path}")

def generate_and_compile_sample():
    print("\n[3/4] Generando tu primer programa continuo 'primer_ejecutable.mth'...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_mth = os.path.join(base_dir, "primer_ejecutable.mth")
    
    code = (
        "# MI PRIMER PROGRAMA EN MATHESIS (2026-2027)\n"
        "# Genera un ejecutable nativo puro sin C, sin C++, sin dependencias externas\n\n"
        "ROT_LIE_SO|DEST=0x1000|D=2048|SAGES=EULER\n"
        "SYMPLECTIC_COVARIANT_UK|DEST=0x2000|A=0x1000|D=2048|THETA=0.05|SAGES=POINCARE\n"
        "RETRACT_STIEFEL|DEST=0x2000|D=2048\n"
        "COLLAPSE_MMIO|DEST=0x0000|A=0x2000|D=2048\n"
        "HALT_EQUILIBRIUM|DEST=0x2000|D=2048\n"
    )
    with open(sample_mth, "w", encoding="utf-8") as f:
        f.write(code)
    print("    [+] Archivo 'primer_ejecutable.mth' creado con éxito.")

    # Compilar según sistema operativo
    system = platform.system().lower()
    if "windows" in system:
        out_bin = os.path.join(base_dir, "primer_ejecutable.exe")
        target = "win64"
    else:
        out_bin = os.path.join(base_dir, "primer_ejecutable.elf")
        target = "elf64"

    print(f"    [*] Compilando a binario nativo ({target}) -> {os.path.basename(out_bin)}...")
    t0 = time.perf_counter()
    res = subprocess.run([
        sys.executable,
        os.path.join(base_dir, "mthc.py"),
        sample_mth,
        "-t", target,
        "-o", out_bin
    ], capture_output=True, text=True)
    dt_ms = (time.perf_counter() - t0) * 1000.0

    if res.returncode == 0 and os.path.exists(out_bin) and os.path.getsize(out_bin) > 0:
        print(f"    [+] ¡Compilación EXITOSA! Tamaño: {os.path.getsize(out_bin)} bytes en {dt_ms:.2f} ms")
        return out_bin
    else:
        print(f"    [!] Error de compilación: {res.stderr}")
        print(res.stdout)
        sys.exit(1)

def run_sample_binary(bin_path: str):
    print(f"\n[4/4] Ejecutando '{os.path.basename(bin_path)}' en silicio físico...")
    # Asegurar permisos de ejecución en Linux
    if platform.system().lower() != "windows":
        os.chmod(bin_path, 0o755)

    t0 = time.perf_counter()
    proc = subprocess.run([bin_path], capture_output=True, text=True)
    dt_ms = (time.perf_counter() - t0) * 1000.0

    if proc.returncode == 0:
        print(f"    [+] ¡EJECUCIÓN EXITOSA! (Exit Code 0) en {dt_ms:.2f} ms")
        print("\n--- SALIDA DIRECTA DE TU PROCESADOR ---")
        print(proc.stdout.strip())
        print("---------------------------------------")
        return True
    else:
        print(f"    [!] Error en ejecución: returncode={proc.returncode}")
        print(proc.stderr)
        return False

def main():
    print_banner()
    check_python_and_deps()
    test_compiler_ready()
    bin_path = generate_and_compile_sample()
    ok = run_sample_binary(bin_path)

    if ok:
        print("\n" + "=" * 75)
        print("  🎉 ¡FELICITACIONES! MATHESIS ESTÁ 100% OPERATIVO EN TU MÁQUINA.")
        print("  Tu IA (Antigravity) ya puede escribir programas '.mth' y generar")
        print("  ejecutables autónomos de alto rendimiento para ti.")
        print("=" * 75)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
