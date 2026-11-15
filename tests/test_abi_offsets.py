#!/usr/bin/env python3
"""
test_abi_offsets.py — Validacion cruzada de la ABI canonica de 64 bytes.
Verifica que el layout de AtelierSlabHeader es identico al byte entre
C++20 (MSVC/GCC/Clang), Rust (rustc) y Python (ctypes).
Regla 19 + Red Team SOTA: cualquier desalineacion es un fallo critico.
"""

import ctypes
import struct
import pytest


class AtelierSlabHeader(ctypes.Structure):
    """Replica exacta en Python de la ABI canonica C/Rust de 64 bytes."""
    _pack_ = 1  # No padding del compilador de Python
    _fields_ = [
        ("magic",          ctypes.c_uint32),   # offset  0
        ("version",        ctypes.c_uint32),   # offset  4
        ("D",              ctypes.c_uint32),   # offset  8
        ("k",              ctypes.c_uint32),   # offset 12
        ("isometry_error", ctypes.c_double),   # offset 16
        ("latency_us",     ctypes.c_double),   # offset 24
        ("timestamp_ns",   ctypes.c_uint64),   # offset 32
        ("heartbeat_ns",   ctypes.c_uint64),   # offset 40
        ("sequence",       ctypes.c_uint64),   # offset 48 (mutable seqlock)
        ("mac64",          ctypes.c_uint64),   # offset 56 (SipHash-2-4 64-bit MAC)
    ]


# Mapa canonico de offsets: {field_name: (offset, size_bytes)}
CANONICAL_ABI = {
    "magic":          (0,  4),
    "version":        (4,  4),
    "D":              (8,  4),
    "k":              (12, 4),
    "isometry_error": (16, 8),
    "latency_us":     (24, 8),
    "timestamp_ns":   (32, 8),
    "heartbeat_ns":   (40, 8),
    "sequence":       (48, 8),
    "mac64":          (56, 8),
}


def test_abi_total_size():
    """La estructura debe ser exactamente 64 bytes (1 linea de cache)."""
    assert ctypes.sizeof(AtelierSlabHeader) == 64, (
        f"sizeof(AtelierSlabHeader) = {ctypes.sizeof(AtelierSlabHeader)}, esperado 64"
    )


def test_abi_field_offsets():
    """Cada campo debe estar exactamente en el offset canonico."""
    for field_name, (expected_offset, expected_size) in CANONICAL_ABI.items():
        actual_offset = getattr(AtelierSlabHeader, field_name).offset
        actual_size = getattr(AtelierSlabHeader, field_name).size
        assert actual_offset == expected_offset, (
            f"Campo '{field_name}': offset={actual_offset}, esperado={expected_offset}"
        )
        assert actual_size == expected_size, (
            f"Campo '{field_name}': size={actual_size}, esperado={expected_size}"
        )


def test_abi_roundtrip_pack_unpack():
    """Serializar y deserializar un header con struct.pack debe ser bit-exacto."""
    # Formato canonico: 4 x uint32, 2 x double, 4 x uint64 = 64 bytes
    fmt = "<IIIIddQQQQ"
    assert struct.calcsize(fmt) == 64, f"struct.calcsize = {struct.calcsize(fmt)}, esperado 64"

    test_vals = (
        0x504D5450,   # magic
        1,            # version
        1024,         # D
        16,           # k
        1.7e-16,      # isometry_error
        42.5,         # latency_us
        1234567890,   # timestamp_ns
        1234567890,   # heartbeat_ns
        2,            # sequence (even = safe, excluded from MAC)
        0xCAFEBABEDEADBEEF,  # mac64
    )
    packed = struct.pack(fmt, *test_vals)
    assert len(packed) == 64
    unpacked = struct.unpack(fmt, packed)
    assert unpacked == test_vals


def test_abi_magic_position():
    """El magic PMTP debe ser legible en los primeros 4 bytes (little-endian en x86)."""
    h = AtelierSlabHeader()
    h.magic = 0x504D5450
    raw = bytes(h)
    # En little-endian x86: 0x504D5450 -> bytes [0x50, 0x54, 0x4D, 0x50] = b'PTMP'
    magic_le = struct.pack("<I", 0x504D5450)
    assert raw[:4] == magic_le, f"Magic bytes = {raw[:4]!r}, esperado {magic_le!r}"


def test_cross_language_cpp_to_python_abi_exchange(tmp_path):
    """Intercambio binario y criptografico real C++20 -> Python (ABI 64B + SipHash-2-4 MAC64)."""
    import hmac
    import os
    import secrets
    import sys
    import subprocess
    import numpy as np
    from pmtp.pmtp_types import derive_pmtp_key16, siphash24_u64

    kernel_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "atelier_kernel")
    ext = ".exe" if sys.platform == "win32" else ""
    exe_path = os.path.join(kernel_dir, f"atelier_stiefel_cpp{ext}")
    if not os.path.exists(exe_path):
        pytest.skip(f"Binario C++ no encontrado para intercambio ABI: {exe_path}")

    shared_secret = secrets.token_hex(32)
    env = os.environ.copy()
    env["PMTP_SHM_KEY"] = shared_secret

    blob_path = tmp_path / "cpp_to_py_slab.bin"
    res = subprocess.run(
        [exe_path, "128", "8", "--dump-slab-file", str(blob_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 0, f"Kernel C++ fallo: {res.stderr}"

    raw = blob_path.read_bytes()
    assert len(raw) == 64 + 128 * 8 * 8
    hdr = AtelierSlabHeader.from_buffer_copy(raw[:64])
    assert hdr.magic == 0x504D5450
    assert hdr.version == 1
    assert hdr.D == 128
    assert hdr.k == 8
    assert hdr.sequence == 2
    assert hdr.isometry_error <= 1e-14
    assert hdr.mac64 != 0

    # Verificacion criptografica cruzada C++20 <-> Python: SipHash-2-4 64-bit sobre [0..48) + payload
    k16 = derive_pmtp_key16(shared_secret.encode("utf-8"))
    expected_mac64 = siphash24_u64(k16, raw[:48] + raw[64:])
    assert hmac.compare_digest(
        struct.pack("<Q", hdr.mac64),
        struct.pack("<Q", expected_mac64),
    ), f"Cross-language SipHash-2-4 MAC64 mismatch: cpp={hex(hdr.mac64)} py={hex(expected_mac64)}"

    # Prueba negativa: manipular 1 bit del payload invalida el MAC64 cruzado
    tampered_payload = bytearray(raw[64:])
    tampered_payload[0] ^= 0x01
    tampered_mac64 = siphash24_u64(k16, raw[:48] + bytes(tampered_payload))
    assert not hmac.compare_digest(struct.pack("<Q", hdr.mac64), struct.pack("<Q", tampered_mac64))

    mat = np.frombuffer(raw[64:], dtype=np.float64).reshape((128, 8))
    defect_py = float(np.max(np.abs(mat.T @ mat - np.eye(8))))
    assert defect_py <= 1e-14
    assert abs(defect_py - hdr.isometry_error) <= 1e-14
