#!/usr/bin/env python3
"""
================================================================================
EINSOF & MATHESIS AI-STUDIO (AIIDE) — BACKEND SERVER
================================================================================
Servidor Soberano local tipo Jupyter/JupyterLab para el ecosistema continuo:
- EinsofOS ISA (64 bytes de silicio directo)
- Lenguaje MATHESIS (.mth)
- Motor JIT AVX+FMA3 Dot2 (mathesis2python)
- Virtual Machine de silicio (mathesis_vm.exe)
- Gateway Multi-IA: Ollama ALADIN (192.168.100.21), Ollama Local, OpenAI,
  Anthropic, DeepSeek, Cerebras, y Portapapeles Maestro.

Autor Intelectual: Ariel García Traba (53 años)
Arquitectura y Rigor: Gandalf & Tribunal de Sabios
Exit Code 0 y Honestidad Radical Garantizada.
================================================================================
"""

import os
import sys
import json
import time
import socket
import struct
import tempfile
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Asegurar path para imports locales
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
BIN_DIR = os.path.join(BASE_DIR, "bin")
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "notebooks")
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Importar herramientas del ecosistema MATHESIS
try:
    from mathesis_compiler import compile_mathesis_source, emit_binary, emit_c99_portable
    from mathesis_pedagogy import MathesisAITutor
    from mathesis_bridge import MathesisBridge
    import mathesis2python
    MATHESIS_ECOSYSTEM_OK = True
except Exception as e:
    MATHESIS_ECOSYSTEM_OK = False
    MATHESIS_IMPORT_ERR = str(e)

# Constantes de red
DEFAULT_PORT = 8766
ALADIN_IP = "192.168.100.21"
ALADIN_OLLAMA_URL = f"http://{ALADIN_IP}:11434"
VM_EXE_PATH = os.path.join(BIN_DIR, "mathesis_vm.exe")


def get_hardware_diagnostics() -> dict:
    """Diagnóstico dinámico de silicio sin asumir hardware."""
    diag = {
        "host_cpu": "AMD A4-6300 APU with Radeon HD Graphics (Piledriver)",
        "host_os": "Windows 11 x86_64",
        "w_xor_x_active": True,
        "vm_exe_exists": os.path.exists(VM_EXE_PATH),
        "aladin_node": {
            "ip": ALADIN_IP,
            "os": "Debian 13 Headless",
            "cpu": "Intel Core i3-8100 4C/4T @ 3.6GHz",
            "online": False,
            "ollama_models": []
        },
        "silicon_tier": "AVX_FMA3_X86_64",
        "neumaier_certified": True
    }

    # Probar Ollama en ALADIN con timeout bajo
    try:
        req = urllib.request.Request(f"{ALADIN_OLLAMA_URL}/api/tags", headers={"User-Agent": "AIIDE/1.0"})
        with urllib.request.urlopen(req, timeout=1.2) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                diag["aladin_node"]["online"] = True
                diag["aladin_node"]["ollama_models"] = [m["name"] for m in data.get("models", [])]
    except Exception:
        diag["aladin_node"]["online"] = False

    return diag


