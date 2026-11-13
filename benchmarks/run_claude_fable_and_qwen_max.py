# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF: EVALUACION DIRECTA CON CLAUDE FABLE 5.1 (DIRECT PAYG $20 USD) Y QWEN 3.8 MAX
"""
import sys
import json
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(line_buffering=True)

CLAUDE_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ALIBABA_PRO_KEY = "sk-ws-H.DIIEMYY.Cu2k.MEYCIQDMymHibLJM4QSrt2NldWLw-NEeTXL3HkP7SqEJx1E4-wIhALTPFAZs1i_F7bs4kJTJy9qadHCQ7MnFtj3hnncr7--w"
ALIBABA_ENDPOINT = "https://ws-t85fm4y7sz8vxo9t.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
OPENROUTER_KEY = "os.environ.get("OPENROUTER_API_KEY", "")"

PROMPT_TRIBUNAL = """[AUDITORIA ADVERSARIAL SOTA: ARQUITECTURA EINSOF, REGLA 31 Y MATEMATICA DE PUERTA ADENTRO]

Contexto y Tesis de Ariel Garcia Traba (EinsofOS / POLYDIM):
1. "Yo no estoy inventando nada nuevo. Estoy metiendo la mejor matematica en vectores dentro del mismo micro / memoria cuantica. Hoy lo que se usa se calcula DE LA PUERTA PARA AFUERA: se leen 100,000 salidas/shots clasicos y afuera se aplican las estadisticas, modas y filtros. Yo lo quiero DE LA PUERTA PARA ADENTRO: que se apliquen esos mismos calculos antes de la salida en los Turings internos del micro/QPU, y cuando salga por la puerta ya esten todos los filtros hechos y salga exactamente 1 sola salida vectorial consolidada."
2. "Regla 31 (Contrato de Silicio): Se pregunta al hardware. Si es CPU trabajo en AVX con estadistica de orden; si es TPU trabajo en JAX/MXU sistolico sin condicionales; si es QPU manejo los datos de forma nativa cuantica, NO como si fuera silicio digital clasico."
   - Error previo detectado: Forzar compuertas booleanas Toffoli (CCX) dentro del QPU para hacer comparaciones aritmeticas destruyo la coherencia (descomposicion en 6 CZ por Toffoli) limitando la fidelidad al 75%.
   - Formulacion Nativa QPU: El QPU opera nativamente por rotaciones continuas de fase SU(2)^{\\otimes D} (R_z, S_x, R_y) y su funcion matematica de salida nativa es el Vector de Expectacion de Pauli:
     \\vec{z}_{QPU} = (\\langle \\hat{Z}_0 \\rangle, \\langle \\hat{Z}_1 \\rangle, \\dots, \\langle \\hat{Z}_{D-1} \\rangle) \\in S^{D-1} via Estimator, con 0 compuertas CCX booleanas.
   - Formulacion Nativa TPU: Matriz de Gram y contraccion diferencial sin ramas:
     G = M M^T, \\quad w = \\text{softmax}(\\beta G 1), \\quad z_{TPU} = \\text{Retract}(M^T w)
     100% matmul sistolico en MXU, 0 condicionales 'if', 0 sorts.
   - Formulacion Nativa CPU: Half-Sample Mode (Shorth) en cache L1/L2 + Acumulador compensado de Neumaier (error <= 10^-15).

EVIDENCIA FISICA DE SILICIO OBTENIDA HOY (IBM Quantum 156-qubit Heron/Eagle `ibm_fez`, Job dbkiq01kdqps7392i1q0):
- Salidas que cruzan la puerta: 1 solo vector continuo en S^{D-1} (reduccion 99.999% de trafico).
- Compuertas booleanas CCX usadas: 0.
- Fidelidad de coseno continua en silicio real: 99.8575% (0.998575).
- Deriva ortonormal Neumaier: 0.0.
- Paridad matematica CPU vs TPU vs QPU: fidelidades > 99.85% en las 3 arquitecturas.

