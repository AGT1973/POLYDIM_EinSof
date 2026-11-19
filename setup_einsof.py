#!/usr/bin/env python3
"""
POLYDIM-EINSOF — Instalador Soberano de 1-Clic para Antigravity IDE (v2.0 Hardened)
====================================================================================
Sello de Calibración: 19.11.2026 | Ecosistema POLYDIM-EINSOF | Ariel García Traba
Configura y verifica en silicio el entorno EINSOF-II + Mathesis PMTP:
  1. Verifica Python >= 3.8 y asegura NumPy (>= 1.26 recomendado) antes de registrar MCP.
  2. Descubre Ollama con failover multi-nodo: local (127.0.0.1:11434) -> ALADIN LAN (192.168.100.21:11434).
  3. Valida modelos reales disponibles (sin crear alias engañosos sobre modelos ajenos).
  4. Respalda y configura ~/.gemini/config/mcp_config.json verificando rutas fisicas en disco.
  5. Ejecuta smoke-test real JSON-RPC 2.0 stdio (Stiefel <= 1e-15 + rechazo k > D) antes de Exit Code 0.

Uso:
  python setup_einsof.py [--aladin-host 192.168.100.21] [--open-intro]
"""

import sys
import os
import json
import time
import shutil
import argparse
import platform
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

SUITE_DIR = Path(__file__).resolve().parent
MCP_DIR = SUITE_DIR / "mcp_servers"
LOCAL_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_ALADIN_IP = os.environ.get("ALADIN_HOST", "192.168.100.21")


def print_banner():
    print("""
======================================================================
  POLYDIM-EINSOF — INSTALADOR SOBERANO ANTIGRAVITY (v2.0 HARDENED)
  Investigacion Independiente | Ariel Garcia Traba | Estandar 2030
  Sello de Calibracion: 19.11.2026
======================================================================
""")