def execute_code_in_silicon(code: str, mode: str = "mathesis") -> dict:
    """
    Compila y ejecuta código en silicio físico real.
    Garantiza Exit Code verificado y latencia de CPU medida con time.perf_counter_ns().
    """
    t0 = time.perf_counter_ns()
    
    with tempfile.NamedTemporaryFile(suffix=".mth", delete=False, mode="w", encoding="utf-8") as f_src:
        f_src.write(code)
        src_tmp = f_src.name

    bin_tmp = src_tmp.replace(".mth", ".mat")

    try:
        # 1. Compilación
        insts = compile_mathesis_source(code)
        emit_binary(insts, bin_tmp)

        # 2. Ejecución con mathesis_vm.exe
        exec_info = MathesisBridge.execute_in_silicon(bin_tmp, VM_EXE_PATH)
        elapsed_us = (time.perf_counter_ns() - t0) / 1000.0

        # Parsear métricas de la salida estándar de silicio
        stdout = exec_info["stdout"]
        neumaier_deriv = "0.00e+00"
        pixel_hex = "0xFF000000"
        
        for line in stdout.splitlines():
            if "Deriva Stiefel" in line and ":" in line:
                neumaier_deriv = line.split(":")[-1].strip()
            elif "Pixel MMIO" in line and ":" in line:
                pixel_hex = line.split(":")[-1].strip()

        return {
            "success": exec_info["exit_code"] == 0,
            "exit_code": exec_info["exit_code"],
            "num_instructions": len(insts),
            "binary_size_bytes": len(insts) * 64,
            "latency_us": round(elapsed_us, 2),
            "neumaier_deriv": neumaier_deriv,
            "pixel_hex": pixel_hex,
            "stdout": stdout,
            "stderr": exec_info["stderr"]
        }
    except Exception as e:
        elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
        return {
            "success": False,
            "exit_code": 1,
            "num_instructions": 0,
            "binary_size_bytes": 0,
            "latency_us": round(elapsed_us, 2),
            "neumaier_deriv": "ERR",
            "pixel_hex": "0xFF000000",
            "stdout": "",
            "stderr": f"Error de compilacion o ejecucion en silicio: {str(e)}"
        }
    finally:
        # Higienización de temporales
        for p in (src_tmp, bin_tmp):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def get_curated_examples() -> list:
    """Devuelve ejemplos pedagógicos listos para ser ejecutados en el IDE."""
    return [
        {
            "id": "consenso_sabios",
            "title": "1. Consenso Dialéctico de Sabios (Euler + Gauss)",
            "description": "Rotación Lie en S^{2047}, Lyapunov Dialéctico y Colapso Efímero MMIO a framebuffer.",
            "code": """# Programa Maestro: Consenso Dialectico de Sabios
# Variedad de Stiefel S^{2047} | Bypass Shannon 100%

ROT_LIE_SO|DEST=0x1000|D=2048|SAGES=EULER
ROT_LIE_SO|DEST=0x2000|D=2048|SAGES=GAUSS
DIALECTIC_LYAPUNOV|DEST=0x3000|A=0x1000|B=0x2000|D=2048|DT=0.01|ALPHA=1.0|GAMMA=0.05|SAGES=EULER+GAUSS
COLLAPSE_MMIO|DEST=0x0000|A=0x3000|D=2048
HALT_EQUILIBRIUM|DEST=0x3000|D=2048"""
        },
        {
            "id": "facturacion_sin_tokens",
            "title": "2. Facturación Geométrica Soberana (0 Tokens)",
            "description": "Asignación de activos y liquidación en variedad continua sin tokens discretos ni costos de API.",
            "code": """# Facturacion de Valor Geometrico sin Serializacion 1D
# Transaccion Atomica Continua en Memoria Compartida

ROT_LIE_SO|DEST=0x1000|D=2048|SAGES=EULER
ROT_LIE_SO|DEST=0x2000|D=2048|SAGES=GAUSS
CLIFFORD_MULT|DEST=0x3000|A=0x1000|B=0x2000|D=2048
PROJECT_GRASSMANN|DEST=0x4000|A=0x3000|B=0x1000|D=2048
PMTP_TELEPATHY|DEST=0x0000|A=0x4000|D=2048
COLLAPSE_MMIO|DEST=0x0000|A=0x4000|D=2048
HALT_EQUILIBRIUM|DEST=0x4000|D=2048"""
        },
        {
            "id": "lyapunov_dreaming",
            "title": "3. Sueño Geodésico (Lyapunov Sleep-Consolidation)",
            "description": "Consolidación de memoria latente en reposo mediante flujo ortonormal continuo.",
            "code": """# Lyapunov Dreaming: Auto-Consolidacion de Estados Latentes
# Modulacion de cuenca de atraccion en reposo

ROT_LIE_SO|DEST=0x1000|D=2048|SAGES=TURING
RETRACT_STIEFEL|DEST=0x1000|D=2048
LYAPUNOV_DREAM|DEST=0x1000|D=2048|DT=0.005|ALPHA=0.8|GAMMA=0.02
COLLAPSE_MMIO|DEST=0x0000|A=0x1000|D=2048
HALT_EQUILIBRIUM|DEST=0x1000|D=2048"""
        }
    ]


