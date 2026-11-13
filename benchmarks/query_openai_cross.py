# -*- coding: utf-8 -*-
import urllib.request
import json
import time

key = "os.environ.get("OPENROUTER_API_KEY", "")"
url = "https://openrouter.ai/api/v1/chat/completions"

with open("e:/POLYDIM_EINSOF/benchmarks/run_tribunal_sabios_regla31.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
prompt = re.search(r'PROMPT_TRIBUNAL = """(.*?)"""', text, re.DOTALL).group(1)

payload = {
    "model": "openai/gpt-4o",
    "messages": [
        {"role": "system", "content": "Eres OpenAI GPT-4o (Arbitro de Arquitecturas de Computacion y Sistemas Cuanticos). Rigor analitico y matematico estricto en espanol, cero adulacion."},
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
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8"))
        txt = data["choices"][0]["message"]["content"]
        latency = round((time.perf_counter() - t0)*1000, 1)
        print("OpenAI GPT-4o respondio exitosamente en", latency, "ms!")
        with open("e:/POLYDIM_EINSOF/benchmarks/tribunal_sabios_regla31_resultado.json", "r", encoding="utf-8") as fp:
            res = json.load(fp)
        res["OpenAI (GPT-4o)"] = {"latency_ms": latency, "verdict": txt}
        with open("e:/POLYDIM_EINSOF/benchmarks/tribunal_sabios_regla31_resultado.json", "w", encoding="utf-8") as fp:
            json.dump(res, fp, ensure_ascii=False, indent=2)
        print("Guardado en tribunal_sabios_regla31_resultado.json.")
except Exception as e:
    print("Error OpenAI:", e)
