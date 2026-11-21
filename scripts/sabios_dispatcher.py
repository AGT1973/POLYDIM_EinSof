# -*- coding: utf-8 -*-
"""
Despachador Dinamico del Tribunal de Sabios — POLYDIM-EINSOF (v2.0 SOTA Paid + Sovereign)
========================================================================================
Ejecucion real y verificada en silicio / APIs vivas sin simulaciones (Regla 1 / Ariel's Law).
Lee credenciales dinamicamente desde PostgreSQL (active_vault), rota claves ante 401/429
integrado con el estado del Carrusel MCP y despacha en paralelo a:
  1. Kimi Direct (api.moonshot.ai/v1 -> kimi-k3.1-pro)
  2. Claude Direct (api.anthropic.com/v1 -> claude-opus-5-5)
  3. Alibaba Bailian SG (compatible-mode/v1 -> qwen4-max & deepseek-v4.1-flash-1017)
  4. Google Gemini Direct (generativelanguage.googleapis.com -> gemini-4-hydrogen)
  5. OpenRouter 3+ IAs Paralelas (openai/gpt-6.2-astra, deepseek/deepseek-v4.1-flash-1017, google/gemini-4-carbon)
  6. Cerebras WSE Direct (api.cerebras.ai/v1 -> gpt-oss-120b)
  7. DeepSeek Direct (api.deepseek.com -> failover automatico a Bailian/OpenRouter si 401)
  8. ALADIN / Ollama Local (192.168.100.21:11434 & 127.0.0.1:11434) si estan en linea.
"""
import argparse
import asyncio
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import psycopg2

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", "postgres")
PG_DB = os.environ.get("PGDATABASE", "polydim_active_db")

CAROUSEL_STATE_FILE = Path(r"C:\Users\eluithi\.gemini\config\mcp_carousel_state.json")
DEFAULT_BAILIAN_BASE = "https://ws-t85fm4y7sz8vxo9t.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
OLLAMA_CANDIDATES = ("http://127.0.0.1:11434", "http://192.168.100.21:11434")

PROVIDER_KEY_POOLS = {
    "kimi": ["kimi_api_key", "Kimi_Moonshot_Pool1", "Kimi_Moonshot_Pool2"],
    "claude": ["Claude_Pool2", "Claude_Pool3", "Claude_Pool5", "Claude_Pool6", "Claude_Pool7"],
    "bailian": ["Alibaba_Bailian_Pro", "alibaba_bailian_pro_key", "Alibaba_Bailian_Flash"],
    "gemini": ["Gemini_Principal", "Gemini_Backup", "Gemini_Studio_Pool1", "Gemini_Studio_Pool2"],
    "openrouter": ["openrouter_api_key", "OpenRouter_Ariel_Master", "OpenRouter"],
    "cerebras": ["cerebras_api_key", "Cerebras_HighSpeed"],
    "deepseek": ["deepseek_api_key", "DeepSeek"],
}


def get_db_connection():
    passwords = [os.environ.get("PGPASSWORD"), "Polydim#2027!", "1234", "123", "postgres", ""]
    for pwd in passwords:
        if pwd is None:
            continue
        try:
            return psycopg2.connect(
                dbname=PG_DB, host=PG_HOST, port=PG_PORT, user=PG_USER, password=pwd, connect_timeout=3
            )
        except Exception:
            continue
    raise RuntimeError("No se pudo conectar a PostgreSQL polydim_active_db")


def load_vault_secrets():
    """Carga claves y endpoints desde active_vault sin exponerlos en disco o logs."""
    wanted = {k for pool in PROVIDER_KEY_POOLS.values() for k in pool}
    wanted.add("Alibaba_Bailian_Endpoint")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT key_name, value FROM active_vault WHERE key_name = ANY(%s);",
        (list(wanted),),
    )
    rows = cur.fetchall()
    conn.close()

    vault = {}
    for kname, raw in rows:
        val = str(raw).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        if not val or "TIER" in val.upper():
            continue
        vault.setdefault(kname, val)

    ep = vault.get("Alibaba_Bailian_Endpoint", "").rstrip("/")
    bailian_base = f"{ep}/compatible-mode/v1" if ep else DEFAULT_BAILIAN_BASE
    return vault, bailian_base


