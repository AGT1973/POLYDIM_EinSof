"""
PMTP Shared Memory Bus V2 — C++ DLL Native Dispatch
=====================================================
Evolución de V1: los workers despachan operaciones geométricas a la DLL
nativa C++20 (libpolydim_cpp_v26255.dll) via ctypes FFI. El cómputo pesado
(dot_neumaier, sphere_project, sphere_transport) corre en código nativo.
Los workers Python son meros despachadores: leen/escriben en shared memory
y llaman a la DLL. Cero serialización. Cero archivos intermedios.

Escalable a D=100,000+ (limitado por RAM de 16GB del AMD A4).

(c) 2026 POLYDIM-EINSOF / Ariel García Traba — UTN-FRBA
"""
import struct
import time
import math
import os
import sys
import ctypes
from multiprocessing import Process, shared_memory, Barrier
from pathlib import Path

# ──────────────────────────────────────────────────────────
# PMTP Protocol Constants
# ──────────────────────────────────────────────────────────
PMTP_MAGIC    = 0x504D5450
PMTP_VERSION  = 4
DESC_SIZE     = 64
DTYPE_F64     = 1
DESC_FMT      = '<IHHIIQQdI20s'

def pack_desc(dim, k, offset, length, checksum=0.0, flags=0):
    return struct.pack(DESC_FMT, PMTP_MAGIC, PMTP_VERSION, DTYPE_F64,
                       dim, k, offset, length, checksum, flags, b'\x00'*20)

def unpack_desc(buf):
    m, v, dt, dim, k, off, ln, cs, fl, _ = struct.unpack(DESC_FMT, buf)
    return dim, k, off, ln, cs, fl

# ──────────────────────────────────────────────────────────
# Shared Memory I/O (binary F64)
# ──────────────────────────────────────────────────────────
def shm_write_vec(shm, offset, vec):
    n = len(vec)
    shm.buf[offset:offset + n*8] = struct.pack(f'<{n}d', *vec)

def shm_read_vec(shm, offset, n):
    return list(struct.unpack(f'<{n}d', bytes(shm.buf[offset:offset+n*8])))

def shm_write_f64(shm, offset, val):
    struct.pack_into('<d', shm.buf, offset, val)

def shm_read_f64(shm, offset):
    return struct.unpack_from('<d', shm.buf, offset)[0]

# ──────────────────────────────────────────────────────────
# PmtpSlabAllocator
# ──────────────────────────────────────────────────────────
class SlabAlloc:
    def __init__(self, pfx='pmtp'):
        self._pfx = pfx; self._m = {}
    def alloc(self, sid, sz):
        nm = f"{self._pfx}_{sid:04x}"
        try:
            old = shared_memory.SharedMemory(name=nm, create=False)
            old.close(); old.unlink()
        except FileNotFoundError: pass
        s = shared_memory.SharedMemory(name=nm, create=True, size=sz)
        self._m[sid] = s; return s
    def free_all(self):
        for s in self._m.values():
            s.close(); s.unlink()
        self._m.clear()

# ──────────────────────────────────────────────────────────
# DLL Loader — C++20 kernel via ctypes
# ──────────────────────────────────────────────────────────
DLL_PATH = r'E:\POLYDIM_EINSOF\libpolydim_cpp_v26255.dll'
MINGW_BIN = r'E:\varios\winlibs_gcc14_zip\mingw64\bin'

def load_polydim_dll():
    """Load the native C++20 POLYDIM kernel DLL."""
    os.add_dll_directory(MINGW_BIN)
    dll = ctypes.CDLL(DLL_PATH)

    # int polydim_dot_neumaier(const double* a, const double* b, int dim, double* result)
    dll.polydim_dot_neumaier.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_double)
    ]
    dll.polydim_dot_neumaier.restype = ctypes.c_int

    # int polydim_sphere_project(double* v, int dim)
    dll.polydim_sphere_project.argtypes = [
        ctypes.POINTER(ctypes.c_double), ctypes.c_int
    ]
    dll.polydim_sphere_project.restype = ctypes.c_int

    # int polydim_sphere_transport(const double* p, const double* xi, double* result, int dim)
    dll.polydim_sphere_transport.argtypes = [
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.c_int
    ]
    dll.polydim_sphere_transport.restype = ctypes.c_int

    return dll

# ──────────────────────────────────────────────────────────
# Neumaier fallback (pure Python, for processes that can't load DLL)
# ──────────────────────────────────────────────────────────
def py_dot_neumaier(a, b):
    s = c = 0.0
    for i in range(len(a)):
        p = a[i]*b[i]; t = s+p
        c += ((s-t)+p) if abs(s)>=abs(p) else ((p-t)+s)
        s = t
    return s+c

