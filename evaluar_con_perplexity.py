#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POLYDIM RESEARCH GROUP — UTN-FRBA
EVALUACIÓN Y PROFUNDIZACIÓN SOTA CON PERPLEXITY (SONAR-PRO)
===========================================================
Audita la suite de reproducibilidad cero-dependencias, las 3 invariantes
matemáticas (S^{D-1}, Stiefel Twice-is-Enough, Superacumulador Kulisch 4352b)
y el protocolo PMTP 88B zero-copy frente al estado del arte internacional.
"""

import sys
import json
import urllib.request
import psycopg

def get_perplexity_key() -> str:
    conn = psycopg.connect("dbname=polydim_active_db user=postgres host=localhost port=5432")
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM active_vault WHERE key_name = 'Perplexity_Paga' AND category = 'api_key';")
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT value FROM active_vault WHERE key_name ILIKE '%perplexity%' LIMIT 1;")
            row = cur.fetchone()
    conn.close()
    if not row:
        raise RuntimeError("No Perplexity API key found in active_vault.")
    return row[0].strip()

def run_evaluation():
    api_key = get_perplexity_key()
    print("[1/3] Conectado a PostgreSQL 16. Clave de Perplexity recuperada con éxito.")

    prompt = """
Act as an Eminent Professor of Numerical Analysis, High-Performance Computing, and Riemannian Geometry at MIT/Stanford, auditing the doctoral research and pedagogical tooling of the POLYDIM Research Group (UTN-FRBA).

Provide a deep, rigorous, peer-reviewed evaluation of the following 4 core mathematical and systems components implemented in our Zero-Dependency Reproducibility Suite (quickstart_harness.py & HOW_TO_USE_LAB_GUIDE.md):

================================================================================
COMPONENT 1: HYPERSPHERICAL NORMALIZATION ON S^{D-1} (D = 10,000)
================================================================================
- Algorithm: Two-pass Blue/LASSQ dynamic scaling (scale = max_i |x_i|, sumsq = sum (x_i/scale)^2) combined with Neumaier compensated summation for both norm computation and normalization verification.
- Empirical Result: ||u||_2 defect | ||u||_2 - 1.0 | = 1.110e-16 (machine precision floor), condition number kappa = 1.0, latency = 27 ms in pure Python (no numpy).
- Audit Question:
  1. What are the formal asymptotic error bounds of Neumaier compensated summation vs naive summation for D = 10^4 and D = 10^7 under non-reassociative IEEE-754 semantics?
  2. How does the Blue/LASSQ two-pass formulation protect against intermediate overflow/underflow near DBL_MAX and DBL_MIN?

================================================================================
COMPONENT 2: ORTHOGONAL STIEFEL PROJECTION ON St(D, K) (D = 10,000, K = 4)
================================================================================
- Algorithm: Twice-Is-Enough Modified Gram-Schmidt (MGS2 / Kahan-Parlett Reorthogonalization Theorem) with Neumaier inner products on pure contiguous arrays.
- Empirical Result: Infinity norm defect ||X^T X - I_K||_inf = 4.441e-16 (surpassing the target bound < 10^-14), latency = 559 ms.
- Audit Question:
  1. Prove or cite why two passes of MGS (Twice-Is-Enough) are mathematically sufficient to reduce the loss of orthogonality from O(kappa^2 * eps) to O(eps), achieving machine precision regardless of the initial condition number.
  2. Compare MGS2 against direct SVD / Polar decomposition or Cayley transforms in terms of DRAM bandwidth and computational complexity when D >> K (e.g. D = 10^4, K = 4).

