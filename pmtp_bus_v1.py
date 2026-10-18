"""
PMTP Shared Memory Bus V1 — Zero-Gusano Real Implementation
============================================================
5 workers concurrentes operan sobre tensores en S^(D-1) via
multiprocessing.shared_memory. Cero archivos intermedios.
Solo el resultado final se materializa en stdout.

(c) 2026 POLYDIM-EINSOF / Ariel Garcia Traba — UTN-FRBA
"""
import struct
import time
import math
import os
import sys
from multiprocessing import Process, shared_memory, Barrier, Value
import ctypes

# ──────────────────────────────────────────────────────────
# PMTP Constants
# ──────────────────────────────────────────────────────────
PMTP_MAGIC = 0x504D5450  # 'PMTP'
PMTP_VERSION = 4
DESCRIPTOR_SIZE = 64      # bytes: magic(4)+ver(2)+dtype(2)+D(4)+K(4)+offset(8)+length(8)+checksum(8)+flags(4)+pad(20)
MAX_SLABS = 16
DTYPE_F64 = 1

# ──────────────────────────────────────────────────────────
# PmtpTensorDescriptor — packed binary struct
# ──────────────────────────────────────────────────────────
DESC_FMT = '<IHHIIQQdI20s'  # little-endian, 64 bytes total

def pack_descriptor(dim, k, offset, length, checksum=0.0, flags=0):
    return struct.pack(DESC_FMT,
        PMTP_MAGIC, PMTP_VERSION, DTYPE_F64,
        dim, k, offset, length, checksum, flags,
        b'\x00' * 20)

def unpack_descriptor(buf):
    magic, ver, dtype, dim, k, offset, length, checksum, flags, _ = struct.unpack(DESC_FMT, buf)
    assert magic == PMTP_MAGIC, f"Bad magic: {magic:#x}"
    assert ver == PMTP_VERSION, f"Bad version: {ver}"
    return {'dim': dim, 'k': k, 'offset': offset, 'length': length, 'checksum': checksum, 'flags': flags}

# ──────────────────────────────────────────────────────────
# PmtpSlabAllocator — real shared memory manager
# ──────────────────────────────────────────────────────────
class PmtpSlabAllocator:
    """Manages named shared memory segments for inter-process tensor exchange."""

    def __init__(self, prefix='pmtp'):
        self._prefix = prefix
        self._slabs = {}

    def alloc(self, slab_id, nbytes):
        name = f"{self._prefix}_{slab_id:04x}"
        try:
            # Clean up any stale segment with same name
            old = shared_memory.SharedMemory(name=name, create=False)
            old.close()
            old.unlink()
        except FileNotFoundError:
            pass
        shm = shared_memory.SharedMemory(name=name, create=True, size=nbytes)
        self._slabs[slab_id] = shm
        return shm

    def attach(self, slab_id):
        name = f"{self._prefix}_{slab_id:04x}"
        shm = shared_memory.SharedMemory(name=name, create=False)
        return shm

    def free(self, slab_id):
        if slab_id in self._slabs:
            shm = self._slabs.pop(slab_id)
            shm.close()
            shm.unlink()

    def free_all(self):
        for sid in list(self._slabs.keys()):
            self.free(sid)

# ──────────────────────────────────────────────────────────
# Shared memory tensor read/write helpers (zero-copy concept)
# ──────────────────────────────────────────────────────────
def write_f64_vector(shm, offset, vec):
    """Write a list of float64 values into shared memory at byte offset."""
    data = struct.pack(f'<{len(vec)}d', *vec)
    shm.buf[offset:offset + len(data)] = data

def read_f64_vector(shm, offset, count):
    """Read count float64 values from shared memory at byte offset."""
    nbytes = count * 8
    data = bytes(shm.buf[offset:offset + nbytes])
    return list(struct.unpack(f'<{count}d', data))