def _load_carousel_cooldowns():
    if not CAROUSEL_STATE_FILE.exists():
        return {}
    try:
        return json.loads(CAROUSEL_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _mark_carousel_cooldown(hub, key_value, reason):
    try:
        data = _load_carousel_cooldowns()
        now = int(time.time())
        entries = data.setdefault(hub, [])
        for entry in entries:
            if entry.get("api_key") == key_value:
                entry["fecha_consumo"] = now
                entry["is_active"] = False
                entry["ultimo_motivo_paro"] = reason[:120]
                entry["veces_agotada"] = entry.get("veces_agotada", 0) + 1
                break
        CAROUSEL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CAROUSEL_STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def resolve_candidate_keys(hub, vault):
    """Devuelve lista ordenada de claves no enfriadas para el hub."""
    cooldowns = _load_carousel_cooldowns().get(hub, [])
    now = int(time.time())
    blocked = set()
    for e in cooldowns:
        consumed = e.get("fecha_consumo")
        rec = e.get("tiempo_recarga_segundos", 3600)
        if consumed and now < consumed + rec:
            blocked.add(e.get("api_key"))

    candidates = []
    for kname in PROVIDER_KEY_POOLS.get(hub, []):
        val = vault.get(kname)
        if val and val not in blocked and val not in [c[1] for c in candidates]:
            candidates.append((kname, val))
    if not candidates:
        for kname in PROVIDER_KEY_POOLS.get(hub, []):
            val = vault.get(kname)
            if val and val not in [c[1] for c in candidates]:
                candidates.append((kname, val))
    return candidates


def _http_post_json(url, headers, body, timeout=45):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _call_with_rotation(hub, candidates, request_fn, label, model):
    """Ejecuta una llamada HTTP rotando claves ante 401/403/429 sin exponer secretos."""
    t0 = time.time()
    last_err = "Sin claves configuradas en active_vault"
    for kname, key in candidates:
        try:
            text = request_fn(key)
            return {
                "sabio": label,
                "model": model,
                "hub": hub,
                "key_alias": kname,
                "status": "OK",
                "latency_ms": round((time.time() - t0) * 1000),
                "opinion": text.strip()[:600],
            }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:240]
            last_err = f"HTTP {e.code} ({kname}): {err_body}"
            err_low = err_body.lower()
            should_rotate = e.code in (401, 402, 403, 429) or (
                e.code == 400 and any(w in err_low for w in ("credit", "balance", "billing", "quota"))
            )
            if should_rotate:
                _mark_carousel_cooldown(hub, key, f"HTTP {e.code}")
                continue
            break
        except Exception as e:
            last_err = f"{type(e).__name__} ({kname}): {e}"
            continue

    return {
        "sabio": label,
        "model": model,
        "hub": hub,
        "status": "FAIL",
        "latency_ms": round((time.time() - t0) * 1000),
        "error": last_err,
    }


def call_openai_compat(hub, base_url, model, prompt, max_tokens, vault, label, extra_headers=None, temperature=0.2):
    candidates = resolve_candidate_keys(hub, vault)
    url = f"{base_url.rstrip('/')}/chat/completions"

    def _do(key):
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "polydim-sabios/2.0",
        }
        if extra_headers:
            headers.update(extra_headers)
        effective_tokens = max(max_tokens, 1024) if any(x in model for x in ("qwen4", "deepseek-v4", "kimi-k3.1", "gemini-4", "gpt-oss", "opus-5.5")) else max_tokens
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": effective_tokens,
            "temperature": temperature,
        }
        data = _http_post_json(url, headers, body)
        msg = data["choices"][0]["message"]
        return msg.get("content") or msg.get("reasoning_content") or json.dumps(msg)[:300]

    return _call_with_rotation(hub, candidates, _do, label, model)


