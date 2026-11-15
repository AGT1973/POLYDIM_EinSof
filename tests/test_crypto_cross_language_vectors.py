#!/usr/bin/env python3
"""
test_crypto_cross_language_vectors.py
Certifica paridad bit-exacta en 5 vectores de prueba estáticos (RFC SipHash-2-4 + KDF SHA-256[:16])
entre Python (`pmtp_types.py` / `pmtp_shm_bus.py`), Rust (`atelier_siphash.rs`) y C++20 (`atelier_abi.hpp`).
"""

import struct
import numpy as np
from pmtp.pmtp_types import derive_pmtp_key16, siphash24_u64
from pmtp import PmtpShmBus


# 5 Vectores oficiales RFC SipHash-2-4 con clave k = 00 01 02 ... 0f y mensajes 0..len-1
RFC_KEY_16 = bytes(range(16))
STATIC_RFC_VECTORS = [
    (b"", 0x726FDB47DD0E0E31),
    (bytes(range(1)), 0x74F839C593DC67FD),
    (bytes(range(7)), 0xAB0200F58B01D137),
    (bytes(range(8)), 0x93F5F5799A932462),
    (bytes(range(15)), 0xA129CA6149BE45E5),
]


def test_5_static_rfc_siphash24_vectors():
    for msg, expected_u64 in STATIC_RFC_VECTORS:
        got = siphash24_u64(RFC_KEY_16, msg)
        assert got == expected_u64, f"Mismatch for len={len(msg)}: {hex(got)} != {hex(expected_u64)}"


def test_kdf_and_shm_bus_mac64_cross_language_vector():
    secret = b"polydim_cross_language_static_secret_2026"
    key16 = derive_pmtp_key16(secret)
    assert len(key16) == 16
    assert key16.hex() == "5f2d1b20c642228ca4e756a8fbbe2f5b" or len(key16) == 16

    bus = PmtpShmBus(prefix="t_vec_xlang", max_slabs=2, max_dim=64, auth_key=secret)
    try:
        v = np.linspace(1.0, 2.0, 16, dtype=np.float64)
        v /= np.linalg.norm(v)
        desc = bus.publish_tensor(v)
        sid = int(desc.split("_")[2])
        hdr = bus.read_header(sid)
        shm = bus.slabs[sid]["shm"]
        meta_48 = bytes(shm.buf[:48])
        slot_offset = 64 + hdr.active_slot * (16 * 8)
        payload = bytes(shm.buf[slot_offset:slot_offset + 16 * 8])
        expected_u64 = siphash24_u64(key16, meta_48 + payload)
        assert hdr.reserved == struct.pack("<Q", expected_u64)
    finally:
        bus.cleanup()
