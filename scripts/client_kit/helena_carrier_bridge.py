# -*- coding: utf-8 -*-
"""
Helena PMTP Carrier Bridge for Closed Commercial Satellites
===========================================================
Implements zero-1D-text tensor transport for closed APIs (OpenAI, Gemini,
Anthropic) where weight-level QLoRA is impossible (`modifies_provider_weights=False`):
  - Mode 1: 128x64 RGB PNG Carrier (~258 fixed vision tokens, up to 24 KB raw payload)
  - Mode 2: 4-Bit Quant Base64 Carrier (<= 2732 chars)
  - Mode 3: 1-Bit Spinor Carrier (512 bytes)
  - Mode 4: Deterministic Python Sandbox verification wrapper (`Exit Code 0` + BLAKE2s)
"""

from __future__ import annotations

import base64
import hashlib
import math
import struct
import zlib
from typing import Any, Dict, Tuple

import numpy as np

HELENA_MAGIC = b"HLN2"


def encode_png_carrier(tensor: np.ndarray, width: int = 128, height: int = 64) -> bytes:
    """
    Encodes a float32/float64 tensor into a lossless 128x64 RGB PNG image (24,576 bytes capacity)
    with CRC/BLAKE2s header using pure stdlib zlib + struct (zero PIL/Pillow dependency).
    """
    arr = np.asarray(tensor, dtype=np.float32).ravel()
    raw_bytes = arr.tobytes()
    digest = hashlib.blake2s(raw_bytes, digest_size=8).digest()
    header = struct.pack("<4sII8s", HELENA_MAGIC, arr.size, len(raw_bytes), digest)
    payload = header + raw_bytes

    capacity = width * height * 3
    if len(payload) > capacity:
        raise ValueError(f"Payload {len(payload)} bytes exceeds {width}x{height}x3={capacity} bytes PNG carrier.")

    buf = bytearray(capacity)
    buf[: len(payload)] = payload

    # Build PNG scanlines (filter byte 0 per row)
    stride = width * 3
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)
        scanlines.extend(buf[y * stride : (y + 1) * stride])

    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    idat = zlib.compress(bytes(scanlines), level=6)
    return b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", idat) + png_chunk(b"IEND", b"")


def decode_png_carrier(png_bytes: bytes) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Extracts and BLAKE2s-verifies the float32 tensor inside a Helena PNG carrier."""
    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG signature.")
    pos = 8
    width = height = 0
    idat_parts = []
    while pos + 8 <= len(png_bytes):
        length = struct.unpack(">I", png_bytes[pos : pos + 4])[0]
        ctype = png_bytes[pos + 4 : pos + 8]
        data = png_bytes[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            width, height = struct.unpack(">II", data[:8])
        elif ctype == b"IDAT":
            idat_parts.append(data)
        elif ctype == b"IEND":
            break

    raw_scan = zlib.decompress(b"".join(idat_parts))
    stride = width * 3
    payload = bytearray()
    for y in range(height):
        row_start = y * (stride + 1) + 1
        payload.extend(raw_scan[row_start : row_start + stride])

    magic, count, byte_len, digest = struct.unpack("<4sII8s", bytes(payload[:20]))
    if magic != HELENA_MAGIC:
        raise ValueError(f"Invalid Helena magic: {magic!r}")
    raw_bytes = bytes(payload[20 : 20 + byte_len])
    actual_digest = hashlib.blake2s(raw_bytes, digest_size=8).digest()
    if actual_digest != digest:
        raise ValueError("Helena PNG carrier BLAKE2s integrity check failed.")

    arr = np.frombuffer(raw_bytes, dtype=np.float32, count=count).copy()
    return arr, {
        "width": width,
        "height": height,
        "elements": count,
        "blake2s_8b": actual_digest.hex(),
        "modifies_provider_weights": False,
        "carrier": "HELENA_PNG_128x64",
    }


def encode_4bit_quant_carrier(tensor: np.ndarray, max_chars: int = 2732) -> Dict[str, Any]:
    """Packs float vector into symmetric 4-bit nibbles + float32 scale encoded in Base64."""
    arr = np.asarray(tensor, dtype=np.float32).ravel()
    absmax = float(np.max(np.abs(arr))) if arr.size else 1.0
    scale = absmax / 7.0 if absmax > 1e-12 else 1.0
    q = np.clip(np.round(arr / scale), -8, 7).astype(np.int8) + 8  # 0..15
    if q.size % 2 != 0:
        q = np.append(q, 8)
    packed = ((q[0::2].astype(np.uint8) << 4) | q[1::2].astype(np.uint8)).tobytes()
    blob = struct.pack("<If", arr.size, scale) + packed
    b64 = base64.b64encode(blob).decode("ascii")
    return {
        "carrier": "HELENA_4BIT_QUANT",
        "b64_truncated": len(b64) > max_chars,
        "char_len": len(b64),
        "payload_b64": b64[:max_chars],
        "modifies_provider_weights": False,
    }


def encode_1bit_spinor_carrier(tensor: np.ndarray, num_bytes: int = 512) -> Dict[str, Any]:
    """Packs sign bits of first `num_bytes * 8` dimensions into a 512-byte spinor signature."""
    arr = np.asarray(tensor, dtype=np.float64).ravel()
    target_bits = num_bytes * 8
    padded = np.zeros(target_bits, dtype=np.float64)
    take = min(arr.size, target_bits)
    padded[:take] = arr[:take]
    bits = (padded >= 0.0).astype(np.uint8)
    packed = np.packbits(bits).tobytes()
    return {
        "carrier": "HELENA_1BIT_SPINOR",
        "bytes_len": len(packed),
        "blake2s": hashlib.blake2s(packed, digest_size=16).hexdigest(),
        "payload_hex": packed.hex(),
        "modifies_provider_weights": False,
    }


def build_sandbox_verification_script(stiefel_defect_tol: float = 1e-15) -> str:
    """Generates a self-contained deterministic Python script for closed-model Sandboxes."""
    return (
        "import hashlib, math, numpy as np\n"
        f"TOL = {stiefel_defect_tol!r}\n"
        "def verify_stiefel_fp64(W):\n"
        "    W = np.asarray(W, dtype=np.float64)\n"
        "    k = min(W.shape)\n"
        "    G = W.T @ W if W.shape[0] >= W.shape[1] else W @ W.T\n"
        "    d = float(np.max(np.abs(G - np.eye(k))))\n"
        "    assert d <= TOL, f'Stiefel defect {d} > {TOL}'\n"
        "    return {'stiefel_defect': d, 'exit_code': 0}\n"
    )
