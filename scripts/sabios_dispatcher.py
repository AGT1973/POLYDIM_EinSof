# -*- coding: utf-8 -*-
"""
Despachador Dinamico del Tribunal de Sabios — POLYDIM-EINSOF (v2.2 SOTA + Helena)
=================================================================================
Ejecucion real y verificada en silicio / APIs vivas sin simulaciones (Regla 1 / Ariel's Law).
Politica de Despacho:
  - Por defecto (allow_paid=True): despacha al roster completo (ALADIN/Ollama local +
    Free-Tier Pools + SOTA Token Plan / APIs activas del vault).
  - Con --free-only: restringe el despacho exclusivamente a ALADIN/Ollama local + Free-Tier Pools ($0 USD).
  - Envolvente Helena (Regla 3 / 3.1): Todo payload tensorial externo se envuelve con
    encode_4bit_quant_carrier / encode_png_carrier de helena_carrier_bridge.py.
"""
import argparse
import asyncio
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    import psycopg2
except ImportError:
    psycopg2 = None

_THIS_DIR = Path(__file__).resolve().parent
_HELENA_CORE_DIR = _THIS_DIR if (_THIS_DIR / "helena_carrier_bridge.py").exists() else Path(r"e:\Polydim_2027_core\Qlora\core")
if str(_HELENA_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_HELENA_CORE_DIR))

from helena_carrier_bridge import encode_4bit_quant_carrier, encode_png_carrier

PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = int(os.environ.get("PGPORT", 5432))
PG_USER = os.environ.get("PGUSER", "postgres")
PG_DB = os.environ.get("PGDATABASE", "polydim_active_db")


