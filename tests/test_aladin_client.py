# ============================================================================
# TEST SUITE: AladinTelepathyClient
# Proyecto: PMTP / POLYDIM-EINSOF
# Exit Code 0 requerido.
# ============================================================================

from __future__ import annotations

import os
import sys
import threading
import time
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pmtp.pmtp_aladin import (
    AladinTelepathyClient,
    _blake2s_mac,
    _encode_message,
    _decode_message,
    _HEADER_SIZE,
    ALADIN_MAGIC,
    ALADIN_VERSION,
)

AUTH_KEY = b"aladin-auth-test-key-32-bytes!!"[:32]
# Puerto no utilizado en localhost para simular estado offline determinista sin depender de la red
UNAVAILABLE_HOST = "127.0.0.1"
UNAVAILABLE_PORT = 54321


@pytest.fixture
def offline_client() -> AladinTelepathyClient:
    return AladinTelepathyClient(host=UNAVAILABLE_HOST, port=UNAVAILABLE_PORT, auth_key=AUTH_KEY)


# ---------------------------------------------------------------------------
# 1. test_aladin_ping_offline
# Verificar que ping() retorna False (no exception) cuando el host no está disponible.
# ---------------------------------------------------------------------------
def test_aladin_ping_offline(offline_client: AladinTelepathyClient):
    """ping() retorna False sin lanzar excepción cuando el host no está disponible."""
    # Verificación directa contra endpoint inalcanzable
    res = offline_client.ping(timeout=0.2)
    assert res is False, f"Se esperaba False en host offline, obtuvo {res!r}"

    # Verificación con fallo simulado a nivel de socket
    with patch("socket.create_connection", side_effect=OSError("Network unreachable")):
        client = AladinTelepathyClient(host="192.168.100.21", port=9999, auth_key=AUTH_KEY)
        assert client.ping() is False


# ---------------------------------------------------------------------------
# 2. test_aladin_send_ptr_offline
# Enviar slab_ptr cuando offline -> retorna False sin exception.
# ---------------------------------------------------------------------------
def test_aladin_send_ptr_offline(offline_client: AladinTelepathyClient):
    """send_slab_ptr() retorna False sin exception cuando ALADIN está offline."""
    metadata = {"D": 512, "dtype": "FP32", "stiefel_defect": 1.1e-16}
    res = offline_client.send_slab_ptr(slab_id=101, metadata=metadata)
    assert res is False, f"Se esperaba False, obtuvo {res!r}"

    # Simular fallo en el host de producción
    with patch("socket.create_connection", side_effect=OSError("Connection refused")):
        client = AladinTelepathyClient(host="192.168.100.21", port=9999, auth_key=AUTH_KEY)
        assert client.send_slab_ptr(slab_id=101, metadata=metadata) is False


# ---------------------------------------------------------------------------
# 3. test_aladin_nonce_anti_replay
# Verificar que dos mensajes con el mismo nonce son rechazados.
# ---------------------------------------------------------------------------
def test_aladin_nonce_anti_replay():
    """Anti-replay: dos mensajes con el mismo nonce son rechazados con ValueError."""
    nonce = 8888
    slab_id = 42
    metadata = {"dim": 128, "rank": 16}

    msg = _encode_message(AUTH_KEY, nonce, slab_id, metadata)

    seen_nonces: set[int] = set()
    s1, m1 = _decode_message(AUTH_KEY, msg, seen_nonces)
    assert s1 == slab_id
    assert m1 == metadata
    assert nonce in seen_nonces

    # Segundo intento con el mismo nonce debe ser rechazado
    with pytest.raises(ValueError, match="Replay detectado"):
        _decode_message(AUTH_KEY, msg, seen_nonces)


