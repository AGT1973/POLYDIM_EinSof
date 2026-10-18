"""
TEST CONTROLADO: 10 LLAMADAS A SERVIDORES NVIDIA NIM (DGX H100)
Consumo: 100% Free Tier (Pool de claves en E:/Antigravity_multyMCP_Rust/.env)
Gasto Económico de Ariel: $0.00
Evalúa latencia RTT y formato de portador Protocolo Helena.
"""

import os
import time
import json
import urllib.request
from polydim.transport.helena_carrier import HelenaCarrier
import numpy as np

def load_nvidia_keys(env_path="E:/Antigravity_multyMCP_Rust/.env"):
    keys = []
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("NVIDIA_API_KEY_"):
                parts = line.split("=", 1)
                if len(parts) == 2:
                    k = parts[1].strip().strip('"').strip("'")
                    if k:
                        keys.append(k)
    return keys

def run_10_nvidia_calls():
    keys = load_nvidia_keys()
    print(f"Total de claves gratuitas de NVIDIA NIM detectadas: {len(keys)}")
    if not keys:
        print("ERROR: No se encontraron claves de NVIDIA NIM.")
        return

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    model_name = "mistralai/mistral-7b-instruct-v0.3"
    
    # Generar vector canónico de prueba D=4096
    rng = np.random.default_rng(2026)
    v = rng.standard_normal(4096)
    v = v / np.linalg.norm(v)
    carrier_text = HelenaCarrier.pack_4bit(v, slab_id="aladin_nvidia_probe")

    print("\n" + "=" * 75)
    print("EJECUTANDO 10 LLAMADAS ROTATIVAS A NVIDIA NIM (FREE TIER $0.00)")
    print("=" * 75)
    print(f"{'Llamada':<8} | {'Key Index':<10} | {'Modelo':<25} | {'RTT (ms)':<10} | {'Status':<10}")
    print("-" * 75)

    results = []
    for i in range(10):
        key_idx = i % len(keys)
        key = keys[key_idx]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Ping de silicio para vector POLYDIM Helena Carrier.\n"
                        f"{carrier_text}\n"
                        f"Responde estrictamente con una sola linea: 'HELENA_ACK_CHALLENGE_{i+1}'"
                    )
                }
            ],
            "max_tokens": 15,
            "temperature": 0.0
        }
        
        t0 = time.perf_counter()
        status_str = "FAIL"
        rtt_ms = 0.0
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                t1 = time.perf_counter()
                rtt_ms = (t1 - t0) * 1000.0
                reply = data["choices"][0]["message"]["content"].strip()
                status_str = f"OK ({reply[:16]})"
        except Exception as e:
            t1 = time.perf_counter()
            rtt_ms = (t1 - t0) * 1000.0
            status_str = f"ERR: {str(e)[:15]}"

        print(f"#{i+1:<7} | Key #{key_idx+1:<8} | {model_name:<25} | {rtt_ms:<10.2f} | {status_str:<10}")
        results.append({"call": i+1, "rtt_ms": rtt_ms, "status": status_str})
        time.sleep(0.3)

    print("=" * 75)
    successes = sum(1 for r in results if "OK" in r["status"])
    avg_rtt = sum(r["rtt_ms"] for r in results if "OK" in r["status"]) / max(1, successes)
    print(f"Resumen: {successes}/10 llamadas exitosas | RTT Promedio: {avg_rtt:.2f} ms")
    print("Costo Total para Ariel: $0.00 USD (Consumido 100% de cuota de bienvenida NVIDIA)")
    print("=" * 75)

if __name__ == "__main__":
    run_10_nvidia_calls()