================================================================================
COMPONENT 3: KULISCH 4,352-BIT SUPERACCUMULATOR & SUBNORMAL UNDERFLOW MITIGATION
================================================================================
- Context: In deep learning manifolds, extreme gradient inner products often involve subnormal products such as (10^-315 * 10^-315 = 10^-630), which standard IEEE-754 binary64 FPUs flush immediately to 0.0, destroying 56 bits of mantissa information. Furthermore, oscillating gradient updates (10^8 + 10^-8 - 10^8) incur 49.01% relative error in naive FP64 summation.
- Implementation: Universal fixed-point superaccumulator (Radix 2^32, 136 words = 4,352 bits). Bit 0 corresponds to 2^-2148, bit 2,148 corresponds to 1.0, bit 4,351 corresponds to 2^+2048.
- Empirical Result: 
  - Standard FPU: (1e-315 * 1e-315) -> 0.0 (Underflow: True, Information lost: 100%).
  - Kulisch Superacc: Exactly preserves all 56 active bits (integer value 40966672019476009) in words 0 and 1 without rounding.
  - Catastrophic cancellation error reduced from 49.01% to 0.00e+00.
- Audit Question:
  1. What is the exact mathematical foundation of Ulrich Kulisch's exact dot product theorem?
  2. Why is a 4,352-bit fixed point accumulator necessary and sufficient to cover all possible products of two IEEE-754 binary64 numbers (including minimum subnormal 2^-1074 * 2^-1074 = 2^-2148 up to maximum finite 2^1024 * 2^1024 = 2^2048)?
  3. What is the impact on neural network convergence and gradient drift in extreme-dimensional optimization?

================================================================================
COMPONENT 4: PMTP ZERO-COPY IPC (88-BYTE C-ABI DESCRIPTOR) VS JSON SERIALIZATION
================================================================================
- Problem: Exchanging R^10000 vectors via JSON creates a 1D token bottleneck: ~117 KB text, ~54 ms latency, heap thrashing, and Data Processing Inequality (DPI) entropy degradation.
- Solution: PMTP (Polydim Multi-Tenant Protocol) 88-byte C-ABI descriptor ('PDM4' header, offsets, lengths, dtype, shapes) pointing to physical shared memory (SharedMemory / memoryview).
- Empirical Result: Latency reduced from 54.02 ms to 0.94 ms (57.7x speedup) with zero memory copies.
- Audit Question:
  1. Evaluate this zero-copy shared memory architecture from the perspective of Shannon entropy preservation and Data Processing Inequality (I(X; Z) <= I(X; Y)).
  2. Critique the CPython buffer protocol lifecycle (handling memoryview references to avoid Win32 BufferError on close()).

================================================================================
COMPONENT 5: PEDAGOGICAL & SYSTEMS REPRODUCIBILITY ASSESSMENT
================================================================================
- Evaluate quickstart_harness.py (< 80 MB RAM constraint, zero external pip packages, automatic hardware probing, pure Python + ctypes fallback) as a gold standard for computer science education and dissertation verification.

Provide a comprehensive, authoritative, deeply technical report with explicit mathematical proofs, citations, and actionable recommendations.
"""

    print("[2/3] Enviando consulta de auditoría profunda a Perplexity (sonar-pro)...")
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are a world-class authority in numerical analysis, high-performance computing, IEEE-754 arithmetic, and Riemannian manifold optimization. Provide an exhaustive, rigorous, technical dissertation-level review."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    req = urllib.request.Request(
        "https://api.perplexity.ai/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "PolydimAuditor/1.0"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            citations = data.get("citations", [])

            print("[3/3] Dictamen recibido exitosamente de Perplexity Sonar-Pro.")
            print("\n" + "=" * 80)
            print("DICTAMEN SOTA — PERPLEXITY SONAR-PRO REVIEW")
            print("=" * 80)
            print(content)
            print("=" * 80)

            report_file = "perplexity_deep_evaluation_report.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("# DICTAMEN DE AUDITORÍA SOTA — PERPLEXITY (SONAR-PRO)\n")
                f.write("## Evaluación de la Suite de Reproducibilidad y Fundamentos de POLYDIM EINSOF\n")
                f.write(f"**Fecha y Hora:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(content)
                if citations:
                    f.write("\n\n## Referencias y Citaciones SOTA\n")
                    for idx, cite in enumerate(citations, 1):
                        f.write(f"{idx}. {cite}\n")

            print(f"\n[OK] Dictamen completo guardado en: {report_file}")

    except Exception as e:
        print(f"[ERROR]: Fallo al invocar la API de Perplexity: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import time
    run_evaluation()
