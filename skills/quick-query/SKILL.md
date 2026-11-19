---
name: quick-query
description: Fast, zero-cost inquiry to Free-Tier SOTA and local offline models (Groq, SambaNova, Google AI Studio Free, OpenRouter Free, ALADIN). Zero student budget consumption ($0 USD). Auto-rotates keys on 429 cooldown. Invoked with /query <question> or /consulta <question>.
---

# Quick Query — Action `/query` (`/consulta`)

Fast, zero-cost AI inquiries designed for student war-economy ($0 USD budget).

---

## What It Does

When you need a quick answer, code explanation, or math sanity-check, you shouldn't have to pay for expensive API tokens or worry about exceeding credit limits.

`/query` sends your prompt to our curated pool of **verified $0 USD free models**:
- **Local ALADIN & Ollama Node:** Completely free, offline, infinite quota.
- **Groq & SambaNova Free Tiers:** Blazing fast LPU/RDU inference at zero cost.
- **Google AI Studio Free Tier:** Gemini Flash models.
- **OpenRouter Free Community Pool:** Open-weights community models.

If any provider hits a rate limit (HTTP 429), `/query` automatically rotates to the next available free provider in under 2 seconds.

---

## How to Use

```text
/query What is the time complexity of the Gram-Schmidt orthonormalization vs. polar retraction?
```
Or in Spanish:
```text
/consulta ¿Cómo configuro mi entorno local para conectarme a ALADIN?
```
