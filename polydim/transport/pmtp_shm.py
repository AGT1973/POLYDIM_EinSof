"""
POLYDIM TRANSPORT: PMTP Shared Memory Slab Allocator (SOTA Zero-Copy)
Implements true Zero-Copy local IPC on Windows (Named Shared Memory) and Linux (/dev/shm).
Uses memoryview and np.frombuffer directly onto the mmap buffer without tobytes() or read() memory allocations.
Enforces 64-byte alignment and BLAKE2s streaming verification.
"""

import hashlib
import mmap
import os
import struct
import numpy as np

class PmtpShmBus:
    MAGIC = 0x504D5450  # 'PMTP' in hex
    HEADER_SIZE = 64     # 64 bytes header
    
    def __init__(self, tag_name: str = "polydim_pmtp_bus", size_bytes: int = 16 * 1024 * 1024):
        self.tag_name = tag_name
        self.size_bytes = size_bytes
        self.is_windows = os.name == "nt"
        
        if self.is_windows:
            self.shm = mmap.mmap(-1, self.size_bytes, tagname=self.tag_name, access=mmap.ACCESS_WRITE)
        else:
            # Linux /dev/shm
            self.file_path = f"/dev/shm/{self.tag_name}"
            self.fd = os.open(self.file_path, os.O_CREAT | os.O_RDWR)
            os.ftruncate(self.fd, self.size_bytes)
            self.shm = mmap.mmap(self.fd, self.size_bytes, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)

    def write_tensor(self, tensor: np.ndarray, slab_id: int = 1) -> dict:
        """
        True Zero-Copy write of continuous tensor directly into shared memory.
        Uses memoryview slice to avoid intermediate string/bytes heap materialization.
        """
        tensor = np.ascontiguousarray(tensor, dtype=np.float64)
        dim = tensor.size
        payload_len = tensor.nbytes
        
        if payload_len + self.HEADER_SIZE > self.size_bytes:
            raise ValueError(f"Tensor size ({payload_len} B) exceeds shared memory capacity ({self.size_bytes} B)")
            
        # Zero-copy view into mmap payload region
        target_view = np.frombuffer(self.shm, dtype=np.float64, count=dim, offset=self.HEADER_SIZE)
        np.copyto(target_view, tensor.ravel())
        
        # Checksum over memoryview without intermediate bytes copy
        shm_mv = memoryview(self.shm)
        payload_mv = shm_mv[self.HEADER_SIZE : self.HEADER_SIZE + payload_len]
        checksum = hashlib.blake2s(payload_mv, digest_size=8).digest()
        
        # Header layout (64 bytes):
        # uint32 magic, uint32 slab_id, uint32 dim, uint32 payload_len, 8 bytes checksum, 40 bytes padding
        header = struct.pack("<IIII8s40x", self.MAGIC, slab_id, dim, payload_len, checksum)
        
        # Write header in-place
        self.shm.seek(0)
        self.shm.write(header)
        self.shm.flush()
        
        return {
            "slab_id": slab_id,
            "dim": dim,
            "bytes_written": payload_len,
            "checksum": checksum.hex()
        }

    def read_tensor(self, expected_slab_id: int = 1) -> tuple[np.ndarray, dict]:
        """
        True Zero-Copy read of continuous tensor from shared memory slab.
        Returns a direct numpy view referencing the memory-mapped physical RAM.
        """
        self.shm.seek(0)
        header_raw = self.shm.read(self.HEADER_SIZE)
        magic, slab_id, dim, payload_len, checksum = struct.unpack("<IIII8s40x", header_raw)
        
        if magic != self.MAGIC:
            raise ValueError(f"Invalid PMTP magic number: {hex(magic)}")
        if slab_id != expected_slab_id:
            raise ValueError(f"Slab ID mismatch: found {slab_id}, expected {expected_slab_id}")
            
        # Verify checksum directly over buffer memoryview without allocating bytes
        shm_mv = memoryview(self.shm)
        payload_mv = shm_mv[self.HEADER_SIZE : self.HEADER_SIZE + payload_len]
        computed_chk = hashlib.blake2s(payload_mv, digest_size=8).digest()
        if computed_chk != checksum:
            raise ValueError("PMTP BLAKE2s checksum failure in shared memory slab")
            
        # Return direct zero-copy view referencing mmap buffer
        tensor_view = np.frombuffer(self.shm, dtype=np.float64, count=dim, offset=self.HEADER_SIZE)
        metadata = {
            "slab_id": slab_id,
            "dim": dim,
            "checksum": checksum.hex()
        }
        return tensor_view, metadata

    def close(self):
        if self.shm:
            try:
                self.shm.close()
            except BufferError:
                # Active zero-copy views still exist; mmap will be garbage collected safely
                pass
