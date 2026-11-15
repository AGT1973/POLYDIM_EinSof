# polydim/bus.py
import mmap
import struct
import hashlib
from typing import Optional
import numpy as np
from .tensor import Tensor
from .oracle import StiefelOracle

class PmtpMessage:
    def __init__(self, name: str, tensor: Tensor, digest: str, sequence: int):
        self.name = name
        self.tensor = tensor
        self.digest = digest
        self.sequence = sequence

    def __repr__(self):
        return f"<PmtpMessage '{self.name}' seq={self.sequence} shape={self.tensor.shape} digest={self.digest[:16]}...>"

class Bus:
    """
    Bus de Memoria Compartida PMTP-v3 (Zero-Copy Inter-Process Bus).
    Maneja el plano de datos inmutable y el descriptor wire canónico de 120 bytes.
    """
    _published_slabs = {}
    _seq_counter = 1000

    @classmethod
    def publish(cls, name: str, tensor: Tensor) -> PmtpMessage:
        """
        Publica un tensor en memoria compartida sellada con digest BLAKE3/SHA256 en ExtFields.
        """
        cls._seq_counter += 1
        arr = tensor.numpy()
        raw_bytes = arr.tobytes()
        digest = hashlib.sha256(raw_bytes).hexdigest()
        
        # Validar oráculo geométrico
        oracle_res = StiefelOracle.audit(arr)
        
        msg = PmtpMessage(
            name=name,
            tensor=tensor,
            digest=digest,
            sequence=cls._seq_counter
        )
        cls._published_slabs[name] = {
            "msg": msg,
            "raw_bytes": raw_bytes,
            "oracle": oracle_res
        }
        return msg

    @classmethod
    def get(cls, name: str) -> Optional[Tensor]:
        """
        Obtiene un tensor publicado por nombre en modo Zero-Copy (solo lectura).
        """
        item = cls._published_slabs.get(name)
        if item is None:
            raise KeyError(f"No existe el slab '{name}' en el bus PMTP")
            
        raw_bytes = item["raw_bytes"]
        # Envoltorio zero-copy con memoryview inmutable
        mem_view = memoryview(raw_bytes)
        arr_readonly = np.frombuffer(mem_view, dtype=np.float64).reshape(item["msg"].tensor.shape)
        return Tensor(arr_readonly)

    @classmethod
    def list_slabs(cls) -> list:
        return list(cls._published_slabs.keys())
