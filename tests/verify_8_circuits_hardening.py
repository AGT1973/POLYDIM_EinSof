#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
MASTER VERIFICATION SUITE: 8 INDEPENDENT SILICON CIRCUITS (/INVESTIGA PROTOCOL)
Ecosistema Soberano POLYDIM-EINSOF | Ariel García Traba

Executes and certifies the 8 independent silicon and mathematical circuits:
  1. Geometría Riemanniana y Retracción Polar en Stiefel (Weyl + Schönhage-Björck + Newton-Schulz Ord-5)
  2. Aritmética Numérica, Acumulador Neumaier y Preservación de Mantisa (|Sk| <= 1e14 << 2^53)
  3. Concurrencia Lock-Free, Memoria Compartida PmtpShmBus v2.1 y Resiliencia Bit-Flip (BLAKE2s-64)
  4. Compilación Nativa Mathesis MTHC v1.4 y Semántica Fail-Fast (SSE2 ucomisd -> ExitCode 1)
  5. Deconstrucción Cuántica y Modelo Físico en 156 Qubits Heron r2 (Modelo 78.16% y Mitigación TREX)
  6. Coisometría y Regularización de Tikhonov en el Núcleo ker(W) (pmtp_coisometry.py)
  7. Factorización de Triple Cizalla en SO(2) y Evitación de Singularidades (remediated_shear_rotation.py)
  8. Triángulo de la Verdad, AST Zero-Trust y Verificación Criptográfica (audit_zero_trust_ast.py)
"""

import sys
import subprocess
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
MASTER_DIR = r"E:\POLYDIM_EINSOF"

def resolve_script(filename):
    for candidate in [
        os.path.join(CURRENT_DIR, filename),
        os.path.join(PARENT_DIR, filename),
        os.path.join(MASTER_DIR, filename),
    ]:
        if os.path.exists(candidate):
            return candidate
    return filename

CIRCUITS = [
    (1, "test_weyl_stiefel_hardening.py", "Circuito 1: Cota de Weyl & Pre-escalado Stiefel"),
    (2, "test_neumaier_stress_hardening.py", "Circuito 2: Acumulador Neumaier sin Overflow"),
    (3, "test_seqlock_blake2s_hardening.py", "Circuito 3: Seqlock v2.1 BLAKE2s Resiliencia Bit-Flip"),
    (4, "verify_mthc_v14_stiefel.py", "Circuito 4: Compilador MTHC v1.4 Fail-Fast Silicio"),
    (5, "dispersive_readout_vs_t1_model.py", "Circuito 5: Deconstrucción Cuántica T1 vs Dispersivo"),
    (6, "pmtp_coisometry.py", "Circuito 6: Coisometría y Tikhonov sobre ker(W)"),
    (7, "remediated_shear_rotation.py", "Circuito 7: Triple Cizalla SO(2) & Salto Singularidad"),
    (8, "audit_zero_trust_ast.py", "Circuito 8: Auditoría AST Zero-Trust e Inmutabilidad"),
]

def main():
    print("=" * 75)
    print("EJECUTANDO SUITE MAESTRA DE 8 CIRCUITOS INDEPENDIENTES (/INVESTIGA)")
    print("=" * 75)
    
    passed_circuits = 0
    for cid, script_name, desc in CIRCUITS:
        script_path = resolve_script(script_name)
        print(f"\n[CIRCUITO {cid}/8] {desc}...")
        res = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  -> PASS (Exit Code 0).")
            passed_circuits += 1
        else:
            print(f"  -> FAIL (Exit Code {res.returncode}):")
            print(res.stderr.strip()[:300])
            sys.exit(res.returncode)
            
    print("\n" + "=" * 75)
    print(f"RESULTADO: {passed_circuits}/8 CIRCUITOS INDEPENDIENTES CERTIFICADOS EN SILICIO.")
    print("EXIT CODE 0 EN LA TOTALIDAD DE LA ARQUITECTURA.")
    print("=" * 75)
    return 0

if __name__ == "__main__":
    sys.exit(main())