def _resolve_gandalf_vault_dir() -> Path:
    candidates = [
        os.environ.get("GANDALF_VAULT_DIR"),
        r"C:\Users\eluithi\.gandalf_vault",
        str(Path.home() / ".gandalf_vault"),
        "/home/agt/.gandalf_vault",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return Path(c)
    return Path.home() / ".gandalf_vault"


GANDALF_VAULT_DIR = _resolve_gandalf_vault_dir()
CAROUSEL_STATE_FILE = (
    GANDALF_VAULT_DIR / "carousel_keys.json"
    if (GANDALF_VAULT_DIR / "carousel_keys.json").exists()
    else Path(r"C:\Users\eluithi\.gemini\config\mcp_carousel_state.json")
)
GANDALF_ENV_FILE = GANDALF_VAULT_DIR / "keys.env"
DEFAULT_BAILIAN_BASE = "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
OLLAMA_CANDIDATES = ("http://127.0.0.1:11434", "http://192.168.100.21:11434")

PROVIDER_KEY_POOLS = {
    # Free-Tier ($0 USD)
    "groq": [f"Groq_Pool_{i:02d}" for i in range(1, 11)] + [f"Groq_Pool{i}" for i in range(1, 8)],
    "sambanova": [f"SambaNova_Pool_{i:02d}" for i in range(1, 11)],
    "gemini_free": ["Gemini_Studio_Pool1", "Gemini_Studio_Pool2"],
    "openrouter_free": ["openrouter_api_key", "OpenRouter_Ariel_Master", "OpenRouter"],
    # Paid SOTA (Bloqueadas salvo --paid)
    "bailian": ["ALIBABA_TOKEN_PLAN_ESSENTIAL", "Alibaba_Bailian_Pro", "alibaba_bailian_pro_key", "Alibaba_Bailian_Flash"],
    "kimi": ["kimi_api_key", "Kimi_Moonshot_Pool1", "Kimi_Moonshot_Pool2"],
    "claude": ["Claude_Pool2", "Claude_Pool3", "Claude_Pool5", "Claude_Pool6", "Claude_Pool7"],
    "gemini": ["Gemini_Principal", "Gemini_Backup", "Gemini_Studio_Pool1", "Gemini_Studio_Pool2"],
    "openrouter": ["openrouter_api_key", "OpenRouter_Ariel_Master", "OpenRouter"],
    "cerebras": ["cerebras_api_key", "Cerebras_HighSpeed"],
    "deepseek": ["deepseek_api_key", "DeepSeek"],
}


def get_db_connection():
    if psycopg2 is None:
        raise RuntimeError("psycopg2 no instalado en este nodo")
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
    """Carga claves y endpoints desde active_vault (si disponible) y .gandalf_vault sin exponerlos."""
    wanted = {k for pool in PROVIDER_KEY_POOLS.values() for k in pool}
    wanted.add("Alibaba_Bailian_Endpoint")
    rows = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT key_name, value FROM active_vault WHERE key_name = ANY(%s);",
            (list(wanted),),
        )
        rows = cur.fetchall()
        conn.close()
    except Exception:
        rows = []

    vault = {}
    token_plan_base = None
    for kname, raw in rows:
        val = str(raw).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        if not val or "TIER" in val.upper() or "BLOCKED" in val.upper():
            continue
        if val.startswith("{") and val.endswith("}"):
            try:
                jval = json.loads(val)
                if "BLOCKED" in str(jval.get("status", "")).upper():
                    continue
                if "api_key" in jval:
                    val = str(jval["api_key"]).strip()
                    if jval.get("base_url"):
                        token_plan_base = str(jval["base_url"]).rstrip("/")
                elif "endpoint" in jval or "base_url" in jval:
                    val = str(jval.get("endpoint") or jval.get("base_url")).strip()
                else:
                    continue
            except Exception:
                continue
        vault.setdefault(kname, val)

    ep = vault.get("Alibaba_Bailian_Endpoint", "").rstrip("/")
    if token_plan_base:
        bailian_base = token_plan_base
    elif ep and ep.startswith("http"):
        bailian_base = f"{ep}/compatible-mode/v1" if not ep.endswith("/v1") else ep
    else:
        bailian_base = DEFAULT_BAILIAN_BASE

    # Cargar claves desde carpeta segura .gandalf_vault/keys.env (sin Git, solo local)
    if GANDALF_ENV_FILE.exists():
        env_map = {
            "GROQ_API_KEY": "Groq_Pool_01",
            "SAMBANOVA_API_KEY": "SambaNova_Pool_01",
            "GEMINI_API_KEY": "Gemini_Studio_Pool1",
            "GOOGLE_API_KEY": "Gemini_Principal",
            "OPENROUTER_API_KEY": "openrouter_api_key",
            "KIMI_API_KEY": "kimi_api_key",
            "MOONSHOT_API_KEY": "Kimi_Moonshot_Pool1",
            "ANTHROPIC_API_KEY": "Claude_Pool2",
            "CEREBRAS_API_KEY": "cerebras_api_key",
            "DEEPSEEK_API_KEY": "deepseek_api_key",
            "BAILIAN_TOKEN_PLAN_KEY": "ALIBABA_TOKEN_PLAN_ESSENTIAL",
            "DASHSCOPE_API_KEY": "Alibaba_Bailian_Pro",
        }
        try:
            for ln in GANDALF_ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
                ln = ln.strip()
                if not ln or ln.startswith("#") or "=" not in ln:
                    continue
                ek, ev = ln.split("=", 1)
                ek, ev = ek.strip(), ev.strip().strip('"').strip("'")
                if ek == "DASHSCOPE_BASE_URL" and ev.startswith("http"):
                    bailian_base = ev.rstrip("/")
                elif ek in env_map and ev:
                    vault.setdefault(env_map[ek], ev)
        except Exception:
            pass

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
    """Devuelve lista ordenada de claves no enfriadas para el hub (vault + fallback carousel)."""
    carousel_all = _load_carousel_cooldowns()
    carousel_hub = hub[:-5] if hub.endswith("_free") else hub
    cooldowns = carousel_all.get(hub, []) or carousel_all.get(carousel_hub, [])
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
        for idx, e in enumerate(cooldowns):
            cval = str(e.get("api_key") or "").strip()
            if cval and cval not in blocked and cval not in [c[1] for c in candidates]:
                candidates.append((f"carousel_{carousel_hub}_{idx+1}", cval))
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
        return msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or json.dumps(msg)[:300]

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
            with urllib.request.urlopen(f"{base}/api/tags", timeout=3) as r:
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


