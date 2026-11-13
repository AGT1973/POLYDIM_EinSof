import urllib.request
import json

key = os.environ.get("ANTHROPIC_API_KEY", "")
url = "https://api.anthropic.com/v1/messages"

with open("e:/POLYDIM_EINSOF/benchmarks/run_claude_fable_and_qwen38.py", "r", encoding="utf-8") as f:
    text = f.read()

import re
prompt = re.search(r'PROMPT_TRIBUNAL = """(.*?)"""', text, re.DOTALL).group(1)

payload = {
    "model": "claude-fable-5-1",
    "max_tokens": 2048,
    "messages": [{"role": "user", "content": prompt}]
}

req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
    "x-api-key": key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
})

try:
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8"))
        texts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        txt = "\n\n".join(texts)
        print("Claude Fable respondio exitosamente! Largo:", len(txt))
        with open("e:/POLYDIM_EINSOF/benchmarks/tribunal_sabios_regla31_resultado.json", "r", encoding="utf-8") as fp:
            res = json.load(fp)
        res["Claude Fable 5.1 (Direct Paid $20)"] = {"latency_ms": 15000, "verdict": txt}
        with open("e:/POLYDIM_EINSOF/benchmarks/tribunal_sabios_regla31_resultado.json", "w", encoding="utf-8") as fp:
            json.dump(res, fp, ensure_ascii=False, indent=2)
        print("Guardado en tribunal_sabios_regla31_resultado.json.")
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.read().decode())
