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
Act as a Principal Theoretical Computer Scientist, Quantum Information Theorist, and Distributed HPC Architect.

Review and mathematically validate the formal specifications and design remediations for the four open frontier problems of POLYDIM V26250 (Bloque 5):

1. FORMAL MECHANIZED VERIFICATION (F-01 - Lean 4 Mathlib):
   - Scope: Mechanizing the fundamental lemmas of the Stiefel manifold St(D,K) retraction and the Kulisch exact accumulator bound in Lean 4.
   - Core specifications:
     * Stiefel retraction lemma: For X in St(D,K) and tangent Z in T_X St(D,K), the Cayley-Padé map R_X(Z) satisfies R_X(Z)^T R_X(Z) = I_K.
     * Kulisch bound lemma: W_min = 2*(e_max - e_min) + 2*p + ceil(log2(N)) ensures zero rounding error prior to final rounding.
   - Question: What is the minimal, sound formalization signature in Lean 4 mathlib for these two theorems?

2. CROSS-NODE RDMA PMTP TENSOR BUS (F-02):
   - Scope: Extending single-node shared memory (PMTP v3) across nodes via InfiniBand / RoCE v2 without falling back to tokenized 1D serialization.
   - Core design:
     * One-sided RDMA Read/Write directly into remote registered memory regions (MR).
     * Distributed Epoch Fencing using atomic 64-bit compare-and-swap (CAS) on remote epoch counters (RC Queue Pairs).
     * Zero-copy wire descriptors (120 bytes) exchanged via lightweight out-of-band channel.
   - Question: Does one-sided RDMA CAS epoch fencing guarantee linearizable read-leases across cluster nodes without host CPU IPC bottlenecks?

3. ACCELERATOR-NATIVE RESIDENCE & ZERO-CPU LEASES (F-03):
   - Scope: GPU HBM/SRAM native leases using CUDA Driver Virtual Memory Management (cuMem API) without CPU round-trip synchronization.
   - Core design:
     * Physical GPU allocations via cuMemCreate with CU_MEM_HANDLE_TYPE_POSIX_FILE_DESCRIPTOR or WIN32_HANDLE.
     * Inter-GPU P2P direct mapping (NVLink / PCIe) via cuMemMap / cuMemSetAccess.
     * GPU-resident atomic epoch counters in Device Memory.
   - Question: What are the exact CUDA Driver APIs and memory coherence semantics required for host-free GPU IPC leases?

4. CLIFFORD QUANTUM SCALING (F-04 - Ross-Selinger QPU Mapping):
   - Scope: Transpiling Cl(3,0) / Cl(p,q) spinor rotors R = cos(theta/2) - sin(theta/2) e_ij into single-qubit quantum circuits over the universal Clifford+T gate set {H, S, T}.
   - Core design:
     * Exact grid problems over Z[1/sqrt(2), i] to approximate R_z(theta) with T-count O(log(1/eps)) using Ross-Selinger algorithm.
     * OpenQASM 2.0 representation and circuit fidelity check F = |<psi|U|psi>|^2 >= 1 - eps.
   - Question: Validate the Ross-Selinger T-count complexity and QASM mapping for high-dimensional Clifford rotor decomposition.

Provide a concise, doctoral-level verification verdict with explicit Lean 4 type signatures, CUDA API sequences, and QASM representations.
"""

    payload = json.dumps({
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a world-class Principal Systems Architect and Quantum/Formal Verification Analyst."},
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
            print("=== PERPLEXITY SONAR-PRO BLOQUE 5 VERDICT ===")
            print(answer)
            with open("perplexity_bloque5_audit.md", "w", encoding="utf-8") as out_f:
                out_f.write(answer)
            print("Saved to perplexity_bloque5_audit.md")
    except Exception as e:
        print(f"Error querying Perplexity API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
