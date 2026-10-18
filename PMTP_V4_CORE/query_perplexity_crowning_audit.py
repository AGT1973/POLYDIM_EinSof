import psycopg
import urllib.request
import json
import sys
import os

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
Act as an uncompromising, world-class Principal Formal Verification Mathematician, Differential Geometer, and Information Theorist on a Doctoral Dissertation Defense Committee.

Provide an exhaustive, deeply technical, and adversarial SOTA review of the two crowning theoretical contributions of the POLYDIM doctoral thesis, which have been formalized in Lean 4 Core (v4.34.1) without 'sorry' and compiled to object code:

==============================================================================
THEORETICAL ARTIFACTS AND FORMALIZATION UNDER SCRUTINY
==============================================================================

1. THE CLIFFORD SPINOR ISOMETRY THEOREM ON S^{D-1}:
   - Setting: Pseudo-Euclidean space R^{p,q} of dimension D = p + q, with Clifford geometric algebra Cl(p,q) equipped with:
     * Associative geometric product with identity 1.
     * Clifford reversion anti-automorphism (dagger): (AB)† = B† A†, (A†)† = A, 1† = 1.
     * Grade-1 vector property: For every state vector psi in S^{D-1}, psi† = psi (self-reversion of 1-vectors).
     * Rotor group Spin(p,q) in the even subalgebra Cl^0(p,q) satisfying: R R† = 1 and R† R = 1.
     * Grade-0 scalar projection <·>_0 with cyclic rotor trace invariance: <R A R†>_0 = <A>_0 for all rotors R and multivectors A.
     * Canonical Riemannian inner product: <psi, phi> = <psi phi†>_0 = <psi phi>_0.
   - Lean 4 Theorem:
     theorem clifford_spinor_isometry:
       <R psi R†, R phi R†> = <psi, phi>
     Proven via:
       (R phi R†)† = R phi R† (reversion invariance)
       (R psi R†)(R phi R†) = R (psi phi) R† (associative grouping + R† R = 1)
       <R (psi phi) R†>_0 = <psi phi>_0 (scalar rotor invariance).
   - Corollary: Preservation of unit sphere S^{D-1}: <R psi R†, R psi R†> = <psi, psi> = 1.
   - Blade Invariance: For k-blades B_k in /\\^k R^{p,q}, R B_k R† preserves grade k and quadratic norm.

2. THE PMTP DATA PROCESSING INEQUALITY (DPI) & ZERO-LOSS ENTROPY PRESERVATION THEOREM:
   - Setting: Continuous latent activation tensor X in R^D (D >= 1000) on S^{D-1}, target reasoning variable Y with I(X; Y) > 0.
   - Pathway A (1D Tokenized Collapse):
     * Continuous X is quantized/collapsed into a 1D discrete sequence T = tokenizer(X) in V^L.
     * Shannon capacity of discrete token channel: C_token = L * log2(|V|).
     * Differential entropy / representation capacity of continuous isotropic Gaussian/spherical latent space:
       h(X) >= D * (1/2) * log2(2*pi*e) ~ D * 2.047 bits (or D * log2(2*pi*e)).
     * When C_token < I(X; Y) (the Information Bottleneck regime where D >> L), the Markov chain Y -> X -> T enforces:
       I(T; Y) <= C_token < I(X; Y) (Strict information destruction).
     * Entropy deficit: Delta H_collapse = h(X) - C_token >= D * log2(2*pi*e) - O(L * log2(|V|)) > 0.
   - Pathway B (PMTP Zero-Copy Shared-Memory Transit):
     * Direct RAM/VRAM physical mapping via 128-byte capability descriptor (RCU leasing, epoch fences).
     * Deterministic memory bijection / isomorphism: X_pmtp = X.
     * Zero conditional uncertainty: H(X | X_pmtp) = 0.
     * Mutual information preservation: I(X_pmtp; Y) = I(X; Y).
     * Zero discrete entropy destruction: Delta H_pmtp = 0.
     * Strict dominance: I(T; Y) < I(X_pmtp; Y).

==============================================================================
EVALUATION RUBRIC & DEEP QUESTIONS FOR THE AUDIT
==============================================================================

Please address each of the following dimensions with maximum mathematical rigor and doctoral depth:

1. MATHEMATICAL VALIDITY OF CLIFFORD SPINOR ISOMETRY:
   - Is the proof algebraic deduction fully sound and self-contained?
   - What are the differential-geometric implications of rotor sandwich conjugation acting on the tangent spaces of S^{D-1}?
   - Address subtleties of Spin(p,q) vs Pin(p,q), connected components, orientation preservation, and signature independence (e.g. Euclidean p=D, q=0 vs Lorentzian/pseudo-Riemannian).
   - How does this generalize to higher k-blades in Grassmannians Gr(k, D)?

2. INFORMATION-THEORETIC RIGOR OF THE PMTP DPI CONSERVATION THEOREM:
   - Critically evaluate the transition between differential entropy h(X) (which is continuous and coordinate-dependent) and discrete Shannon entropy H(T) / channel capacity C_token.
   - Is the entropy deficit Delta H >= D log2(2 pi e) - O(L log |V|) dissertation-grade? Under what precise measure-theoretic and rate-distortion formulations is this bound exact?
   - Does Cover & Thomas Theorem 2.8.1 (DPI) formally guarantee strict inequality I(T; Y) < I(X; Y) whenever the support cardinality / rate-distortion capacity of T is strictly less than the entropy/information content of X?
   - How does epsilon-net covering of S^{D-1} (requiring (1/epsilon)^D points) reinforce the curse of dimensionality against 1D discrete tokenization?

3. COMPARATIVE ARCHITECTURAL SCRUTINY (PMTP VS SOTA):
   - In physical systems, does zero-copy shared memory truly deliver Delta H = 0? Address page faults, NUMA migration, IEEE 754 bit-preservation, and cache coherency.
   - Compare the mathematical formulation of PMTP's descriptor against Apache Arrow Plasma, Ray object store, and CUDA IPC handles.

4. LEAN 4 FORMALIZATION RIGOR (CORE VS MATHLIB):
   - Assess the decision to formalize in Lean 4 Core using an axiomatic algebraic structure (typeclass/structure contract) vs developing the full manifold theory in Mathlib.
   - Does compiling the Lean 4 proof to C and machine object code (.o) with Exit Code 0 provide verified extraction, or what are the exact verification guarantees provided by the Lean kernel in this mode?

5. SUMMARY RED-TEAM VERDICT:
   - Formal doctoral committee assessment: Strengths, potential objections, required caveats in thesis defense, and definitive academic verdict.
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a world-class Principal Formal Verification Mathematician, Differential Geometer, and Information Theory Professor on a doctoral dissertation committee. Be uncompromising, deeply analytical, and mathematically precise."},
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

    out_file = r"E:\POLYDIM_EINSOF\PMTP_V4_CORE\perplexity_crowning_theorems_audit.md"
    try:
        print("Calling Perplexity API (model: sonar-pro)...")
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            print("=== PERPLEXITY SONAR-PRO EVALUATION RECEIVED ===")
            with open(out_file, "w", encoding="utf-8") as out_f:
                out_f.write(content)
            print(f"Persisted in {out_file} ({len(content)} characters)")
            print("\nPreview of evaluation:\n")
            lines = content.splitlines()
            for line in lines[:40]:
                print(line)
            if len(lines) > 40:
                print("... [Full text saved to markdown file] ...")
    except Exception as e:
        print("Error calling Perplexity API:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
