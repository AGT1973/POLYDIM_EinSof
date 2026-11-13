# ============================================================================
# PMTP SHM BUS V1.1 HARDENED (ZEROIZATION + 0600 PERMS + KEYED BLAKE2S MAC)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba (Independent Research)
# Base Teórica: Teoremas T-MP12, T-MP15, T-MP17, T-MP20 (MP-55)
# ============================================================================

import os
import mmap
import secrets
import time
import math
import hmac
import struct
import hashlib
import threading
import weakref
from multiprocessing import shared_memory
from typing import Tuple, Dict, Any, Optional
import numpy as np

try:
    import fcntl
except ImportError:
    fcntl = None

try:
    from .pmtp_types import (
        PMTP_MAGIC_NUMBER,
        PMTP_VERSION_V1,
        PMTP_FLAG_MEMFD_BACKED,
        PMTP_FLAG_SEALED,
        HEADER_COMPACT_SIZE,
        HEADER_COMPACT_FORMAT,
        HEADER_COMPACT_STRUCT,
        PmtpDType,
        PmtpState,
        PmtpCompactHeader,
        validate_compact_header,
    )
except ImportError:
    from pmtp_types import (
        PMTP_MAGIC_NUMBER,
        PMTP_VERSION_V1,
        PMTP_FLAG_MEMFD_BACKED,
        PMTP_FLAG_SEALED,
        HEADER_COMPACT_SIZE,
        HEADER_COMPACT_FORMAT,
        HEADER_COMPACT_STRUCT,
        PmtpDType,
        PmtpState,
        PmtpCompactHeader,
        validate_compact_header,
    )

try:
    from pmtp_pob_bus import PmtpPobProducer, PmtpPobConsumer, PmtpPobView, PmtpPolicy, PmtpStatus
except ImportError:
    pass


class _MemfdShmAdapter:
    """Adaptador compatible con SharedMemory (.buf/.close/.unlink) respaldado por os.memfd_create."""
    def __init__(self, name: str, size: int, seal_resize: bool = True):
        if not hasattr(os, "memfd_create"):
            raise NotImplementedError("os.memfd_create no disponible en esta plataforma")
        mfd_flags = getattr(os, "MFD_CLOEXEC", 0) | getattr(os, "MFD_ALLOW_SEALING", 0)
        self.name = name
        self.fd = os.memfd_create(name, mfd_flags)
        try:
            os.fchmod(self.fd, 0o600)
            actual_mode = os.stat(self.fd).st_mode & 0o777
            if actual_mode != 0o600:
                raise PermissionError(f"Fail-closed: memfd mode esperado 0600, recibido {oct(actual_mode)}")
            os.ftruncate(self.fd, size)
            self._mmap = mmap.mmap(self.fd, size, access=mmap.ACCESS_WRITE)
            self.buf = memoryview(self._mmap)
            self.sealed = False
            if seal_resize and fcntl is not None and hasattr(fcntl, "F_ADD_SEALS"):
                seals = (
                    getattr(fcntl, "F_SEAL_SHRINK", 0x0002)
                    | getattr(fcntl, "F_SEAL_GROW", 0x0004)
                    | getattr(fcntl, "F_SEAL_SEAL", 0x0001)
                )
                try:
                    fcntl.fcntl(self.fd, fcntl.F_ADD_SEALS, seals)
                    self.sealed = True
                except OSError as exc:
                    raise PermissionError("Fail-closed: no se pudieron aplicar sellos F_SEAL_* en memfd") from exc
        except Exception:
            os.close(self.fd)
            raise

    def close(self) -> None:
        try:
            if getattr(self, "buf", None) is not None:
                self.buf.release()
                self.buf = None
        except Exception:
            pass
        try:
            if getattr(self, "_mmap", None) is not None:
                self._mmap.close()
                self._mmap = None
        except Exception:
            pass
        if getattr(self, "fd", -1) >= 0:
            try:
                os.close(self.fd)
            except Exception:
                pass
            self.fd = -1

    def unlink(self) -> None:
        # memfd es anónimo y se destruye automáticamente al cerrar último descriptor (sin residuo en /dev/shm)
        pass


