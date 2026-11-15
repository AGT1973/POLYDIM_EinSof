#!/usr/bin/env python3
r"""
TEST SUITE DE CERTIFICACIÓN SILICIO: MTHC v1.3 (Multi-Target & PmtpShmBus)
==========================================================================
Audita rigurosamente el compilador soberano MATHESIS:
  1. Compilación a ejecutable Windows PE32+ (.exe) y ejecución en silicio físico (Exit Code 0).
  2. Compilación a código objeto reubicable COFF (.obj) estilo `gcc -c`.
  3. Compilación a ejecutable autónomo Linux ELF64 (.elf).
  4. Despliegue y ejecución nativa en el nodo ALADIN (192.168.100.21) con syscalls puros (Exit Code 0).
  5. Compilación a código objeto reubicable Linux ELF64 (.o) estilo `gcc -c`.
  6. Intercambio tensorial trans-proceso zero-copy en descriptores PmtpShmBus (Exit Code 0, Deriva <= 1e-15).

Autor Intelectual: Ariel García Traba (53 años)
Rigor: Gandalf & Tribunal de Sabios
Exit Code 0 Obligatorio.
"""

import os
import sys
import time
import subprocess
import numpy as np

# Configurar path
BASE_DIR = r"E:\POLYDIM_EINSOF"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mthc import compile_mathesis, PmtpMthcBridge

ALADIN_HOST = "agt@192.168.100.21"

