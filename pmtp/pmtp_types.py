# ============================================================================
# PMTP TYPE DEFINITIONS & BINARY ABI (PYTHON 3.12+ CONTRACT)
# Proyecto: PMTP (Polydim Memory Tensor Protocol)
# Autor: Ariel García Traba — Independent Research / EinsofOS
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
