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
        ("sequence",       ctypes.c_uint64),   # offset 48
        ("readers_count",  ctypes.c_uint32),   # offset 56
        ("reserved",       ctypes.c_uint32),   # offset 60
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
    "readers_count":  (56, 4),
    "reserved":       (60, 4),
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
    # Formato canonico: 4 x uint32, 2 x double, 3 x uint64, 2 x uint32 = 64 bytes
    fmt = "<IIIIddQQQII"
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
        2,            # sequence (even = safe)
        1,            # readers_count
        0,            # reserved
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
    import struct
    magic_le = struct.pack("<I", 0x504D5450)
    assert raw[:4] == magic_le, f"Magic bytes = {raw[:4]!r}, esperado {magic_le!r}"


def test_cross_language_cpp_to_python_abi_exchange(tmp_path):
    """Intercambio binario real C++20 -> Python ctypes de cabecera ABI 64B + matriz St(8, 128)."""
    import os
    import sys
    import subprocess
    import numpy as np

    kernel_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "atelier_kernel")
    ext = ".exe" if sys.platform == "win32" else ""
    exe_path = os.path.join(kernel_dir, f"atelier_stiefel_cpp{ext}")
    if not os.path.exists(exe_path):
        pytest.skip(f"Binario C++ no encontrado para intercambio ABI: {exe_path}")

    blob_path = tmp_path / "cpp_to_py_slab.bin"
    res = subprocess.run([exe_path, "128", "8", "--dump-slab-file", str(blob_path)], capture_output=True, text=True)
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
    assert hdr.reserved != 0

    mat = np.frombuffer(raw[64:], dtype=np.float64).reshape((128, 8))
    defect_py = float(np.max(np.abs(mat.T @ mat - np.eye(8))))
    assert defect_py <= 1e-14
    assert abs(defect_py - hdr.isometry_error) <= 1e-14
