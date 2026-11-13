import os
import sys
import json
from multiprocessing import shared_memory
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pmtp import (
    PmtpShmBus,
    PmtpChannel,
    assert_safe_checkpoint_path,
    build_safe_hf_load_kwargs,
    load_numpy_safe,
)
from pmtp.pmtp_types import HEADER_COMPACT_SIZE


def test_unpredictable_nonce_prevents_predictable_slab_names():
    b1 = PmtpShmBus(prefix="t_nonce", max_slabs=4, max_dim=256)
    b2 = PmtpShmBus(prefix="t_nonce", max_slabs=4, max_dim=256)
    try:
        assert len(b1._instance_nonce) == 8
        assert b1._instance_nonce != b2._instance_nonce
        v = np.ones(16, dtype=np.float64) / 4.0
        d1 = b1.publish_tensor(v)
        d2 = b2.publish_tensor(v)
        sid1 = int(d1.split("_")[2])
        sid2 = int(d2.split("_")[2])
        n1 = b1.slabs[sid1]["name"]
        n2 = b2.slabs[sid2]["name"]
        assert n1 != n2
        assert b1._instance_nonce in n1
        assert b2._instance_nonce in n2
    finally:
        b1.cleanup()
        b2.cleanup()


def test_fail_closed_against_shm_name_squatting():
    bus = PmtpShmBus(prefix="t_squat", max_slabs=4, max_dim=128)
    victim_name = f"t_squat_{bus._instance_nonce}_0001"
    squatter = shared_memory.SharedMemory(name=victim_name, create=True, size=HEADER_COMPACT_SIZE + 256)
    try:
        with pytest.raises(PermissionError, match="name-squatting"):
            bus.allocate_tensor_slab(slab_id=1, num_elements=16, dtype=np.float64)
    finally:
        bus.cleanup()
        try:
            squatter.close()
            squatter.unlink()
        except Exception:
            pass


def test_release_all_zeroizes_entire_slab_before_unlink():
    bus = PmtpShmBus(prefix="t_zall", max_slabs=2, max_dim=128, auth_key=b"zero_test_key")
    v = np.ones(64, dtype=np.float64) / 8.0
    desc = bus.publish_tensor(v)
    sid = int(desc.split("_")[2])
    shm = bus.slabs[sid]["shm"]

    # Keep a second handle temporarily only to inspect bytes wiped by release_all
    name = bus.slabs[sid]["name"]
    observer = shared_memory.SharedMemory(name=name, create=False)
    try:
        assert any(b != 0 for b in bytes(observer.buf[:HEADER_COMPACT_SIZE + 64]))
        bus.release_all()
        assert bytes(observer.buf[:observer.size]) == b"\x00" * observer.size
    finally:
        try:
            observer.close()
        except Exception:
            pass
        try:
            shm.unlink()
        except Exception:
            pass


def test_nan_vector_and_fallback_flag(capsys):
    bus = PmtpShmBus(prefix="t_nanfb", max_slabs=2, max_dim=128)
    try:
        ch = PmtpChannel(bus, emit_warn_logs=True)
        bad = np.ones(16, dtype=np.float64) / 4.0
        bad[0] = float("nan")
        msg = ch.send("probe", latent=bad)
        captured = capsys.readouterr().err
        assert msg["text"] == "probe"
        assert msg["pmtp"] is None
        assert ch.fallback_active is True
        assert "PMTP_FLAG_FALLBACK_ACTIVE" in captured
        last_line = json.loads(captured.strip().splitlines()[-1])
        assert last_line["flag"] == "PMTP_FLAG_FALLBACK_ACTIVE"
    finally:
        bus.cleanup()


def test_fail_closed_safetensors_and_no_pickle_policy(tmp_path):
    assert assert_safe_checkpoint_path(tmp_path / "model.safetensors").name == "model.safetensors"

    for ext in (".bin", ".pt", ".pth", ".ckpt", ".pkl", ".pickle"):
        with pytest.raises(PermissionError, match="blocked pickle-backed"):
            assert_safe_checkpoint_path(tmp_path / f"weights{ext}")

    with pytest.raises(PermissionError, match="unsupported checkpoint"):
        assert_safe_checkpoint_path(tmp_path / "weights.unknown")

    safe_kwargs = build_safe_hf_load_kwargs({"device_map": "cpu"})
    assert safe_kwargs["use_safetensors"] is True
    assert safe_kwargs["trust_remote_code"] is False

    with pytest.raises(PermissionError, match="use_safetensors=False"):
        build_safe_hf_load_kwargs({"use_safetensors": False})

    with pytest.raises(PermissionError, match="trust_remote_code=True"):
        build_safe_hf_load_kwargs({"trust_remote_code": True})

    # Verify load_numpy_safe works on numeric arrays and blocks pickled object arrays
    good_npy = tmp_path / "good.npy"
    np.save(good_npy, np.array([1.0, 2.0, 3.0], dtype=np.float64), allow_pickle=False)
    loaded = load_numpy_safe(good_npy)
    assert np.allclose(loaded, [1.0, 2.0, 3.0])

    bad_npy = tmp_path / "bad_obj.npy"
    np.save(bad_npy, np.array([{"evil": "payload"}], dtype=object), allow_pickle=True)
    with pytest.raises(ValueError):
        load_numpy_safe(bad_npy)
