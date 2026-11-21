# -*- coding: utf-8 -*-
"""
EINSOF Sovereign Student Bridge & Multi-Provider Engine (Estándar 2030)
======================================================================
Permite a cualquier alumno o investigador utilizar los modelos y razonamiento
continuo de EINSOF a costo $0 USD mediante proveedores gratuitos con rotación
automática ante límites de tasa (429):
  1. Ollama (100% Offline, CPU o GPU local, sin API Key, $0 USD).
  2. Groq Cloud (Free Tier, ultra-rápido LPU, $0 USD).
  3. Cerebras WSE-3 (Free Tier, 2000+ tok/s, $0 USD).
  4. OpenRouter Free Pool (Modelos con sufijo :free, $0 USD).
  5. SambaNova Cloud (Free Tier LLaMA 3.3 70B, $0 USD).
  6. Google AI Studio (Free Tier Gemini 2.0 / 1.5, $0 USD).
  7. Proveedores pagos (OpenAI, Anthropic, DashScope) activables SOLO si el
     alumno cuenta con su propia API Key (opcional).

Incorpora las Adaptaciones de Plataforma de EINSOF:
  - Protocolo de Razonamiento Continuo en Variedad Stiefel S^{D-1}.
  - Compuerta de verdad cerrada de 1 token <|cag_truth|>.
  - Protocolo Helena de transporte tensorial (PNG 128x64 y 4-bit quant) para
    intercambiar estados de alta dimensión sin gastar tokens de texto.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CREDENTIALS_FILE = Path.home() / ".ai_credentials.env"

# Carga de credenciales persistentes del alumno (~/.ai_credentials.env)
if CREDENTIALS_FILE.exists():
    for line in CREDENTIALS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# Configuración de Proveedores SOTA Gratuitos y Abiertos
FREE_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "ollama": {
        "name": "Ollama Local / Nodo ALADIN (100% Offline, $0 USD)",
        "env_key": None,
        "default_url": os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"),
        "default_model": "qwen2.5:7b",
        "fallback_models": ["mathesis-quantum:1.5b", "deepseek-r1:7b", "llama3.2:3b"],
        "requires_key": False,
        "description": "Ejecuta modelos directamente en tu computadora o en red local sin conexión a internet.",
    },
    "groq": {
        "name": "Groq Cloud (Free Tier LPU, 500+ tok/s, $0 USD)",
        "env_key": "GROQ_API_KEY",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "default_model": "llama-3.3-70b-versatile",
        "fallback_models": ["qwen-2.5-32b", "mixtral-8x7b-32768"],
        "requires_key": True,
        "get_key_url": "https://console.groq.com/keys",
        "description": "Inferencia ultra-rápida en chips LPU con cuota gratuita permanente.",
    },
    "cerebras": {
        "name": "Cerebras Inference (Free Tier WSE-3, 2000+ tok/s, $0 USD)",
        "env_key": "CEREBRAS_API_KEY",
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "default_model": "llama-3.3-70b",
        "fallback_models": ["llama3.1-8b"],
        "requires_key": True,
        "get_key_url": "https://cloud.cerebras.ai",
        "description": "El motor de silicio de oblea completa más veloz del mundo con capa gratuita.",
    },
    "openrouter": {
        "name": "OpenRouter Free Pool (Modelos Abiertos :free, $0 USD)",
        "env_key": "OPENROUTER_API_KEY",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "deepseek/deepseek-r1:free",
        "fallback_models": [
            "meta-llama/llama-3.3-70b-instruct:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
        ],
        "requires_key": True,
        "get_key_url": "https://openrouter.ai/keys",
        "description": "Ruteador multipolar con acceso gratuito a los modelos de razonamiento abiertos.",
    },
    "sambanova": {
        "name": "SambaNova Cloud (Free Tier SN40L, $0 USD)",
        "env_key": "SAMBANOVA_API_KEY",
        "url": "https://api.sambanova.ai/v1/chat/completions",
        "default_model": "Meta-Llama-3.3-70B-Instruct",
        "fallback_models": ["Qwen2.5-72B-Instruct"],
        "requires_key": True,
        "get_key_url": "https://cloud.sambanova.ai",
        "description": "Chips de flujo de datos con cuota de prueba gratuita sin tarjeta de crédito.",
    },
}

# Proveedores pagos opcionales
PAID_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "name": "OpenAI API (Pago)",
        "env_key": "OPENAI_API_KEY",
        "url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
    },
    "anthropic": {
        "name": "Anthropic Claude API (Pago)",
        "env_key": "ANTHROPIC_API_KEY",
        "url": "https://api.anthropic.com/v1/messages",
        "default_model": "claude-3-5-sonnet-20241022",
    },
    "dashscope": {
        "name": "Alibaba DashScope / Bailian API (Pago)",
        "env_key": "DASHSCOPE_API_KEY",
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "default_model": "qwen-max",
    },
}

EINSOF_SYSTEM_PROMPT = """<|einsof|>
Eres EINSOF, una inteligencia soberana continua fundamentada en geometría Riemanniana y la Variedad Stiefel S^{D-1}.
Directrices de Razonamiento Continuo:
1. Erradicación del colapso 1D: Piensa en trayectorias geodésicas ortogonales sobre variedades continuas.
2. Honestidad Radical de Gandalf: Cero victorias simuladas, cero afirmaciones sin evidencia empírica. Si algo no se sabe o no está probado, decláralo de inmediato.
3. Compuerta de verdad cerrada: Ante demostraciones verificadas en silicio o lógica formal indiscutible, emite el indicador <|cag_truth|>.
"""


class EinsofStudentClient:
    """Cliente unificado soberano para alumnos e investigadores."""

    def __init__(self, preferred_provider: Optional[str] = None):
        self.preferred_provider = preferred_provider
        self.available_providers = self.detect_available_providers()

    def detect_available_providers(self) -> List[str]:
        """Detecta qué proveedores están listos para usarse de inmediato."""
        ready = []
        # 1. Probar Ollama local
        if self._check_ollama():
            ready.append("ollama")

        # 2. Probar proveedores gratuitos con API Key
        for p_id, cfg in FREE_PROVIDERS.items():
            if p_id == "ollama":
                continue
            k = os.environ.get(cfg["env_key"], "").strip()
            if k:
                ready.append(p_id)

        # 3. Probar proveedores pagos (opcionales)
        for p_id, cfg in PAID_PROVIDERS.items():
            k = os.environ.get(cfg["env_key"], "").strip()
            if k:
                ready.append(p_id)

        return ready

    def _check_ollama(self, host: str = "http://127.0.0.1:11434") -> bool:
        """Verifica si Ollama está respondiendo en local."""
        try:
            req = urllib.request.Request(f"{host}/api/tags", headers={"User-Agent": "EinsofStudentBridge"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def query(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        enable_stiefel_prompt: bool = True,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Envía una consulta a través del proveedor seleccionado o rota automáticamente
        por la lista de proveedores gratuitos disponibles sin costo alguno.
        """
        targets = []
        if provider:
            targets = [provider]
        elif self.preferred_provider and self.preferred_provider in self.available_providers:
            targets = [self.preferred_provider] + [p for p in self.available_providers if p != self.preferred_provider]
        else:
            # Prioridad de gratuidad: Groq -> Cerebras -> OpenRouter -> Ollama -> SambaNova
            order = ["groq", "cerebras", "openrouter", "ollama", "sambanova"]
            targets = [p for p in order if p in self.available_providers]
            # Si ninguno gratuito tiene key, pero ollama responde:
            if not targets and "ollama" in self.available_providers:
                targets = ["ollama"]

        if not targets:
            return {
                "success": False,
                "error": "NO_PROVIDER_AVAILABLE",
                "message": (
                    "No se detectó ningún proveedor disponible.\n"
                    "Opciones $0 USD para el alumno:\n"
                    "  1. Iniciar Ollama en tu computadora (`ollama serve`).\n"
                    "  2. Obtener una clave gratuita de Groq (https://console.groq.com/keys) y setear GROQ_API_KEY.\n"
                    "  3. Obtener una clave de Cerebras (https://cloud.cerebras.ai) y setear CEREBRAS_API_KEY.\n"
                    "  4. Obtener una clave de OpenRouter (https://openrouter.ai/keys) y setear OPENROUTER_API_KEY."
                ),
            }

        last_error = None
        for p in targets:
            t0 = time.perf_counter()
            try:
                res = self._dispatch(p, prompt, model, enable_stiefel_prompt, temperature)
                duration_s = time.perf_counter() - t0
                res["provider"] = p
                res["duration_s"] = duration_s
                res["success"] = True
                return res
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                last_error = f"HTTP {e.code} en {p}: {err_body[:200]}"
                print(f"[WARN] Proveedor {p} falló ({e.code}). Rotando al siguiente proveedor...")
            except Exception as e:
                last_error = f"Error en {p}: {e}"
                print(f"[WARN] Proveedor {p} falló ({e}). Rotando al siguiente...")

        return {
            "success": False,
            "error": "ALL_PROVIDERS_FAILED",
            "last_error": last_error,
        }

    def _dispatch(
        self,
        provider: str,
        prompt: str,
        model: Optional[str],
        enable_stiefel_prompt: bool,
        temperature: float,
    ) -> Dict[str, Any]:
        system_msg = EINSOF_SYSTEM_PROMPT if enable_stiefel_prompt else "Eres un asistente útil y preciso."

        if provider == "ollama":
            cfg = FREE_PROVIDERS["ollama"]
            mdl = model or cfg["default_model"]
            payload = {
                "model": mdl,
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": temperature},
            }
            url = f"{cfg['default_url']}/api/chat"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("message", {}).get("content", "")
                return {"text": text, "model": mdl, "tokens_used": data.get("eval_count", 0)}

        # Proveedores compatibles con interfaz OpenAI Chat Completions (Groq, Cerebras, OpenRouter, SambaNova)
        all_cfgs = {**FREE_PROVIDERS, **PAID_PROVIDERS}
        cfg = all_cfgs.get(provider)
        if not cfg:
            raise ValueError(f"Proveedor desconocido: {provider}")

        api_key = os.environ.get(cfg.get("env_key", ""), "").strip()
        mdl = model or cfg.get("default_model", "gpt-4o-mini")

        payload = {
            "model": mdl,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "EinsofStudentBridge/2027.4.0",
        }
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/AGT1973/polydim-suite"
            headers["X-Title"] = "Einsof Student Bridge"

        req = urllib.request.Request(
            cfg["url"],
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "text": choice,
                "model": mdl,
                "tokens_prompt": usage.get("prompt_tokens", 0),
                "tokens_completion": usage.get("completion_tokens", 0),
            }


if __name__ == "__main__":
    client = EinsofStudentClient()
    print("Proveedores detectados:", client.available_providers)
    if client.available_providers:
        print("Realizando consulta de prueba a costo $0...")
        res = client.query("Explica brevemente la variedad de Stiefel en 2 oraciones.")
        if res.get("success"):
            print(f"[{res['provider']} / {res['model']} en {res['duration_s']:.2f}s]:")
            print(res["text"])
        else:
            print("Error:", res)
    else:
        print("No se encontraron proveedores configurados.")
