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


def test_max_dim_fail_closed_cap():
    bus = PmtpShmBus(prefix="t_sec_cap", max_slabs=2, max_dim=512)
    try:
        with pytest.raises(ValueError, match="excede el límite máximo configurado max_dim"):
            bus.allocate_tensor_slab(slab_id=1, num_elements=1024)
    finally:
        bus.cleanup()


def test_dlpack_zero_copy_capsule_and_device():
    bus = PmtpShmBus(prefix="t_sec_dlpack", max_slabs=2, max_dim=512)
    try:
        v = _unit_vec(dim=256)
        desc = bus.publish_tensor(v)
        sid = int(desc.split("_")[2])
        leased = bus.get_zero_copy_dlpack_tensor(sid, verify_mac=True)
        # 1. Verificar métodos DLPack canónicos
        assert hasattr(leased, "__dlpack__")
        assert hasattr(leased, "__dlpack_device__")
        dev = leased.__dlpack_device__()
        assert dev == (1, 0)
        capsule = leased.__dlpack__()
        assert capsule is not None
        # 2. Ingesta Zero-Copy vía NumPy DLPack consumidor sin copia de payload
        consumed = np.from_dlpack(leased)
        assert np.allclose(consumed, v, atol=1e-15)
        # Ambos apuntan exactamente a la misma memoria física compartida
        assert consumed.__array_interface__["data"][0] == leased.__array_interface__["data"][0]
    finally:
        bus.cleanup()


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


def test_rfc_siphash24_cross_language_parity():
    from pmtp.pmtp_types import siphash24_u64
    rfc_key = bytes(range(16))
    rfc_msg = bytes(range(15))
    assert siphash24_u64(rfc_key, rfc_msg) == 0xA129CA6149BE45E5


def test_dlpack_context_manager_detects_unauthorized_mutation():
    bus = PmtpShmBus(prefix="t_sec_dlmut", max_slabs=2, max_dim=256)
    try:
        v = _unit_vec(dim=128)
        desc = bus.publish_tensor(v)
        sid = int(desc.split("_")[2])
        with pytest.raises(PermissionError, match="PMTP MAC authentication failure"):
            with bus.get_zero_copy_dlpack_tensor(sid, verify_mac=True) as leased:
                consumed = np.from_dlpack(leased)
                # Capa 1: NumPy marca el tensor importado desde DLPack como read-only por defecto
                with pytest.raises(ValueError, match="read-only"):
                    consumed[0] += 0.5
                # Capa 2: NumPy bloquea incluso el intento de forzar writeable=True en el consumidor DLPack
                with pytest.raises(ValueError, match="cannot set WRITEABLE"):
                    consumed.flags.writeable = True
                # Capa 3: Si un proceso malicioso altera directamente el slot activo del mmap durante el lease, __exit__ lo atrapa vía MAC64
                shm = bus.slabs[sid]["shm"]
                active_offset = 64 + leased._leased_slot * leased._payload_bytes
                shm.buf[active_offset] ^= 0xFF
    finally:
        bus.cleanup()


def test_sabios_non_human_primitives_swhs_hfct_cwgb():
    from tools.atelier_dev.mathesis_semantic_bus import MathesisSemanticBus
    msb = MathesisSemanticBus(agent_weight=50, turing_weight=50)
    rng = np.random.default_rng(2026)
    q0, _ = np.linalg.qr(rng.standard_normal((128, 8)))
    q1, _ = np.linalg.qr(q0 + 0.01 * rng.standard_normal((128, 8)))
    swhs = msb.compute_swhs_holonomy(q0, q1, rank_k=8)
    assert len(swhs["swhs_phases_rad"]) == 8
    assert swhs["topological_abort"] is False

    traj = rng.standard_normal((32, 128))
    hfct = msb.compress_hfct_spectral(traj, m_modes=8)
    assert hfct["shape"] == (128, 8)
    assert hfct["isometry_defect"] <= 1e-14

    v1 = _unit_vec(128, seed=1)
    v2 = _unit_vec(128, seed=2)
    v3 = _unit_vec(128, seed=3)
    cwgb = msb.karcher_cwgb_barycenter([v1, v2, v3], weights=[0.5, 0.3, 0.2])
    assert cwgb["isometry_defect"] <= 1e-15
    assert cwgb["tokens_consumed"] == 0