# ---------------------------------------------------------------------------
# 4. test_aladin_blake2s_mac
# Verificar integridad del MAC en el protocolo de mensajes.
# ---------------------------------------------------------------------------
def test_aladin_blake2s_mac():
    """Verificación de integridad BLAKE2s-256 en el protocolo wire."""
    nonce = 1234
    slab_id = 777
    metadata = {"status": "OK", "step": 1}

    msg = _encode_message(AUTH_KEY, nonce, slab_id, metadata)
    seen: set[int] = set()

    # Mensaje íntegro decodifica correctamente
    s_dec, m_dec = _decode_message(AUTH_KEY, msg, seen)
    assert s_dec == slab_id
    assert m_dec == metadata

    # MAC alterado -> debe fallar con ValueError
    tampered = bytearray(msg)
    mac_offset = 4 + 2 + 8 + 8 + 8 + 2  # Offset del campo mac (32 bytes)
    tampered[mac_offset] ^= 0x01
    with pytest.raises(ValueError, match="MAC BLAKE2s inválido"):
        _decode_message(AUTH_KEY, bytes(tampered), set())

    # Truncamiento -> debe fallar con ValueError
    with pytest.raises(ValueError, match="truncado"):
        _decode_message(AUTH_KEY, msg[:20], set())


# ---------------------------------------------------------------------------
# 5. test_aladin_ghost_protocol_no_tensor_in_metadata
# Ghost Protocol: vetar datos crudos de tensor en el canal TCP.
# ---------------------------------------------------------------------------
def test_aladin_ghost_protocol_no_tensor_in_metadata():
    """Ghost Protocol: NUNCA serializar tensores en el canal TCP."""
    # Claves prohibidas
    for forbidden in ["tensor_data", "raw_bytes", "weights", "tensor"]:
        meta = {forbidden: [1.0, 2.0, 3.0]}
        with pytest.raises(ValueError, match="Ghost Protocol violation"):
            _encode_message(AUTH_KEY, nonce=1, slab_id=1, metadata=meta)

    # Exceso de tamaño (>512 bytes)
    huge_meta = {"metric_" + str(i): "x" * 20 for i in range(30)}
    with pytest.raises(ValueError, match="demasiado grande"):
        _encode_message(AUTH_KEY, nonce=1, slab_id=1, metadata=huge_meta)


# ---------------------------------------------------------------------------
# 6. test_aladin_mac_key_isolation
# ---------------------------------------------------------------------------
def test_aladin_mac_key_isolation():
    """Una clave distinta no puede verificar un mensaje legítimo."""
    other_key = b"completely-different-key-32bytes"[:32]
    msg = _encode_message(AUTH_KEY, nonce=55, slab_id=1, metadata={"ok": True})
    with pytest.raises(ValueError, match="MAC BLAKE2s inválido"):
        _decode_message(other_key, msg, set())


# ---------------------------------------------------------------------------
# 7. test_aladin_nonce_monotonic
# ---------------------------------------------------------------------------
def test_aladin_nonce_monotonic(offline_client: AladinTelepathyClient):
    """Los nonces generados por el cliente son estrictamente crecientes."""
    n0 = offline_client._next_nonce()
    n1 = offline_client._next_nonce()
    n2 = offline_client._next_nonce()
    assert n1 > n0
    assert n2 > n1


# ---------------------------------------------------------------------------
# 8. test_aladin_concurrent_send_ptr_offline
# ---------------------------------------------------------------------------
def test_aladin_concurrent_send_ptr_offline(offline_client: AladinTelepathyClient):
    """Múltiples hilos concurrentes en modo offline retornan False sin exceptions."""
    errors: list[Exception] = []
    results: list[bool] = []
    lock = threading.Lock()

    def worker(slab_id: int):
        try:
            r = offline_client.send_slab_ptr(slab_id=slab_id, metadata={"D": slab_id})
            with lock:
                results.append(r)
        except Exception as e:
            with lock:
                errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)

    assert not errors, f"Errores en concurrencia: {errors}"
    assert len(results) == 8
    assert all(r is False for r in results)


# ---------------------------------------------------------------------------
# 9. test_aladin_recv_slab_ptr_offline
# ---------------------------------------------------------------------------
def test_aladin_recv_slab_ptr_offline(offline_client: AladinTelepathyClient):
    """recv_slab_ptr retorna None sin exception cuando está offline."""
    res = offline_client.recv_slab_ptr(timeout=0.2)
    assert res is None