# ──────────────────────────────────────────────────────────
# Worker 1: Native C++ Sphere Projection
# ──────────────────────────────────────────────────────────
def w1_native_sphere_project(slab_name, D, v_off, proj_off, stat_off, barrier):
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=60)
        dll = load_polydim_dll()
        # Read vector from shared memory into ctypes array
        v_raw = bytes(shm.buf[v_off:v_off+D*8])
        arr = (ctypes.c_double * D)()
        ctypes.memmove(arr, v_raw, D*8)
        # Call C++ sphere_project IN-PLACE
        rc = dll.polydim_sphere_project(arr, D)
        # Write projected vector back to shared memory
        shm.buf[proj_off:proj_off+D*8] = bytes(arr)
        # Verify norm via C++ dot_neumaier
        result = ctypes.c_double(0.0)
        dll.polydim_dot_neumaier(arr, arr, D, ctypes.byref(result))
        shm_write_f64(shm, stat_off, result.value)
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 2: Native C++ Parallel Transport
# ──────────────────────────────────────────────────────────
def w2_native_transport(slab_name, D, base_off, xi_off, out_off, stat_off, barrier):
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=60)
        dll = load_polydim_dll()
        p_raw = bytes(shm.buf[base_off:base_off+D*8])
        xi_raw = bytes(shm.buf[xi_off:xi_off+D*8])
        p_arr = (ctypes.c_double * D)(); ctypes.memmove(p_arr, p_raw, D*8)
        xi_arr = (ctypes.c_double * D)(); ctypes.memmove(xi_arr, xi_raw, D*8)
        out_arr = (ctypes.c_double * D)()
        rc = dll.polydim_sphere_transport(p_arr, xi_arr, out_arr, D)
        shm.buf[out_off:out_off+D*8] = bytes(out_arr)
        # Tangency check: <transported, endpoint>
        # Endpoint = cos(||xi||)*p + sin(||xi||)*xi/||xi||
        xi_list = list(xi_arr); p_list = list(p_arr); out_list = list(out_arr)
        xi_norm = math.sqrt(py_dot_neumaier(xi_list, xi_list))
        if xi_norm > 1e-14:
            cos_t = math.cos(xi_norm); sin_t = math.sin(xi_norm)
            endpoint = [(cos_t*p_list[i] + sin_t*xi_list[i]/xi_norm) for i in range(D)]
            tang = abs(py_dot_neumaier(out_list, endpoint))
        else:
            tang = 0.0
        shm_write_f64(shm, stat_off, tang)
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 3: Native C++ Norm Validation
# ──────────────────────────────────────────────────────────
def w3_native_norm(slab_name, D, v_off, stat_off, barrier):
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=60)
        dll = load_polydim_dll()
        v_raw = bytes(shm.buf[v_off:v_off+D*8])
        arr = (ctypes.c_double * D)(); ctypes.memmove(arr, v_raw, D*8)
        result = ctypes.c_double(0.0)
        dll.polydim_dot_neumaier(arr, arr, D, ctypes.byref(result))
        shm_write_f64(shm, stat_off, abs(result.value - 1.0))
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 4: Descriptor Checksum (pure Python — no DLL needed)
# ──────────────────────────────────────────────────────────
def w4_checksum(slab_name, D, v_off, desc_off, stat_off, barrier):
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=60)
        v = shm_read_vec(shm, v_off, D)
        s1 = s2 = 0.0
        for x in v: s1 += abs(x); s2 += s1
        cs = s1 + s2*1e-15
        # Update descriptor
        d = pack_desc(D, 0, v_off, D*8, cs, 0x01)
        shm.buf[desc_off:desc_off+DESC_SIZE] = d
        shm_write_f64(shm, stat_off, cs)
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# Worker 5: Stiefel Orthogonality via Native C++ dot
# ──────────────────────────────────────────────────────────
def w5_native_stiefel(slab_name, D, K, mat_off, stat_off, barrier):
    shm = shared_memory.SharedMemory(name=slab_name, create=False)
    try:
        barrier.wait(timeout=60)
        dll = load_polydim_dll()
        cols = []
        for j in range(K):
            off = mat_off + j*D*8
            raw = bytes(shm.buf[off:off+D*8])
            arr = (ctypes.c_double * D)(); ctypes.memmove(arr, raw, D*8)
            cols.append(arr)
        max_dev = 0.0
        for i in range(K):
            for j in range(K):
                r = ctypes.c_double(0.0)
                dll.polydim_dot_neumaier(cols[i], cols[j], D, ctypes.byref(r))
                expected = 1.0 if i==j else 0.0
                dev = abs(r.value - expected)
                if dev > max_dev: max_dev = dev
        shm_write_f64(shm, stat_off, max_dev)
    finally:
        shm.close()