CUESTIONARIO DE AUDITORIA FORMAL (Responde con rigor matematico y fisico, sin complacencias, en espanol):
1. Formula y evalua la equivalencia matematica entre:
   (A) Medir 100,000 configuraciones afuera y calcular la moda/media estadistica en la CPU del host.
   (B) Aplicar la reduccion tensorial/cuantica adentro (intra-chip / intra-QPU) a lo largo de T iteraciones internas y emitir 1 solo vector representativo a traves del bus I/O.
   ¿En que condiciones formales (ergodicidad, convergencia de Borel-Cantelli, Teorema Central del Limite) esta equivalencia es exacta o asintoticamente cuasi-exacta?
2. Evalua la Regla 31 de Silicio:
   - ¿Por que tratar a un QPU como silicio booleano (usando compuertas Toffoli/CCX para aritmetica de umbrales) es una aberracion de coherencia, y por que el formalismo de estimadores de observables continuos SU(2) es la verdadera funcion de salida nativa?
   - ¿Por que la contraccion softmax-Gram matmul (M^T softmax(\\beta M M^T 1)) es la adaptacion optima de la moda para las matrices sistolicas (MXU) de los TPUs?
3. Dictamen final: ¿Es este paradigma (puerta adentro + adaptacion al contrato de silicio) cientificamente solido y publicable en el estado del arte de la computacion de altas dimensiones y computacion cuantica?
"""

def query_claude_fable():
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": "claude-fable-5-1",
        "max_tokens": 3000,
        "temperature": 0.1,
        "system": "Eres Claude Fable 5.1 (Arbitro Supremo de Fisica Cuantica y Geometria Diferencial de Anthropic). Rigor formal hostil, cero adulacion, analisis matematico puro en espanol.",
        "messages": [{"role": "user", "content": PROMPT_TRIBUNAL}]
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={
        "x-api-key": CLAUDE_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    })
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
        txt = data["content"][0]["text"]
        return "Claude Fable 5.1 (Direct Pay-As-You-Go)", round((time.perf_counter() - t0)*1000, 1), txt

def query_qwen_max():
    # Try Alibaba Bailian Endpoint first with qwen-max / qwen3.8-max
    models_to_try = [
        (ALIBABA_ENDPOINT, ALIBABA_PRO_KEY, "qwen-max"),
        (ALIBABA_ENDPOINT, ALIBABA_PRO_KEY, "qwen3.8-max"),
        ("https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions", ALIBABA_PRO_KEY, "qwen-max"),
        ("https://openrouter.ai/api/v1/chat/completions", OPENROUTER_KEY, "qwen/qwen-max"),
        ("https://openrouter.ai/api/v1/chat/completions", OPENROUTER_KEY, "qwen/qwen-2.5-72b-instruct")
    ]
    for url, key, m in models_to_try:
        payload = {
            "model": m,
            "messages": [
                {"role": "system", "content": "Eres Qwen 3.8 Max (Arquitecto de Microarquitectura de Silicio y Aceleradores Cuanticos/Neuronales de Alibaba Tongyi). Rigor analitico y matematico en espanol, cero adulacion."},
                {"role": "user", "content": PROMPT_TRIBUNAL}
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
                return f"Qwen 3.8 Max ({m})", round((time.perf_counter() - t0)*1000, 1), txt
        except Exception as e:
            # print(f"Fallo {m} en {url}: {e}")
            continue
    raise RuntimeError("Qwen Max fallo en todos los endpoints")

def main():
    print("=== EJECUTANDO CLAUDE FABLE 5.1 (CUENTA DIRECTA PAYG) Y QWEN 3.8 MAX ===")
    results = {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_claude = executor.submit(query_claude_fable)
        f_qwen = executor.submit(query_qwen_max)

        for f in [f_claude, f_qwen]:
            try:
                name, latency, text = f.result()
                print(f"[OK] {name} respondio exitosamente en {latency} ms!")
                results[name] = {"latency_ms": latency, "verdict": text}
            except Exception as e:
                print(f"[ERR] Fallo: {e}")

    # Guardar y fusionar con el tribunal previo
    out_file = "e:/POLYDIM_EINSOF/benchmarks/tribunal_sabios_regla31_resultado.json"
    try:
        with open(out_file, "r", encoding="utf-8") as f:
            prev = json.load(f)
    except Exception:
        prev = {}
    prev.update(results)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(prev, f, ensure_ascii=False, indent=2)
    print(f"\n[FIN] Guardado en: {out_file}")

if __name__ == "__main__":
    main()
