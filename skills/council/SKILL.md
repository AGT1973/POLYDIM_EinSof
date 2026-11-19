---
name: council
description: Convenes the Council of Sages (Tribunal de Sabios). Dispatches your inquiry simultaneously to multiple top-tier models (Local Ollama, Alibaba Bailian Qwen-Max, DeepSeek-Chat, OpenRouter, Cerebras CS-3), compares their perspectives, highlights consensus (>=75%), logs dissenting angles, and synthesizes a definitive, unbiased answer. Invoked with /council <topic> or /sabios <topic>.
---

# Council of Sages — Action `/council` (`/sabios`)

Multi-model dialectic deliberation for students, researchers, and autonomous agents.

---

## The Problem for Beginners

When you ask a single AI model (like ChatGPT, Gemini, or Claude), you often get:
- Subtle hallucinations or outdated training data.
- Commercial or regional bias (US-centric, corporate-filtered).
- Blind agreement with whatever premise you ask.

## How the Council Solves This

Instead of trusting one model, `/council` queries a fleet of diverse, world-class models at the same time:
1. **Local Silicon (Debian / ALADIN / Ollama):** `qwen2.5:1.5b`, `mathesis-quantum:1.5b`, `deepseek-r1:7b`.
2. **Flagship Frontier APIs:**
   - **Alibaba Bailian:** `qwen-max`, `qwen-plus` (SOTA East Asia / Mathematics).
   - **DeepSeek:** `deepseek-chat`, `deepseek-reasoner` (Logical & Code SOTA).
   - **OpenRouter / Global:** `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`.
   - **Cerebras CS-3:** Wafer-Scale ultra-fast inference (170 ms response).
3. **Automatic Synthesis:**
   - Evaluates common ground ($\ge 75\%$ agreement).
   - Extracts dissenting critiques ($\le 25\%$).
   - Gives you a clean executive summary backed by verified facts.

---

## How to Invoke (Zero Code)

Simply write in chat:
```text
/council What is the exact mathematical difference between discrete autoregressive attention and continuous manifold projection?
```
Or in Spanish:
```text
/sabios Explicame en términos sencillos por qué la variedad de Stiefel evita el colapso 1D.
```

The underlying runner (`skills/scripts/council_runner.py`) handles all HTTP dispatch, timeout management, and consensus collation automatically.