def call_anthropic(model, prompt, max_tokens, vault, label):
    candidates = resolve_candidate_keys("claude", vault)
    url = "https://api.anthropic.com/v1/messages"

    def _do(key):
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
            "User-Agent": "polydim-sabios/2.0",
        }
        body = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        data = _http_post_json(url, headers, body)
        blocks = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
        return "\n".join(blocks).strip()

    res = _call_with_rotation("claude", candidates, _do, label, model)
    if res.get("status") != "OK":
        or_res = call_openai_compat(
            "openrouter",
            "https://openrouter.ai/api/v1",
            "anthropic/claude-opus-5.5",
            prompt,
            max_tokens,
            vault,
            "Claude Opus 5.5 (OpenRouter Failover)",
            extra_headers={"HTTP-Referer": "https://github.com/AGT1973/POLYDIM_EinSof", "X-Title": "POLYDIM-Sabios"},
        )
        if or_res.get("status") == "OK":
            or_res["direct_claude_note"] = res.get("error", "")[:120]
            return or_res
    return res


def call_gemini(model, prompt, max_tokens, vault, label):
    candidates = resolve_candidate_keys("gemini", vault)

    def _do(key):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max(max_tokens, 1024), "temperature": 0.2},
        }
        data = _http_post_json(url, {"Content-Type": "application/json"}, body)
        parts = data["candidates"][0]["content"]["parts"]
        answer_parts = [p.get("text", "") for p in parts if not p.get("thought") and p.get("text")]
        if not answer_parts:
            answer_parts = [p.get("text", "") for p in parts if p.get("text")]
        return "".join(answer_parts)

    return _call_with_rotation("gemini", candidates, _do, label, model)


def probe_ollama_models():
    for base in OLLAMA_CANDIDATES:
        try:
            with urllib.request.urlopen(f"{base}/api/tags", timeout=2) as r:
                data = json.loads(r.read().decode("utf-8"))
                return base, [m["name"] for m in data.get("models", [])]
        except Exception:
            continue
    return None, []


def call_ollama(base, model, prompt, max_tokens):
    t0 = time.time()
    try:
        data = _http_post_json(
            f"{base}/api/generate",
            {"Content-Type": "application/json"},
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": max_tokens},
            },
            timeout=35,
        )
        return {
            "sabio": f"ALADIN/Ollama ({model})",
            "model": model,
            "hub": "ollama_local",
            "status": "OK",
            "latency_ms": round((time.time() - t0) * 1000),
            "opinion": data.get("response", "").strip()[:600],
        }
    except Exception as e:
        return {
            "sabio": f"ALADIN/Ollama ({model})",
            "model": model,
            "hub": "ollama_local",
            "status": "FAIL",
            "latency_ms": round((time.time() - t0) * 1000),
            "error": str(e),
        }


def build_sabios_roster(bailian_base):
    """Roster SOTA verificado con credito real (API directas + OpenRouter 3 paralelas)."""
    or_headers = {"HTTP-Referer": "https://github.com/AGT1973/POLYDIM_EinSof", "X-Title": "POLYDIM-Sabios"}
    return [
        {"label": "Kimi K3.1 Pro (Moonshot Direct)", "kind": "openai", "hub": "kimi", "base": "https://api.moonshot.ai/v1", "model": "kimi-k3.1-pro", "temperature": 1.0},
        {"label": "Claude Opus 5.5 (Anthropic Direct)", "kind": "claude", "hub": "claude", "model": "claude-opus-5-5"},
        {"label": "Qwen4 Max (Alibaba Bailian SG)", "kind": "openai", "hub": "bailian", "base": bailian_base, "model": "qwen4-max"},
        {"label": "DeepSeek V4.1 Flash (Bailian SG)", "kind": "openai", "hub": "bailian", "base": bailian_base, "model": "deepseek-v4.1-flash-1017"},
        {"label": "Gemini 4 Hydrogen (Google Direct)", "kind": "gemini", "hub": "gemini", "model": "gemini-4-hydrogen"},
        {"label": "Cerebras gpt-oss-120b (WSE)", "kind": "openai", "hub": "cerebras", "base": "https://api.cerebras.ai/v1", "model": "gpt-oss-120b"},
        {"label": "OpenAI GPT-6.2 Astra (OpenRouter #1)", "kind": "openai", "hub": "openrouter", "base": "https://openrouter.ai/api/v1", "model": "openai/gpt-6.2-astra", "headers": or_headers},
        {"label": "DeepSeek V4 Pro (OpenRouter #2)", "kind": "openai", "hub": "openrouter", "base": "https://openrouter.ai/api/v1", "model": "deepseek/deepseek-v4-pro-0813", "headers": or_headers},
        {"label": "Gemini 4 Carbon (OpenRouter #3)", "kind": "openai", "hub": "openrouter", "base": "https://openrouter.ai/api/v1", "model": "google/gemini-4-carbon", "headers": or_headers},
    ]


