import sys
import os
import requests
import json

sys.path.append(r'E:\Mantenimiento')
import agent_vault_pg

prompt_sabios = """You are an elite Theoretical Computer Scientist and Information Theorist specializing in Shannon Theory, High-Dimensional Geometry, and Transformer Complexity.

Context:
A researcher formulated the following hypothesis:
"According to the Data Processing Inequality (DPI), in any Markov chain X -> H -> T -> Y (where X is input, H is continuous high-dimensional latent space, T is 1D discrete text token sequence, and Y is downstream task), I(X; T) <= I(X; H). Therefore, intermediate text/tokens strictly destroy mutual information, proving that text scratchpads/tokens are unnecessary and intermediate cognition should happen entirely in continuous high-dimensional vector spaces (e.g. S^{D-1} via shared memory / continuous latent streams)."

GPT and DeepSeek reviewed this claim and scored it 3/10 as a scientific thesis, stating:
"The logical jump from the Data Processing Inequality (DPI) to 'intermediate text is not necessary' is formally invalid and does not hold."

Your Task:
1. Formally dissect why the naive DPI deduction fails (the 30% that was flawed: e.g. computational complexity, Chain-of-Thought as an external Turing-tape / dynamical system expanding effective depth, conditioning vs lossy projection, noise decoupling/regularization).
2. Detail the exact 70% missing theoretical foundations required to make a valid, rigorous, PhD-level mathematical thesis out of the critique of 1D discretization:
   - When does 1D discretization provably cause catastrophic capacity bottlenecks? (Rate-Distortion Theory, metric entropy, Kolmogorov epsilon-capacity in D >= 10^4).
   - Manifold topology & topological obstructions: embedding S^{D-1} or high-rank Grassmannian/Stiefel manifolds into 1D discrete token chains without topological tearing or distortion.
   - Computational capacity vs Information Capacity: compare continuous internal recurrent scratchpads (PMTP / Modern Hopfield / continuous vector streaming) vs discrete autoregressive token scratchpads in terms of sample complexity, runtime latency, and representational bounds.
   - Exact mathematical conditions under which direct continuous vector streaming strictly dominates autoregressive discrete tokenization.

Be rigorous, technical, mathematical, and unsparing. No shallow analogies."""

def call_cerebras():
    key = agent_vault_pg.get_vault_value('cerebras_api_key', 'api_key')
    if not key:
        return "Cerebras key missing"
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3.1-70b",
        "messages": [
            {"role": "system", "content": "You are a world-class theoretical computer scientist and information theorist."},
            {"role": "user", "content": prompt_sabios}
        ],
        "temperature": 0.2,
        "max_tokens": 3000
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            return f"Cerebras error {r.status_code}: {r.text}"
    except Exception as e:
        return f"Cerebras exception: {e}"

def call_kimi():
    key = agent_vault_pg.get_vault_value('Kimi_Moonshot_Paga', 'api_key')
    if not key:
        return "Kimi key missing"
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "moonshot-v1-32k",
        "messages": [
            {"role": "system", "content": "You are a world-class theoretical computer scientist and information theorist."},
            {"role": "user", "content": prompt_sabios}
        ],
        "temperature": 0.2,
        "max_tokens": 3000
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            return f"Kimi error {r.status_code}: {r.text}"
    except Exception as e:
        return f"Kimi exception: {e}"

if __name__ == "__main__":
    print("--- CALLING CEREBRAS ---")
    c_out = call_cerebras()
    with open(r"E:\POLYDIM_EINSOF\sabios_cerebras_critique.txt", "w", encoding="utf-8") as f:
        f.write(c_out)
    print("Cerebras saved. Length:", len(c_out))
    
    print("--- CALLING KIMI ---")
    k_out = call_kimi()
    with open(r"E:\POLYDIM_EINSOF\sabios_kimi_critique.txt", "w", encoding="utf-8") as f:
        f.write(k_out)
    print("Kimi saved. Length:", len(k_out))
