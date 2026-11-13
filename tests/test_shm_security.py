#!/usr/bin/env python3
"""
test_shm_security.py — Auditoría Adversarial Red Team sobre PmtpShmBus y PmtpChannel.
Verifica:
  1. Autenticación Keyed MAC BLAKE2s-64 (anti-snooping y anti-inyección co-inquilino).
  2. Zeroización determinista a 0x00 al liberar/cerrar slabs.
  3. Política de permisos 0600 (POSIX S_IRUSR|S_IWUSR / Private Session en Win32).
  4. Degradación observable (log WARN JSON, PMTP_FLAG_FALLBACK_ACTIVE, auto-rearme).
"""

import os
import sys
import json
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pmtp import PmtpShmBus, PmtpChannel  # noqa: E402
from pmtp.pmtp_types import HEADER_COMPACT_SIZE  # noqa: E402


def _unit_vec(dim=1024, seed=42):
    v = np.random.default_rng(seed).standard_normal(dim).astype(np.float64)
    return v / np.linalg.norm(v)


def test_keyed_mac_authenticates_valid_tensor():
    bus = PmtpShmBus(prefix="t_sec_mac_ok", max_slabs=4, max_dim=1024, auth_key=b"secret_key_alpha")
    try:
        v = _unit_vec()
        desc = bus.publish_tensor(v)
        out = bus.read_tensor(desc, verify_stiefel=True, verify_mac=True)
        assert np.allclose(out, v, atol=1e-15)
    finally:
        bus.cleanup()


def test_mac_rejects_cotenant_payload_injection():
    bus = PmtpShmBus(prefix="t_sec_tamper", max_slabs=4, max_dim=1024, auth_key=b"secret_key_beta")
    try:
        v = _unit_vec()
        desc = bus.publish_tensor(v)
        sid = int(desc.split("_")[2])
        info = bus.slabs[sid]
        shm = info["shm"]
        hdr = bus.read_header(sid)

        # Ataque co-inquilino: alterar 1 byte del payload activo sin conocer auth_key
        slot_offset = HEADER_COMPACT_SIZE + (hdr.active_slot * info["payload_bytes"])
        shm.buf[slot_offset] = shm.buf[slot_offset] ^ 0x01

        with pytest.raises(PermissionError, match="MAC authentication failure"):
            bus.read_tensor(desc, verify_stiefel=False, verify_mac=True)
    finally:
        bus.cleanup()


def test_deterministic_zeroization_on_release_slab():
    bus = PmtpShmBus(prefix="t_sec_zero", max_slabs=4, max_dim=512, auth_key=b"secret_key_gamma")
    try:
        v = _unit_vec(dim=512)
        desc = bus.publish_tensor(v)
        sid = int(desc.split("_")[2])
        info = bus.slabs[sid]
        shm = info["shm"]

        payload_start = HEADER_COMPACT_SIZE
        payload_end = payload_start + 2 * info["payload_bytes"]
        assert any(b != 0 for b in bytes(shm.buf[payload_start:payload_end]))

        bus.release_slab(desc)
        # Todo el buffer de payload debe quedar exactamente en 0x00 tras release_slab
        assert bytes(shm.buf[payload_start:payload_end]) == b"\x00" * (payload_end - payload_start)
    finally:
        bus.cleanup()


def test_explicit_0600_permission_policy():
    bus = PmtpShmBus(prefix="t_sec_perm", max_slabs=2, max_dim=256)
    try:
        v = _unit_vec(dim=256)
        desc = bus.publish_tensor(v)
        sid = int(desc.split("_")[2])
        perm = bus.slabs[sid]["perm_mode"]
        if os.name == "posix" and os.path.isdir("/dev/shm"):
            assert perm == "0600"
            shm_path = os.path.join("/dev/shm", bus.slabs[sid]["name"].lstrip("/"))
            assert (os.stat(shm_path).st_mode & 0o777) == 0o600
        else:
            assert perm == "0600_PRIVATE_SESSION"
    finally:
        bus.cleanup()


