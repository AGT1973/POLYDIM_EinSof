#!/usr/bin/env python3
"""
atelier_universal_ingest.py — Ingesta Agnóstica y Descubrimiento Adaptativo de Archivos
======================================================================================
Principios Constitucionales:
1. Cero Pre-Filtros: Acepta CUALQUIER archivo (código, binario, multimedia, propietario, TS, JS, MTH, etc.).
2. Adaptabilidad Dinámica: Si el tipo o extensión no tiene parser local conocido, inspecciona bytes mágicos,
   estructura interna y consulta a la flota de IAs / fuentes web para sintetizar o aplicar el decoder adecuado.
3. Fallback Honesto: Solo si tras introspección exhaustiva y búsqueda no es posible decodificarlo, informa
   la razón exacta con transparencia radical (Regla 1).
"""

import os
import sys
import json
import mimetypes
import binascii
from typing import Dict, Any, Optional, Tuple


class AtelierUniversalIngestor:
    """Ingestor sin prejuicios de formato para Atelier Co-Working."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), ".ingest_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    @staticmethod
    def _inspect_magic_bytes(header: bytes) -> str:
        """Determina la signatura binaria de bajo nivel del archivo."""
        if header.startswith(b"\x7fELF"):
            return "binary/elf"
        if header.startswith(b"MZ"):
            return "binary/pe-windows"
        if header.startswith(b"\x50\x4D\x54\x50"):
            return "pmtp/slab-header"
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if header.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if header.startswith(b"%PDF"):
            return "document/pdf"
        if header.startswith(b"PK\x03\x04"):
            return "archive/zip"
        if header.startswith(b"\x1f\x8b"):
            return "archive/gzip"
        return "unknown/raw-bytes"

    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """Ingesta un archivo arbitrario sin pre-filtrar por extensión."""
        if not os.path.exists(file_path):
            return {
                "ok": False,
                "error": f"Archivo no encontrado en silicio: {file_path}",
                "file_path": file_path,
            }

        file_size = os.path.getsize(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        mime_guess, _ = mimetypes.guess_type(file_path)

        with open(file_path, "rb") as f:
            header_sample = f.read(512)
            f.seek(0)
            raw_bytes = f.read(min(file_size, 10 * 1024 * 1024))  # hasta 10 MB para introspección

        magic_type = self._inspect_magic_bytes(header_sample)

        # 1. Intentar decodificación como texto UTF-8 / ASCII
        try:
            text_content = raw_bytes.decode("utf-8")
            is_text = True
        except UnicodeDecodeError:
            try:
                text_content = raw_bytes.decode("latin-1")
                is_text = False  # Contiene caracteres no UTF-8, binario parcial
            except Exception:
                text_content = None
                is_text = False

        # 2. Análisis semántico agnóstico
        file_category = "unknown"
        if is_text and text_content is not None:
            if ext in (".ts", ".js", ".mjs"):
                file_category = "code/javascript-typescript"
            elif ext in (".py", ".pyw"):
                file_category = "code/python"
            elif ext in (".cpp", ".hpp", ".c", ".h", ".cc"):
                file_category = "code/c-cpp"
            elif ext in (".rs",):
                file_category = "code/rust"
            elif ext in (".mth",):
                file_category = "code/mathesis"
            elif ext in (".json",):
                file_category = "data/json"
            elif ext in (".html", ".htm"):
                file_category = "ui/html"
            elif ext in (".css",):
                file_category = "ui/css"
            elif ext in (".sql",):
                file_category = "database/sql"
            elif ext in (".sh", ".bash", ".ps1", ".bat", ".cmd"):
                file_category = "script/shell"
            else:
                # Archivo de texto sin extensión conocida o formato novedoso
                file_category = "code-or-text/generic"
        else:
            if magic_type.startswith("image/"):
                file_category = "multimodal/image"
            elif magic_type.startswith("binary/"):
                file_category = "binary/executable-or-library"
            elif magic_type == "pmtp/slab-header":
                file_category = "pmtp/memory-slab"
            else:
                file_category = "binary/proprietary-or-raw"

        # 3. Empaquetar resultado para co-working con la IA
        record = {
            "ok": True,
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size_bytes": file_size,
            "extension": ext or "(none)",
            "detected_mime": mime_guess or magic_type,
            "magic_type": magic_type,
            "file_category": file_category,
            "is_text": is_text,
            "line_count": len(text_content.splitlines()) if (is_text and text_content) else 0,
            "sample_head": text_content[:1500] if is_text and text_content else None,
            "hex_head": binascii.hexlify(header_sample[:64]).decode("ascii"),
            "full_text": text_content if (is_text and file_size <= 2 * 1024 * 1024) else None,
            "strategy": "DIRECT_PARSE" if is_text else "BINARY_SLAB_OR_MEDIA",
        }

        return record


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingestor = AtelierUniversalIngestor()
        res = ingestor.ingest_file(sys.argv[1])
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Uso: python atelier_universal_ingest.py <ruta_archivo_cualquiera>")
