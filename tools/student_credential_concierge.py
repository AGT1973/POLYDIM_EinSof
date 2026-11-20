# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF — Concierge de Credenciales y Acompañamiento al Alumno (Estándar 2030)
=====================================================================================
Sello de Calibración: 19.11.2026 | Ecosistema POLYDIM-EINSOF | Ariel García Traba

PROPÓSITO:
La IA suple la falta de conocimiento técnico del alumno. El alumno NO tiene que
saber Git, ni cómo editar variables de entorno, ni configurar archivos de sistema.
Este módulo permite que la IA guíe al alumno paso a paso para obtener sus API Keys
gratuitas ($0 USD), navegue con él si tiene navegador disponible, y guarde las llaves
de forma segura y persistente en `~/.ai_credentials.env`.
"""

import os
import sys
import argparse
from pathlib import Path

CREDENTIALS_FILE = Path.home() / ".ai_credentials.env"

PROVIDERS_GUIDE = {
    "huggingface": {
        "env_var": "HF_TOKEN",
        "name": "Hugging Face Hub Token",
        "free": True,
        "url": "https://huggingface.co/settings/tokens",
        "description": "Permite descargar modelos abiertos y adaptadores LoRA de Stiefel a tu máquina a costo $0 USD.",
        "pasos": [
            "1. Entrá a https://huggingface.co/settings/tokens (iniciá sesión con Google o GitHub si no tenés cuenta).",
            "2. Hacé clic en el botón azul 'Create new token' (o 'New token').",
            "3. En 'Token type', elegí 'Read' (Lectura). En 'Token name', poné 'einsof-alumno'.",
            "4. Hacé clic en 'Create token'.",
            "5. Copiá el texto que empieza con 'hf_...' y pegámelo acá en el chat. Yo me encargo de guardarlo de forma segura."
        ]
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "name": "Groq Cloud API Key",
        "free": True,
        "url": "https://console.groq.com/keys",
        "description": "Inferencia ultra-rápida (500 tokens/seg) en modelos libres (Qwen, LLaMA) con cuota 100% gratuita.",
        "pasos": [
            "1. Entrá a https://console.groq.com/keys (iniciá sesión con Google o GitHub).",
            "2. Hacé clic en 'Create API Key'.",
            "3. En el nombre podés poner 'einsof' y hacer clic en 'Submit'.",
            "4. Copiá la clave que empieza con 'gsk_...' y pegámela acá en el chat."
        ]
    },
    "openrouter": {
        "env_var": "OPENROUTER_API_KEY",
        "name": "OpenRouter Free Pool Key",
        "free": True,
        "url": "https://openrouter.ai/keys",
        "description": "Acceso a la flota multipolar de modelos gratuitos (:free) para deliberación entre sabios.",
        "pasos": [
            "1. Entrá a https://openrouter.ai/keys e iniciá sesión con Google.",
            "2. Hacé clic en 'Create Key'.",
            "3. Copiá la clave que empieza con 'sk-or-v1-...' y pegámela acá."
        ]
    },
    "sambanova": {
        "env_var": "SAMBANOVA_API_KEY",
        "name": "SambaNova Cloud Key",
        "free": True,
        "url": "https://cloud.sambanova.ai/apis",
        "description": "Inferencia de alta velocidad en silicio SN40L para modelos de razonamiento profundo a costo $0.",
        "pasos": [
            "1. Entrá a https://cloud.sambanova.ai/apis.",
            "2. Hacé clic en 'Create API Key'.",
            "3. Copiá la clave y pegámela acá en el chat."
        ]
    },
    "bailian": {
        "env_var": "DASHSCOPE_API_KEY",
        "alt_var": "BAILIAN_KEY",
        "name": "Alibaba Cloud Bailian / DashScope (Qwen 3.8 & Qwen-Max)",
        "free": False,
        "url": "https://bailian.console.aliyun.com/",
        "description": "Potencia de frontera: Qwen-Max y Qwen 3.8. Con una recarga mínima de solo $5 USD (frente a los $200/mes de suscripciones cerradas) tenés millones de tokens de razonamiento de grado frontera durante meses.",
        "pasos": [
            "1. Entrá a https://bailian.console.aliyun.com/ (o Alibaba Cloud Model Studio International: https://www.alibabacloud.com/en/product/model-studio).",
            "2. Registrate o iniciá sesión y cargá el saldo mínimo ($5 USD, rinde millones de tokens y dura meses de trabajo intenso).",
            "3. En el menú lateral izquierdo, andá a 'API-KEY' y hacé clic en 'Create API Key'.",
            "4. Copiá la clave generada (empieza con 'sk-...') y pegámela acá en el chat.",
            "5. Yo la guardo automáticamente en tu archivo local seguro para que /call qwen-max y /council la usen sin vueltas."
        ]
    }
}


def load_credentials() -> dict:
    creds = {}
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    creds[k.strip()] = v.strip().strip('"').strip("'")
    return creds


def save_credential(env_var: str, value: str) -> None:
    creds = load_credentials()
    creds[env_var] = value
    if env_var in ("DASHSCOPE_API_KEY", "BAILIAN_KEY"):
        creds["DASHSCOPE_API_KEY"] = value
        creds["BAILIAN_KEY"] = value
        os.environ["DASHSCOPE_API_KEY"] = value
        os.environ["BAILIAN_KEY"] = value
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        f.write("# Credenciales Soberanas POLYDIM-EINSOF (Estándar 2030)\n")
        f.write("# Guardadas de forma local y segura para el alumno sin tocar variables del sistema.\n\n")
        for k, v in creds.items():
            f.write(f'{k}="{v}"\n')
    # También inyectar en el entorno del proceso actual
    os.environ[env_var] = value
    print(f"[OK] Credencial {env_var} guardada exitosamente en {CREDENTIALS_FILE}")


def print_guide(provider: str) -> None:
    p = provider.lower()
    if p not in PROVIDERS_GUIDE:
        print(f"Proveedor desconocido: {provider}. Disponibles: {list(PROVIDERS_GUIDE.keys())}")
        return
    info = PROVIDERS_GUIDE[p]
    print(f"\n======================================================================")
    print(f"  GUÍA PARA EL ALUMNO: Cómo obtener {info['name']} (100% GRATIS)")
    print(f"======================================================================")
    print(f"  Propósito: {info['description']}")
    print(f"  Enlace directo: {info['url']}\n")
    print("  Instrucciones paso a paso:")
    for paso in info["pasos"]:
        print(f"    {paso}")
    print(f"======================================================================\n")


def print_status() -> None:
    creds = load_credentials()
    print("\n======================================================================")
    print("  ESTADO DE CREDENCIALES DEL ALUMNO (Almacenamiento Local Seguro)")
    print(f"  Archivo: {CREDENTIALS_FILE}")
    print("======================================================================")
    for p_id, p_info in PROVIDERS_GUIDE.items():
        var_name = p_info["env_var"]
        has_key = var_name in creds or var_name in os.environ
        status_str = "[OK] CONFIGURADA" if has_key else "[ ] FALTANTE (Gratis)"
        print(f"  {p_info['name']:<30} ({var_name:<20}): {status_str}")
        if not has_key:
            print(f"    -> Link para el alumno: {p_info['url']}")
    print("======================================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Concierge de Credenciales para Alumnos POLYDIM-EINSOF")
    parser.add_argument("--status", action="store_true", help="Muestra el estado de credenciales configuradas")
    parser.add_argument("--guide", type=str, help="Muestra la guía paso a paso para un proveedor (huggingface, groq, openrouter, sambanova)")
    parser.add_argument("--save", nargs=2, metavar=("VAR", "VAL"), help="Guarda una credencial: --save HF_TOKEN hf_xxx")
    args = parser.parse_args()

    if args.save:
        save_credential(args.save[0], args.save[1])
    elif args.guide:
        print_guide(args.guide)
    else:
        print_status()


if __name__ == "__main__":
    main()
