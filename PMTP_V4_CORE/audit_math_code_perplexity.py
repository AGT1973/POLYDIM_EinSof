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
Act as a Principal Computer Systems and Information Theory Auditor (Doctoral Thesis Committee Level).
Evaluate the following specific technical points submitted for formal dissertation certification:

PART 1: CODE VULNERABILITIES & BUG MITIGATION (PYTHON 3.14 & WIN32)
1. Python 3.14 Windows BufferError mitigation:
   - When using multiprocessing.shared_memory on Windows, holding an active memoryview or ndarray slice over shm.buf raises BufferError: "cannot close exported pointers exist" upon calling shm.close().
   - Mitigation: get_descriptor_header() extracts bytes(self.shm.buf[:128]) (decoupled byte copy of header), and lifecycle cleanly decouples array references before calling close() and unlink().
   - Evaluate: Is this mitigation standard, leak-free, and safe under Win32 FileMapping semantics?
2. F-String LaTeX Escaping:
   - Escaping \\textbf{{0.00 (PMTP)}} inside Python f-strings to avoid NameError: 'PMTP'.

PART 2: MATHEMATICAL FORMULATIONS (GEODESIC DISTORTION & DPI ENTROPY LOSS)
1. Chordal Geodesic Distance Formulation:
   - The naive formula theta = arccos(clip(x · x_rec, -1.0, 1.0)) suffers from catastrophic floating-point cancellation when x · x_rec ≈ 1.0 - O(10^-17), collapsing artificially to 0.0 in double precision.
   - Implemented chordal formulation: theta = 2 * arcsin( ||x - x_rec||_2 / (2 * ||x_rec||_2) ).
   - At D = 1,000,000, 1D REST float formatting (8 digits scientific) yields residual angular distortion theta = 1.641e-9 rad, while PMTP-v4 zero-copy yields theta = 0.000 rad exact.
   - Evaluate: Is this chordal formulation mathematically rigorous, standard in Riemannian geometry/numerical analysis, and numerically stable for S^{D-1}?
2. Data Processing Inequality (DPI) & Shannon Entropy Loss:
   - Floating-point truncation in 1D REST formatting induces MSE_1D ≈ 2.69e-18.
   - Compared against native FP64 precision noise floor eps_mach ≈ 2.22e-16.
   - Formulated mutual information reduction / entropy deficit:
     Delta H_1D = 0.5 * D * log2( MSE_1D / eps_mach^2 ) = 12,851,097 bits lost across D=1,000,000.
   - Contrast with PMTP-v4 SHA-256 bit-exact invariance yielding Delta H_PMTP = 0.000 bits.
   - Evaluate: Assess the theoretical validity and notation of this entropy loss formulation. How should it be phrased in a formal doctoral dissertation (rate-distortion, quantization noise entropy, or continuous differential entropy)?

Provide a rigorous, peer-review critique with actionable mathematical recommendations.
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a rigorous, highly critical mathematician and systems researcher."},
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
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            print("=== PERPLEXITY SONAR-PRO MATH & CODE REVIEW ===")
            print(content)
            with open("perplexity_math_code_audit.md", "w", encoding="utf-8") as out_f:
                out_f.write(content)
            print("\n[Persisted in perplexity_math_code_audit.md]")
    except Exception as e:
        print("Error calling Perplexity API:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
