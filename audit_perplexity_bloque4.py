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
Act as an uncompromising Principal Numerical Verification Architect and Lead High-Performance Systems Engineer.

Review and mathematically validate the remediation architecture for four critical flaws in a 1,571-theorem verification suite (POLYDIM V26250, high-dimensional manifolds S^{D-1} and St(D,K), C++20/Rust/PMTP):

1. TEST RUNNER BOOLEAN TRAP & CONFORMANCE CONTRACT (T-01):
   - Flaw: The runner implemented `code = 0 if ret in (0, None) else int(ret)`. In Python, `isinstance(False, int)` is True and `False == 0` evaluates to True. Any test returning `False` was recorded as `Exit Code: 0` (PASS).
   - Solution: Strict fail-closed dispatch:
     ```python
     if ret is False:
         code = 1
     elif ret is True or ret == 0 or ret is None:
         code = 0
     else:
         code = int(ret)
     ```
   - Validation question: Is this dispatch fully fail-closed, and how should unexpected exceptions and non-zero return codes be propagated in safety-critical automated theorem suites?

2. DECOUPLING TAUTOLOGICAL MOCKS INTO REAL SILICON ORACLES (T-02, T-03, T-05):
   - Flaw: Over 1,100 theorems fell back to `norm(np.linspace(-1, 1, 1000)) == 18.2757`, bypassing native C++ and Rust libraries entirely and recording static mocked constants in execution logs.
   - Solution: Architecture of a centralized multi-family silicon oracle dispatch:
     * Stiefel & retractions -> Call C++20 `polydim_sphere_transport_v26155` and Orchestrator `retract_stiefel`, validating ||X^T X - I|| < 1e-12.
     * Compensated summation & denormals -> Call C++20 `polydim_sphere_project_v26155` with denormal floats (1e-305).
     * Clifford algebra -> Spin(D) rotor unitarity ||R||^2 = 1.0 in Cl(p, q).
     * Lanczos Jackson damping -> Tridiagonalization with Jackson kernel on simplicial Hodge Laplacian.
     * Matrix Martingales -> Freedman concentration bound P[||S_n|| >= t, V_n <= v] <= 2D exp(-t^2 / (2(v + Rt/3))).
     * Poincaré / Lorentz hyperbolic embeddings -> Isometry check from Poincaré ball to Lorentzian hyperboloid <x, x>_L = -1 (fixing Th 344).
   - Validation question: Does this multi-family oracle design provide rigorous empirical falsifiability across high-dimensional geometric invariants without tautological mock fallbacks?

3. SUBSTRING ROUTING COLLISION (T-04):
   - Flaw: Substring check `any(k in topic_lower for k in [..., "rust"])` matched Spanish words like "incrustación" (Th 344), incorrectly routing hyperbolic manifold theorems to FFI Rust buffer alignment checks.
   - Solution: Replace substring containment with word-boundary regex `r"\\brust\\b"` or exact keyword matching.

4. METHODOLOGICAL FORMULATION IN THEOREMS 1664 AND 1665 (T-06):
   - Flaw in Th 1664: Tested `n_naive * 18.7 = 1870` instead of the specified cluster clinical trial formula:
     DEFF = 1 + (m - 1)*rho = 18.7 (m=60, rho=0.3).
     n_individual = ceil((sigma_d^2 / delta_NI^2) * (z_{alpha/2} + z_beta)^2) = 238.
     n_clusters = ceil((238 * 18.7) / 60) = 75 clusters per arm.
     Intersection-Union Principle (IUR) for co-endpoints.
   - Flaw in Th 1665: Tested trivial dict lookup instead of BLAKE3 21-level chunk tree hashing, monotonic sequence counter journal G_n > G_last with atomic fsync, and replay bound P[replay] <= 2^{-128} + q^2 / 2^{128}.
   - Validation question: Validate the mathematical formulas and operational verification steps for Th 1664 and Th 1665.

Provide a concise, doctoral-level verification verdict with explicit formulas and numerical bounds.
"""

    payload = json.dumps({
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a world-class Principal Systems Architect and Numerical Verification Analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.perplexity.ai/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            answer = res_data["choices"][0]["message"]["content"]
            print("=== PERPLEXITY SONAR-PRO AUDIT REPORT ===")
            print(answer)
            with open("perplexity_bloque4_audit.md", "w", encoding="utf-8") as out_f:
                out_f.write(answer)
            print("Report saved to perplexity_bloque4_audit.md")
    except Exception as e:
        print(f"Error querying Perplexity API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
