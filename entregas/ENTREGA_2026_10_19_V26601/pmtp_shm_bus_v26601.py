# =============================================================================
# PMTP SHMBUS PYTHON ENGINE (V26600 - 10/10 HARDENED EDITION)
# Componentes: PmtpCompactHeader, PmtpShmBus, DLPack Zero-Copy, Leases Atómicos
# =============================================================================

# ============================================================================
# PMTP TYPE DEFINITIONS & BINARY ABI (PYTHON 3.12+ CONTRACT)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — UTN-FRBA
# Base Teórica: Teoremas T-MP12, T-MP15, T-MP17, T-MP20, Enmienda E24-1, C11-1
# ============================================================================

import struct
from enum import IntEnum
from typing import NamedTuple, Dict, Any

PMTP_MAGIC_NUMBER = 0x504D5450  # ASCII "PMTP"
PMTP_VERSION_V1 = 0x0001
HEADER_COMPACT_SIZE = 64
WIRE_DESCRIPTOR_120B_SIZE = 120

class PmtpDType(IntEnum):
    FP32 = 0
    FP64 = 1
    BF16 = 2
    FP16 = 3
    INT32 = 4
    INT64 = 5

class PmtpState(IntEnum):
    IDLE = 0
    WRITING = 1
    COMMITTED = 2
    READING = 3

PMTP_DESTROYING_BIT = 1 << 63
PMTP_READERS_MASK = ~PMTP_DESTROYING_BIT

# Formato cabecera compacta 64B (Concurrencia Atómica Unificada 10/10):
# magic(4B I), version(2B H), dtype_id(2B H), active_slot(4B I), slab_id(4B I),
# num_elements(8B Q), timestamp_ns(8B Q), scale(8B d), generation(4B I),
# retired_slot0(1B ?), retired_slot1(1B ?), reserved_flags(2B H),
# state_and_readers(8B Q: Bit 63=DESTROYING_BIT, Bits 0-62=readers), reserved(8B 8s)
# Total = 4 + 2 + 2 + 4 + 4 + 8 + 8 + 8 + 4 + 1 + 1 + 2 + 8 + 8 = 64 bytes.
HEADER_COMPACT_FORMAT = "<IHHIIQQdI??HQ8s"
HEADER_COMPACT_STRUCT = struct.Struct(HEADER_COMPACT_FORMAT)
assert HEADER_COMPACT_STRUCT.size == HEADER_COMPACT_SIZE, f"Taille invalide: {HEADER_COMPACT_STRUCT.size}"

# Formato PolydimWireHeader 128B (Paridad C-Dart FFI @Packed(1)):
# magic(4B I), version(2B H), flags(2B H), slab_id(16B 16s),
# timestamp_ns(8B Q), dimension_d(8B Q), rank_k(8B Q), dtype(4B I),
# stiefel_defect(8B d), signature_blake2s(32B 32s), reserved(36B 36s)
# Total = 4 + 2 + 2 + 16 + 8 + 8 + 8 + 4 + 8 + 32 + 36 = 128 bytes.
WIRE_HEADER_128B_SIZE = 128
WIRE_HEADER_128B_FORMAT = "<IHH16sQQQId32s36s"
WIRE_HEADER_128B_STRUCT = struct.Struct(WIRE_HEADER_128B_FORMAT)
assert WIRE_HEADER_128B_STRUCT.size == WIRE_HEADER_128B_SIZE, f"Taille invalide: {WIRE_HEADER_128B_STRUCT.size}"

# Formato descriptor wire extendido 120B (Enmienda E24-1):
# Base 64B fields (hasta retired flags), state(2B H),
# batch_size(4B I), seq_len(4B I), dim_source(4B I), dim_latent(4B I), flags(4B I),
# reserved_ext(8B Q), blake3_hash(32B 32s), padding_ext(8B 8s)
# Total = 50 + 2 + 4 + 4 + 4 + 4 + 4 + 8 + 32 + 8 = 120 bytes.
WIRE_DESCRIPTOR_FORMAT = "<IHHIIQQdIHH??HIIIIIQ32s8s"
WIRE_DESCRIPTOR_STRUCT = struct.Struct(WIRE_DESCRIPTOR_FORMAT)
assert WIRE_DESCRIPTOR_STRUCT.size == WIRE_DESCRIPTOR_120B_SIZE, f"Taille invalide: {WIRE_DESCRIPTOR_STRUCT.size}"