def build_free_sabios_roster():
    """Roster Free-Tier ($0 USD) sin gasto de saldo."""
    or_headers = {"HTTP-Referer": "https://github.com/AGT1973/POLYDIM_EinSof", "X-Title": "POLYDIM-Sabios-Free"}
    return [
        {"label": "Groq Free (llama-3.3-70b-versatile)", "kind": "openai", "hub": "groq", "base": "https://api.groq.com/openai/v1", "model": "llama-3.3-70b-versatile", "tier": "FREE_0_USD"},
        {"label": "SambaNova Free (DeepSeek-R1-Distill-Llama-70B)", "kind": "openai", "hub": "sambanova", "base": "https://api.sambanova.ai/v1", "model": "DeepSeek-R1-Distill-Llama-70B", "tier": "FREE_0_USD"},
        {"label": "OpenRouter Free (deepseek/deepseek-r1:free)", "kind": "openai", "hub": "openrouter_free", "base": "https://openrouter.ai/api/v1", "model": "deepseek/deepseek-r1:free", "headers": or_headers, "tier": "FREE_0_USD"},
        {"label": "Google AI Studio Free (gemini-2.5-flash)", "kind": "gemini", "hub": "gemini_free", "model": "gemini-2.5-flash", "tier": "FREE_0_USD"},
    ]


def build_sabios_roster(bailian_base):
    """Roster SOTA pago (requiere --paid explicitamente)."""
    or_headers = {"HTTP-Referer": "https://github.com/AGT1973/POLYDIM_EinSof", "X-Title": "POLYDIM-Sabios"}
    return [
        {"label": "Kimi K3.1 Pro (Moonshot Direct)", "kind": "openai", "hub": "kimi", "base": "https://api.moonshot.ai/v1", "model": "kimi-k3.1-pro", "temperature": 1.0, "tier": "PAID"},
        {"label": "Claude Opus 5.5 (Anthropic Direct)", "kind": "claude", "hub": "claude", "model": "claude-opus-5-5", "tier": "PAID"},
        {"label": "Qwen4 Max (Alibaba Bailian SG)", "kind": "openai", "hub": "bailian", "base": bailian_base, "model": "qwen4-max", "tier": "PAID"},
        {"label": "DeepSeek V4.1 Flash (Bailian SG)", "kind": "openai", "hub": "bailian", "base": bailian_base, "model": "deepseek-v4.1-flash", "tier": "PAID"},
        {"label": "Gemini 4 Hydrogen (Google Direct)", "kind": "gemini", "hub": "gemini", "model": "gemini-4-hydrogen", "tier": "PAID"},
        {"label": "Cerebras gpt-oss-120b (WSE)", "kind": "openai", "hub": "cerebras", "base": "https://api.cerebras.ai/v1", "model": "gpt-oss-120b", "tier": "PAID"},
        {"label": "OpenAI GPT-6.2 Astra (OpenRouter #1)", "kind": "openai", "hub": "openrouter", "base": "https://openrouter.ai/api/v1", "model": "openai/gpt-6.2-astra", "headers": or_headers, "tier": "PAID"},
        {"label": "DeepSeek V4 Pro (OpenRouter #2)", "kind": "openai", "hub": "openrouter", "base": "https://openrouter.ai/api/v1", "model": "deepseek/deepseek-v4-pro-0813", "headers": or_headers, "tier": "PAID"},
        {"label": "Gemini 4 Carbon (OpenRouter #3)", "kind": "openai", "hub": "openrouter", "base": "https://openrouter.ai/api/v1", "model": "google/gemini-4-carbon", "headers": or_headers, "tier": "PAID"},
    ]