def check_python_and_numpy():
    v = platform.python_version()
    print(f"[1/5] Python detectado: {v} en {sys.executable}")
    if sys.version_info < (3, 8):
        print("  [X] Se requiere Python 3.8 o superior.")
        sys.exit(1)
    try:
        import numpy as np
        print(f"  [OK] Python compatible y NumPy v{np.__version__} disponible.")
    except ImportError:
        print("  [!] NumPy no encontrado (requerido por el servidor MCP). Instalando wheel binario precompilado...")
        res = subprocess.run([sys.executable, "-m", "pip", "install", "--only-binary=:all:", "numpy"], capture_output=True, text=True)
        if res.returncode != 0:
            res = subprocess.run([sys.executable, "-m", "pip", "install", "numpy"], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  [X] Error instalando NumPy: {res.stderr.strip()[:300]}")
            sys.exit(1)
        import numpy as np
        print(f"  [OK] NumPy v{np.__version__} instalado correctamente.")


def _probe_ollama(url: str, timeout: float = 2.0) -> tuple[bool, list[str]]:
    try:
        req = urllib.request.Request(f"{url.rstrip('/')}/api/tags")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
            models = [m["name"] for m in data.get("models", [])]
            return True, models
    except Exception:
        return False, []


def check_or_start_ollama(aladin_ip: str) -> tuple[str | None, list[str], bool]:
    """Retorna (endpoint_activo, lista_modelos, es_local)."""
    env_url = os.environ.get("OLLAMA_HOST", "").strip()
    if env_url and not env_url.startswith(("http://", "https://")):
        env_url = f"http://{env_url}"

    print(f"\n[2/5] Descubriendo motor Ollama (Local -> ALADIN {aladin_ip}:11434)...")
    if env_url:
        ok, models = _probe_ollama(env_url, timeout=2.0)
        if ok:
            print(f"  [OK] Ollama ONLINE via OLLAMA_HOST={env_url} ({len(models)} modelos).")
            return env_url.rstrip("/"), models, ("127.0.0.1" in env_url or "localhost" in env_url)

    ok, models = _probe_ollama(LOCAL_OLLAMA_URL, timeout=2.0)
    if ok:
        print(f"  [OK] Ollama local ONLINE en {LOCAL_OLLAMA_URL} ({len(models)} modelos).")
        return LOCAL_OLLAMA_URL, models, True

    print("  [!] Ollama local no responde. Intentando iniciar 'ollama serve'...")
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(5):
            time.sleep(1)
            ok, models = _probe_ollama(LOCAL_OLLAMA_URL, timeout=2.0)
            if ok:
                print(f"  [OK] Ollama local iniciado ({len(models)} modelos).")
                return LOCAL_OLLAMA_URL, models, True
    except FileNotFoundError:
        print("  [i] Binario local 'ollama' no instalado en PATH.")
    except Exception as e:
        print(f"  [!] No se pudo iniciar Ollama local: {e}")

    aladin_url = f"http://{aladin_ip}:11434"
    ok, models = _probe_ollama(aladin_url, timeout=2.5)
    if ok:
        print(f"  [OK] Failover LAN activo -> Nodo ALADIN ONLINE en {aladin_url} ({len(models)} modelos).")
        return aladin_url, models, False

    print("  [!] Ningun servidor Ollama local o ALADIN responde actualmente.")
    print("      Las herramientas matematicas Stiefel/PMTP seguiran funcionando 100% en silicio local.")
    return None, [], False


def resolve_einsof_model(endpoint: str | None, models: list[str], is_local: bool) -> str:
    print("\n[3/5] Verificando catalogo real de modelos EINSOF-II...")
    if is_local and endpoint and not models and os.environ.get("EINSOF_AUTO_PULL", "") == "1":
        print("  [i] Ollama local tiene 0 modelos. Descargando modelo base ligero qwen2.5-coder:1.5b...")
        subprocess.run(["ollama", "pull", "qwen2.5-coder:1.5b"], check=False)
        _, models = _probe_ollama(endpoint, timeout=2.0)

    if not endpoint or not models:
        print("  [i] Sin catalogo Ollama activo. Usando Motor Analitico Soberano Local (einsof2-analytical-stiefel, $0 USD).")
        return "einsof2-analytical-stiefel"

    sovereign = [
        m for m in models
        if any(k in m.lower() for k in ("einsof2", "mathesis", "einsof", "polydim"))
    ]
    if sovereign:
        # Prioritize reasoning EINSOF-II / Mathesis models over lightweight comms SLMs
        chosen = sovereign[0]
        for pref in ("einsof2-deepseek", "einsof2-", "mathesis-quantum", "einsof"):
            hits = [m for m in sovereign if pref in m.lower() and "comms" not in m.lower()]
            if hits:
                chosen = hits[0]
                break
        print(f"  [OK] Modelos soberanos detectados ({len(sovereign)}) -> seleccionado '{chosen}'.")
        return chosen

    if is_local:
        compatible = [m for m in models if any(k in m.lower() for k in ("deepseek", "qwen", "gemma", "glm", "llama", "mistral"))]
        if compatible:
            base = compatible[0]
            alias_name = "einsof2-local-stiefel"
            print(f"  [i] Modelo base local '{base}' detectado. Creando perfil honesto '{alias_name}'...")
            modelfile_content = (
                f"FROM {base}\n"
                "PARAMETER temperature 0.2\n"
                "PARAMETER num_ctx 4096\n"
                f'SYSTEM "Eres EINSOF-II (perfil local sobre {base}), asistente matematico especializado en variedad de Stiefel St(k,D), retraccion polar QDWH y suma de Neumaier."\n'
            )
            temp_mf = SUITE_DIR / "Modelfile.temp_student"
            temp_mf.write_text(modelfile_content, encoding="utf-8")
            try:
                r = subprocess.run(["ollama", "create", alias_name, "-f", str(temp_mf)], capture_output=True, text=True)
                if r.returncode == 0:
                    print(f"  [OK] Perfil '{alias_name}' creado sobre '{base}'.")
                    return alias_name
            except Exception as e:
                print(f"  [!] No se pudo crear perfil local: {e}")
            finally:
                if temp_mf.exists():
                    temp_mf.unlink()
            return base

    chosen = models[0]
    print(f"  [OK] Usando modelo disponible en {endpoint}: '{chosen}'.")
    return chosen


def _resolve_mcp_paths() -> tuple[Path, Path | None]:
    einsof_mcp = MCP_DIR / "polydim_einsof_mcp.py"
    if not einsof_mcp.is_file():
        print(f"  [X] ERROR CRITICO: No existe {einsof_mcp}. Verifica la integridad del repositorio.")
        sys.exit(1)

    mathesis_mcp = None
    for cand in (MCP_DIR / "mathesis_mcp_server.py", SUITE_DIR / "mathesis_mcp_server.py"):
        if cand.is_file():
            mathesis_mcp = cand
            break
    return einsof_mcp, mathesis_mcp


def configure_antigravity_mcp(endpoint: str | None, default_model: str) -> tuple[Path, dict]:
    print("\n[4/5] Configurando integracion MCP en Antigravity IDE...")
    einsof_mcp, mathesis_mcp = _resolve_mcp_paths()

    config_dir = Path.home() / ".gemini" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "mcp_config.json"

    mcp_config = {"mcpServers": {}}
    if config_path.exists():
        try:
            mcp_config = json.loads(config_path.read_text(encoding="utf-8"))
            backup_path = config_dir / "mcp_config.json.bak"
            shutil.copy2(config_path, backup_path)
            print(f"  [i] Respaldo previo guardado en: {backup_path}")
        except Exception:
            mcp_config = {"mcpServers": {}}

    if not isinstance(mcp_config, dict) or "mcpServers" not in mcp_config or not isinstance(mcp_config["mcpServers"], dict):
        mcp_config = {"mcpServers": {}}

    py_exec = sys.executable.replace("\\", "/")
    env_vars = {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1",
        "EINSOF_DEFAULT_MODEL": default_model,
    }
    if endpoint:
        env_vars["OLLAMA_HOST"] = endpoint

    mcp_config["mcpServers"]["polydim_einsof"] = {
        "command": py_exec,
        "args": ["-W", "ignore", "-u", str(einsof_mcp).replace("\\", "/")],
        "env": env_vars,
    }

    if mathesis_mcp is not None:
        mcp_config["mcpServers"]["mathesis_pmtp"] = {
            "command": py_exec,
            "args": ["-W", "ignore", "-u", str(mathesis_mcp).replace("\\", "/")],
            "env": {
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUNBUFFERED": "1",
            },
        }

    config_path.write_text(json.dumps(mcp_config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK] mcp_config.json actualizado en: {config_path}")

    # Sincronizar tambien con rutas adicionales de Antigravity/IDEs si existen en la maquina del alumno
    for extra_cfg in (
        Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
        Path.home() / ".cursor" / "mcp.json",
    ):
        if extra_cfg.parent.exists() and extra_cfg != config_path:
            try:
                ext_data = {"mcpServers": {}}
                if extra_cfg.exists():
                    ext_data = json.loads(extra_cfg.read_text(encoding="utf-8"))
                if not isinstance(ext_data, dict) or "mcpServers" not in ext_data:
                    ext_data = {"mcpServers": {}}
                ext_data["mcpServers"]["polydim_einsof"] = mcp_config["mcpServers"]["polydim_einsof"]
                if "mathesis_pmtp" in mcp_config["mcpServers"]:
                    ext_data["mcpServers"]["mathesis_pmtp"] = mcp_config["mcpServers"]["mathesis_pmtp"]
                extra_cfg.write_text(json.dumps(ext_data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"  [OK] Configuracion MCP sincronizada en: {extra_cfg}")
            except Exception:
                pass

    print(f"       -> polydim_einsof: {einsof_mcp}")
    if mathesis_mcp:
        print(f"       -> mathesis_pmtp : {mathesis_mcp}")
    return config_path, {"einsof_mcp": einsof_mcp, "mathesis_mcp": mathesis_mcp, "env": env_vars}


def run_mcp_smoke_test(server_info: dict):
    print("\n[5/5] Ejecutando smoke-test real JSON-RPC 2.0 stdio en silicio...")
    einsof_mcp = server_info["einsof_mcp"]
    env = os.environ.copy()
    env.update(server_info["env"])

    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "setup_einsof", "version": "2.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "stiefel_metric_verify", "arguments": {"dim_d": 128, "dim_k": 16, "order": 4}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "stiefel_metric_verify", "arguments": {"dim_d": 4, "dim_k": 16, "order": 4}}},
    ]
    stdin_payload = "\n".join(json.dumps(r) for r in reqs) + "\n"
    proc = subprocess.run(
        [sys.executable, "-W", "ignore", "-u", str(einsof_mcp)],
        input=stdin_payload,
        capture_output=True,
        text=True,
        timeout=25,
        env=env,
    )
    if proc.returncode != 0:
        print(f"  [X] Smoke-test MCP fallo con rc={proc.returncode}: {proc.stderr[:300]}")
        sys.exit(1)

    resps = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "id" in obj:
            resps[obj["id"]] = obj

    tools = [t["name"] for t in resps.get(2, {}).get("result", {}).get("tools", [])]
    if "stiefel_metric_verify" not in tools or "ask_einsof" not in tools:
        print(f"  [X] tools/list incompleto: {tools}")
        sys.exit(1)

    valid_res = resps.get(3, {}).get("result", {})
    valid_json = json.loads(valid_res.get("content", [{}])[0].get("text", "{}"))
    defect = valid_json.get("isometry_defect_inf", 1.0)
    if valid_res.get("isError") or not valid_json.get("is_machine_precision") or defect > 1e-15:
        print(f"  [X] Falla verificacion Stiefel St(16,128): {valid_json}")
        sys.exit(1)

    adv_res = resps.get(4, {}).get("result", {})
    if not adv_res.get("isError"):
        print(f"  [X] Falla guardia adversarial k>D (acepto dim_d=4, dim_k=16): {adv_res}")
        sys.exit(1)

    print(f"  [OK] Smoke-test polydim_einsof PASS | tools={len(tools)} | St(16,128) defect={defect:.2e} | k>D rechazado.")

    mathesis_mcp = server_info.get("mathesis_mcp")
    if mathesis_mcp is not None:
        m_reqs = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "setup_einsof", "version": "2.0"}}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        ]
        m_proc = subprocess.run(
            [sys.executable, "-W", "ignore", "-u", str(mathesis_mcp)],
            input="\n".join(json.dumps(r) for r in m_reqs) + "\n",
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
        )
        if m_proc.returncode != 0:
            print(f"  [X] Smoke-test mathesis_pmtp fallo rc={m_proc.returncode}: {m_proc.stderr[:250]}")
            sys.exit(1)
        m_lines = [json.loads(l) for l in m_proc.stdout.splitlines() if l.strip()]
        m_tools = [t["name"] for t in m_lines[-1].get("result", {}).get("tools", [])]
        print(f"  [OK] Smoke-test mathesis_pmtp PASS | tools={len(m_tools)}")