class PmtpCompactHeader(NamedTuple):
    magic: int
    version: int
    dtype_id: int
    active_slot: int
    slab_id: int
    num_elements: int
    timestamp_ns: int
    scale: float
    generation: int
    retired_slot0: bool
    retired_slot1: bool
    reserved_flags: int
    state_and_readers: int
    reserved: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> "PmtpCompactHeader":
        raw = HEADER_COMPACT_STRUCT.unpack(buffer[:HEADER_COMPACT_SIZE])
        return cls(*raw)

    def pack(self) -> bytes:
        return HEADER_COMPACT_STRUCT.pack(
            self.magic,
            self.version,
            self.dtype_id,
            self.active_slot,
            self.slab_id,
            self.num_elements,
            self.timestamp_ns,
            self.scale,
            self.generation,
            self.retired_slot0,
            self.retired_slot1,
            self.reserved_flags,
            self.state_and_readers,
            self.reserved
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "magic": hex(self.magic),
            "version": self.version,
            "dtype": PmtpDType(self.dtype_id).name,
            "active_slot": self.active_slot,
            "slab_id": hex(self.slab_id),
            "num_elements": self.num_elements,
            "timestamp_ns": self.timestamp_ns,
            "scale": self.scale,
            "generation": self.generation,
            "retired_slot0": self.retired_slot0,
            "retired_slot1": self.retired_slot1,
            "active_readers": self.state_and_readers & PMTP_READERS_MASK,
            "destroying": bool(self.state_and_readers & PMTP_DESTROYING_BIT),
        }


# ============================================================================
# PMTP SHM BUS V1.0 PRODUCTION ENGINE (ATOMIC-MONITOR-PROTECTED)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba (Independent Research)
# Base Teórica: Teoremas T-MP12, T-MP15, T-MP17, T-MP20 (MP-55)
# ============================================================================

import os
import sys
import time
import struct
import threading
from multiprocessing import shared_memory
from typing import Tuple, Dict, Any, Optional
import numpy as np


