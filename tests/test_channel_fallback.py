"""Verifica que PMTP es opcional: sin PMTP no se pierde nada; con PMTP se agrega el latente."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pmtp import PmtpShmBus, PmtpChannel  # noqa: E402

TEXT = "Plan: refactorizar el parser y agregar tests de borde."


def _latent(dim=1024, seed=7):
    return np.random.default_rng(seed).standard_normal(dim)


def test_receiver_without_pmtp_gets_identical_text():
    bus = PmtpShmBus(prefix="t_fb_a", max_slabs=4, max_dim=1024)
    try:
        ch = PmtpChannel(bus)
        msg = ch.send(TEXT, _latent())
        text, latent = ch.receive(msg, supports_pmtp=False)
        assert text == TEXT
        assert latent is None
    finally:
        bus.cleanup()


def test_receiver_with_pmtp_gets_text_and_bit_exact_latent():
    bus = PmtpShmBus(prefix="t_fb_b", max_slabs=4, max_dim=1024)
    try:
        ch = PmtpChannel(bus)
        v = _latent()
        msg = ch.send(TEXT, v)
        text, latent = ch.receive(msg, supports_pmtp=True)
        assert text == TEXT
        assert latent is not None
        assert np.max(np.abs(latent - v)) < 1e-12
    finally:
        bus.cleanup()


def test_no_bus_degrades_to_text():
    ch = PmtpChannel(bus=None)
    msg = ch.send(TEXT, _latent())
    assert msg["pmtp"] is None
    assert ch.receive(msg, supports_pmtp=True) == (TEXT, None)


class _BrokenBus:
    def publish_tensor(self, vec):
        raise OSError("shared memory unavailable")

    def read_tensor(self, desc, verify_stiefel=True):
        raise OSError("shared memory unavailable")


def test_broken_bus_degrades_to_text_without_raising():
    ch = PmtpChannel(_BrokenBus())
    msg = ch.send(TEXT, _latent())
    assert msg == {"text": TEXT, "pmtp": None}
    assert "OSError" in ch.last_degradation


def test_nan_latent_degrades_to_text():
    bus = PmtpShmBus(prefix="t_fb_c", max_slabs=4, max_dim=1024)
    try:
        ch = PmtpChannel(bus)
        bad = _latent()
        bad[3] = np.nan
        msg = ch.send(TEXT, bad)
        assert msg["pmtp"] is None
        assert ch.receive(msg, supports_pmtp=True) == (TEXT, None)
    finally:
        bus.cleanup()


def test_stale_slab_degrades_to_text():
    bus = PmtpShmBus(prefix="t_fb_d", max_slabs=4, max_dim=1024)
    try:
        ch = PmtpChannel(bus)
        msg = ch.send(TEXT, _latent())
        bus.release_slab(msg["pmtp"]["slab"])
        text, latent = ch.receive(msg, supports_pmtp=True)
        assert text == TEXT and latent is None
        assert "RuntimeError" in ch.last_degradation
    finally:
        bus.cleanup()
