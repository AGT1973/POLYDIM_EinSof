import ctypes
import os
import time
import psutil

dll_path = r"E:\POLYDIM_EINSOF\ENTREGAS\ENTREGA_2026_10_31_V_turing_018\02_FUENTES_KERNELS_SILICIO\pmtp_tri_segment.dll"
if not os.path.exists(dll_path):
    print(f"ERROR: DLL not found at {dll_path}")
    exit(1)

tri = ctypes.CDLL(dll_path)

# Signatures
tri.pmtp_tri_create.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint64, ctypes.c_uint16, ctypes.c_uint32]
tri.pmtp_tri_create.restype = ctypes.c_void_p

tri.pmtp_tri_open.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint64, ctypes.c_uint16, ctypes.c_uint32]
tri.pmtp_tri_open.restype = ctypes.c_void_p

tri.pmtp_tri_publish.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64, ctypes.c_double]
tri.pmtp_tri_publish.restype = ctypes.c_int

tri.pmtp_tri_acquire_lease.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
tri.pmtp_tri_acquire_lease.restype = ctypes.c_int

tri.pmtp_tri_release_lease.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
tri.pmtp_tri_release_lease.restype = ctypes.c_int

tri.pmtp_tri_get_leased_ptr.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
tri.pmtp_tri_get_leased_ptr.restype = ctypes.c_void_p

tri.pmtp_tri_close.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
tri.pmtp_tri_close.restype = ctypes.c_int

def run_tests():
    t0 = time.perf_counter()
    proc = psutil.Process()
    ram_before = proc.memory_info().rss / (1024 * 1024)
    checks_passed = 0

    session_name = b"pmtp_sota_d04_d13_test"
    slab_id = 999
    num_elements = 1024
    dtype_id = 1 # float64
    max_readers = 8

    # 1. Create publisher
    pub_ctx = tri.pmtp_tri_create(session_name, slab_id, num_elements, dtype_id, max_readers)
    assert pub_ctx, "Failed to create publisher context"
    checks_passed += 1

    # 2. Publish initial data
    data = (ctypes.c_double * num_elements)(*[float(i) for i in range(num_elements)])
    rc = tri.pmtp_tri_publish(pub_ctx, ctypes.byref(data), num_elements, 1.0)
    assert rc == 0, f"Publish failed with rc={rc}"
    checks_passed += 1

    # 3. Open consumer
    sub_ctx = tri.pmtp_tri_open(session_name, slab_id, num_elements, dtype_id, 0)
    assert sub_ctx, "Failed to open consumer context"
    checks_passed += 1

    # 4. Acquire lease
    gen = ctypes.c_uint64(0)
    cookie = ctypes.c_uint64(0)
    rc = tri.pmtp_tri_acquire_lease(sub_ctx, ctypes.byref(gen), ctypes.byref(cookie))
    assert rc == 0 and cookie.value != 0 and gen.value > 0, f"Acquire failed: rc={rc}, cookie={cookie.value}"
    ptr = tri.pmtp_tri_get_leased_ptr(sub_ctx, cookie.value)
    assert ptr is not None, "get_leased_ptr returned null for valid cookie"
    checks_passed += 1

    # 5. Release lease
    rc = tri.pmtp_tri_release_lease(sub_ctx, cookie.value)
    assert rc == 0, f"release_lease failed with rc={rc}"
    checks_passed += 1

    # 6. Replay test: double release of consumed cookie
    rc_replay = tri.pmtp_tri_release_lease(sub_ctx, cookie.value)
    assert rc_replay != 0, f"Security violation: double release succeeded with rc={rc_replay}"
    checks_passed += 1

    # 7. Stale pointer access test
    stale_ptr = tri.pmtp_tri_get_leased_ptr(sub_ctx, cookie.value)
    assert stale_ptr is None or stale_ptr == 0, "Security violation: get_leased_ptr succeeded with released cookie"
    checks_passed += 1

    # 8. Forged cookie test
    gen2 = ctypes.c_uint64(0)
    cookie2 = ctypes.c_uint64(0)
    rc = tri.pmtp_tri_acquire_lease(sub_ctx, ctypes.byref(gen2), ctypes.byref(cookie2))
    assert rc == 0 and cookie2.value != 0, "Acquire 2 failed"

    # Forge cookie by altering nonce
    forged_cookie = cookie2.value ^ 0x0000000000000001
    forged_ptr = tri.pmtp_tri_get_leased_ptr(sub_ctx, forged_cookie)
    assert forged_ptr is None or forged_ptr == 0, "Security violation: forged cookie returned valid pointer"

    rc_forged_rel = tri.pmtp_tri_release_lease(sub_ctx, forged_cookie)
    assert rc_forged_rel != 0, "Security violation: forged cookie release succeeded"

    # Valid release of cookie2
    rc = tri.pmtp_tri_release_lease(sub_ctx, cookie2.value)
    assert rc == 0, "Legitimate cookie2 release failed"
    checks_passed += 1

    # 9. Clean shutdown
    rc_sub_close = tri.pmtp_tri_close(sub_ctx, 1000)
    assert rc_sub_close == 0, f"sub close failed rc={rc_sub_close}"
    rc_pub_close = tri.pmtp_tri_close(pub_ctx, 1000)
    assert rc_pub_close == 0, f"pub close failed rc={rc_pub_close}"

    t1 = time.perf_counter()
    ram_after = proc.memory_info().rss / (1024 * 1024)
    dt_ms = (t1 - t0) * 1000.0
    ram_mb = max(0.0, ram_after - ram_before)

    print(f"SILICON_TUPLE: (Exit Code: 0, Latency: {dt_ms:.2f} ms, RAM: {ram_mb:.2f} MB, Checks: {checks_passed}/{checks_passed} passed)")
    print("ALL D04 & D13 ANTI-REPLAY AND LEASE SECURITY TESTS PASSED ON WINDOWS AGY HOST")

if __name__ == "__main__":
    run_tests()
