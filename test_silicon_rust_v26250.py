import ctypes
import numpy as np
import time
import sys

dll_path = r"E:\POLYDIM_EINSOF\ENTREGA_2026_10_10_V26250\Auditoria_Externa\libpolydim_rust_v26250.dll"
try:
    lib = ctypes.CDLL(dll_path)
except Exception as e:
    print(f"FAILED to load Rust DLL {dll_path}: {e}")
    sys.exit(1)

class PolydimF64ConstView(ctypes.Structure):
    _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]

class PolydimF64MutView(ctypes.Structure):
    _fields_ = [("ptr", ctypes.POINTER(ctypes.c_double)), ("len", ctypes.c_uint64)]

lib.polydim_sphere_project_v26155.argtypes = [PolydimF64ConstView, PolydimF64MutView]
lib.polydim_sphere_project_v26155.restype = ctypes.c_int32

lib.polydim_sphere_transport_v26155.argtypes = [
    PolydimF64ConstView, PolydimF64ConstView, PolydimF64ConstView, PolydimF64MutView
]
lib.polydim_sphere_transport_v26155.restype = ctypes.c_int32

print("=== SILICON AUDIT SUITE: RUST CORE V26250 (ZOMBIE BUFFER CLEANUP + SCALE-INVARIANT TANGENCY) ===")

D = 100000
x = np.random.randn(D).astype(np.float64)
out = np.zeros(D, dtype=np.float64)

in_v = PolydimF64ConstView(x.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), D)
out_v = PolydimF64MutView(out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), D)

t0 = time.perf_counter()
ret = lib.polydim_sphere_project_v26155(in_v, out_v)
t1 = time.perf_counter()

assert ret == 0, f"Project failed: {ret}"
norm_out = np.linalg.norm(out)
diff_norm = abs(norm_out - 1.0)
print(f"[PASS] Rust D={D} Project: Exit Code 0 | Latency: {(t1-t0)*1000:.3f} ms | ||out|| - 1 = {diff_norm:.2e}")
assert diff_norm < 1e-13

# Test Scale-invariant small norm tangency
x_pt = np.random.randn(1000).astype(np.float64)
x_pt /= np.linalg.norm(x_pt)
y_pt = np.random.randn(1000).astype(np.float64)
y_pt /= np.linalg.norm(y_pt)

v_rand = np.random.randn(1000).astype(np.float64)
v_tang = v_rand - np.dot(x_pt, v_rand) * x_pt
v_small = v_tang * (1e-8 / np.linalg.norm(v_tang))
out_t = np.zeros(1000, dtype=np.float64)

xv = PolydimF64ConstView(x_pt.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
yv = PolydimF64ConstView(y_pt.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
vv = PolydimF64ConstView(v_small.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
ov = PolydimF64MutView(out_t.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)

ret = lib.polydim_sphere_transport_v26155(xv, yv, vv, ov)
print(f"[PASS] Rust Small Norm Tangency (||v||=1e-8): Exit Code {ret}")
assert ret == 0

# Test defective tangency rejection
v_bad = v_small + x_pt * 1e-10
vv_bad = PolydimF64ConstView(v_bad.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
ret_bad = lib.polydim_sphere_transport_v26155(xv, yv, vv_bad, ov)
print(f"[PASS] Rust Defective Tangency Rejection: Exit Code {ret_bad} (Expected POLYDIM_NOT_TANGENT = -6)")
assert ret_bad == -6

# Test zero vector tangency rejection
v_zero = np.zeros(1000, dtype=np.float64)
vv_zero = PolydimF64ConstView(v_zero.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), 1000)
ret_zero = lib.polydim_sphere_transport_v26155(xv, yv, vv_zero, ov)
print(f"[PASS] Rust Zero Vector Tangency Rejection: Exit Code {ret_zero} (Expected POLYDIM_ZERO_VECTOR = -7)")
assert ret_zero == -7

print("\nALL SILICON TESTS FOR RUST CORE V26250 COMPLETED WITH EXIT CODE 0.")
sys.exit(0)
