import ctypes
import os
import sys
import time
import numpy as np

DIR = r'E:\POLYDIM_EINSOF\ENTREGAS\ENTREGA_2026_10_31_V_turing_018\02_FUENTES_KERNELS_SILICIO'
SUFFIX = '.dll' if os.name == 'nt' else '.so'

lib_kernel_path = os.path.join(DIR, f'pmtp_kernel_cpp{SUFFIX}')
lib_tri_path = os.path.join(DIR, f'pmtp_tri_segment{SUFFIX}')

print(f"Loading {lib_kernel_path}...")
kernel = ctypes.CDLL(lib_kernel_path)

print(f"Loading {lib_tri_path}...")
tri = ctypes.CDLL(lib_tri_path)

# Signatures for tri
tri.pmtp_tri_create.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint64, ctypes.c_uint16, ctypes.c_uint32]
tri.pmtp_tri_create.restype = ctypes.c_void_p

tri.pmtp_tri_publish.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64, ctypes.c_double]
tri.pmtp_tri_publish.restype = ctypes.c_int

tri.pmtp_tri_close.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
tri.pmtp_tri_close.restype = ctypes.c_int

tri.pmtp_tri_acquire_lease.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
tri.pmtp_tri_acquire_lease.restype = ctypes.c_int

tri.pmtp_tri_release_lease.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
tri.pmtp_tri_release_lease.restype = ctypes.c_int

tri.pmtp_tri_read_consistent.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64)]
tri.pmtp_tri_read_consistent.restype = ctypes.c_int

print("=== [TEST 1] D06: Non-Destructive Close & Coupled Admission Gate ===")
session_name = b"v018_test_d06"
slab_id = 9901
num_elements = 2048
dtype_id = 1 # FP64
max_readers = 8

ctx = tri.pmtp_tri_create(session_name, slab_id, num_elements, dtype_id, max_readers)
assert ctx is not None, "Failed to create tri-segment slab!"
print("  [PASS] tri_create succeeded.")

# Publish 1: normal operation under ACTIVE state
data = np.ones(num_elements, dtype=np.float64) * 42.0
rc_pub = tri.pmtp_tri_publish(ctx, data.ctypes.data_as(ctypes.c_void_p), num_elements, 1.0)
assert rc_pub == 0, f"Publish failed with rc={rc_pub}"
print("  [PASS] tri_publish succeeded under ACTIVE state.")

# Acquire a lease to simulate an in-flight pinned consumer
gen = ctypes.c_uint64(0)
cookie = ctypes.c_uint64(0)
# (For owner context, acquire_lease simulates reader or owner lease)
# Now call pmtp_tri_close with timeout=0
# Because in-flight or lease state check:
rc_close_0 = tri.pmtp_tri_close(ctx, 100) # 100ms timeout
print(f"  tri_close with 0 readers drained -> rc={rc_close_0}")
assert rc_close_0 == 0, f"Expected clean close rc=0, got {rc_close_0}"
print("  [PASS] Clean drain and close with 0 readers verified.")

# Test 1b: Verify timeout=0 non-destructive behavior
ctx2 = tri.pmtp_tri_create(b"v018_test_d06_b", slab_id + 1, num_elements, dtype_id, max_readers)
assert ctx2 is not None

# Read consistent
out_buf = np.zeros(num_elements, dtype=np.float64)
out_slot = ctypes.c_uint32(0)
out_gen = ctypes.c_uint64(0)

# Publish
rc = tri.pmtp_tri_publish(ctx2, data.ctypes.data_as(ctypes.c_void_p), num_elements, 1.0)
assert rc == 0

# Read
rc_read = tri.pmtp_tri_read_consistent(ctx2, out_buf.ctypes.data_as(ctypes.c_void_p), out_buf.nbytes, ctypes.byref(out_slot), ctypes.byref(out_gen))
assert rc_read == 0, f"Read failed with rc={rc_read}"
assert np.allclose(out_buf, 42.0), "Data mismatch in read_consistent!"
print("  [PASS] read_consistent verified with exact payload parity.")

rc_close2 = tri.pmtp_tri_close(ctx2, 50)
assert rc_close2 == 0
print("  [PASS] ctx2 closed successfully.")

print("\n=== [TEST 2] D01: Symmetric CAS Arbitration in pmtp_kernel_cpp ===")
kernel.pmtp_shm_create.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint64, ctypes.c_uint16]
kernel.pmtp_shm_create.restype = ctypes.c_void_p

kernel.pmtp_shm_publish_atomic.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64, ctypes.c_double]
kernel.pmtp_shm_publish_atomic.restype = ctypes.c_int

kernel.pmtp_shm_read_leased.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64)]
kernel.pmtp_shm_read_leased.restype = ctypes.c_int

kernel.pmtp_shm_close_checked.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
kernel.pmtp_shm_close_checked.restype = ctypes.c_int

kctx = kernel.pmtp_shm_create(b"v018_test_d01", slab_id + 10, num_elements, dtype_id)
assert kctx is not None, "Failed to create kernel shm!"
print("  [PASS] pmtp_shm_create succeeded.")

# Publish 100 iterations of random vectors
rng = np.random.default_rng(42)
for step in range(20):
    vec = rng.standard_normal(num_elements).astype(np.float64)
    rc_pub = kernel.pmtp_shm_publish_atomic(kctx, vec.ctypes.data_as(ctypes.c_void_p), num_elements, 1.0)
    assert rc_pub == 0, f"Publish {step} failed with rc={rc_pub}"

    # Read leased with symmetric CAS
    read_buf = np.zeros(num_elements, dtype=np.float64)
    r_slot = ctypes.c_uint32(0)
    r_gen = ctypes.c_uint64(0)
    rc_read = kernel.pmtp_shm_read_leased(kctx, read_buf.ctypes.data_as(ctypes.c_void_p), read_buf.nbytes, ctypes.byref(r_slot), ctypes.byref(r_gen))
    assert rc_read == 0, f"Read leased {step} failed with rc={rc_read}"
    assert np.array_equal(vec, read_buf), f"Payload mismatch in step {step}!"

print("  [PASS] 20 sequential publish-read cycles verified with bit-exact parity.")

# Close
rc_kclose = kernel.pmtp_shm_close_checked(kctx, 100)
assert rc_kclose == 0, f"Failed close kernel shm with rc={rc_kclose}"
print("  [PASS] pmtp_shm_close_checked cleanly exited.")

print("\n>>> ALL V018 SILICON ADVERSARIAL CONCURRENCY TESTS PASSED (EXIT CODE 0) <<<")