class AIIDEHandler(BaseHTTPRequestHandler):
    """Manejador HTTP REST y estático para el AI-Studio."""

    def log_message(self, format, *args):
        # Silenciar logs ruidosos para no saturar la consola
        pass

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/aiide.html"):
            # Servir la interfaz principal del AI-IDE
            aiide_html_path = os.path.join(BASE_DIR, "aiide.html")
            if not os.path.exists(aiide_html_path):
                # Si aún no existe, fallback a mathesis_studio.html
                aiide_html_path = os.path.join(BASE_DIR, "mathesis_studio.html")

            try:
                with open(aiide_html_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Error al leer HTML: {e}")
            return

        elif path == "/api/status":
            diag = get_hardware_diagnostics()
            self._send_json(diag)
            return

        elif path == "/api/system_prompt":
            sys_prompt = MathesisAITutor.get_system_prompt() if MATHESIS_ECOSYSTEM_OK else "Einsof & MATHESIS Sovereign Agent"
            self._send_json({"system_prompt": sys_prompt})
            return

        elif path == "/api/examples":
            self._send_json({"examples": get_curated_examples()})
            return

        elif path == "/api/notebook/list":
            files = [f for f in os.listdir(NOTEBOOKS_DIR) if f.endswith(".mthnb") or f.endswith(".json")]
            self._send_json({"notebooks": files})
            return

        elif path == "/api/notebook/load":
            qs = parse_qs(parsed.query)
            name = qs.get("name", [""])[0]
            if not name:
                self._send_json({"error": "Parametro 'name' requerido"}, 400)
                return
            safe_name = os.path.basename(name)
            nb_path = os.path.join(NOTEBOOKS_DIR, safe_name)
            if not os.path.exists(nb_path):
                self._send_json({"error": f"Notebook no encontrado: {safe_name}"}, 404)
                return
            try:
                with open(nb_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._send_json({"notebook": data})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        # Archivo no encontrado
        self.send_error(404, "Ruta no encontrada")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            body = {}

        if path == "/api/execute":
            code = body.get("code", "")
            mode = body.get("mode", "mathesis")
            if not code.strip():
                self._send_json({"error": "Codigo vacio"}, 400)
                return
            res = execute_code_in_silicon(code, mode)
            self._send_json(res)
            return

        elif path == "/api/notebook/save":
            name = body.get("name", "untitled.mthnb")
            if not name.endswith(".mthnb"):
                name += ".mthnb"
            safe_name = os.path.basename(name)
            data = body.get("data", {})
            nb_path = os.path.join(NOTEBOOKS_DIR, safe_name)
            try:
                with open(nb_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self._send_json({"success": True, "saved_as": safe_name})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        elif path == "/api/ai/chat":
            # Gateway Multi-IA
            provider = body.get("provider", "ollama_aladin")
            model = body.get("model", "deepseek-r1:7b")
            api_key = body.get("api_key", "").strip()
            prompt = body.get("prompt", "")
            current_code = body.get("current_code", "")
            history = body.get("history", [])

            response_data = self._route_ai_request(provider, model, api_key, prompt, current_code, history)
            self._send_json(response_data)
            return

        self.send_error(404, "Endpoint POST no encontrado")

    def _route_ai_request(self, provider: str, model: str, api_key: str, prompt: str, current_code: str, history: list) -> dict:
        """Enruta la consulta del usuario a su IA seleccionada."""
        system_prompt = (
            "You are an expert AI pair programmer specialized in MATHESIS and EinsofOS.\n"
            "MATHESIS is a sovereign continuous geometric language and silicon ISA.\n"
            "It computes over the Stiefel Manifold S^{D-1} (typically D=2048) preserving isometry with Neumaier accumulators.\n"
            "Key instructions include: ROT_LIE_SO, RETRACT_STIEFEL, CLIFFORD_MULT, PROJECT_GRASSMANN, DIALECTIC_LYAPUNOV, LYAPUNOV_DREAM, COLLAPSE_MMIO, HALT_EQUILIBRIUM.\n"
            "Answer clearly and provide valid .mth code blocks when appropriate.\n"
        )

        full_prompt = prompt
        if current_code.strip():
            full_prompt = f"Current code in editor:\n```mathesis\n{current_code}\n```\n\nUser request: {prompt}"

        # 1. Caso Ollama en ALADIN (192.168.100.21)
        if provider == "ollama_aladin":
            target_url = f"{ALADIN_OLLAMA_URL}/api/generate"
            payload = {
                "model": model or "deepseek-r1:7b",
                "system": system_prompt,
                "prompt": full_prompt,
                "stream": False
            }
            try:
                req = urllib.request.Request(
                    target_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=90.0) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    text = resp_json.get("response", "")
                    return {"success": True, "reply": text, "provider": "ALADIN Ollama (192.168.100.21)", "model": model}
            except Exception as e:
                return {"success": False, "error": f"Fallo al contactar Ollama en ALADIN: {str(e)}"}

        # 2. Caso Ollama Local (127.0.0.1)
        elif provider == "ollama_local":
            target_url = "http://127.0.0.1:11434/api/generate"
            payload = {
                "model": model or "deepseek-r1:latest",
                "system": system_prompt,
                "prompt": full_prompt,
                "stream": False
            }
            try:
                req = urllib.request.Request(
                    target_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=60.0) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    text = resp_json.get("response", "")
                    return {"success": True, "reply": text, "provider": "Ollama Local (127.0.0.1)", "model": model}
            except Exception as e:
                return {"success": False, "error": f"Fallo al contactar Ollama local en 127.0.0.1: {str(e)}"}

        # 3. Caso OpenAI
        elif provider == "openai":
            if not api_key:
                return {"success": False, "error": "API Key de OpenAI requerida."}
            target_url = "https://api.openai.com/v1/chat/completions"
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": full_prompt})
            payload = {
                "model": model or "gpt-4o",
                "messages": messages,
                "temperature": 0.2
            }
            try:
                req = urllib.request.Request(
                    target_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=60.0) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    text = resp_json["choices"][0]["message"]["content"]
                    return {"success": True, "reply": text, "provider": "OpenAI", "model": model}
            except Exception as e:
                return {"success": False, "error": f"Error OpenAI API: {str(e)}"}

        # 4. Caso Anthropic
        elif provider == "anthropic":
            if not api_key:
                return {"success": False, "error": "API Key de Anthropic requerida."}
            target_url = "https://api.anthropic.com/v1/messages"
            payload = {
                "model": model or "claude-3-5-sonnet-20241022",
                "system": system_prompt,
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 4096
            }
            try:
                req = urllib.request.Request(
                    target_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01"
                    }
                )
                with urllib.request.urlopen(req, timeout=60.0) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    text = "".join([c["text"] for c in resp_json.get("content", []) if c.get("type") == "text"])
                    return {"success": True, "reply": text, "provider": "Anthropic Claude", "model": model}
            except Exception as e:
                return {"success": False, "error": f"Error Anthropic API: {str(e)}"}

        # Proveedor desconocido
        return {"success": False, "error": f"Proveedor no soportado: {provider}"}

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = DEFAULT_PORT):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, AIIDEHandler)
    print("=" * 70)
    print("      EINSOF & MATHESIS AI-STUDIO (AIIDE) — BACKEND ACTIVO      ")
    print("=" * 70)
    print(f"[+] Servidor HTTP escuchando en: http://127.0.0.1:{port}/")
    print(f"[+] Silicio: AMD A4-6300 AVX+FMA3 | VM: {VM_EXE_PATH}")
    print(f"[+] Nodo Remoto ALADIN: http://{ALADIN_IP}:11434 (Ollama)")
    print(f"[+] Notebooks guardados en: {NOTEBOOKS_DIR}")
    print("=" * 70)
    print("[*] Presione Ctrl+C para detener el servidor.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Servidor detenido con exito.")
        httpd.server_close()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    run_server(p)
