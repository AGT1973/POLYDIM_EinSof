# ============================================================================
# PMTP ALADIN TELEPATHY CLIENT
# Proyecto: PMTP / POLYDIM-EINSOF
# Autor: Ariel García Traba — Independent Research / EinsofOS
# Ghost Protocol: tensores D≥100 viven en PmtpShmBus (zero-copy).
#   Este canal TCP transporta SOLO punteros SLAB_ID (int) + metadata (dict<64B).
#   NUNCA serializar tensores como texto en el canal TCP.
# Auth: BLAKE2s MAC (32 bytes) por mensaje.
# Anti-replay: nonce incremental (uint64, monotónico) + timestamp_ns.
# Degraded mode: si ALADIN offline → retorna False/None sin exception.
# ============================================================================

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import socket
import struct
import threading
import time
from typing import Optional

log = logging.getLogger(__name__)

# ---- Wire format ALADIN v1 ------------------------------------------------
# Header: magic(4s) | version(H) | nonce(Q) | timestamp_ns(Q) | slab_id(Q)
#         metadata_len(H) | mac(32s)
# Payload: metadata_bytes (UTF-8 JSON, metadata_len bytes, max 512 bytes)
#
# Total header: 4+2+8+8+8+2+32 = 64 bytes (alineado a cache line)
# -------------------------------------------------------------------------

ALADIN_MAGIC = b"ALDI"
ALADIN_VERSION = 0x0001
_HEADER_FMT  = "<4sHQQQH32s"   # 64 bytes
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)
assert _HEADER_SIZE == 64, f"Header size mismatch: {_HEADER_SIZE}"

_METADATA_MAX_BYTES = 512

# Claves expresamente prohibidas bajo Ghost Protocol (prohibido transportar datos crudos)
GHOST_FORBIDDEN_KEYS = frozenset({
    "tensor_data",
    "raw_bytes",
    "tensor",
    "weights",
    "payload_tensor",
    "data_vector",
})


def _blake2s_mac(auth_key: bytes, nonce: int, timestamp_ns: int,
                 slab_id: int, metadata_bytes: bytes) -> bytes:
    """Calcula MAC BLAKE2s-256 sobre (nonce | timestamp_ns | slab_id | metadata)."""
    h = hashlib.blake2s(key=auth_key[:32], digest_size=32)
    h.update(struct.pack("<QQQ", nonce, timestamp_ns, slab_id))
    h.update(metadata_bytes)
    return h.digest()


def _encode_message(auth_key: bytes, nonce: int, slab_id: int,
                    metadata: dict) -> bytes:
    """
    Codifica un mensaje ALADIN: header 64B + payload JSON.
    Valida estricta conformidad con Ghost Protocol.
    """
    # Verificación Ghost Protocol: vetar serialización de tensores
    for k in metadata:
        if k in GHOST_FORBIDDEN_KEYS:
            raise ValueError(f"Ghost Protocol violation: clave de tensor '{k}' prohibida en canal TCP")

    meta_bytes = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    if len(meta_bytes) > _METADATA_MAX_BYTES:
        raise ValueError(f"metadata demasiado grande: {len(meta_bytes)} > {_METADATA_MAX_BYTES}")
    ts_ns = time.time_ns()
    mac = _blake2s_mac(auth_key, nonce, ts_ns, slab_id, meta_bytes)
    header = struct.pack(
        _HEADER_FMT,
        ALADIN_MAGIC, ALADIN_VERSION, nonce, ts_ns, slab_id,
        len(meta_bytes), mac,
    )
    return header + meta_bytes


def _decode_message(auth_key: bytes, data: bytes,
                    seen_nonces: set[int]) -> tuple[int, dict]:
    """
    Decodifica y verifica un mensaje ALADIN.
    Raises:
        ValueError  — magic, version, MAC inválidos, nonce repetido.
    """
    if len(data) < _HEADER_SIZE:
        raise ValueError(f"Mensaje truncado: {len(data)} < {_HEADER_SIZE}")
    magic, version, nonce, ts_ns, slab_id, meta_len, mac_recv = \
        struct.unpack_from(_HEADER_FMT, data, 0)
    if magic != ALADIN_MAGIC:
        raise ValueError(f"Magic inválido: {magic!r}")
    if version != ALADIN_VERSION:
        raise ValueError(f"Versión no soportada: {version}")
    if len(data) < _HEADER_SIZE + meta_len:
        raise ValueError("Payload truncado")
    meta_bytes = data[_HEADER_SIZE: _HEADER_SIZE + meta_len]
    # Anti-replay
    if nonce in seen_nonces:
        raise ValueError(f"Replay detectado: nonce={nonce} ya fue visto")
    # MAC verify
    mac_expected = _blake2s_mac(auth_key, nonce, ts_ns, slab_id, meta_bytes)
    if not _hmac_compare(mac_recv, mac_expected):
        raise ValueError("MAC BLAKE2s inválido — mensaje corrupto o forjado")
    # Nonce se acepta solo después de verificar MAC
    seen_nonces.add(nonce)
    metadata = json.loads(meta_bytes.decode("utf-8"))
    return slab_id, metadata


def _hmac_compare(a: bytes, b: bytes) -> bool:
    """Comparación en tiempo constante para MACs."""
    return hmac.compare_digest(a, b)


# ---------------------------------------------------------------------------