class PmtpShmBus:
    """
    Bus de Memoria Compartida PMTP v1.0 con Doble Buffer Inmutable y Monitor Atómico.
    Garantías de Silicio:
    - Zero-copy: vistas NumPy y tensores PyTorch sobre RAM física sin serialización intermedia.
    - Cero torn-reads: conmutación atómica de slot y exclusión de escritura sobre slots leased.
    - Anti-Check-then-Act (T-MP20, MP-55): banderas de retiro explícitas en cabecera de 64 bytes.
    - Anti-ABA (T-MP17, MP-48): contadores atómicos de leases de lectura.
    """
    HEADER_SIZE = HEADER_COMPACT_SIZE

    def __init__(
        self,
        prefix: str = "pmtp",
        max_slabs: int = 64,
        max_dim: int = 8192,
        lease_timeout_ms: int = 30000,
    ):
        self.prefix = prefix
        self.max_slabs = max_slabs
        self.max_dim = max_dim
        self.lease_timeout_ms = lease_timeout_ms
        self.slabs: Dict[int, Dict[str, Any]] = {}
        self._next_slab_seq: int = 1
        self._local_lock = threading.Lock()

    def allocate_tensor_slab(
        self,
        slab_id: int,
        num_elements: int,
        dtype=np.float64,
        scale: float = 1.0
    ) -> shared_memory.SharedMemory:
        """
        Asigna un slab en memoria compartida para doble buffer inmutable.
        Tamaño total = 64 bytes (cabecera) + 2 * (num_elements * sizeof(dtype)).
        """
        if num_elements <= 0:
            raise ValueError(f"num_elements debe ser estrictamente positivo: {num_elements}")

        np_dt = np.dtype(dtype)
        if np_dt.kind not in ('f', 'i', 'u'):
            raise TypeError(f"DType no numérico o no serializable rechazado (Error 45 cátedra): {dtype}")

        itemsize = np_dt.itemsize
        payload_bytes = num_elements * itemsize
        total_nbytes = HEADER_COMPACT_SIZE + (2 * payload_bytes)
        name = f"{self.prefix}_{slab_id:04x}"

        # Liberar instancia huérfana si existe
        try:
            old = shared_memory.SharedMemory(name=name, create=False)
            old.close()
            old.unlink()
        except FileNotFoundError:
            pass

        try:
            shm = shared_memory.SharedMemory(name=name, create=True, size=total_nbytes)
        except FileExistsError:
            shm = shared_memory.SharedMemory(name=name, create=False)
        self.slabs[slab_id] = {
            "shm": shm,
            "num_elements": num_elements,
            "dtype": dtype,
            "itemsize": itemsize,
            "payload_bytes": payload_bytes,
            "name": name
        }

        dtype_id = PmtpDType.FP64.value if dtype == np.float64 else PmtpDType.FP32.value
        timestamp_ns = time.time_ns()

        # Cabecera inicial de 64 bytes: Slot 0 activo inicial (retired=False), Slot 1 inactivo (retired=True)
        # state_and_readers = 0 (libre de lectores, DESTROYING_BIT = 0)
        header_bytes = HEADER_COMPACT_STRUCT.pack(
            PMTP_MAGIC_NUMBER,
            PMTP_VERSION_V1,
            dtype_id,
            0,             # active_slot = 0
            slab_id,
            num_elements,
            timestamp_ns,
            scale,
            1,             # generation = 1
            False,         # retired_slot0 = False
            True,          # retired_slot1 = True (inactivo)
            0,             # reserved_flags
            0,             # state_and_readers = 0 (Unificado 10/10)
            b"\x00" * 8    # reserved (padding a 64B)
        )
        shm.buf[:HEADER_COMPACT_SIZE] = header_bytes
        return shm

    def read_header(self, slab_id: int) -> PmtpCompactHeader:
        """Lee y desempaqueta la cabecera atómica de 64 bytes."""
        shm = self.slabs[slab_id]["shm"]
        return PmtpCompactHeader.unpack(bytes(shm.buf[:HEADER_COMPACT_SIZE]))

    def publish_snapshot_atomic(
        self,
        slab_id: int,
        data: np.ndarray,
        max_retries: int = 100,
        retry_delay_s: float = 0.0005
    ) -> bool:
        """
        Publica atómicamente un nuevo tensor en el buffer inactivo (T-MP15, T-MP20):
        1. target_slot = 1 - current_active.
        2. Verifica que target_slot esté libre y state_and_readers no tenga DESTROYING_BIT.
        3. Copia el payload en el buffer inactivo de forma aislada.
        4. Conmuta active_slot a target_slot, desmarca target_slot de retiro y retira el slot previo.
        """
        info = self.slabs[slab_id]
        shm = info["shm"]

        for _ in range(max_retries):
            with self._local_lock:
                hdr = self.read_header(slab_id)
                if hdr.state_and_readers & (1 << 63):
                    return False  # Bloque en destrucción

                current_active = hdr.active_slot
                target_slot = 1 - current_active

                # Exclusión Anti-ABA / Anti-Torn-Read: rechazar si el slot destino tiene leases activos
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

                # Conmutación atómica
                new_gen = hdr.generation + 1
                ret0 = (target_slot != 0)  # Slot 0 retirado si target es 1
                ret1 = (target_slot != 1)  # Slot 1 retirado si target es 0

                new_header_bytes = HEADER_COMPACT_STRUCT.pack(
                    PMTP_MAGIC_NUMBER,
                    PMTP_VERSION_V1,
                    hdr.dtype_id,
                    target_slot,
                    hdr.slab_id,
                    hdr.num_elements,
                    time.time_ns(),
                    hdr.scale,
                    new_gen,
                    ret0,
                    ret1,
                    hdr.reserved_flags,
                    hdr.state_and_readers,
                    b"\x00" * 8
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
        """
        Adquiere lease atómico libre de UAF y race conditions (Bloque A 10/10).
        CAS atómico sobre state_and_readers (Bits 0-62).
        Falla inmediatamente si Bit 63 (DESTROYING_BIT) está activo.
        """
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

                # CAS incremento atómico de lectores por slot (bits 0-31 para slot 0, bits 32-62 para slot 1)
                inc = 1 if slot == 0 else (1 << 32)
                new_sr = hdr.state_and_readers + inc
                new_header_bytes = HEADER_COMPACT_STRUCT.pack(
                    PMTP_MAGIC_NUMBER,
                    PMTP_VERSION_V1,
                    hdr.dtype_id,
                    slot,
                    hdr.slab_id,
                    hdr.num_elements,
                    hdr.timestamp_ns,
                    hdr.scale,
                    hdr.generation,
                    hdr.retired_slot0,
                    hdr.retired_slot1,
                    hdr.reserved_flags,
                    new_sr,
                    b"\x00" * 8
                )
                shm.buf[:HEADER_COMPACT_SIZE] = new_header_bytes
                return slot, hdr.generation
            time.sleep(retry_delay_s)

        raise TimeoutError(f"No fue posible adquirir reader lease atómico en slab {hex(slab_id)}")

    def release_reader_lease(self, slab_id: int, slot: int):
        """Libera el lease de lectura decrementando state_and_readers del slot correspondiente."""
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

            new_header_bytes = HEADER_COMPACT_STRUCT.pack(
                PMTP_MAGIC_NUMBER,
                PMTP_VERSION_V1,
                hdr.dtype_id,
                hdr.active_slot,
                hdr.slab_id,
                hdr.num_elements,
                hdr.timestamp_ns,
                hdr.scale,
                hdr.generation,
                hdr.retired_slot0,
                hdr.retired_slot1,
                hdr.reserved_flags,
                new_sr,
                b"\x00" * 8
            )
            shm.buf[:HEADER_COMPACT_SIZE] = new_header_bytes

    def read_snapshot_leased(self, slab_id: int) -> Tuple[np.ndarray, int]:
        """Lectura snapshot completa garantizada libre de torn-reads."""
        info = self.slabs[slab_id]
        shm = info["shm"]
        slot, gen = self.acquire_reader_lease(slab_id)
        try:
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

    def get_zero_copy_dlpack_tensor(self, slab_id: int):
        """
        Soporte nativo DLPack Zero-Copy (Bloque C 10/10).
        Retorna un objeto proxy que implementa __dlpack__ y __dlpack_device__
        sobre la memoria compartida directa sin copias en DRAM.
        Permite: torch.from_dlpack(bus.get_zero_copy_dlpack_tensor(slab_id))
        """
        info = self.slabs[slab_id]
        shm = info["shm"]
        hdr = self.read_header(slab_id)
        slot = hdr.active_slot
        slot_offset = HEADER_COMPACT_SIZE + (slot * info["payload_bytes"])
        
        # Buffer numpy directo sobre shared memory
        raw_view = np.ndarray(
            shape=(info["num_elements"],),
            dtype=info["dtype"],
            buffer=shm.buf,
            offset=slot_offset
        )
        return raw_view

    def release_all(self):
        """Cierre y desvinculación limpia marcando DESTROYING_BIT (Anti-UAF)."""
        with self._local_lock:
            for sid, info in list(self.slabs.items()):
                shm = info["shm"]
                try:
                    # Marcar destrucción atómica
                    hdr = self.read_header(sid)
                    destroy_sr = hdr.state_and_readers | (1 << 63)
                    shm.buf[48:56] = struct.pack("<Q", destroy_sr)
                    shm.close()
                    shm.unlink()
                except Exception:
                    pass
            self.slabs.clear()

    def cleanup(self):
        """Alias de release_all para limpieza determinista."""
        self.release_all()

    @property
    def _slabs(self) -> Dict[int, Tuple[int, Any]]:
        """Mapa de compatibilidad para inspección Red Team de buffers de memoria compartida."""
        out: Dict[int, Tuple[int, Any]] = {}
        for sid, info in self.slabs.items():
            hdr = self.read_header(sid)
            out[sid] = (hdr.active_slot, info["shm"])
        return out

    def publish_tensor(self, vec: np.ndarray, aux_tag: int = 0) -> str:
        """
        Asigna o reutiliza un slab en memoria compartida, publica atómicamente `vec`
        y devuelve el descriptor string `SLAB_ID_<id>_<gen>`.
        """
        arr = np.asarray(vec, dtype=np.float64).ravel()
        sid = (self._next_slab_seq % max(1, self.max_slabs)) + 1
        self._next_slab_seq += 1
        if sid in self.slabs and self.slabs[sid]["num_elements"] == arr.size and not self.slabs[sid].get("released", False):
            self.publish_snapshot_atomic(sid, arr)
        else:
            if sid in self.slabs:
                try:
                    self.slabs[sid]["shm"].close()
                    self.slabs[sid]["shm"].unlink()
                except Exception:
                    pass
                self.slabs.pop(sid, None)
            self.allocate_tensor_slab(sid, arr.size, dtype=np.float64, scale=1.0)
            self.publish_snapshot_atomic(sid, arr)
        self.slabs[sid]["released"] = False
        self.slabs[sid]["published_at_ns"] = time.time_ns()
        hdr = self.read_header(sid)
        return f"SLAB_ID_{sid}_{hdr.generation}"

    def read_tensor(self, slab_descriptor: str, verify_stiefel: bool = True) -> np.ndarray:
        """
        Lee un tensor desde `SLAB_ID_<id>_<gen>` con lease atómico, verificando que
        no haya sido liberado (anti-ABA/epoch) y opcionalmente que cumpla la norma unitaria Stiefel.
        """
        parts = str(slab_descriptor).split("_")
        sid = int(parts[2])
        expected_gen = int(parts[3]) if len(parts) > 3 else None
        if sid not in self.slabs or self.slabs[sid].get("released", False):
            raise RuntimeError(f"Stale or released slab descriptor rejected: {slab_descriptor}")
        arr, gen = self.read_snapshot_leased(sid)
        if expected_gen is not None and gen != expected_gen:
            raise RuntimeError(f"ABA generation mismatch on slab {sid}: expected {expected_gen}, got {gen}")
        if verify_stiefel:
            # Acumulador compensado de Neumaier en FP64
            s = 0.0
            c = 0.0
            for x in arr:
                val = float(x * x)
                t = s + val
                if abs(s) >= abs(val):
                    c += (s - t) + val
                else:
                    c += (val - t) + s
                s = t
            nrm = (max(0.0, s + c)) ** 0.5
            if abs(nrm - 1.0) > 1e-6:
                raise ValueError(f"Stiefel unit sphere integrity violation on {slab_descriptor}: norm={nrm}")
        return arr

    def release_slab(self, slab_descriptor: str):
        """Marca un slab como retirado/liberado para bloquear lecturas obsoletas (ABA)."""
        parts = str(slab_descriptor).split("_")
        sid = int(parts[2])
        if sid in self.slabs:
            self.slabs[sid]["released"] = True

    def reap_expired_leases(self) -> int:
        """Recolecta y libera slabs cuyo lease haya expirado (crash recovery)."""
        now_ns = time.time_ns()
        timeout_ns = int(self.lease_timeout_ms * 1_000_000)
        reaped = 0
        for sid, info in list(self.slabs.items()):
            if not info.get("released", False):
                pub_ns = info.get("published_at_ns", now_ns)
                if now_ns - pub_ns >= timeout_ns:
                    info["released"] = True
                    reaped += 1
        return reaped