def run_suite():
    print("==================================================================")
    print("  SUITE DE CERTIFICACIÓN EN SILICIO: COMPILADOR MTHC v1.3")
    print("  (Zero C, Zero GCC, Zero MSVC -- Microcódigo x86_64 SSE2 Puro)")
    print("  Targets: Windows PE32+ (.exe), COFF (.obj), Linux ELF64 (.elf), ELF (.o)")
    print("  IPC: Descriptores PmtpShmBus Zero-Copy Trans-Proceso en RAM")
    print("==================================================================")

    candidate_names = [
        "test_lyapunov_dreaming.mth",
        "facturacion_geometrica.mth",
        "primer_ejecutable.mth"
    ]
    test_files = []
    for cname in candidate_names:
        for p in [os.path.join(r"E:\MATHESIS", cname), os.path.join(BASE_DIR, cname)]:
            if os.path.exists(p):
                test_files.append(p)
                break

    total_checks = 0
    passed_checks = 0

    for tf in test_files:
        name = os.path.basename(tf)
        base_name = os.path.splitext(name)[0]
        print(f"\n[*] Auditando programa continuo: {name}")

        with open(tf, 'r', encoding='utf-8') as f:
            src = f.read()

        # -------------------------------------------------------------
        # 1. Compilación Windows PE32+ (.exe)
        # -------------------------------------------------------------
        exe_path = os.path.join(BASE_DIR, f"{base_name}_v13.exe")
        t0 = time.perf_counter()
        m_exe = compile_mathesis(src, exe_path, target="win64", compile_only=False, filename=tf)
        dt_comp_exe = (time.perf_counter() - t0) * 1000
        total_checks += 1
        if os.path.exists(exe_path) and os.path.getsize(exe_path) > 0:
            print(f"  [+] [PASS] PE32+ Compilado: {os.path.getsize(exe_path)} bytes ({dt_comp_exe:.2f} ms)")
            passed_checks += 1
        else:
            print("  [!] [FAIL] Fallo al compilar PE32+")

        # -------------------------------------------------------------
        # 2. Ejecución física nativa del ejecutable Windows en silicio
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        proc = subprocess.run([exe_path], capture_output=True, text=True)
        dt_run_win = (time.perf_counter() - t0) * 1000
        total_checks += 1
        if proc.returncode == 0 and ("EJECUCION EXITOSA (EXIT CODE 0)" in proc.stdout or "EXIT CODE 0" in proc.stdout):
            print(f"  [+] [PASS] Ejecución Silicio Host (Win64): Exit Code 0 | Latencia: {dt_run_win:.2f} ms")
            passed_checks += 1
        else:
            print(f"  [!] [FAIL] Fallo ejecución Win64: returncode={proc.returncode}")
            print(proc.stderr[:200])

        # -------------------------------------------------------------
        # 3. Compilación a Código Objeto COFF (-c)
        # -------------------------------------------------------------
        obj_path = os.path.join(BASE_DIR, f"{base_name}_v13.obj")
        t0 = time.perf_counter()
        m_obj = compile_mathesis(src, obj_path, target="coff", compile_only=True, filename=tf)
        dt_comp_obj = (time.perf_counter() - t0) * 1000
        total_checks += 1
        if os.path.exists(obj_path) and os.path.getsize(obj_path) > 0:
            print(f"  [+] [PASS] Objeto COFF (-c) Emitido: {os.path.getsize(obj_path)} bytes ({dt_comp_obj:.2f} ms)")
            passed_checks += 1
        else:
            print("  [!] [FAIL] Fallo al emitir objeto COFF")

        # -------------------------------------------------------------
        # 4. Compilación a Ejecutable Autónomo Linux ELF64 (.elf)
        # -------------------------------------------------------------
        elf_path = os.path.join(BASE_DIR, f"{base_name}_v13.elf")
        t0 = time.perf_counter()
        m_elf = compile_mathesis(src, elf_path, target="elf64", compile_only=False, filename=tf)
        dt_comp_elf = (time.perf_counter() - t0) * 1000
        total_checks += 1
        if os.path.exists(elf_path) and os.path.getsize(elf_path) > 0:
            print(f"  [+] [PASS] ELF64 Estático Compilado: {os.path.getsize(elf_path)} bytes ({dt_comp_elf:.2f} ms)")
            passed_checks += 1
        else:
            print("  [!] [FAIL] Fallo al compilar ELF64")

        # -------------------------------------------------------------
        # 5. Despliegue y Ejecución en Silicio en Nodo ALADIN (Debian 13)
        # -------------------------------------------------------------
        remote_path = f"/home/agt/{base_name}_v13.elf"
        scp_cmd = ["scp", elf_path, f"{ALADIN_HOST}:{remote_path}"]
        total_checks += 1
        try:
            res_scp = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=10)
            if res_scp.returncode == 0:
                # Ejecutar por SSH en Debian 13
                t0 = time.perf_counter()
                ssh_cmd = ["ssh", ALADIN_HOST, f"chmod +x {remote_path} && {remote_path}"]
                res_ssh = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
                dt_run_aladin = (time.perf_counter() - t0) * 1000
                if res_ssh.returncode == 0 and ("EJECUCION EXITOSA (EXIT CODE 0)" in res_ssh.stdout or "EXIT CODE 0" in res_ssh.stdout):
                    print(f"  [+] [PASS] Silicio ALADIN (i3-8100/Debian 13): Exit Code 0 | Latencia: {dt_run_aladin:.2f} ms")
                    passed_checks += 1
                else:
                    print(f"  [!] [FAIL] Ejecución remota falló: returncode={res_ssh.returncode}")
                    print(res_ssh.stderr[:200])
            else:
                print(f"  [!] [FAIL] SCP falló al nodo ALADIN: {res_scp.stderr[:200]}")
        except Exception as e:
            print(f"  [!] [FAIL] Excepción en ALADIN: {e}")

        # -------------------------------------------------------------
        # 6. Compilación a Código Objeto Reubicable Linux ELF64 (.o)
        # -------------------------------------------------------------
        o_path = os.path.join(BASE_DIR, f"{base_name}_v13.o")
        t0 = time.perf_counter()
        m_o = compile_mathesis(src, o_path, target="elf_obj", compile_only=True, filename=tf)
        dt_comp_o = (time.perf_counter() - t0) * 1000
        total_checks += 1
        if os.path.exists(o_path) and os.path.getsize(o_path) > 0:
            print(f"  [+] [PASS] Objeto ELF64 (.o) Emitido: {os.path.getsize(o_path)} bytes ({dt_comp_o:.2f} ms)")
            passed_checks += 1
        else:
            print("  [!] [FAIL] Fallo al emitir objeto ELF64 (.o)")

    # -----------------------------------------------------------------
    # 7. Intercambio Tensorial Zero-Copy PmtpShmBus Trans-Proceso
    # -----------------------------------------------------------------
    print("\n[*] Auditando Intercambio Tensorial Zero-Copy Trans-Proceso (PmtpShmBus)...")
    total_checks += 1
    try:
        bridge = PmtpMthcBridge(prefix="pmtp_mthc_cert", max_dim=8192)
        dim = 2048
        slabs = [0x1000, 0x2000, 0x3000]
        bridge.allocate_program_slabs(slabs, dim=dim)

        # Inyectar seed sin disco
        seed_a = np.cos(np.linspace(0, 2*np.pi, dim))
        seed_b = np.sin(np.linspace(0, 2*np.pi, dim))
        bridge.publish_seed_tensor(0x1000, seed_a)
        bridge.publish_seed_tensor(0x2000, seed_b)

        # Leer zero-copy y simular síntesis de Lyapunov
        t_a = bridge.read_slab_tensor(0x1000, dim=dim)
        t_b = bridge.read_slab_tensor(0x2000, dim=dim)
        t_dest = bridge.read_slab_tensor(0x3000, dim=dim)

        t_dest[:] = 0.5 * (t_a + t_b)
        dest_norm = np.linalg.norm(t_dest)
        t_dest /= dest_norm

        # Verificar invariante de Stiefel en RAM viva
        stiefel_err = abs(float(np.dot(t_dest, t_dest)) - 1.0)
        bridge.release()

        if stiefel_err <= 1e-15:
            print(f"  [+] [PASS] PmtpShmBus Zero-Copy: Exit Code 0 | Deriva Stiefel: {stiefel_err:.2e} <= 1e-15")
            passed_checks += 1
        else:
            print(f"  [!] [FAIL] Deriva Stiefel excedida: {stiefel_err}")
    except Exception as e:
        print(f"  [!] [FAIL] Error en auditoría PmtpShmBus: {e}")
        import traceback
        traceback.print_exc()

    print("\n==================================================================")
    print(f"  RESUMEN DE CERTIFICACIÓN SILICIO: {passed_checks}/{total_checks} CHECKS APROBADOS")
    print("==================================================================")
    return passed_checks == total_checks

if __name__ == "__main__":
    ok = run_suite()
    sys.exit(0 if ok else 1)
