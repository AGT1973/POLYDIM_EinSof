---
name: whisper
description: Inter-AI vector messaging protocol using semantic routing, free-tier pools, and local offline nodes. Executes `/whisper <payload>` to route complex queries through local Einsof models (Ollama, ALADIN) and free-tier SOTA APIs with zero token waste.
---

# Whisper Protocol — Action `/whisper`

Sovereign, token-efficient inter-AI semantic routing and knowledge persistence for students and researchers.

> [!IMPORTANT]
> **DEFAULT BASAL STATE:**
> `/whisper` operates **ACTIVE BY DEFAULT** alongside `/ghost`.
> All inter-model consultations, multi-agent debates, and SOTA routing prioritize $0 USD local models and verified free-tier pools before calling any paid API.

---

## Why Students Need Whisper

If you don't know how to code API integrations, Whisper acts as your automatic AI dispatcher:
1. **Zero Coding Needed:** Just type `/whisper <your topic or question>`.
2. **$0 USD Student Cost:** Whisper automatically checks:
   - First: Your local Ollama models (`127.0.0.1:11434` or ALADIN node `192.168.100.21`).
   - Second: Free-tier SOTA pools (Groq, SambaNova, Google AI Studio Free, OpenRouter community pools).
   - Third: Authenticated high-tier models only if explicitly requested.
3. **No Hallucinations:** Whisper records the semantic results in vector storage so your agent never forgets previous lessons or steps.

---

## How to Use

- `/whisper summarize how continuous manifold reasoning outperforms discrete tokens`
- `/whisper route this math problem to the best available free model`
- `/whisper status` — Displays the currently active model pool and latency stats.
