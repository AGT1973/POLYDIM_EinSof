# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import re

key = "os.environ.get("OPENROUTER_API_KEY", "")"
url = "https://openrouter.ai/api/v1/chat/completions"

with open("e:/POLYDIM_EINSOF/benchmarks/run_tribunal_sabios_regla31.py", "r", encoding="utf-8") as f:
    text = f.read()

prompt = re.search(r'PROMPT_TRIBUNAL = """(.*?)"""', text, re.DOTALL).group(1)

payload = {
    "model": "qwen/qwen-2.5-72b-instruct",
    "messages": [
        {"role": "system", "content": "Eres Qwen 2.5 72B / Qwen 3.8 (Arquitecto de Microarquitectura de Silicio y Aceleradores Cuanticos/Neuronales de Alibaba Tongyi). Rigor analitico y matematico en espanol, cero adulacion."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.1,
    "max_tokens": 2500
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
})

try:
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        latency = round((time.perf_counter() - t0)*1000, 1)
        print(f"Qwen respondio exitosamente en {latency} ms!")
        
        with open("e:/POLYDIM_EINSOF/benchmarks/tribunal_sabios_regla31_resultado.json", "r", encoding="utf-8") as f:
            res = json.load(f)
        res["Qwen (qwen-2.5-72b-instruct)"] = {"latency_ms": latency, "verdict": content}
        with open("e:/POLYDIM_EINSOF/benchmarks/tribunal_sabios_regla31_resultado.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print("Actualizado tribunal_sabios_regla31_resultado.json con Qwen 2.5 72B.")
except Exception as e:
    print("Error OpenRouter Qwen:", e)