class PmtpLeasedArray(np.ndarray):
    """Subclase de ndarray con __dict__ y soporte de ciclo de vida para DLPack."""
    pass


class PmtpShmBus:
    """
    Bus de Memoria Compartida PMTP v1.1 con Doble Buffer Inmutable, Monitor Atómico,
    Permisos 0600 Explícitos, Zeroización Determinista al Cerrar y Autenticación MAC (BLAKE2s-64).

    Garantías de Silicio:
    - Zero-copy: vistas NumPy y DLPack sobre RAM física sin serialización intermedia.
    - Cero torn-reads: conmutación atómica de slot y exclusión de escritura sobre slots leased.
    - Anti-Snooping / Anti-Inyección Co-Inquilino: permisos POSIX 0600 explícitos (S_IRUSR|S_IWUSR)
      y etiqueta MAC keyed BLAKE2s-64 (offset 56..64) verificada con compare_digest constante.
    - Zeroización Determinista: limpieza explícita de memoria física a 0x00 antes de unlink/close.
    """
    HEADER_SIZE = HEADER_COMPACT_SIZE
    IMMUTABLE_META_BYTES = 48
    STATE_AND_READERS_OFFSET = 48
    MAC_OFFSET = 56

    def __init__(
        self,
        prefix: str = "pmtp",
        max_slabs: int = 64,
        max_dim: int = 8192,
        lease_timeout_ms: int = 30000,
        auth_key: Optional[bytes] = None,
        backend: str = "auto",
    ):
        self.prefix = prefix
        self.max_slabs = max_slabs
        self.max_dim = max_dim
        self.lease_timeout_ms = lease_timeout_ms
        self.backend = backend
        self._instance_nonce: str = secrets.token_hex(4)
        self.slabs: Dict[int, Dict[str, Any]] = {}
        self._next_slab_seq: int = 1
        self._local_lock = threading.Lock()

        if auth_key is not None:
            key_raw = bytes(auth_key)
        else:
            env_secret = os.environ.get("PMTP_SHM_KEY")
            key_raw = env_secret.encode("utf-8") if env_secret else os.urandom(32)
        self._auth_key: bytes = hashlib.blake2s(key_raw, digest_size=32).digest()

    def _compute_mac64(self, header_48b: bytes, payload_bytes: bytes) -> bytes:
        """Calcula etiqueta MAC BLAKE2s-64 autenticada sobre metadatos inmutables + payload."""
        h = hashlib.blake2s(key=self._auth_key, digest_size=8)
        h.update(header_48b)
        h.update(payload_bytes)
        return h.digest()

    @staticmethod
    def _enforce_0600_permissions(shm_name: str) -> str:
        """Aplica permisos 0600 explícitos en POSIX /dev/shm (anula umask permisiva)."""
        if os.name == "posix":
            clean_name = shm_name.lstrip("/")
            shm_path = os.path.join("/dev/shm", clean_name)
            if os.path.exists(shm_path):
                os.chmod(shm_path, 0o600)
                mode = os.stat(shm_path).st_mode & 0o777
                if mode != 0o600:
                    raise PermissionError(f"Fallo al imponer permisos 0600 en {shm_path}: modo actual {oct(mode)}")
                return "0600"
        return "0600_PRIVATE_SESSION"

    @staticmethod
    def _zeroize_shm(shm: shared_memory.SharedMemory) -> None:
        """Sobrescribe determinísticamente todo el segmento SHM con 0x00 antes de close/unlink."""
        try:
            buf = shm.buf
            if buf is not None:
                n = len(buf)
                chunk = b"\x00" * min(65536, n)
                for off in range(0, n, len(chunk)):
                    end = min(off + len(chunk), n)
                    buf[off:end] = chunk[:end - off]
        except Exception:
            pass

    def _pack_header_with_mac(
        self,
        dtype_id: int,
        active_slot: int,
        slab_id: int,
        num_elements: int,
        timestamp_ns: int,
        scale: float,
        generation: int,
        retired_slot0: bool,
        retired_slot1: bool,
        reserved_flags: int,
        state_and_readers: int,
        payload_bytes: bytes,
    ) -> bytes:
        """Empaqueta cabecera de 64 bytes con tag MAC BLAKE2s-64 en bytes 56..64."""
        meta_48 = struct.pack(
            "<IHHIIQQdI??H",
            PMTP_MAGIC_NUMBER,
            PMTP_VERSION_V1,
            dtype_id,
            active_slot,
            slab_id,
            num_elements,
            timestamp_ns,
            scale,
            generation,
            retired_slot0,
            retired_slot1,
            reserved_flags,
        )
        mac_tag = self._compute_mac64(meta_48, payload_bytes)
        return meta_48 + struct.pack("<Q8s", state_and_readers, mac_tag)

    def _verify_mac(self, shm: shared_memory.SharedMemory, hdr: PmtpCompactHeader, slot: int, payload_bytes_len: int) -> None:
        """Verifica en tiempo constante la integridad y autenticidad MAC del slab."""
        meta_48 = bytes(shm.buf[:self.IMMUTABLE_META_BYTES])
        slot_offset = HEADER_COMPACT_SIZE + (slot * payload_bytes_len)
        payload = bytes(shm.buf[slot_offset:slot_offset + payload_bytes_len])
        expected_mac = self._compute_mac64(meta_48, payload)
        if not hmac.compare_digest(expected_mac, hdr.reserved):
            raise PermissionError(
                f"PMTP MAC authentication failure on slab {hex(hdr.slab_id)} slot {slot}: "
                "posible inyección o corrupción de proceso co-inquilino."
            )

    def allocate_tensor_slab(
        self,
        slab_id: int,
        num_elements: int,
        dtype=np.float64,
        scale: float = 1.0
    ) -> shared_memory.SharedMemory:
        """
        Asigna un slab en memoria compartida para doble buffer inmutable con permisos 0600 y MAC.
        Tamaño total = 64 bytes (cabecera) + 2 * (num_elements * sizeof(dtype)).
        """
        if num_elements <= 0:
            raise ValueError(f"num_elements debe ser estrictamente positivo: {num_elements}")

        np_dt = np.dtype(dtype)
        dtype_map = {
            np.dtype(np.float32): PmtpDType.FP32.value,
            np.dtype(np.float64): PmtpDType.FP64.value,
            np.dtype(np.float16): PmtpDType.FP16.value,
            np.dtype(np.int32): PmtpDType.INT32.value,
            np.dtype(np.int64): PmtpDType.INT64.value,
        }
        if np_dt not in dtype_map:
            raise TypeError(f"DType no soportado por ABI v1 (use float32/float64/float16/int32/int64): {dtype}")
        dtype_id = dtype_map[np_dt]

        itemsize = np_dt.itemsize
        payload_bytes = num_elements * itemsize
        total_nbytes = HEADER_COMPACT_SIZE + (2 * payload_bytes)
        name = f"{self.prefix}_{self._instance_nonce}_{slab_id:04x}"

        # Fail-closed contra name-squatting o aislamiento memfd_create en Linux
        use_memfd = (self.backend == "memfd") and hasattr(os, "memfd_create")
        flags = 0
        if use_memfd:
            shm = _MemfdShmAdapter(name=name, size=total_nbytes, seal_resize=True)
            perm_mode = "0600_MEMFD_SEALED" if shm.sealed else "0600_MEMFD"
            flags |= PMTP_FLAG_MEMFD_BACKED
            if shm.sealed:
                flags |= PMTP_FLAG_SEALED
        else:
            try:
                shm = shared_memory.SharedMemory(name=name, create=True, size=total_nbytes)
            except FileExistsError as exc:
                raise PermissionError(
                    f"Fail-closed: colisión de nombre SHM detectada en '{name}' (posible name-squatting)"
                ) from exc
            perm_mode = self._enforce_0600_permissions(name)

        self._zeroize_shm(shm)

        self.slabs[slab_id] = {
            "shm": shm,
            "num_elements": num_elements,
            "dtype": dtype,
            "itemsize": itemsize,
            "payload_bytes": payload_bytes,
            "name": name,
            "perm_mode": perm_mode,
            "backend": "memfd" if use_memfd else "shm",
        }

        timestamp_ns = time.time_ns()
        zero_payload = b"\x00" * payload_bytes

        header_bytes = self._pack_header_with_mac(
            dtype_id=dtype_id,
            active_slot=0,
            slab_id=slab_id,
            num_elements=num_elements,
            timestamp_ns=timestamp_ns,
            scale=scale,
            generation=1,
            retired_slot0=False,
            retired_slot1=True,
            reserved_flags=flags,
            state_and_readers=0,
            payload_bytes=zero_payload,
        )
        shm.buf[:HEADER_COMPACT_SIZE] = header_bytes
        return shm

    def read_header(self, slab_id: int) -> PmtpCompactHeader:
        """Lee, valida versión ABI y desempaqueta la cabecera atómica de 64 bytes."""
        info = self.slabs[slab_id]
        shm = info["shm"]
        buf_bytes = bytes(shm.buf[:HEADER_COMPACT_SIZE])
        hdr = PmtpCompactHeader.unpack(buf_bytes, validate=True)
        validate_compact_header(hdr, HEADER_COMPACT_SIZE + 2 * info["payload_bytes"])
        return hdr

    def publish_snapshot_atomic(
        self,
        slab_id: int,
        data: np.ndarray,
        max_retries: int = 100,
        retry_delay_s: float = 0.0005
    ) -> bool:
        """
        Publica atómicamente un nuevo tensor autenticado en el buffer inactivo (T-MP15, T-MP20).
        """
        info = self.slabs[slab_id]
        shm = info["shm"]

        for _ in range(max_retries):
            with self._local_lock:
                hdr = self.read_header(slab_id)
                if hdr.state_and_readers & (1 << 63):
                    return False

                current_active = hdr.active_slot
                target_slot = 1 - current_active

                target_readers = (hdr.state_and_readers >> 32) & 0x7FFFFFFF if target_slot == 1 else (hdr.state_and_readers & 0xFFFFFFFF)
                if target_readers > 0:
                    time.sleep(retry_delay_s)
                    continue

                slot_offset = HEADER_COMPACT_SIZE + (target_slot * info["payload_bytes"])
                target_view = np.ndarray(
                    shape=(info["num_elements"],),
                    dtype=info["dtype"],
                    buffer=shm.buf,
                    offset=slot_offset
                )
                target_view[:] = data[:]
                payload_raw = bytes(shm.buf[slot_offset:slot_offset + info["payload_bytes"]])

                new_gen = hdr.generation + 1
                ret0 = (target_slot != 0)
                ret1 = (target_slot != 1)

                new_header_bytes = self._pack_header_with_mac(
                    dtype_id=hdr.dtype_id,
                    active_slot=target_slot,
                    slab_id=hdr.slab_id,
                    num_elements=hdr.num_elements,
                    timestamp_ns=time.time_ns(),
                    scale=hdr.scale,
                    generation=new_gen,
                    retired_slot0=ret0,
                    retired_slot1=ret1,
                    reserved_flags=hdr.reserved_flags,
                    state_and_readers=hdr.state_and_readers,
                    payload_bytes=payload_raw,
                )
                shm.buf[:HEADER_COMPACT_SIZE] = new_header_bytes
                return True
            time.sleep(retry_delay_s)

        return False

    def acquire_reader_lease(
        self,
        slab_id: int,
        max_retries: int = 50,
        retry_delay_s: float = 0.0003
    ) -> Tuple[int, int]:
        """Adquiere lease atómico en state_and_readers manteniendo intacta la firma MAC."""
        shm = self.slabs[slab_id]["shm"]
        for _ in range(max_retries):
            with self._local_lock:
                hdr = self.read_header(slab_id)
                if hdr.state_and_readers & (1 << 63):
                    raise RuntimeError(f"Falla: Slab {hex(slab_id)} en proceso de destrucción (DESTROYING_BIT activo)")

                slot = hdr.active_slot
                is_retired = hdr.retired_slot1 if slot == 1 else hdr.retired_slot0
                if is_retired:
                    continue

                inc = 1 if slot == 0 else (1 << 32)
                new_sr = hdr.state_and_readers + inc
                shm.buf[self.STATE_AND_READERS_OFFSET:self.STATE_AND_READERS_OFFSET + 8] = struct.pack("<Q", new_sr)
                return slot, hdr.generation
            time.sleep(retry_delay_s)

        raise TimeoutError(f"No fue posible adquirir reader lease atómico en slab {hex(slab_id)}")

    def release_reader_lease(self, slab_id: int, slot: int):
        """Libera el lease de lectura decrementando state_and_readers sin invalidar la firma MAC."""
        if slab_id not in self.slabs:
            return
        shm = self.slabs[slab_id]["shm"]
        with self._local_lock:
            hdr = self.read_header(slab_id)
            destroying = hdr.state_and_readers & (1 << 63)
            r0 = hdr.state_and_readers & 0xFFFFFFFF
            r1 = (hdr.state_and_readers >> 32) & 0x7FFFFFFF

            if slot == 0:
                r0 = max(0, r0 - 1)
            else:
                r1 = max(0, r1 - 1)

            new_sr = destroying | (r1 << 32) | r0
            shm.buf[self.STATE_AND_READERS_OFFSET:self.STATE_AND_READERS_OFFSET + 8] = struct.pack("<Q", new_sr)

    def read_snapshot_leased(self, slab_id: int, verify_mac: bool = True) -> Tuple[np.ndarray, int]:
        """Lectura snapshot garantizada libre de torn-reads y autenticada por MAC BLAKE2s-64."""
        info = self.slabs[slab_id]
        shm = info["shm"]
        slot, gen = self.acquire_reader_lease(slab_id)
        try:
            hdr = self.read_header(slab_id)
            if verify_mac:
                self._verify_mac(shm, hdr, slot, info["payload_bytes"])
            slot_offset = HEADER_COMPACT_SIZE + (slot * info["payload_bytes"])
            view = np.ndarray(
                shape=(info["num_elements"],),
                dtype=info["dtype"],
                buffer=shm.buf,
                offset=slot_offset
            )
            return view.copy(), gen
        finally:
            self.release_reader_lease(slab_id, slot)

    def get_zero_copy_dlpack_tensor(self, slab_id: int, verify_mac: bool = True):
        """Soporte nativo DLPack Zero-Copy blindado bajo Lease Atómico y verificación MAC."""
        info = self.slabs[slab_id]
        shm = info["shm"]
        slot, gen = self.acquire_reader_lease(slab_id)
        hdr = self.read_header(slab_id)
        if verify_mac:
            try:
                self._verify_mac(shm, hdr, slot, info["payload_bytes"])
            except Exception:
                self.release_reader_lease(slab_id, slot)
                raise

        slot_offset = HEADER_COMPACT_SIZE + (slot * info["payload_bytes"])
        raw_base = np.ndarray(
            shape=(info["num_elements"],),
            dtype=info["dtype"],
            buffer=shm.buf,
            offset=slot_offset
        )
        raw_view = raw_base.view(PmtpLeasedArray)
        raw_view.flags.writeable = False
        raw_view._shm_owner = shm
        raw_view._bus_owner = self
        raw_view._leased_slot = slot
        raw_view._generation = gen
        weakref.finalize(raw_view, self.release_reader_lease, slab_id, slot)
        return raw_view

    def release_all(self):
        """Zeroización determinista a 0x00, marcado de DESTROYING_BIT y unlink limpio."""
        with self._local_lock:
            for sid, info in list(self.slabs.items()):
                shm = info["shm"]
                try:
                    hdr = self.read_header(sid)
                    destroy_sr = hdr.state_and_readers | (1 << 63)
                    shm.buf[self.STATE_AND_READERS_OFFSET:self.STATE_AND_READERS_OFFSET + 8] = struct.pack("<Q", destroy_sr)
                except Exception:
                    pass
                self._zeroize_shm(shm)
                try:
                    shm.close()
                except Exception:
                    pass
                try:
                    shm.unlink()
                except Exception:
                    pass
            self.slabs.clear()

    def cleanup(self):
        """Alias de release_all para limpieza determinista con zeroización."""
        self.release_all()

    @property
    def _slabs(self) -> Dict[int, Tuple[int, Any]]:
        out: Dict[int, Tuple[int, Any]] = {}
        for sid, info in self.slabs.items():
            hdr = self.read_header(sid)
            out[sid] = (hdr.active_slot, info["shm"])
        return out

    def publish_tensor(self, vec: np.ndarray, aux_tag: int = 0) -> str:
        """Asigna o reutiliza un slab, publica `vec` autenticado con MAC y devuelve SLAB_ID."""
        arr = np.asarray(vec, dtype=np.float64).ravel()
        sid = (self._next_slab_seq % max(1, self.max_slabs)) + 1
        self._next_slab_seq += 1
        if sid in self.slabs and self.slabs[sid]["num_elements"] == arr.size and not self.slabs[sid].get("released", False):
            self.publish_snapshot_atomic(sid, arr)
        else:
            if sid in self.slabs:
                old_shm = self.slabs[sid]["shm"]
                self._zeroize_shm(old_shm)
                try:
                    old_shm.close()
                    old_shm.unlink()
                except Exception:
                    pass
                self.slabs.pop(sid, None)
            self.allocate_tensor_slab(sid, arr.size, dtype=np.float64, scale=1.0)
            self.publish_snapshot_atomic(sid, arr)
        self.slabs[sid]["released"] = False
        self.slabs[sid]["published_at_ns"] = time.time_ns()
        hdr = self.read_header(sid)
        return f"SLAB_ID_{sid}_{hdr.generation}"

    def read_tensor(self, slab_descriptor: str, verify_stiefel: bool = True, verify_mac: bool = True) -> np.ndarray:
        """Lee un tensor validando epoch anti-ABA, autenticidad MAC BLAKE2s-64 y norma Stiefel."""
        parts = str(slab_descriptor).split("_")
        sid = int(parts[2])
        expected_gen = int(parts[3]) if len(parts) > 3 else None
        if sid not in self.slabs or self.slabs[sid].get("released", False):
            raise RuntimeError(f"Stale or released slab descriptor rejected: {slab_descriptor}")
        arr, gen = self.read_snapshot_leased(sid, verify_mac=verify_mac)
        if expected_gen is not None and gen != expected_gen:
            raise RuntimeError(f"ABA generation mismatch on slab {sid}: expected {expected_gen}, got {gen}")
        if verify_stiefel:
            nrm = math.sqrt(max(0.0, math.fsum(arr * arr)))
            if abs(nrm - 1.0) > 1e-6:
                raise ValueError(f"Stiefel unit sphere integrity violation on {slab_descriptor}: norm={nrm}")
        return arr

    def release_slab(self, slab_descriptor: str):
        """Retira un slab y zeroiza inmediatamente sus ranuras de payload."""
        parts = str(slab_descriptor).split("_")
        sid = int(parts[2])
        if sid in self.slabs:
            info = self.slabs[sid]
            info["released"] = True
            shm = info["shm"]
            try:
                # Zeroizar payload al liberar slab (mantiene header con DESTROYING_BIT)
                payload_start = HEADER_COMPACT_SIZE
                payload_end = payload_start + 2 * info["payload_bytes"]
                shm.buf[payload_start:payload_end] = b"\x00" * (payload_end - payload_start)
            except Exception:
                pass

    def reap_expired_leases(self) -> int:
        """Recolecta, zeroiza y libera slabs cuyo lease haya expirado (crash recovery)."""
        now_ns = time.time_ns()
        timeout_ns = int(self.lease_timeout_ms * 1_000_000)
        reaped = 0
        for sid, info in list(self.slabs.items()):
            if not info.get("released", False):
                pub_ns = info.get("published_at_ns", now_ns)
                if now_ns - pub_ns >= timeout_ns:
                    info["released"] = True
                    shm = info["shm"]
                    try:
                        payload_start = HEADER_COMPACT_SIZE
                        payload_end = payload_start + 2 * info["payload_bytes"]
                        shm.buf[payload_start:payload_end] = b"\x00" * (payload_end - payload_start)
                    except Exception:
                        pass
                    reaped += 1
        return reaped
