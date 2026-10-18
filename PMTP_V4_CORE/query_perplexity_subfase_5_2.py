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
Act as an uncompromising Doctoral Committee Examiner in Differential Geometry, Riemannian Optimization, and Computer Arithmetic / Formal Methods (Lean 4).

Critically evaluate and provide formal rigorous arbitration for the following 3 mathematical formulations for inclusion in a PhD thesis and Lean 4 formalization:

1. GRASSMANN MANIFOLD Gr(K, D) QUOTIENT SPACE & CHORDAL PROJECTION METRIC:
   - Manifold: Gr(K, D) = St(K, D) / O(K) where St(K, D) = { X in R^{D x K} | X^T X = I_K }.
   - Subspace projector: P_X = X X^T in R^{D x D} (for orthonormal X).
   - Canonical chordal projection metric between subspaces span(X) and span(Y):
     d_c(X, Y) = (1 / sqrt(2)) * || X X^T - Y Y^T ||_F = sqrt( sum_{i=1}^K sin^2(theta_i) ) = sqrt( K - ||X^T Y||_F^2 ).
   - Question: Is this formulation standard, mathematically exact, gauge-invariant under right O(K) action, and consistent for constructive Lean 4 formalization?

2. THEOREM 683 / CAYLEY-SMW RETRACTION ASYMPTOTIC CONVERGENCE:
   - For X in St(D, K) and tangent vector Z in T_X St(D, K), with skew-symmetric generator W(t) = t (P Z X^T - X Z^T P) where P = I - 0.5 X X^T:
   - Cayley retraction trajectory R_X(t Z) = (I - 0.5 W(t))^{-1} (I + 0.5 W(t)) X.
   - Using Sherman-Morrison-Woodbury / low-rank structure W = U V^T with rank r <= 2K:
     lim_{t -> infinity} R_X(t Z) = (2 P_{ker(A)} - I) X
     where P_{ker(A)} is the orthogonal projection onto ker(A) (or generalized Cayley reflector on the complement of range(A)).
   - Question: How does this asymptotic limit ensure numerical stability compared to naive Woodbury inversion when t -> infty, and what is the exact algebraic property of the limit operator (2 P_{ker} - I) being an orthogonal Householder-like involution / reflection preserving isometry?

3. LEMMA 1.2 / KULISCH ACCUMULATOR 4,288-BIT BOUND FOR IEEE-754 BINARY64:
   - For finite binary64 floating-point sequence x_i, y_i with N <= 2^64:
     * Minimum subnormal exponent = -1074 (-1022 - 52)
     * Maximum finite exponent = +1023
     * Product of two binary64 has exponent range from 2 * (-1074) = -2148 up to 2 * 1024 = 2048, or for normalized/finite products:
     * Exponent span: (1022 + 1023) = 2045, or subnormal to max finite: (-1074 to +1024)
     * Kulisch bound derivation: W_min = (1022 + 1023) + 106 + 64 + 1 = 4,258 bits.
     * Word alignment: ceil(4258 / 64) * 64 = 67 words = 4,288 bits.
   - Question: Validate the arithmetic proof that 4,288 bits strictly precludes intermediate arithmetic overflow and underflow for exact dot products up to N = 2^64 terms.

Provide formal validation, necessary corrections or nuances, and concrete mathematical lemmas ready for Lean 4 formal verification.
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are an uncompromising, world-class expert in Riemannian geometry, numerical linear algebra, and formal interactive theorem proving (Lean 4)."},
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

    print("Despachando consulta de auditoría matemática SOTA a Perplexity Sonar-Pro...")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            print("\n=== RESPUESTA PERPLEXITY SONAR-PRO ===\n")
            print(content)
            
            with open("E:/POLYDIM_EINSOF/PMTP_V4_CORE/perplexity_subfase_5_2_audit.md", "w", encoding="utf-8") as f:
                f.write("# AUDITORÍA PERPLEXITY SONAR-PRO: SUBFASE 5.2 (LEAN 4 FORMAL VERIFICATION)\n\n")
                f.write(content)
            print("\nAudit guardada en E:/POLYDIM_EINSOF/PMTP_V4_CORE/perplexity_subfase_5_2_audit.md")
    except Exception as e:
        print(f"Error al consultar Perplexity: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
