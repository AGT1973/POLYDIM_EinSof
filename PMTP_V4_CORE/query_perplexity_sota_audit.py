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
Act as a Principal Computer Systems Researcher and Information Theory Auditor (Doctoral Committee Level).
Critically evaluate the following empirical claim and findings from a systems research paper:

FINDINGS UNDER SCRUTINY:
1. 1D Serialization Bottleneck:
   - Textual serialization (json.dumps / json.loads or REST tokens) for high-dimensional latent states x in S^{D-1} scales strictly as O(D).
   - At D = 1,000,000 (FP64, 8 MB physical payload), serialization and parsing requires ~2,942.54 ms (~3 seconds) on bare-metal silicon, expanding volume by ~1.94x.
   - Textual truncation/quantization induces irreversible entropy loss Delta H = H(x) - I(x; x_rec) > 0 (Data Processing Inequality) and non-zero geodesic distortion theta(x, x_rec) > 0.
2. Temporal Invariance in PMTP-v4 (Zero-Copy Shared Memory IPC):
   - By transferring a 128-byte canonical wire descriptor and acquiring an OS shared memory lease (Win32 / POSIX shm / RCU acquire-release), latency is bounded by the 128-byte header exchange: 208.40 microseconds at D = 1,000,000.
   - Bit-exact preservation: Pre- and post-transmission SHA-256 hashes match identically (Delta H = 0.000 bits, theta = 0.000 rad).
3. Empirical Speedup:
   - Measured silicon speedup: 14,120x at D = 1,000,000.

EVALUATION RUBRIC:
1. Systems Architecture: Compare against Apache Arrow Plasma store, Ray Object Store, FlatBuffers, Protobuf, POSIX shm, and CUDA IPC. Is the 128-byte descriptor paradigm standard or superior?
2. Complexity Analysis: Contrast O(D) textual memory allocations/string formatting against O(1) pointer-passing / RCU leasing.
3. Information-Theoretic Validity: Does the collapse to 1D textual tokens violate the Data Processing Inequality (DPI)? Is Delta H = 0.000 bits in PMTP mathematically and physically sound?
4. Counterarguments & Edge Cases: Address page table faults (first-touch overhead), TLB misses, cache line invalidation, and whether zero-copy IPC assumes homogeneous memory space.
5. Final Verdict: Formal academic assessment of the 14,120x speedup claim for inclusion in a doctoral dissertation.
"""

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are an uncompromising, highly technical reviewer in computer systems and information theory."},
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
            print("=== PERPLEXITY SONAR-PRO EVALUATION ===")
            print(content)
            with open("perplexity_dpi_sota_review.md", "w", encoding="utf-8") as out_f:
                out_f.write(content)
            print("\n[Persisted in perplexity_dpi_sota_review.md]")
    except Exception as e:
        print("Error calling Perplexity API:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
