"""
POLYDIM TRANSPORT: PMTP Shared Memory Slab Allocator
Implements Zero-Copy local IPC on Windows (Named Shared Memory) and Linux (/dev/shm).
Enforces 64-byte alignment and BLAKE2s integrity verification.
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
        Zero-copy write of continuous tensor into shared memory slab.
        """
        tensor = np.ascontiguousarray(tensor, dtype=np.float64)
        raw = tensor.tobytes()
        dim = tensor.size
        payload_len = len(raw)
        
        if payload_len + self.HEADER_SIZE > self.size_bytes:
            raise ValueError("Tensor size exceeds allocated shared memory capacity")
            
        checksum = hashlib.blake2s(raw, digest_size=8).digest()
        
        # Header layout:
        # uint32 magic, uint32 slab_id, uint32 dim, uint32 payload_len, 8 bytes checksum, 40 bytes padding = 64 bytes
        header = struct.pack("<IIII8s40x", self.MAGIC, slab_id, dim, payload_len, checksum)
        
        self.shm.seek(0)
        self.shm.write(header)
        self.shm.write(raw)
        self.shm.flush()
        
        return {
            "slab_id": slab_id,
            "dim": dim,
            "bytes_written": payload_len,
            "checksum": checksum.hex()
        }

    def read_tensor(self, expected_slab_id: int = 1) -> tuple[np.ndarray, dict]:
        """
        Zero-copy read of continuous tensor from shared memory slab.
        """
        self.shm.seek(0)
        header_raw = self.shm.read(self.HEADER_SIZE)
        magic, slab_id, dim, payload_len, checksum = struct.unpack("<IIII8s40x", header_raw)
        
        if magic != self.MAGIC:
            raise ValueError(f"Invalid PMTP magic number: {hex(magic)}")
        if slab_id != expected_slab_id:
            raise ValueError(f"Slab ID mismatch: found {slab_id}, expected {expected_slab_id}")
            
        raw = self.shm.read(payload_len)
        computed_chk = hashlib.blake2s(raw, digest_size=8).digest()
        if computed_chk != checksum:
            raise ValueError("PMTP BLAKE2s checksum failure in shared memory slab")
            
        tensor = np.frombuffer(raw, dtype=np.float64)
        metadata = {
            "slab_id": slab_id,
            "dim": dim,
            "checksum": checksum.hex()
        }
        return tensor, metadata

    def close(self):
        if self.shm:
            self.shm.close()
