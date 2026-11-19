#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
================================================================================
  POLYDIM-EINSOF: STUDENT UNIFIED MODEL BRIDGE (v1.0)
  Zero-code AI Model Invoker for Students and Autonomous Agents.
  
  Seamlessly connects to:
  1. ALADIN SOTA Gateway (192.168.100.21:8000) - Bailian, DeepSeek, Cerebras, OpenRouter
  2. Local Ollama (127.0.0.1:11434) - Offline $0 USD SLMs
  3. Alibaba Cloud Bailian Workspace - qwen-max, qwen-plus
  4. Cerebras CS-3 Wafer-Scale - qwen-3.8-27b, gpt-oss-120b (<200ms)
  5. OpenRouter Global SOTA Pool - gpt-4o, claude-3.5-sonnet, deepseek-chat
  6. Hugging Face Serverless Inference API
================================================================================
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path


def load_student_credentials():
    """Loads student API tokens from ~/.ai_credentials.env if present."""
    creds_file = Path.home() / ".ai_credentials.env"
    creds = {}
    if creds_file.exists():
        try:
            with open(creds_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        creds[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass
    return creds


CREDENTIALS = load_student_credentials()

DEFAULT_ALADIN_GATEWAY = os.environ.get("ALADIN_GATEWAY_URL", CREDENTIALS.get("ALADIN_GATEWAY_URL", "http://192.168.100.21:8000/v1/chat/completions"))
DEFAULT_LOCAL_OLLAMA = os.environ.get("OLLAMA_HOST", CREDENTIALS.get("OLLAMA_HOST", "http://127.0.0.1:11434/v1/chat/completions"))
BAILIAN_ENDPOINT = os.environ.get("BAILIAN_ENDPOINT", CREDENTIALS.get("BAILIAN_ENDPOINT", "https://ws-t85fm4y7sz8vxo9t.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/chat/completions"))
BAILIAN_KEY = os.environ.get("BAILIAN_KEY", CREDENTIALS.get("BAILIAN_KEY", ""))
OPENROUTER_ENDPOINT = os.environ.get("OPENROUTER_ENDPOINT", CREDENTIALS.get("OPENROUTER_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions"))
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY", CREDENTIALS.get("OPENROUTER_KEY", ""))
CEREBRAS_ENDPOINT = os.environ.get("CEREBRAS_ENDPOINT", CREDENTIALS.get("CEREBRAS_ENDPOINT", "https://api.cerebras.ai/v1/chat/completions"))
CEREBRAS_KEY = os.environ.get("CEREBRAS_KEY", CREDENTIALS.get("CEREBRAS_KEY", ""))
HF_TOKEN = os.environ.get("HF_TOKEN", CREDENTIALS.get("HF_TOKEN", ""))


def check_url_alive(url: str, timeout: float = 0.8) -> bool:
    try:
        base = url.split("/v1")[0] if "/v1" in url else url
        test_url = f"{base}/health" if "8000" in url else (f"{base}/api/tags" if "11434" in url else url)
        req = urllib.request.Request(test_url, headers={"User-Agent": "EinsofStudentBridge"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 204)
    except Exception:
        return False


def call_model(model: str, prompt: str, system_prompt: str = None, max_tokens: int = 500, stream: bool = False):
    m = model.strip()
    sys_content = system_prompt or "You are a precise, rigorous AI research partner operating under POLYDIM Radical Honesty."
    
    messages = [
        {"role": "system", "content": sys_content},
        {"role": "user", "content": prompt}
    ]
    
    # Priority 1: ALADIN Gateway (if reachable on LAN, manages all keys and proxy routing transparently)
    if check_url_alive(DEFAULT_ALADIN_GATEWAY, timeout=0.8):
        target_url = DEFAULT_ALADIN_GATEWAY
        headers = {"Content-Type": "application/json", "Authorization": "Bearer aladin-gateway"}
        target_model = m
    # Priority 2: Direct Alibaba Bailian (if student has key configured)
    elif BAILIAN_KEY and any(m.lower().startswith(p) for p in ["qwen-max", "qwen-plus", "qwen-turbo", "qwen3.8"]):
        target_url = BAILIAN_ENDPOINT
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BAILIAN_KEY}"}
        target_model = "qwen-max" if "max" in m.lower() else ("qwen-plus" if "plus" in m.lower() else "qwen-turbo")
    # Priority 3: Direct Cerebras Wafer-Scale (if key configured)
    elif CEREBRAS_KEY and ("cerebras" in m.lower() or m.lower() in ["qwen-3.8-27b", "gpt-oss-120b"]):
        target_url = CEREBRAS_ENDPOINT
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {CEREBRAS_KEY}"}
        target_model = "qwen-3.8-27b" if "qwen" in m.lower() else "gpt-oss-120b"
    # Priority 4: OpenRouter SOTA (if key configured)
    elif OPENROUTER_KEY and ("/" in m or any(m.lower().startswith(p) for p in ["gpt-", "claude-", "deepseek"])):
        target_url = OPENROUTER_ENDPOINT
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "HTTP-Referer": "https://polydim.org",
            "X-Title": "Einsof Student Bridge"
        }
        target_model = m
        if target_model == "gpt-4o":
            target_model = "openai/gpt-4o"
        elif target_model == "deepseek-chat":
            target_model = "deepseek/deepseek-chat"
        elif target_model.startswith("claude-"):
            target_model = f"anthropic/{m}"
    # Priority 5: Local Ollama (Completely $0 USD, offline, no API key required)
    else:
        target_url = DEFAULT_LOCAL_OLLAMA
        headers = {"Content-Type": "application/json", "Authorization": "Bearer ollama"}
        target_model = m

    payload = {
        "model": target_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": stream
    }

    t0 = time.perf_counter()
    req = urllib.request.Request(target_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            dt = time.perf_counter() - t0
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content", "").strip()
            reasoning = msg.get("reasoning", "") or msg.get("reasoning_content", "")
            usage = data.get("usage", {})
            
            return {
                "success": True,
                "model_requested": m,
                "model_executed": target_model,
                "endpoint_used": target_url,
                "latency_sec": round(dt, 2),
                "reply": content,
                "reasoning": reasoning,
                "usage": usage,
                "exit_code": 0
            }
    except Exception as e:
        return {
            "success": False,
            "model_requested": m,
            "error": str(e),
            "endpoint_used": target_url,
            "exit_code": 1
        }


def main():
    parser = argparse.ArgumentParser(description="POLYDIM-EINSOF Student Model Bridge")
    parser.add_argument("--model", "-m", default="qwen-max", help="Model name (e.g. qwen-max, qwen-plus, deepseek-chat, gpt-4o, qwen2.5:1.5b)")
    parser.add_argument("--prompt", "-p", required=True, help="Prompt text to evaluate")
    parser.add_argument("--system", "-s", default=None, help="Optional system prompt")
    parser.add_argument("--tokens", "-t", type=int, default=300, help="Max output tokens")
    parser.add_argument("--json", action="store_true", help="Output full JSON response")
    args = parser.parse_args()

    res = call_model(args.model, args.prompt, system_prompt=args.system, max_tokens=args.tokens)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(res["exit_code"])
        
    if res["success"]:
        print(f"[{res['model_executed']}] ({res['latency_sec']}s via {res['endpoint_used']}):")
        if res.get("reasoning"):
            print(f"[REASONING]: {res['reasoning']}\n")
        print(res["reply"])
        sys.exit(0)
    else:
        print(f"[ERROR {res['model_requested']}]: {res['error']} (endpoint: {res['endpoint_used']})")
        sys.exit(1)


if __name__ == "__main__":
    main()