def verify_mathesis_and_atelier(start_atelier: bool = False, port: int = 8766) -> str:
    mthc_py = SUITE_DIR / "mthc.py"
    setup_mth = SUITE_DIR / "setup_mathesis.py"
    aiide_py = SUITE_DIR / "aiide_server.py"
    if mthc_py.exists():
        print(f"  [OK] Compilador nativo Mathesis detectado: {mthc_py}")
    elif setup_mth.exists():
        print(f"  [OK] Bootstrap Mathesis detectado: {setup_mth}")

    status_url = f"http://127.0.0.1:{port}/api/status"

    def _is_atelier_up() -> bool:
        try:
            with urllib.request.urlopen(status_url, timeout=0.8) as r:
                return r.status == 200
        except Exception:
            return False

    if _is_atelier_up():
        print(f"  [OK] Atelier Studio (aiide_server.py) ONLINE en http://127.0.0.1:{port}/")
        return f"ONLINE (http://127.0.0.1:{port}/)"

    if start_atelier and aiide_py.exists():
        print(f"  [*] Iniciando Atelier Studio (aiide_server.py) en http://127.0.0.1:{port}/ ...")
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        subprocess.Popen(
            [sys.executable, str(aiide_py), str(port)],
            cwd=str(SUITE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        for _ in range(10):
            time.sleep(0.25)
            if _is_atelier_up():
                print(f"  [OK] Atelier Studio iniciado en http://127.0.0.1:{port}/atelier")
                return f"ONLINE (http://127.0.0.1:{port}/atelier)"
        return f"STARTING (http://127.0.0.1:{port}/atelier)"

    return f"READY (python aiide_server.py -> http://127.0.0.1:{port}/atelier)"


def install_student_skills_pack():
    skills_dir = SUITE_DIR / "skills"
    if not skills_dir.exists():
        return
    print("  [*] Instalando Pack de Skills Soberanas para el Alumno...")
    home = Path.home()
    targets = [
        home / ".gemini" / "antigravity" / "skills",
        home / ".gemini" / "config" / "skills",
    ]
    skills_to_copy = ["ghost", "whisper", "council", "model-bridge", "quick-query", "manifold-verify", "redteam", "einsof-bootstrap"]
    for target in targets:
        try:
            target.mkdir(parents=True, exist_ok=True)
            for s in skills_to_copy:
                src = skills_dir / s / "SKILL.md"
                if src.exists():
                    dest = target / s
                    dest.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest / "SKILL.md")
        except Exception as e:
            print(f"  [!] Advertencia instalando skills en {target}: {e}")
    print(f"  [OK] {len(skills_to_copy)} skills soberanas instaladas para Antigravity (/ghost, /whisper, /council, /call, /query, /verify-manifold, /redteam).")


def print_completion(endpoint: str | None, default_model: str, atelier_status: str = "READY"):
    intro_html = SUITE_DIR / "introduction" / "index.html"
    print(f"""
======================================================================
  INSTALACION Y VERIFICACION EN SILICIO COMPLETADAS (EXIT CODE 0)
  Sello de Calibracion: 19.11.2026
======================================================================
  Endpoint Ollama : {endpoint or 'Offline (Motor Analitico Stiefel/Mathesis local 100% operativo)'}
  Modelo EINSOF   : {default_model}
  Herramientas MCP: ask_einsof, list_einsof_models, stiefel_metric_verify,
                    ask_cerebras_einsof + mathesis_pmtp (8 tools incl. Atelier & Polyglot)
  Skills Alumno   : ghost, whisper, council, model-bridge, quick-query,
                    manifold-verify, redteam, einsof-bootstrap (skills/README.md)
  Atelier Studio  : {atelier_status}
  Guia visual     : {intro_html if intro_html.exists() else SUITE_DIR / 'AGENT_BOOTSTRAP.md'}
======================================================================
""")


def main():
    parser = argparse.ArgumentParser(description="Instalador Soberano POLYDIM-EINSOF v2.2 (19.11.2026) para Antigravity & Atelier")
    parser.add_argument("--aladin-host", default=DEFAULT_ALADIN_IP, help="IP del nodo ALADIN LAN para failover Ollama")
    parser.add_argument("--open-intro", action="store_true", help="Abre introduction/index.html en el navegador al finalizar")
    parser.add_argument("--check-only", action="store_true", help="Ejecuta auditoria rapida sin modificar mcp_config.json")
    parser.add_argument("--start-atelier", action="store_true", help="Inicia el servidor Atelier Studio (aiide_server.py) en el puerto 8766")
    parser.add_argument("--auto", action="store_true", help="Modo onboarding automatico para alumnos sin conocimientos previos")
    args = parser.parse_args()

    print_banner()
    check_python_and_numpy()
    einsof_mcp, mathesis_mcp = _resolve_mcp_paths()

    if args.check_only:
        atelier_st = verify_mathesis_and_atelier(start_atelier=False)
        run_mcp_smoke_test({
            "einsof_mcp": einsof_mcp,
            "mathesis_mcp": mathesis_mcp,
            "env": {"PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"},
        })
        print(f"  [OK] Check-only completado exitosamente | Atelier: {atelier_st}")
        return

    endpoint, models, is_local = check_or_start_ollama(args.aladin_host)
    default_model = resolve_einsof_model(endpoint, models, is_local)
    _, server_info = configure_antigravity_mcp(endpoint, default_model)
    atelier_st = verify_mathesis_and_atelier(start_atelier=(args.start_atelier or args.auto))
    install_student_skills_pack()
    run_mcp_smoke_test(server_info)
    print_completion(endpoint, default_model, atelier_st)

    if args.open_intro:
        intro_html = SUITE_DIR / "introduction" / "index.html"
        if intro_html.exists():
            import webbrowser
            webbrowser.open(intro_html.as_uri())


if __name__ == "__main__":
    main()