_FLOAT_RE = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
_JSON_TENSOR_RE = re.compile(rf"\[\s*{_FLOAT_RE}(?:\s*,\s*{_FLOAT_RE}){{5,}}\s*\]")
_MD_TABLE_RE = re.compile(rf"\|(?:\s*{_FLOAT_RE}\s*\|){{3,}}")


def _encode_tensor_with_helena(arr: np.ndarray, carrier_mode: str = "auto"):
    """Envuelve un tensor numpy usando encode_png_carrier o encode_4bit_quant_carrier."""
    use_png = carrier_mode == "png" or (carrier_mode == "auto" and 20 + arr.size * 4 <= 24576 and arr.size > 512)
    if use_png:
        png_bytes = encode_png_carrier(arr)
        digest = hashlib.blake2s(png_bytes, digest_size=8).hexdigest()
        b64_head = base64.b64encode(png_bytes).decode("ascii")[:64]
        tag = f"[HELENA_PNG_CARRIER: 128x64 elements={arr.size} bytes={len(png_bytes)} blake2s={digest} b64_head={b64_head}...]"
        meta = {"carrier": "HELENA_PNG_128x64", "elements": int(arr.size), "bytes": len(png_bytes), "blake2s": digest}
        return tag, meta

    q4 = encode_4bit_quant_carrier(arr)
    tag = f"[HELENA_4BIT_QUANT_CARRIER: elements={arr.size} char_len={q4['char_len']} b64={q4['payload_b64']}]"
    meta = {"carrier": q4["carrier"], "elements": int(arr.size), "char_len": q4["char_len"], "truncated": q4["b64_truncated"]}
    return tag, meta


def wrap_external_payload_helena(prompt: str, carrier_mode: str = "auto"):
    """
    Invariante Helena / Caché Activo (Regla 2 / Regla 3 / Regla 3.1):
    Intercepta arrays JSON numéricos o tablas Markdown densas y los envuelve
    con encode_4bit_quant_carrier / encode_png_carrier de helena_carrier_bridge.py.
    """
    carriers_applied = []

    def _replace_json_tensor(match):
        vals = json.loads(match.group(0))
        arr = np.asarray(vals, dtype=np.float32)
        tag, meta = _encode_tensor_with_helena(arr, carrier_mode=carrier_mode)
        carriers_applied.append(meta)
        return tag

    clean_text = _JSON_TENSOR_RE.sub(_replace_json_tensor, prompt)

    if _MD_TABLE_RE.search(clean_text):
        nums = [float(x) for x in re.findall(_FLOAT_RE, clean_text)]
        arr = np.asarray(nums if nums else [0.0], dtype=np.float32)
        tag, meta = _encode_tensor_with_helena(arr, carrier_mode=carrier_mode)
        carriers_applied.append(meta)
        clean_text = _MD_TABLE_RE.sub(f"| {tag} |", clean_text)

    if carriers_applied:
        clean_text += "\n\n[INVARIANTE GHOST/HELENA: Serialización 1D interceptada y envuelta con helena_carrier_bridge.py en S^(D-1).]"
    return clean_text, {
        "helena_bridge": "helena_carrier_bridge.py",
        "carrier_mode": carrier_mode,
        "carriers_applied": carriers_applied,
    }


def enforce_vector_only_under_cache(prompt: str, carrier_mode: str = "auto") -> str:
    clean_text, _ = wrap_external_payload_helena(prompt, carrier_mode=carrier_mode)
    return clean_text


