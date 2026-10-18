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

    prompt = """
Act as a world-class Research Mathematician, Numerical Analyst, and Formal Verification Architect (Lean 4, IEEE-754 arithmetic, Stiefel & Grassmann geometry).

In our previous audit, two mathematical problems were identified in our formulations:
Problem 1: The alleged asymptotic limit lim_{t -> infty} R_X(tZ) = (2 P_{ker(A)} - I) X for the standard Cayley retraction R_X(tZ) = (I - 0.5 t A)^{-1} (I + 0.5 t A) X fails because the eigenvalues of (I - 0.5 t A)^{-1}(I + 0.5 t A) on the range of A are (1 + 0.5 i t lambda) / (1 - 0.5 i t lambda) = exp(2 i arctan(0.5 t lambda)) -> -1 as t -> infty! 
Wait: does exp(2 i arctan(0.5 t lambda)) converge to -1 as t -> +infty?
Because arctan(x) -> pi/2 as x -> +infty, 2 arctan(0.5 t lambda) -> pi (if lambda > 0) or -pi (if lambda < 0), and exp(i pi) = -1!
Wait, let's examine: On range(A), do the eigenvalues actually converge to -1 as t -> +infty, while on ker(A) they are identically +1?
If on ker(A) the eigenvalues are +1, and on range(A) the eigenvalues converge to -1 as t -> +infty, then the operator limit would be:
lim_{t -> +infty} (I - 0.5 t A)^{-1}(I + 0.5 t A) = P_{ker(A)} - P_{range(A)} = P_{ker(A)} - (I - P_{ker(A)}) = 2 P_{ker(A)} - I !
Did the previous reviewer make a mistake by claiming it oscillates like a periodic rotation, or does (I - 0.5 t A)^{-1}(I + 0.5 t A) actually have a real limit as t -> +infty?!

Please rigorously analyze:
1. PROBLEM 1 RE-EXAMINATION (CAYLEY ASYMPTOTIC CONVERGENCE):
   - For a real skew-symmetric matrix A with purely imaginary eigenvalues +/- i lambda_k (lambda_k > 0):
     Evaluate the scalar rational Cayley transform c(t) = (1 + 0.5 i t lambda_k) / (1 - 0.5 i t lambda_k).
     What is lim_{t -> +infty} c(t)? Is it not (-1)?
     Is there an oscillation, or is it a monotonic phase progression from 0 to pi?
     Does the matrix limit lim_{t -> +infty} (I - 0.5 t A)^{-1} (I + 0.5 t A) exist and equal 2 P_{ker(A)} - I ?
     If so, why did the previous reviewer claim it oscillates? (Did they confuse exp(t A) with the Cayley rational transform (I - 0.5 t A)^{-1}(I + 0.5 t A)?).
     Give the definitive theorem, conditions, and formal proof.
   - What are the robust numerical alternatives for large t (e.g. Polar QR retraction, Householder reflection, Cayley-Padé, or projective retraction) that avoid Sherman-Morrison-Woodbury cancellation at large t?

2. PROBLEM 2 RESOLUTION (KULISCH ACCUMULATOR 4,288 BITS):
   - Provide the definitive, mathematically watertight derivation of the exact Kulisch accumulator bit-width for IEEE-754 binary64 products up to N = 2^64 terms.
   - Clearly delineate:
     * Exponent range of single binary64 (min subnormal, min normal, max normal)
     * Exact exponent range and significand size of the product of two binary64 numbers
     * The fixed-point register format (Kulisch superaccumulator): exact number of integer bits, fraction bits, and guard bits for N = 2^64
     * How the 4,288 bits (or 4,261 / 4,258 / 4,224 bits) is rigorously computed down to the single bit.
     * State the exact theorem and lemma ready for Lean 4.

Provide an uncompromising, mathematically precise arbitration.
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a world-leading mathematician, numerical analyst, and IEEE-754 arithmetic expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.05
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

    print("Despachando consulta de contra-auditoría matemática SOTA a Perplexity Sonar-Pro...")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            print("\n=== RESPUESTA PERPLEXITY SONAR-PRO ===\n")
            print(content)
            
            with open("E:/POLYDIM_EINSOF/PMTP_V4_CORE/perplexity_subfase_5_2_counter_audit.md", "w", encoding="utf-8") as f:
                f.write("# CONTRA-AUDITORÍA PERPLEXITY SONAR-PRO: RESOLUCIÓN DEFINITIVA CAYLEY & KULISCH\n\n")
                f.write(content)
            print("\nAudit guardada en E:/POLYDIM_EINSOF/PMTP_V4_CORE/perplexity_subfase_5_2_counter_audit.md")
    except Exception as e:
        print(f"Error al consultar Perplexity: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
