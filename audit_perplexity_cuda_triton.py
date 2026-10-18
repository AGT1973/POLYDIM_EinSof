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
Act as a Principal GPU Systems Architect and Differential Geometer on Stiefel Manifolds.

We are auditing and hardening two GPU kernels for St(D, K) manifold operations (D up to 10^7, K <= 64):

1. CUDA C++20 STIEFEL CAYLEY ORCHESTRATION & WOODBURY SOLVE:
   - Setting: X in St(D, K) with X^T X = I_K. Tangent direction Z with X^T Z + Z^T X = 0.
   - Cayley Retraction: R_X(tau Z) = (I - (tau/2) A)^(-1) (I + (tau/2) A) X where A = Z X^T - X Z^T.
   - Low-Rank SMW Formulation: Let U = [Z, X] in R^(D x 2K), V = [X, -Z] in R^(D x 2K) such that A = U V^T.
     Show the exact 2K x 2K Woodbury linear system:
     (I_{2K} - (tau/2) V^T U) W = V^T X
     R_X(tau Z) = X + (tau/2) U W.
   - Memory & FFI Contract:
     * To adhere to a Monolithic Memory Pool (zero dynamic cudaMalloc), what is the exact workspace size for:
       V^T U (2K x 2K), V^T X (2K x K), LU decomposition (cusolverDnDgetrf / dgetrs or cuBLAS batched LU)?
     * Why did the previous Lyapunov formulation fail when assuming positive eigenvalues in k_lyapunov_elemwise_solve (denom > 1e-15)?
     * Provide the exact mathematically certified orchestration flow using cuBLAS (gemm) and cuSOLVER.

2. TRITON GPU KERNEL DETERMINISM & OOB SAFETY:
   - Setting: High-dimensional inner products and projections in Triton.
   - Non-determinism: Why does tl.atomic_add across thread blocks destroy IEEE-754 bit-exact reproducibility, and how is it replaced by a 2-pass hierarchical block reduction (tl.sum + inter-block reduction)?
   - Boundary Masking: How must SRAM Tiling enforce `mask = offs < N` in `tl.load` and `tl.store` when dimension D is not a multiple of BLOCK_SIZE?

Provide rigorous mathematical derivations, complexity bounds O(D K^2 + K^3), and exact C++/CUDA and Triton signatures.
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a Principal GPU Systems Architect and Differential Geometer. Provide rigorous formulas, complexity, and exact code contracts."},
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

    out_file = r"E:\POLYDIM_EINSOF\perplexity_cuda_triton_audit.md"
    try:
        print("Consultando Perplexity Sonar-Pro para CUDA y Triton...")
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Dictamen de Perplexity guardado en {out_file} ({len(content)} bytes)")
    except Exception as e:
        print("Error al consultar Perplexity:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
