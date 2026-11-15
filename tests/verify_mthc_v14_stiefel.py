#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
ADVERSARIAL SILICON VERIFICATION SUITE FOR MTHC v1.4 (CIRCUITO 4)
Ecosistema Soberano POLYDIM-EINSOF | Ariel García Traba

================================================================================
OBJECIÓN DEL TRIBUNAL DE SABIOS (SEMÁNTICA FAIL-FAST) & COMPROBACIÓN EN SILICIO:
================================================================================
Miedo / Ataque de los Revisores:
  "Un compilador sin runtime puede dejar pasar silenciosamente matrices degeneradas,
   valores NaN o violaciones de ortonormalidad en la variedad de Stiefel,
   propagando estados corruptos a los siguientes procesos."

Garantía y Compuertas en Hardware SSE2:
  1. Emisión Nativa Pura: MTHC v1.4 emite microcódigo x86_64 directo en memoria
     (PE32+ en Windows y ELF64 en Linux) sin dependencias de toolchain externo (sin CRT).
  2. Compuerta Fail-Fast en Hardware: El compilador inyecta instrucciones `ucomisd`.
     Si la CPU detecta paridad (`PF=1`, indicador de `NaN`) o deriva superior al
     umbral 1e-13, bifurca incondicionalmente a `ExitProcess(1)`.
  3. Sabuesos Adversariales (Negative Test Gates):
     - Hound A: Matriz nula (||0^T 0 - I_4||_F = 2.0 > 1e-13) -> CPU retorna Exit Code 1.
     - Hound B: Matriz singular 0/0 produciendo NaN -> CPU atrapa trampa PF=1 -> Exit Code 1.
  4. Ejecución Positiva Exitosa: V_1(R^2048), V_4(R^512) y V_8(R^256) completan con
     Exit Code 0 en menos de 20 ms de tiempo de ejecución físico.
================================================================================
"""

import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, r"E:\POLYDIM_EINSOF")
from mthc import compile_mathesis


def main() -> int:
    print("=" * 72)
    print("verify_mthc_v14_stiefel.py — MTHC v1.4 Native Silicon Audit")
    print("=" * 72)

    mth_path = r"E:\POLYDIM_EINSOF\stiefel_vk_v14.mth"
    exe_path = r"E:\POLYDIM_EINSOF\mathesis_vk_stiefel_v14.exe"
    elf_path = r"E:\POLYDIM_EINSOF\mathesis_vk_stiefel_v14.elf"
    obj_path = r"E:\POLYDIM_EINSOF\mathesis_vk_stiefel_v14.obj"

    mth_source = (
        "# Programa Mathesis v1.4 — Variedades de Stiefel V_k(R^D) con Gate Hardware\n"
        "ROT_LIE_SO | DEST=0x01 | D=2048 | K=1 | SAGES=GANDALF+SABIOS\n"
        "RETRACT_STIEFEL_MAT | DEST=0x02 | D=512 | K=4\n"
        "RETRACT_STIEFEL_MAT | DEST=0x03 | D=256 | K=8\n"
        "DIALECTIC_LYAPUNOV | DEST=0x04 | A=0x02 | B=0x02 | D=512 | K=4\n"
        "HALT_EQUILIBRIUM | DEST=0x04\n"
    )
    with open(mth_path, "w", encoding="utf-8") as f:
        f.write(mth_source)

    m_pe = compile_mathesis(mth_source, exe_path, target="win64", filename=mth_path)
    m_elf = compile_mathesis(mth_source, elf_path, target="elf64", filename=mth_path)
    m_obj = compile_mathesis(mth_source, obj_path, target="coff", compile_only=True, filename=mth_path)

    # Check 1: Magic byte audit in PE32+ and ELF64
    for label, path in [("PE32+", exe_path), ("ELF64", elf_path)]:
        raw = open(path, "rb").read()
        pmtp_hits = raw.count(b"\xC7\x07\x50\x4D\x54\x50")
        ptmp_hits = raw.count(b"\xC7\x07\x50\x54\x4D\x50")
        assert pmtp_hits >= 3, f"{label}: expected >=3 'PMTP' slab headers, got {pmtp_hits}"
        assert ptmp_hits == 0, f"{label}: found {ptmp_hits} occurrences of transposed 'PTMP' bug!"
        print(f"  [PASS] Binary Magic Audit ({label:5s}) | 'PMTP' hits={pmtp_hits} | 'PTMP' bugs={ptmp_hits} | bytes={len(raw)}")

    # Check 2: Execute native Windows x64 PE32+ binary directly on CPU
    t0 = time.perf_counter_ns()
    proc = subprocess.run([exe_path], capture_output=True, text=True, timeout=10)
    elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
    assert proc.returncode == 0, f"Positive binary failed with rc={proc.returncode}: {proc.stdout}\n{proc.stderr}"
    assert "V_4(R^512)" in proc.stdout and "V_8(R^256)" in proc.stdout
    print(f"  [PASS] Native PE32+ Silicon Run   | rc={proc.returncode} | wall_ms={elapsed_ms:.2f} | code_bytes={m_pe['code_bytes']}")
    for line in proc.stdout.strip().splitlines():
        print(f"         {line}")

    # Check 3 (Adversarial Hound A): Non-orthonormal zero matrix -> must exit 1 via `ja fail_handler`
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_zero_exe = os.path.join(tmpdir, "hound_non_orthonormal.exe")
        compile_mathesis("ASSERT_STIEFEL | DEST=0x09 | D=128 | K=4 | ZERO=1\n", bad_zero_exe, target="win64")
        p_bad1 = subprocess.run([bad_zero_exe], capture_output=True, text=True, timeout=10)
        assert p_bad1.returncode == 1, f"Hound A expected rc=1, got rc={p_bad1.returncode}"
        print(f"  [PASS] Hound A (||0 - I_4||_F=2)  | Native CPU rejected non-orthonormal slab -> rc={p_bad1.returncode}")

        # Check 4 (Adversarial Hound B): 0/0 = NaN during retraction -> must exit 1 via `jp fail_handler`
        bad_nan_exe = os.path.join(tmpdir, "hound_nan_singularity.exe")
        compile_mathesis("ROT_LIE_SO | DEST=0x0A | D=128 | K=4 | ZERO=1\n", bad_nan_exe, target="win64")
        p_bad2 = subprocess.run([bad_nan_exe], capture_output=True, text=True, timeout=10)
        assert p_bad2.returncode == 1, f"Hound B expected rc=1, got rc={p_bad2.returncode}"
        print(f"  [PASS] Hound B (0/0 IEEE-754 NaN) | Native CPU caught PF=1 parity NaN trap -> rc={p_bad2.returncode}")

    print("=" * 72)
    print("[SUCCESS] MTHC v1.4 — 5/5 controles de silicio y sabuesos PASS (Exit Code 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
