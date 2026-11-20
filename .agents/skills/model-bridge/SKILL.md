---
name: model-bridge
description: Unified Model Bridge for students. Seamlessly calls any AI model across Hugging Face, local Ollama, OpenRouter, Alibaba Cloud Bailian, or Cerebras without writing a single line of API or networking code. Invoked with /call <model> <prompt> or /model <name> <prompt>.
---

# Unified Model Bridge — Action `/call` (`/model`)

The zero-code interface for students to access world-class AI models across all platforms.

---

## Why this Skill Exists

Students often get stuck trying to understand:
- How to write Python `urllib` / `requests` / `aiohttp` scripts.
- How to format OpenAI-compatible JSON payloads (`{"messages": [{"role": "user", ...}]}`).
- How to configure Authorization Bearer tokens, CORS, timeouts, and rate limits.
- Where Hugging Face models are hosted vs. Ollama local vs. OpenRouter.

**Model Bridge eliminates all of that friction.**

---

## Supported Ecosystems (All Built-in)

| Platform | Model Examples | How it Routes |
| :--- | :--- | :--- |
| **Local Ollama** | `qwen2.5:1.5b`, `mathesis-quantum:1.5b`, `llama3.2:3b` | Direct to `127.0.0.1:11434` or ALADIN node |
| **Alibaba Bailian** | `qwen-max`, `qwen-plus`, `qwen-turbo` | Direct to Bailian MaaS Workspace |
| **OpenRouter SOTA** | `openai/gpt-4o`, `anthropic/claude-3.5-sonnet`, `deepseek/deepseek-chat` | Direct to OpenRouter global pool |
| **Cerebras CS-3** | `qwen-3.8-27b`, `gpt-oss-120b` | Wafer-Scale engine (<200ms latency) |
| **Hugging Face** | Any public HF repository (`meta-llama/...`, `mistralai/...`) | Serverless Inference API |

---

## How to Use as a Student

### 1. In Plain English or Spanish
Just tell your AI assistant:
- *"Call model qwen-max and ask it to explain Stiefel polar retraction."*
- *"Call my local Ollama model mathesis-quantum:1.5b with this prompt..."*
- *"Ask Cerebras qwen-3.8-27b to solve this algebraic equation."*

### 2. Using Slash Commands
```text
/call qwen-max Explain why Neumaier summation prevents floating point drift
/call deepseek-chat Review this Python code for memory leaks
/call mathesis-quantum:1.5b Verify the dimension boundary D=2048, k=16
```

### 3. Behind the Scenes
The assistant automatically runs `python skills/scripts/model_bridge.py --model <model> --prompt "<prompt>"` using Python's standard library. Zero external dependencies required.
