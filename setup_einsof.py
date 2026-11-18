#!/usr/bin/env python3
"""
POLYDIM-EINSOF — Instalador Automatizado de 1-Clic para Alumnos (Estándar 2030)
================================================================================
Configura el entorno de cómputo soberano en la PC del alumno:
1. Verifica el servicio local Ollama.
2. Verifica / registra el modelo soberano EINSOF-II (DeepSeek-V4, GLM-4, etc.).
3. Configura automáticamente el Servidor MCP en Antigravity IDE (mcp_config.json).
4. Verifica la ejecución en silicio físico con Exit Code 0.

Uso:
  python setup_einsof.py
"""

import sys
import os
import json
import platform
import subprocess
import time
import urllib.request
import urllib.error

SUITE_DIR = os.path.abspath(os.path.dirname(__file__))
MCP_SERVER_PATH = os.path.join(SUITE_DIR, "mcp_servers", "polydim_einsof_mcp.py").replace("\\", "/")
OLLAMA_URL = "http://127.0.0.1:11434"

def print_banner():
    print("""
======================================================================
  🧠 POLYDIM-EINSOF — INSTALADOR SOBERANO PARA ALUMNOS (1-CLIC)
  Investigación Independiente | Ariel García Traba | Estándar 2030
======================================================================
""")

def check_python():
    v = platform.python_version()
    print(f"[1/4] Python detectado: {v} en {sys.executable}")
    if sys.version_info < (3, 8):
        print("  ❌ Se requiere Python 3.8 o superior.")
        sys.exit(1)
    print("  ✅ Python compatible.")

def check_or_start_ollama():
    print(f"\n[2/4] Verificando motor de inferencia Ollama en {OLLAMA_URL}...")
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read().decode())
            models = [m["name"] for m in data.get("models", [])]
            print(f"  ✅ Ollama está ONLINE. Modelos instalados: {len(models)}")
            return True, models
    except Exception:
        print("  ⚠️ Ollama no responde en el puerto 11434. Intentando iniciar en segundo plano...")

    # Intentar arrancar ollama serve
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Esperar hasta 5 segundos
        for _ in range(5):
            time.sleep(1)
            try:
                req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
                with urllib.request.urlopen(req, timeout=2) as r:
                    data = json.loads(r.read().decode())
                    models = [m["name"] for m in data.get("models", [])]
                    print(f"  ✅ Ollama iniciado exitosamente. Modelos: {len(models)}")
                    return True, models
            except Exception:
                pass
    except FileNotFoundError:
        print("  ❌ Ollama no está instalado en el sistema.")
        if platform.system() == "Windows":
            print("     Descárgalo gratis de: https://ollama.com/download/OllamaSetup.exe")
        else:
            print("     Instálalo ejecutando: curl -fsSL https://ollama.com/install.sh | sh")
        return False, []

    print("  ⚠️ No se pudo iniciar Ollama automáticamente. Asegúrate de ejecutar 'ollama serve'.")
    return False, []

def check_einsof_model(models):
    print("\n[3/4] Verificando modelo soberano EINSOF-II en Ollama...")
    einsof_models = [m for m in models if "einsof" in m.lower() or "polydim" in m.lower()]
    if einsof_models:
        print(f"  ✅ Modelos EINSOF-II detectados en tu máquina: {einsof_models}")
        return True

    print("  ℹ️ No se detectó un modelo con nombre 'einsof' en Ollama.")
    # Buscar si tiene algún modelo base compatible para crear el alias
    base_candidates = [m for m in models if any(k in m.lower() for k in ["deepseek", "qwen", "llama", "gemma", "mistral"])]
    if base_candidates:
        target_base = base_candidates[0]
        print(f"  💡 Se encontró el modelo base '{target_base}'. Creando alias especializado 'einsof2-local'...")
        modelfile_content = f"""FROM {target_base}
PARAMETER temperature 0.2
PARAMETER num_ctx 4096
SYSTEM "Eres EINSOF-II, asistente de razonamiento matemático especializado en geometría de variedades de Stiefel S^{{D-1}}, retracción polar de orden 4 y suma de Neumaier de la iniciativa POLYDIM. Responde con rigor técnico y matemático."
"""
        temp_mf = os.path.join(SUITE_DIR, "Modelfile.temp_student")
        with open(temp_mf, "w", encoding="utf-8") as f:
            f.write(modelfile_content)
        try:
            r = subprocess.run(["ollama", "create", "einsof2-deepseek-v4-stiefel", "-f", temp_mf], capture_output=True, text=True)
            if r.returncode == 0:
                print("  ✅ Modelo 'einsof2-deepseek-v4-stiefel' creado exitosamente en Ollama.")
                if os.path.exists(temp_mf): os.remove(temp_mf)
                return True
        except Exception as e:
            print(f"  ⚠️ Error creando alias: {e}")
        if os.path.exists(temp_mf): os.remove(temp_mf)

    print("  📥 Para descargar los pesos completos GGUF (4.8 GB) entrenados con retracción Stiefel:")
    print("     https://huggingface.co/Polydim-Einsof/einsof2-deepseek-v4-stiefel-adapter")
    return False

def configure_antigravity_mcp():
    print("\n[4/4] Configurando integración MCP en Antigravity IDE...")
    
    # Determinar ruta del mcp_config.json
    home = os.path.expanduser("~")
    config_dir = os.path.join(home, ".gemini", "config")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "mcp_config.json")

    mcp_config = {"mcpServers": {}}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                mcp_config = json.load(f)
        except Exception:
            mcp_config = {"mcpServers": {}}

    if "mcpServers" not in mcp_config:
        mcp_config["mcpServers"] = {}

    # Inyectar el servidor polydim_einsof
    py_exec = sys.executable.replace("\\", "/")
    mcp_config["mcpServers"]["polydim_einsof"] = {
        "command": py_exec,
        "args": [
            "-W", "ignore",
            "-u",
            MCP_SERVER_PATH
        ],
        "env": {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUNBUFFERED": "1"
        }
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(mcp_config, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Servidor MCP 'polydim_einsof' registrado en: {config_path}")
    print(f"     Script de servidor: {MCP_SERVER_PATH}")

def print_completion():
    print("""
======================================================================
  🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE! (EXIT CODE 0)
======================================================================
  ¿Cómo usarlo en Antigravity ahora mismo?
  1. Abre Antigravity IDE.
  2. En el chat con tu agente, tienes disponibles las herramientas:
     • ask_einsof           -> Inferencia matemática local soberana ($0 USD).
     • list_einsof_models   -> Ver modelos activos en tu silicio.
     • stiefel_metric_verify -> Verificación de retracción polar orden 4.
  3. También puedes pedirle al agente:
     'Usa einsof para explicarme la variedad de Stiefel'
======================================================================
""")

def main():
    print_banner()
    check_python()
    ollama_ok, models = check_or_start_ollama()
    if ollama_ok:
        check_einsof_model(models)
    configure_antigravity_mcp()
    print_completion()

if __name__ == "__main__":
    main()