def test_observable_graceful_degradation_and_autorearm(capsys):
    bus = PmtpShmBus(prefix="t_sec_obs", max_slabs=4, max_dim=512)
    try:
        ch = PmtpChannel(bus, emit_warn_logs=True)
        bad = _unit_vec(dim=512)
        bad[0] = np.nan

        msg_bad = ch.send("fallback payload", bad)
        assert msg_bad["pmtp"] is None
        assert ch.fallback_active is True
        assert ch.fallback_count == 1
        captured = capsys.readouterr()
        log_obj = json.loads(captured.err.strip().splitlines()[-1])
        assert log_obj["level"] == "WARN"
        assert log_obj["flag"] == "PMTP_FLAG_FALLBACK_ACTIVE"

        # Auto-rearme tras recuperarse el canal con tensor válido
        good = _unit_vec(dim=512)
        msg_good = ch.send("healthy payload", good)
        assert msg_good["pmtp"] is not None
        assert ch.fallback_active is False
    finally:
        bus.cleanup()


def test_abi_v1_rejects_invalid_version_and_overflow():
    import struct
    from pmtp.pmtp_types import PmtpCompactHeader, HEADER_COMPACT_FORMAT, PMTP_MAGIC_NUMBER

    # Versión ABI no soportada (v=99)
    bad_ver = struct.pack(
        HEADER_COMPACT_FORMAT,
        PMTP_MAGIC_NUMBER, 99, 1, 0, 1, 16, 1000, 1.0, 1, False, True, 0, 0, b"\x00" * 8
    )
    with pytest.raises(ValueError, match="Unsupported PMTP ABI version"):
        PmtpCompactHeader.unpack(bad_ver, validate=True)

    # Desbordamiento de dimensiones (num_elements > PMTP_MAX_ELEMENTS)
    bad_dim = struct.pack(
        HEADER_COMPACT_FORMAT,
        PMTP_MAGIC_NUMBER, 1, 1, 0, 1, (1 << 30), 1000, 1.0, 1, False, True, 0, 0, b"\x00" * 8
    )
    with pytest.raises(ValueError, match="Out-of-bounds num_elements"):
        PmtpCompactHeader.unpack(bad_dim, validate=True)


def test_qdwh_primary_solver_without_upfront_svd():
    from pmtp.pmtp_stiefel import PmtpStiefelAdapter

    rng = np.random.default_rng(777)
    U, _ = np.linalg.qr(rng.standard_normal((256, 16)))
    V, _ = np.linalg.qr(rng.standard_normal((16, 16)))
    # Matriz moderadamente mal condicionada kappa = 500
    sigmas = np.geomspace(1.0, 1.0 / 500.0, 16)
    X = (U * sigmas) @ V.T
    Q, _, _, status = PmtpStiefelAdapter.polar_safe_v2(X, max_iters=10, tol=1e-14)
    assert status == "ACCEPTED_QDWH_POLAR", f"Expected QDWH primary, got {status}"
    defect = float(np.max(np.abs(Q.T @ Q - np.eye(16))))
    assert defect <= 1e-14, f"QDWH defect too high: {defect}"


@pytest.mark.skipif(not hasattr(os, "memfd_create"), reason="Requiere syscall Linux os.memfd_create (Docker/POSIX)")
def test_memfd_create_0600_sealed_on_linux():
    bus = PmtpShmBus(prefix="t_sec_memfd", max_slabs=2, max_dim=512, backend="memfd", auth_key=b"memfd_key")
    try:
        v = _unit_vec(dim=512, seed=99)
        desc = bus.publish_tensor(v)
        sid = int(desc.split("_")[2])
        assert bus.slabs[sid]["backend"] == "memfd"
        assert "0600_MEMFD" in bus.slabs[sid]["perm_mode"]
        out = bus.read_tensor(desc, verify_stiefel=True, verify_mac=True)
        assert np.allclose(out, v, atol=1e-15)
    finally:
        bus.cleanup()
