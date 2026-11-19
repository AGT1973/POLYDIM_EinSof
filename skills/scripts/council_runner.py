#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
================================================================================
  POLYDIM-EINSOF: COUNCIL OF SAGES RUNNER (v1.0)
  Parallel Multi-LLM Deliberation Engine for Students.
================================================================================
"""

import sys
import json
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from model_bridge import call_model

COUNCIL_FLEET = [
    {"alias": "Bailian-Qwen-Max", "model": "qwen-max"},
    {"alias": "DeepSeek-V4-Chat", "model": "deepseek-chat"},
    {"alias": "Cerebras-CS3-Qwen", "model": "qwen-3.8-27b"}
]

def run_council(prompt: str, max_tokens: int = 250):
    print("=" * 75)
    print(f"[*] CONVENING THE COUNCIL OF SAGES ON TOPIC:")
    print(f"    \"{prompt}\"")
    print("=" * 75)
    
    results = {}
    t0 = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=len(COUNCIL_FLEET)) as executor:
        future_to_sage = {
            executor.submit(call_model, s["model"], prompt, max_tokens=max_tokens): s
            for s in COUNCIL_FLEET
        }
        for future in as_completed(future_to_sage):
            sage = future_to_sage[future]
            try:
                res = future.result()
                results[sage["alias"]] = res
                if res["success"]:
                    print(f"[+] [{sage['alias']}] ({res['latency_sec']}s):")
                    print(f"    {res['reply'][:200]}...\n")
                else:
                    print(f"[-] [{sage['alias']}] FAILED: {res.get('error')}\n")
            except Exception as e:
                results[sage["alias"]] = {"success": False, "error": str(e)}
                print(f"[-] [{sage['alias']}] EXCEPTION: {e}\n")
                
    total_dt = round(time.perf_counter() - t0, 2)
    successful = [k for k, v in results.items() if v.get("success")]
    
    print("=" * 75)
    print(f"[SUMMARY] Council completed in {total_dt}s | Quorum: {len(successful)}/{len(COUNCIL_FLEET)} sages responding")
    print("=" * 75)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Council of Sages Multi-LLM Runner")
    parser.add_argument("prompt", help="Prompt or inquiry to deliberate")
    parser.add_argument("--tokens", "-t", type=int, default=200, help="Max tokens per sage")
    args = parser.parse_args()
    
    res = run_council(args.prompt, args.tokens)
    sys.exit(0)