async def run_sabios_fanout(prompt, max_tokens=160, dry_run=False, include_local=True):
    vault, bailian_base = load_vault_secrets()
    roster = build_sabios_roster(bailian_base)
    ollama_base, ollama_models = probe_ollama_models() if include_local else (None, [])

    if dry_run:
        plan = []
        for item in roster:
            cands = resolve_candidate_keys(item["hub"], vault)
            plan.append({
                "sabio": item["label"],
                "hub": item["hub"],
                "model": item["model"],
                "candidate_key_aliases": [c[0] for c in cands],
                "ready": len(cands) > 0,
            })
        return {
            "mode": "DRY_RUN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "api_sabios": plan,
            "ollama_online": bool(ollama_base),
            "ollama_models": ollama_models,
        }

    tasks = []
    for item in roster:
        kind = item["kind"]
        if kind == "openai":
            tasks.append(asyncio.to_thread(
                call_openai_compat,
                item["hub"], item["base"], item["model"], prompt, max_tokens,
                vault, item["label"], item.get("headers"), item.get("temperature", 0.2),
            ))
        elif kind == "claude":
            tasks.append(asyncio.to_thread(
                call_anthropic, item["model"], prompt, max_tokens, vault, item["label"]
            ))
        elif kind == "gemini":
            tasks.append(asyncio.to_thread(
                call_gemini, item["model"], prompt, max_tokens, vault, item["label"]
            ))

    if ollama_base and ollama_models:
        for slug in ollama_models[:3]:
            tasks.append(asyncio.to_thread(call_ollama, ollama_base, slug, prompt, max_tokens))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    ok_list, fail_list = [], []
    for r in results:
        if isinstance(r, dict):
            (ok_list if r.get("status") == "OK" else fail_list).append(r)
        else:
            fail_list.append({"sabio": "unknown", "status": "FAIL", "error": str(r)})

    ts = datetime.now(timezone.utc).isoformat()
    payload = {
        "timestamp": ts,
        "prompt": prompt,
        "total_consultadas": len(tasks),
        "total_validas": len(ok_list),
        "opiniones": ok_list,
        "fallos": fail_list,
    }
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO active_vault (category, key_name, value, notes)
            VALUES ('sabios_deliberations', %s, %s, 'Deliberacion real SOTA APIs pagas + OpenRouter + local')
            ON CONFLICT (category, key_name) DO UPDATE SET value=EXCLUDED.value, updated_at=CURRENT_TIMESTAMP;
            """,
            (f"DELIBERATION_SOTA_{int(time.time())}", json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    return payload


def main():
    parser = argparse.ArgumentParser(description="Tribunal de Sabios SOTA Dispatcher v2.0")
    parser.add_argument("prompt", nargs="?", default="Evaluar en una linea la invariancia Stiefel X^T X = I_k.")
    parser.add_argument("--max-tokens", type=int, default=160)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-local", action="store_true")
    args = parser.parse_args()

    res = asyncio.run(run_sabios_fanout(
        args.prompt, max_tokens=args.max_tokens, dry_run=args.dry_run, include_local=not args.no_local
    ))
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