# ──────────────────────────────────────────────────────────
# ORCHESTRATOR
# ──────────────────────────────────────────────────────────
def main():
    import resource_check
    t0 = time.perf_counter()

    # Configurable dimension — scale up as RAM allows
    D = 100000      # 100K dimensions
    K = 4
    SLAB = 0x8F01

    # Memory layout
    v_off     = DESC_SIZE
    proj_off  = v_off + D*8
    xi_off    = proj_off + D*8
    tr_off    = xi_off + D*8
    st_off    = tr_off + D*8
    stat_base = st_off + K*D*8
    total     = stat_base + 5*8

    ram_mb = total / (1024*1024)

    alloc = SlabAlloc()
    try:
        shm = alloc.alloc(SLAB, total)
        nm = shm.name

        # Write descriptor
        shm.buf[0:DESC_SIZE] = pack_desc(D, K, v_off, D*8)

        # LCG PRNG — deterministic, finite, fast
        def lcg(dim, seed):
            s = seed & 0xFFFFFFFF; out = []
            for _ in range(dim):
                s = (s*1664525+1013904223) & 0xFFFFFFFF
                out.append(s/2147483648.0 - 1.0)
            return out

        # Generate and normalize input vector
        v = lcg(D, 42)
        n = math.sqrt(py_dot_neumaier(v,v))
        v = [x/n for x in v]
        shm_write_vec(shm, v_off, v)

        # Tangent vector orthogonal to v
        xi = lcg(D, 0xDEAD)
        pc = py_dot_neumaier(xi, v)
        xi = [xi[i]-pc*v[i] for i in range(D)]
        xn = math.sqrt(py_dot_neumaier(xi,xi))
        if xn > 1e-12: xi = [x*0.1/xn for x in xi]
        shm_write_vec(shm, xi_off, xi)

        # Stiefel matrix K orthonormal columns
        scols = []
        for j in range(K):
            c = lcg(D, 100+j)
            for p in scols:
                dp = py_dot_neumaier(c,p)
                c = [c[i]-dp*p[i] for i in range(D)]
            cn = math.sqrt(py_dot_neumaier(c,c))
            c = [x/cn for x in c]
            scols.append(c)
            shm_write_vec(shm, st_off+j*D*8, c)

        t_setup = time.perf_counter() - t0

        # PHASE 1: Workers 1,3,4,5 — independent reads from input
        b1 = Barrier(4, timeout=120)
        p1 = [
            Process(target=w1_native_sphere_project, args=(nm,D,v_off,proj_off,stat_base,b1)),
            Process(target=w3_native_norm,           args=(nm,D,v_off,stat_base+16,b1)),
            Process(target=w4_checksum,              args=(nm,D,v_off,0,stat_base+24,b1)),
            Process(target=w5_native_stiefel,        args=(nm,D,K,st_off,stat_base+32,b1)),
        ]
        for w in p1: w.start()
        for w in p1: w.join(timeout=300)

        # PHASE 2: Worker 2 — depends on Worker 1 output
        b2 = Barrier(1, timeout=120)
        w2 = Process(target=w2_native_transport, args=(nm,D,proj_off,xi_off,tr_off,stat_base+8,b2))
        w2.start(); w2.join(timeout=300)

        # Read metrics from shared memory
        s1 = shm_read_f64(shm, stat_base)      # ||proj||^2
        s2 = shm_read_f64(shm, stat_base+8)    # tangency dev
        s3 = shm_read_f64(shm, stat_base+16)   # norm dev
        s4 = shm_read_f64(shm, stat_base+24)   # checksum
        s5 = shm_read_f64(shm, stat_base+32)   # stiefel dev

        elapsed = time.perf_counter() - t0
        ec = 0
        if abs(s1-1.0) > 1e-12: ec=1
        if s3 > 1e-12: ec=2
        if s5 > 1e-12: ec=3

        print(f"PMTP_BUS_V2_NATIVE|D={D}|K={K}|slab=0x{SLAB:04X}|ram_mb={ram_mb:.1f}|setup_s={t_setup:.3f}")
        print(f"W1_cpp_sphere_norm={s1:.16e}")
        print(f"W2_cpp_transport_tang={s2:.16e}")
        print(f"W3_cpp_norm_dev={s3:.16e}")
        print(f"W4_py_checksum={s4:.6e}")
        print(f"W5_cpp_stiefel_dev={s5:.16e}")
        print(f"total_s={elapsed:.3f}|exit_code={ec}")
        sys.exit(ec)

    finally:
        alloc.free_all()

if __name__ == '__main__':
    main()
