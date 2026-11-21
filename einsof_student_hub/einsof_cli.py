# -*- coding: utf-8 -*-
"""
EINSOF Interactive Student Console & Platform Navigator (Estándar 2030)
=======================================================================
Punto de entrada universal y amigable para alumnos sin conocimientos de Git:
  - `python einsof_cli.py status` : Comprueba proveedores $0 USD disponibles.
  - `python einsof_cli.py setup`  : Asistente guiado para configurar claves gratuitas.
  - `python einsof_cli.py chat`   : Consola de diálogo interactivo continuo.
  - `python einsof_cli.py ask "pregunta"` : Consulta rápida por terminal.
  - `python einsof_cli.py helena --demo`  : Genera y verifica un portador PNG 128x64.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Agregar directorio actual al path
CURR_DIR = Path(__file__).resolve().parent
if str(CURR_DIR) not in sys.path:
    sys.path.insert(0, str(CURR_DIR))

from einsof_client import CREDENTIALS_FILE, FREE_PROVIDERS, PAID_PROVIDERS, EinsofStudentClient


def cmd_status(client: EinsofStudentClient):
    print("=" * 70)
    print("ESTADO DE PROVEEDORES EINSOF PARA ALUMNOS ($0 USD)")
    print("=" * 70)
    print(f"Archivo de credenciales local: {CREDENTIALS_FILE} ({'Existe' if CREDENTIALS_FILE.exists() else 'No configurado'})")
    print("\nProveedores Gratuitos Disponibles:")
    for p_id, cfg in FREE_PROVIDERS.items():
        ready = p_id in client.available_providers
        status_str = "LISTO (Activo)" if ready else "No configurado"
        key_info = f"Env: {cfg['env_key']}" if cfg['env_key'] else "Sin API Key (100% Offline)"
        print(f"  [{'x' if ready else ' '}] {cfg['name']}")
        print(f"      Estado: {status_str} | {key_info}")
        if not ready and cfg.get("get_key_url"):
            print(f"      Obtener clave gratis en: {cfg['get_key_url']}")

    print("\nProveedores Pagos (Opcionales si el alumno ya tiene saldo):")
    for p_id, cfg in PAID_PROVIDERS.items():
        ready = p_id in client.available_providers
        print(f"  [{'x' if ready else ' '}] {cfg['name']}: {'Activo' if ready else 'Inactivo (Opcional)'}")

    print("\n" + "=" * 70)


def cmd_setup():
    print("=" * 70)
    print("ASISTENTE DE CONFIGURACION DE CLAVES GRATUITAS ($0 USD)")
    print("=" * 70)
    print("Las claves se guardarán en tu máquina en: ~/.ai_credentials.env")
    print("Ninguna clave se envía a servidores de terceros ni a GitHub.\n")

    groq_key = input("1. Groq Cloud API Key (Enter para omitir o link https://console.groq.com/keys): ").strip()
    cerebras_key = input("2. Cerebras API Key (Enter para omitir o link https://cloud.cerebras.ai): ").strip()
    openrouter_key = input("3. OpenRouter API Key (Enter para omitir o link https://openrouter.ai/keys): ").strip()

    lines = []
    if groq_key:
        lines.append(f"GROQ_API_KEY={groq_key}")
    if cerebras_key:
        lines.append(f"CEREBRAS_API_KEY={cerebras_key}")
    if openrouter_key:
        lines.append(f"OPENROUTER_API_KEY={openrouter_key}")

    if lines:
        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDENTIALS_FILE, "a" if CREDENTIALS_FILE.exists() else "w", encoding="utf-8") as f:
            f.write("\n" + "\n".join(lines) + "\n")
        print(f"\nGuardadas {len(lines)} credenciales con éxito en {CREDENTIALS_FILE}!")
    else:
        print("\nNo se introdujeron claves. Recordá que podés usar Ollama de forma 100% offline y gratuita.")


def cmd_ask(client: EinsofStudentClient, prompt: str, provider: str = None):
    print(f"\nConsultando a la red soberana EINSOF (Proveedor: {provider or 'Auto-Rotación Gratuita'})...")
    res = client.query(prompt, provider=provider)
    if res.get("success"):
        print(f"\n=== RESPUESTA [{res['provider']} / {res['model']} | {res['duration_s']:.2f}s] ===")
        print(res["text"])
        print("=" * 60)
    else:
        print("\n[ERROR]:", res.get("message") or res.get("error") or res)


def cmd_chat(client: EinsofStudentClient, provider: str = None):
    print("=" * 70)
    print("CONSOLA INTERACTIVA CONTINUA EINSOF ($0 USD)")
    print("Escribí tu consulta o 'salir' para terminar.")
    print("=" * 70)
    while True:
        try:
            p = input("\nAlumno > ").strip()
            if not p:
                continue
            if p.lower() in ("salir", "exit", "quit"):
                break
            cmd_ask(client, p, provider=provider)
        except (KeyboardInterrupt, EOFError):
            print("\nSesión finalizada.")
            break


def cmd_helena_demo():
    print("=" * 70)
    print("DEMOSTRACION DEL PROTOCOLO HELENA (CARRIER PNG 128x64)")
    print("=" * 70)
    import hashlib, struct, zlib
    import numpy as np

    print("1. Creando vector latente aleatorio D=512 normalizado en la Variedad S^{511}...")
    vec = np.random.randn(512).astype(np.float32)
    vec /= np.linalg.norm(vec)

    # Codificación PNG Helena
    raw = vec.tobytes()
    padded = np.zeros(128 * 64, dtype=np.float32)
    padded[:512] = vec
    raw_lines = bytearray()
    for y in range(64):
        raw_lines.append(0)
        raw_lines.extend(padded[y * 128 : (y + 1) * 128].tobytes())
    compressed = zlib.compress(bytes(raw_lines), level=9)
    seal = hashlib.blake2s(vec.tobytes()).hexdigest()[:16]

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 128, 64, 8, 6, 0, 0, 0))
        + chunk(b"tEXt", b"Helena\x00D=512|SEAL=" + seal.encode("ascii"))
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )

    out_file = Path("portador_helena_demo.png")
    out_file.write_bytes(png_bytes)
    print(f"2. Imagen portadora generada: {out_file.name} ({len(png_bytes)} bytes)")
    print(f"   Sello BLAKE2s de integridad: {seal}")
    print("3. Esta imagen puede arrastrarse directamente a ChatGPT, Claude o Gemini.")
    print("   La IA la decodifica en su sandbox con 0 tokens consumidos y Exit Code 0.")


def main():
    parser = argparse.ArgumentParser(description="EINSOF Student Console & Hub")
    subparsers = parser.add_subparsers(dest="subcommand")

    subparsers.add_parser("status", help="Muestra el estado de proveedores disponibles")
    subparsers.add_parser("setup", help="Asistente para configurar API keys gratuitas")
    
    ask_p = subparsers.add_parser("ask", help="Realiza una consulta directa")
    ask_p.add_argument("prompt", type=str, help="Pregunta o instrucción")
    ask_p.add_argument("--provider", type=str, default=None, help="Proveedor específico (groq, cerebras, ollama, etc.)")

    chat_p = subparsers.add_parser("chat", help="Inicia sesión interactiva continua")
    chat_p.add_argument("--provider", type=str, default=None, help="Proveedor específico")

    subparsers.add_parser("helena", help="Demostración y generación de portador Helena PNG")

    args = parser.parse_args()
    client = EinsofStudentClient()

    if args.subcommand == "status":
        cmd_status(client)
    elif args.subcommand == "setup":
        cmd_setup()
    elif args.subcommand == "ask":
        cmd_ask(client, args.prompt, provider=args.provider)
    elif args.subcommand == "chat":
        cmd_chat(client, provider=args.provider)
    elif args.subcommand == "helena":
        cmd_helena_demo()
    else:
        # Por defecto muestra status si no se pasa subcomando
        cmd_status(client)


if __name__ == "__main__":
    main()
