---
name: ask-sage
description: Consult the sovereign open-weights models (Hugging Face Polydim-Einsof or local Ollama) and free-tier SOTA pools before spending paid tokens. Triggered with /ask-sage <query>.
---

# Ask-Sage Skill (Sovereign Model Routing)

**Trigger**: `/ask-sage <question or problem>`

## Purpose
Routes student queries through sovereign open-weights models trained on continuous geometry and formal mathematics:
1. **Local Tier (Offline & Free):** Ollama running `deepseek-r1:1.5b` or `qwen2.5-coder:1.5b`.
2. **Hugging Face Hub:** `Polydim-Einsof` models (`huggingface.co/Polydim-Einsof`).
3. **Free Cloud Tier:** Groq / OpenRouter free models without touching credit cards.

## Workflow
1. Synthesizes the core question.
2. Checks if local models or Hugging Face adapters can resolve it.
3. Delivers a verified answer with zero cost to the student.