class AladinTelepathyClient:
    """
    Cliente TCP hacia el nodo ALADIN (192.168.100.21:9999).

    Ghost Protocol:
    - Solo SLAB_ID (int64) + metadata (dict JSON ≤512B) viajan por el socket.
    - Los tensores residen en PmtpShmBus (memoria compartida, zero-copy).
    - Si el nodo está offline → modo degradado silencioso (False/None).

    Auth: BLAKE2s-256 (clave de hasta 32 bytes).
    Anti-replay: nonce incremental monotónico + timestamp_ns por mensaje.
    Thread-safe: lock interno para nonce y socket.
    """

    def __init__(self, host: str = "192.168.100.21", port: int = 9999,
                 auth_key: bytes = b""):
        if len(auth_key) > 32:
            raise ValueError("auth_key debe tener ≤32 bytes para BLAKE2s")
        if len(auth_key) < 1:
            # Permitir clave por defecto para pruebas
            auth_key = b"\x00"
        self.host = host
        self.port = port
        self._auth_key: bytes = auth_key
        self._nonce: int = 0
        self._lock = threading.Lock()
        # Conjunto de nonces vistos (anti-replay local para recv)
        self._seen_nonces: set[int] = set()

    # ------------------------------------------------------------------
    # Nonce management
    # ------------------------------------------------------------------
    def _next_nonce(self) -> int:
        """Retorna siguiente nonce y lo incrementa. Thread-safe vía _lock."""
        n = self._nonce
        self._nonce += 1
        return n

    # ------------------------------------------------------------------
    # ping — no bloqueante, timeout ≤2s
    # ------------------------------------------------------------------
    def ping(self, timeout: float = 2.0) -> bool:
        """
        Verifica conectividad TCP al nodo ALADIN.
        Timeout: ≤2s. Nunca lanza exception — retorna True/False.
        """
        effective_timeout = min(timeout, 2.0)
        try:
            with socket.create_connection((self.host, self.port),
                                          timeout=effective_timeout) as sock:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            return True
        except (OSError, TimeoutError):
            log.debug("ALADIN offline (ping failed): %s:%d", self.host, self.port)
            return False
        except Exception as e:
            log.debug("ALADIN ping exception: %s", e)
            return False

    # ------------------------------------------------------------------
    # send_slab_ptr — enviar puntero SLAB_ID + metadata
    # ------------------------------------------------------------------
    def send_slab_ptr(self, slab_id: int, metadata: dict) -> bool:
        """
        Envía un puntero SLAB_ID al nodo ALADIN con BLAKE2s MAC.
        Ghost Protocol: NUNCA incluye datos del tensor, solo el ID.
        Si ALADIN offline → retorna False sin exception.

        Args:
            slab_id:  Identificador del slab en PmtpShmBus (int).
            metadata: Dict pequeño con métricas (ej. shape, dtype, D). ≤512B JSON.

        Returns:
            True si el mensaje fue enviado con éxito, False si offline o error.
        """
        try:
            with self._lock:
                nonce = self._next_nonce()
            payload = _encode_message(self._auth_key, nonce, slab_id, metadata)
            with socket.create_connection((self.host, self.port),
                                          timeout=2.0) as sock:
                frame = struct.pack("<I", len(payload)) + payload
                sock.sendall(frame)
                return True
        except (OSError, TimeoutError) as e:
            log.debug("send_slab_ptr failed (offline?): %s", e)
            return False
        except Exception as e:
            log.warning("send_slab_ptr unexpected error: %s", e)
            return False

    # ------------------------------------------------------------------
    # recv_slab_ptr — recibir puntero SLAB_ID desde ALADIN
    # ------------------------------------------------------------------
    def recv_slab_ptr(self, timeout: float = 5.0) -> Optional[tuple[int, dict]]:
        """
        Recibe un puntero SLAB_ID enviado por el nodo ALADIN.
        Verifica BLAKE2s MAC y anti-replay.

        Returns:
            (slab_id, metadata) si válido, None si timeout/offline/error.
        """
        try:
            with socket.create_connection((self.host, self.port),
                                          timeout=min(timeout, 2.0)) as sock:
                # Leer 4 bytes de longitud
                raw_len = _recv_exact(sock, 4, timeout)
                if raw_len is None:
                    return None
                (msg_len,) = struct.unpack("<I", raw_len)
                if msg_len < _HEADER_SIZE or msg_len > _HEADER_SIZE + _METADATA_MAX_BYTES:
                    log.warning("recv_slab_ptr: longitud de mensaje inválida: %d", msg_len)
                    return None
                raw_msg = _recv_exact(sock, msg_len, timeout)
                if raw_msg is None:
                    return None
                with self._lock:
                    slab_id, metadata = _decode_message(
                        self._auth_key, raw_msg, self._seen_nonces
                    )
                return slab_id, metadata
        except (OSError, TimeoutError) as e:
            log.debug("recv_slab_ptr failed (offline?): %s", e)
            return None
        except ValueError as e:
            log.warning("recv_slab_ptr protocol error: %s", e)
            return None
        except Exception as e:
            log.warning("recv_slab_ptr unexpected error: %s", e)
            return None


def _recv_exact(sock: socket.socket, n: int, timeout: float) -> Optional[bytes]:
    """Lee exactamente n bytes del socket, con timeout total."""
    buf = bytearray()
    deadline = time.monotonic() + timeout
    while len(buf) < n:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        sock.settimeout(remaining)
        try:
            chunk = sock.recv(n - len(buf))
        except OSError:
            return None
        if not chunk:
            return None
        buf.extend(chunk)
    return bytes(buf)
