import psycopg
import urllib.request
import json
import sys

def main():
    conn = psycopg.connect("dbname=polydim_active_db user=postgres host=localhost port=5432")
    with conn.cursor() as cur:
        cur.execute("SELECT value FROM active_vault WHERE key_name = 'Perplexity_Paga' AND category = 'api_key';")
        row = cur.fetchone()
        if not row:
            print("Perplexity key not found in vault")
            sys.exit(1)
        api_key = row[0].strip()
    conn.close()

    prompt = """
Act as an uncompromising Principal Numerical Analyst and High-Performance Computing (HPC) Systems Architect.

Review and validate the mathematical and architectural remediation for three critical issues in a C++20 high-dimensional manifold kernel (S^{D-1} with D up to 10^7):

1. NEUMAIER ACCUMULATION SIMD UNROLLING (8-WAY CASCADED REDUCTION):
   - Problem: Standard Neumaier compensated summation has a loop-carried dependency (sum, comp) preventing SIMD auto-vectorization under strict non-associative FP flags (#pragma GCC optimize("no-associative-math")).
   - Proposed Fix: Partition the array across 8 independent lanes (sum[8], comp[8]) processed in chunks of 8. Each lane updates its own (sum[k], comp[k]) independently. After processing n elements, combine the 8 partial results using a cascade Neumaier accumulation:
     for k in 0..7:
         neumaier_accumulate(sum[k], total_sum, total_comp)
         neumaier_accumulate(comp[k], total_sum, total_comp)
   - Questions:
     * Does the 8-lane partitioned Neumaier preserve the asymptotic error bound O(eps) + O(n eps^2) of standard Neumaier summation?
     * What is the exact condition number behavior compared to scalar Neumaier?
     * Is the cascaded combination of the 8 lanes numerically sound?

2. OPENMP PARALLEL WRITE & NUMERICAL DEFENSE:
   - Problem: OpenMP loop writing normalized vector components omitted finite-checks or risked data race on shared error flags.
   - Proposed Fix: Use `#pragma omp parallel for reduction(||:has_nan)` with `if (!std::isfinite(res)) has_nan = true;` inside the loop.
   - Question: Is OpenMP reduction(||:has_nan) standard C++ OpenMP conforming across GCC, Clang, and MSVC?

3. RELATIVE TANGENCY TOLERANCE SCALING:
   - Problem: Checking x^T v == 0 using `tol = tol_d * std::max(1.0, ||v||)` artificially inflates tolerance to 1.0 when ||v|| << 1 (e.g. ||v|| = 10^-8), allowing relative orthogonality errors of 1000%.
   - Proposed Fix: Replace with `tol = tol_d * (||v|| + 1e-16)` or `tol = std::max(1e-15, tol_d * ||v||)`.
   - Question: What is the rigorous differential-geometric definition of relative tangency tolerance in S^{D-1} for subnormal or infinitesimal vectors?

Provide a concise, doctoral-level verification verdict with explicit numerical bounds and formulas.
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a Principal Numerical Analyst and HPC Systems Architect. Be rigorous, exact, and concise with formulas."},
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

    out_file = r"E:\POLYDIM_EINSOF\perplexity_cpp_kernel_audit.md"
    try:
        print("Consultando Perplexity Sonar-Pro...")
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Dictamen de Perplexity guardado en {out_file} ({len(content)} bytes)")
            print("--- RESUMEN DEL DICTAMEN ---")
            for line in content.splitlines()[:35]:
                print(line)
    except Exception as e:
        print("Error al consultar Perplexity:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