def write_f64_scalar(shm, offset, val):
    struct.pack_into('<d', shm.buf, offset, val)

def read_f64_scalar(shm, offset):
    return struct.unpack_from('<d', shm.buf, offset)[0]

# ──────────────────────────────────────────────────────────
# Neumaier compensated dot product (pure Python)
# ──────────────────────────────────────────────────────────
def dot_neumaier(a, b):
    s = 0.0
    c = 0.0
    for i in range(len(a)):
        prod = a[i] * b[i]
        t = s + prod
        if abs(s) >= abs(prod):
            c += (s - t) + prod
        else:
            c += (prod - t) + s
        s = t
    return s + c

# ──────────────────────────────────────────────────────────
# Worker 1: Sphere Projection (S^{D-1})
# ──────────────────────────────────────────────────────────
def worker_sphere_project(slab_name, dim, vec_offset, result_offset, status_offset, barrier):
    """Project vector onto S^{D-1} in shared memory. Zero disk."""
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=30)
        v = read_f64_vector(shm, vec_offset, dim)
        # Neumaier norm
        norm_sq = dot_neumaier(v, v)
        norm = math.sqrt(norm_sq)
        if norm < 1e-300:
            norm = 1e-300  # subnormal guard
        inv_norm = 1.0 / norm
        projected = [x * inv_norm for x in v]
        write_f64_vector(shm, result_offset, projected)
        # Verify: ||projected||^2
        check = dot_neumaier(projected, projected)
        write_f64_scalar(shm, status_offset, check)  # should be ~1.0
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 2: Parallel Transport (Levi-Civita on S^{D-1})
# ──────────────────────────────────────────────────────────
def worker_parallel_transport(slab_name, dim, base_offset, tangent_offset, result_offset, status_offset, barrier):
    """Levi-Civita parallel transport on S^{D-1}. Haversine-stable."""
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=30)
        p = read_f64_vector(shm, base_offset, dim)
        xi = read_f64_vector(shm, tangent_offset, dim)
        # xi_norm via Neumaier
        xi_norm_sq = dot_neumaier(xi, xi)
        xi_norm = math.sqrt(xi_norm_sq)
        if xi_norm < 1e-14:
            # Near-zero tangent: transport is identity
            write_f64_vector(shm, result_offset, xi)
            write_f64_scalar(shm, status_offset, 0.0)
            return
        theta = xi_norm
        half_theta = theta / 2.0
        sin_theta = math.sin(theta)
        # Haversine: vers = 2*sin^2(theta/2) instead of (1-cos(theta))
        vers = 2.0 * math.sin(half_theta) ** 2
        xi_unit = [x / xi_norm for x in xi]
        # transported = -vers*p + sin(theta)*xi_unit (tangent component)
        # This is the velocity after transport along geodesic
        transported = [(-vers * p[i]) + (sin_theta * xi_unit[i]) for i in range(dim)]
        write_f64_vector(shm, result_offset, transported)
        # Status: deviation from tangency <transported, endpoint>
        endpoint = [(math.cos(theta) * p[i]) + (sin_theta * xi_unit[i]) for i in range(dim)]
        tangency = dot_neumaier(transported, endpoint)
        write_f64_scalar(shm, status_offset, abs(tangency))
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 3: Norm Validator (exhaustive Neumaier audit)
# ──────────────────────────────────────────────────────────
def worker_norm_validator(slab_name, dim, vec_offset, status_offset, barrier):
    """Validate ||v|| == 1.0 with Neumaier precision."""
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=30)
        v = read_f64_vector(shm, vec_offset, dim)
        norm_sq = dot_neumaier(v, v)
        deviation = abs(norm_sq - 1.0)
        write_f64_scalar(shm, status_offset, deviation)
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 4: Checksum Computer (descriptor integrity)
# ──────────────────────────────────────────────────────────
def worker_checksum(slab_name, dim, vec_offset, desc_offset, status_offset, barrier):
    """Compute Fletcher-64 style checksum of tensor data, write to descriptor."""
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=30)
        v = read_f64_vector(shm, vec_offset, dim)
        # Fletcher-style sum
        sum1 = 0.0
        sum2 = 0.0
        for x in v:
            sum1 += abs(x)
            sum2 += sum1
        checksum = sum1 + sum2 * 1e-15
        # Update descriptor checksum field
        desc_buf = bytes(shm.buf[desc_offset:desc_offset + DESCRIPTOR_SIZE])
        desc = unpack_descriptor(desc_buf)
        new_desc = pack_descriptor(desc['dim'], desc['k'], desc['offset'], desc['length'], checksum, desc['flags'] | 0x01)
        shm.buf[desc_offset:desc_offset + DESCRIPTOR_SIZE] = new_desc
        write_f64_scalar(shm, status_offset, checksum)
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 5: Stiefel Column Orthogonality Check
# ──────────────────────────────────────────────────────────
def worker_stiefel_ortho(slab_name, dim, k, matrix_offset, status_offset, barrier):
    """Check ||X^T X - I_k||_inf for a D x K matrix in shared memory."""
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=30)
        # Read K columns of dimension D
        cols = []
        for j in range(k):
            col_offset = matrix_offset + j * dim * 8
            cols.append(read_f64_vector(shm, col_offset, dim))
        # Compute X^T X (K x K)
        max_dev = 0.0
        for i in range(k):
            for j in range(k):
                dot = dot_neumaier(cols[i], cols[j])
                expected = 1.0 if i == j else 0.0
                dev = abs(dot - expected)
                if dev > max_dev:
                    max_dev = dev
        write_f64_scalar(shm, status_offset, max_dev)
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# ORCHESTRATOR — Main
# ──────────────────────────────────────────────────────────
def main():
    t0 = time.perf_counter()

    D = 10000       # dimension
    K = 4           # Stiefel columns
    SLAB_ID = 0x7F01

    # Memory layout in slab:
    # [0..64)           descriptor
    # [64..64+D*8)      input vector v (D doubles)
    # [64+D*8..64+2*D*8) projected vector (result of worker 1)
    # [64+2*D*8..64+3*D*8) tangent vector xi
    # [64+3*D*8..64+4*D*8) transported vector (result of worker 2)
    # [64+4*D*8..64+4*D*8+K*D*8) Stiefel matrix (K columns of D)
    # [status area] 5 x 8 bytes for worker status scalars

    desc_offset = 0
    v_offset = DESCRIPTOR_SIZE
    proj_offset = v_offset + D * 8
    xi_offset = proj_offset + D * 8
    transport_offset = xi_offset + D * 8
    stiefel_offset = transport_offset + D * 8
    status_base = stiefel_offset + K * D * 8
    total_bytes = status_base + 5 * 8

    alloc = PmtpSlabAllocator()
    try:
        shm = alloc.alloc(SLAB_ID, total_bytes)
        slab_name = shm.name

        # Write descriptor
        desc = pack_descriptor(D, K, v_offset, D * 8)
        shm.buf[desc_offset:desc_offset + DESCRIPTOR_SIZE] = desc

        # Deterministic PRNG for reproducible finite vectors (LCG)
        def lcg_vec(dim, seed):
            """Generate dim values in (-1,1) deterministically."""
            s = seed & 0xFFFFFFFF
            out = []
            for _ in range(dim):
                s = (s * 1664525 + 1013904223) & 0xFFFFFFFF
                out.append((s / 2147483648.0) - 1.0)  # map to (-1, 1)
            return out

        # Generate input vector on S^{D-1}
        v = lcg_vec(D, 42)
        norm = math.sqrt(dot_neumaier(v, v))
        v = [x / norm for x in v]
        write_f64_vector(shm, v_offset, v)

        # Generate tangent vector (orthogonal to v via Gram-Schmidt)
        xi_raw = lcg_vec(D, 0xDEAD)
        proj_coeff = dot_neumaier(xi_raw, v)
        xi = [xi_raw[i] - proj_coeff * v[i] for i in range(D)]
        xi_norm = math.sqrt(dot_neumaier(xi, xi))
        if xi_norm > 1e-12:
            xi = [x * (0.1 / xi_norm) for x in xi]  # ~0.1 rad geodesic
        write_f64_vector(shm, xi_offset, xi)

        # Generate Stiefel matrix: K orthonormal columns via Gram-Schmidt
        stiefel_cols = []
        for j in range(K):
            col = lcg_vec(D, 100 + j)
            for prev in stiefel_cols:
                dp = dot_neumaier(col, prev)
                col = [col[i] - dp * prev[i] for i in range(D)]
            cn = math.sqrt(dot_neumaier(col, col))
            col = [x / cn for x in col]
            stiefel_cols.append(col)
            write_f64_vector(shm, stiefel_offset + j * D * 8, col)

        # PHASE 1: Workers 1,3,4,5 — all read from input vectors (no dependencies)
        barrier_p1 = Barrier(4, timeout=60)
        phase1 = [
            Process(target=worker_sphere_project,
                    args=(slab_name, D, v_offset, proj_offset, status_base + 0, barrier_p1)),
            Process(target=worker_norm_validator,
                    args=(slab_name, D, v_offset, status_base + 16, barrier_p1)),
            Process(target=worker_checksum,
                    args=(slab_name, D, v_offset, desc_offset, status_base + 24, barrier_p1)),
            Process(target=worker_stiefel_ortho,
                    args=(slab_name, D, K, stiefel_offset, status_base + 32, barrier_p1)),
        ]
        for w in phase1:
            w.start()
        for w in phase1:
            w.join(timeout=120)

        # PHASE 2: Worker 2 — reads projected vector from Worker 1's output
        barrier_p2 = Barrier(1, timeout=60)
        w2 = Process(target=worker_parallel_transport,
                     args=(slab_name, D, proj_offset, xi_offset, transport_offset, status_base + 8, barrier_p2))
        w2.start()
        w2.join(timeout=120)

        # Read results from shared memory — zero file I/O
        norm_check = read_f64_scalar(shm, status_base + 0)       # Worker 1: ||projected||^2
        tangency_dev = read_f64_scalar(shm, status_base + 8)     # Worker 2: tangency deviation
        norm_dev = read_f64_scalar(shm, status_base + 16)        # Worker 3: ||v||^2 - 1
        checksum = read_f64_scalar(shm, status_base + 24)        # Worker 4: Fletcher checksum
        stiefel_dev = read_f64_scalar(shm, status_base + 32)     # Worker 5: ||X^T X - I||_inf

        elapsed = time.perf_counter() - t0

        # Exit code logic
        exit_code = 0
        if abs(norm_check - 1.0) > 1e-12:
            exit_code = 1
        if norm_dev > 1e-12:
            exit_code = 2
        if stiefel_dev > 1e-12:
            exit_code = 3

        # Single materialization to stdout — the ONLY 1D collapse
        print(f"PMTP_BUS_V1|D={D}|K={K}|slab=0x{SLAB_ID:04X}|bytes={total_bytes}")
        print(f"W1_sphere_proj_norm_sq={norm_check:.16e}")
        print(f"W2_transport_tangency_dev={tangency_dev:.16e}")
        print(f"W3_input_norm_dev={norm_dev:.16e}")
        print(f"W4_fletcher_checksum={checksum:.6e}")
        print(f"W5_stiefel_ortho_dev={stiefel_dev:.16e}")
        print(f"elapsed_s={elapsed:.3f}|exit_code={exit_code}")

        sys.exit(exit_code)

    finally:
        alloc.free_all()


if __name__ == '__main__':
    main()