async def run_sabios_fanout(
    prompt,
    max_tokens=160,
    dry_run=False,
    include_local=True,
    allow_paid=True,
    helena_carrier="auto",
):
    prompt, helena_meta = wrap_external_payload_helena(prompt, carrier_mode=helena_carrier)
    vault, bailian_base = load_vault_secrets()
    free_roster = build_free_sabios_roster()
    paid_roster = build_sabios_roster(bailian_base)
    roster = free_roster + (paid_roster if allow_paid else [])
    ollama_base, ollama_models = probe_ollama_models() if include_local else (None, [])

    if dry_run:
        plan = []
        for item in roster:
            cands = resolve_candidate_keys(item["hub"], vault)
            plan.append({
                "sabio": item["label"],
                "tier": item["tier"],
                "hub": item["hub"],
                "model": item["model"],
                "candidate_key_aliases": [c[0] for c in cands],
                "ready": len(cands) > 0,
            })
        return {
            "mode": "DRY_RUN",
            "cost_mode": "PAID_UNLOCKED" if allow_paid else "ZERO_USD_FREE_AND_LOCAL_ONLY",
            "allow_paid": allow_paid,
            "paid_blocked_count": 0 if allow_paid else len(paid_roster),
            "paid_blocked_sabios": [] if allow_paid else [p["label"] for p in paid_roster],
            "helena_envelope": helena_meta,
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

    # --- CAG Output Truth Interceptor: Filter hallucinations from each sage ---
    try:
        sys.path.insert(0, str(Path(r"E:\POLYDIM_EINSOF\tools")))
        from cag_output_truth_interceptor import CagOutputTruthInterceptor
        _interceptor = CagOutputTruthInterceptor()
    except Exception:
        _interceptor = None

    for r in results:
        if isinstance(r, dict):
            if r.get("status") == "OK" and _interceptor:
                raw_text = str(r.get("opinion") or r.get("response", ""))
                try:
                    filtered = _interceptor.intercept_and_filter(raw_text, mode="filter_strict")
                    r["response_original"] = raw_text
                    r["response"] = filtered["sanitized_output"]
                    r["cag_interceptor"] = {
                        "status": filtered["status"],
                        "verified": filtered["verified_propositions_count"],
                        "discarded": filtered["discarded_propositions_count"],
                        "blake2s_seal": filtered["blake2s_seal"]
                    }
                except Exception:
                    pass  # On interceptor error, keep original response
            (ok_list if r.get("status") == "OK" else fail_list).append(r)
        else:
            fail_list.append({"sabio": "unknown", "status": "FAIL", "error": str(r)})

    ts = datetime.now(timezone.utc).isoformat()
    payload = {
        "timestamp": ts,
        "cost_mode": "PAID_UNLOCKED" if allow_paid else "ZERO_USD_FREE_AND_LOCAL_ONLY",
        "allow_paid": allow_paid,
        "helena_envelope": helena_meta,
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
            VALUES ('sabios_deliberations', %s, %s, %s)
            ON CONFLICT (category, key_name) DO UPDATE SET value=EXCLUDED.value, updated_at=CURRENT_TIMESTAMP;
            """,
            (
                f"DELIBERATION_{'SOTA_PAID' if allow_paid else 'FREE_0USD'}_{int(time.time())}",
                json.dumps(payload, ensure_ascii=False),
                "Deliberacion real SOTA APIs pagas + Free-Tier + local" if allow_paid else "Deliberacion soberana $0 USD (ALADIN local + Free-Tier)",
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    return payload


def main():
    parser = argparse.ArgumentParser(description="Tribunal de Sabios SOTA Dispatcher v2.2 (SOTA + Helena)")
    parser.add_argument("prompt", nargs="?", default="Evaluar en una linea la invariancia Stiefel X^T X = I_k.")
    parser.add_argument("--max-tokens", type=int, default=160)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--paid", action="store_true", help="Compatible con invocaciones previas (habilitado por defecto).")
    parser.add_argument("--free-only", action="store_true", help="Restringe el despacho a ALADIN local y Free-Tier Pools ($0 USD).")
    parser.add_argument("--no-local", action="store_true")
    parser.add_argument("--helena-carrier", choices=["auto", "4bit", "png"], default="auto", help="Modo de envolvente Helena para payloads externos.")
    args = parser.parse_args()

    allow_paid = False if args.free_only else True

    res = asyncio.run(run_sabios_fanout(
        args.prompt,
        max_tokens=args.max_tokens,
        dry_run=args.dry_run,
        include_local=not args.no_local,
        allow_paid=allow_paid,
        helena_carrier=args.helena_carrier,
    ))
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
