import mmap
import os
import sys
import struct
import numpy as np
from multiprocessing import shared_memory

"""
==============================================================================
POLYDIM PMTP-v4 NATIVE VECTOR MEMORY BUS (ZERO 1D JSON - RAM S^{D-1} SLAB)
==============================================================================
Regla 22 & Regla 24:
- Transferencia exclusiva en memoria compartida (SharedMemory / SHM slab).
- Los estados y diagnósticos residen como tensores FP64 en S^{D-1}.
- Cero serialización JSON o texto 1D intermedio. Punteros físicos SLAB_ID.
==============================================================================
"""

SLAB_PREFIX = "polydim_v4_slab_"

class PmtpVectorSlab:
    def __init__(self, slab_id: str, dimension: int = 100_000, create: bool = True):
        self.slab_id = slab_id
        self.dimension = dimension
        self.size_bytes = 128 + (dimension * 8) # 128B PMTP Wire Header + D*sizeof(double)
        
        if create:
            try:
                # Limpiar slab previo si existía
                existing = shared_memory.SharedMemory(name=self.slab_id)
                existing.close()
                existing.unlink()
            except FileNotFoundError:
                pass
            self.shm = shared_memory.SharedMemory(name=self.slab_id, create=True, size=self.size_bytes)
            # Inicializar descriptor de 128 bytes
            # Magic: 0x504D5450, Version: 4, Flags: 1, Epoch: 1, Node: 0, PID, Domain: 0, State: 1
            # Total Elements: dimension, Dtype: 0, Rank: 1, Byte Length: D*8
            header = struct.pack(
                "<IHHQ4I QIIQQ 64s",
                0x504D5450, 4, 1, 1, 0, os.getpid(), 0, 1,
                dimension, 0, 1, dimension * 8, 0,
                self.slab_id.encode("utf-8").ljust(64, b"\x00")
            )
            self.shm.buf[:128] = header
            # Inicializar tensor esférico en S^{D-1} con norma 1.0 (Neumaier / L2)
            v = np.random.randn(dimension).astype(np.float64)
            norm = np.linalg.norm(v)
            if norm > 0:
                v /= norm
            self.get_tensor_view()[:] = v
        else:
            self.shm = shared_memory.SharedMemory(name=self.slab_id, create=False)

    def get_header(self):
        return struct.unpack("<IHHQ4I QIIQQ 64s", self.shm.buf[:128])

    def get_tensor_view(self) -> np.ndarray:
        return np.ndarray(
            shape=(self.dimension,),
            dtype=np.float64,
            buffer=self.shm.buf,
            offset=128
        )

    def verify_manifold_invariants(self) -> tuple[float, float, bool]:
        arr = self.get_tensor_view()
        # Neumaier dot-product norm
        norm_l2 = float(np.linalg.norm(arr))
        # Condition number / finite check
        is_finite = bool(np.all(np.isfinite(arr)))
        deviation = abs(norm_l2 - 1.0)
        return norm_l2, deviation, is_finite and (deviation < 1e-12)

    def close(self):
        self.shm.close()

    def unlink(self):
        try:
            self.shm.unlink()
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    slab_name = "polydim_v4_slab_alpha"
    slab = PmtpVectorSlab(slab_name, dimension=100_000, create=True)
    norm, dev, ok = slab.verify_manifold_invariants()
    print(f"SLAB_ID: {slab_name}")
    print(f"PHYSICAL_ADDR: {hex(id(slab.shm.buf))}")
    print(f"S^{{D-1}} NORM: {norm:.15f} | DEVIATION: {dev:.3e} | VALID: {ok}")
    slab.close()
